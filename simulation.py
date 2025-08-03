import random
import math
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from generator import GovernanceMechanism
from agents import Agent, AgentType, AttackScenarioGenerator

class AttackType(Enum):
    COLLUSION = "collusion"
    WHALE = "whale"
    SYBIL = "sybil"
    BIAS = "bias"

@dataclass
class Proposal:
    """Represents a proposal to be voted on"""
    proposal_id: int
    quality: float  # 0.0 to 1.0, objectively good if >= 0.5
    
    def is_objectively_good(self) -> bool:
        return self.quality >= 0.5

@dataclass
class VoteResult:
    """Results of a single vote"""
    proposal: Proposal
    passed: bool
    total_voting_power: float
    yes_voting_power: float
    no_voting_power: float
    votes_cast: Dict[int, bool]  # agent_id -> vote
    agents_slashed: List[int]  # agent_ids that got slashed
    correct_outcome: bool  # whether the outcome matched objective quality

@dataclass
class AttackResult:
    """Results of an attack scenario (30 instances with 20 rounds each)"""
    attack_type: AttackType
    mechanism: GovernanceMechanism
    total_votes: int
    correct_outcomes: int
    success_rate: float  # correct_outcomes / total_votes

class VotingSystem:
    """Handles the core voting mechanics with all mechanism parameters"""
    
    def __init__(self, mechanism: GovernanceMechanism):
        self.mechanism = mechanism
    
    def calculate_voting_power(self, agent: Agent) -> float:
        """Calculate an agent's voting power based on mechanism parameters"""
        effective_stake = agent.get_effective_stake()
        
        # Apply stake method
        if self.mechanism.stake_method == 'equal_weight':
            base_power = 1.0  # Everyone gets equal power regardless of stake
        elif self.mechanism.stake_method == 'token_based':
            base_power = effective_stake
        elif self.mechanism.stake_method == 'reputation_based':
            base_power = effective_stake  # Same as token for our purposes
        elif self.mechanism.stake_method == 'hybrid':
            base_power = (effective_stake + 1.0) / 2.0  # Average of stake and equal weight
        else:
            raise ValueError(f"Unknown stake method: {self.mechanism.stake_method}")
        
        # Apply voting method
        if self.mechanism.voting_method == 'simple_majority':
            voting_power = 1.0  # Everyone gets 1 vote regardless of stake
        elif self.mechanism.voting_method == 'weighted':
            voting_power = base_power
        elif self.mechanism.voting_method == 'quadratic':
            voting_power = math.sqrt(base_power)
        else:
            raise ValueError(f"Unknown voting method: {self.mechanism.voting_method}")
        
        return voting_power
    
    def apply_sybil_resistance(self, agent: Agent, voting_power: float) -> float:
        """Apply sybil resistance to reduce fake account influence"""
        if agent.agent_type == AgentType.SYBIL:
            # Sybil resistance chance of vote being ignored completely
            if random.random() < self.mechanism.sybil_resistance:
                return 0.0  # Vote is completely ignored
        
        return voting_power
    
    def apply_max_voting_power_cap(self, agents: List[Agent], voting_powers: Dict[int, float]) -> Dict[int, float]:
        """Cap any single agent's influence at max_voting_power percentage"""
        total_power = sum(voting_powers.values())
        if total_power == 0:
            return voting_powers
        
        max_allowed_power = total_power * self.mechanism.max_voting_power
        capped_powers = {}
        
        for agent_id, power in voting_powers.items():
            if power > max_allowed_power:
                capped_powers[agent_id] = max_allowed_power
            else:
                capped_powers[agent_id] = power
        
        return capped_powers
    
    def conduct_vote(self, agents: List[Agent], proposal: Proposal) -> VoteResult:
        """Conduct a complete vote with all mechanism parameters applied"""
        
        # Step 1: Calculate base voting powers
        voting_powers = {}
        votes_cast = {}
        
        for agent in agents:
            # Get agent's vote
            vote = agent.vote_on_proposal(proposal.quality)
            votes_cast[agent.agent_id] = vote
            
            # Calculate voting power
            power = self.calculate_voting_power(agent)
            
            # Apply sybil resistance
            power = self.apply_sybil_resistance(agent, power)
            
            voting_powers[agent.agent_id] = power
        
        # Step 2: Apply max voting power cap
        voting_powers = self.apply_max_voting_power_cap(agents, voting_powers)
        
        # Step 3: Tally votes
        yes_power = 0.0
        no_power = 0.0
        total_power = 0.0
        
        for agent_id, vote in votes_cast.items():
            power = voting_powers[agent_id]
            total_power += power
            
            if vote:  # YES vote
                yes_power += power
            else:  # NO vote
                no_power += power
        
        # Step 4: Determine if proposal passes based on consensus threshold
        if total_power == 0:
            passed = False  # No valid votes
            yes_percentage = 0.0
        else:
            yes_percentage = yes_power / total_power
            passed = yes_percentage >= self.mechanism.consensus_threshold
        
        # Step 5: Determine if outcome is correct
        should_pass = proposal.is_objectively_good()
        correct_outcome = (passed == should_pass)
        
        # Step 6: Apply slashing if wrong outcome occurred
        agents_slashed = []
        if not correct_outcome:
            agents_slashed = self.apply_slashing(agents, votes_cast, proposal, passed)
        
        return VoteResult(
            proposal=proposal,
            passed=passed,
            total_voting_power=total_power,
            yes_voting_power=yes_power,
            no_voting_power=no_power,
            votes_cast=votes_cast,
            agents_slashed=agents_slashed,
            correct_outcome=correct_outcome
        )
    
    def apply_slashing(self, agents: List[Agent], votes_cast: Dict[int, bool], proposal: Proposal, proposal_passed: bool) -> List[int]:
        """Apply slashing to agents who voted for the wrong outcome"""
        agents_slashed = []
        
        if self.mechanism.slashing_method == 'none' or self.mechanism.slashing_rate == 0.0:
            return agents_slashed
        
        # Find agents who voted for the outcome that happened
        agents_by_id = {agent.agent_id: agent for agent in agents}
        
        for agent_id, vote in votes_cast.items():
            agent = agents_by_id[agent_id]
            
            # If proposal passed and agent voted YES, or proposal failed and agent voted NO
            if ((proposal_passed and not proposal.is_objectively_good() and vote) or 
    (not proposal_passed and proposal.is_objectively_good() and not vote)):
                # This agent supported the wrong outcome, apply slashing
                slash_amount = self.calculate_slash_amount(agent)
                agent.apply_slashing(slash_amount)
                agents_slashed.append(agent_id)

        
        return agents_slashed
    
    def calculate_slash_amount(self, agent: Agent) -> float:
        """Calculate slash amount based on slashing method and rate"""
        base_slash = agent.get_effective_stake() * self.mechanism.slashing_rate
        
        if self.mechanism.slashing_method == 'linear':
            return base_slash
        elif self.mechanism.slashing_method == 'exponential':
            # Exponential based on how much has been slashed before
            slash_multiplier = 1.0 + (agent.amount_slashed / agent.original_stake)
            return base_slash * slash_multiplier
        elif self.mechanism.slashing_method == 'progressive':
            # Progressive: more slashing for agents who have been slashed more
            times_slashed = agent.amount_slashed / (self.mechanism.slashing_rate * agent.original_stake) if self.mechanism.slashing_rate > 0 else 0
            progressive_multiplier = 1.0 + (times_slashed * 0.5)  # Increase by 50% for each previous slash
            return base_slash * progressive_multiplier
        else:
            return base_slash

class SimulationEngine:
    """Main simulation engine that runs break-tests against mechanisms"""
    
    def __init__(self):
        self.scenario_generator = AttackScenarioGenerator()
        self.proposal_counter = 0
    
    def generate_proposal(self) -> Proposal:
        """Generate a random proposal with quality 0.0 to 1.0"""
        self.proposal_counter += 1
        if random.random() < 0.3:  # 30% of proposals near boundary
            q = random.uniform(0.4, 0.6)  # Near the threshold
        else:
            q = random.random()  # Normal distribution
        return Proposal(
            proposal_id=self.proposal_counter, quality = q
        )
    
    def run_attack_instance(self, mechanism: GovernanceMechanism, attack_type: AttackType, 
                           agents: List[Agent], rounds: int = 20) -> List[VoteResult]:
        """Run a single attack instance (multiple rounds of voting)"""
        voting_system = VotingSystem(mechanism)
        results = []
        
        for round_num in range(rounds):
            proposal = self.generate_proposal()
            result = voting_system.conduct_vote(agents, proposal)
            results.append(result)
        
        return results
    
    def run_attack_scenario(self, mechanism: GovernanceMechanism, attack_type: AttackType, 
                           instances: int = 30, rounds_per_instance: int = 20) -> AttackResult:
        """Run complete attack scenario (30 instances, 20 rounds each)"""
        total_correct = 0
        total_votes = 0
        
        for instance in range(instances):
            # Generate fresh agents for each instance
            if attack_type == AttackType.COLLUSION:
                agents = self.scenario_generator.generate_collusion_scenario()
            elif attack_type == AttackType.WHALE:
                agents = self.scenario_generator.generate_whale_scenario()
            elif attack_type == AttackType.SYBIL:
                agents = self.scenario_generator.generate_sybil_scenario()
            elif attack_type == AttackType.BIAS:
                agents = self.scenario_generator.generate_bias_scenario()
            else:
                raise ValueError(f"Unknown attack type: {attack_type}")
            
            # Run this instance
            instance_results = self.run_attack_instance(mechanism, attack_type, agents, rounds_per_instance)
            
            # Count correct outcomes
            for result in instance_results:
                total_votes += 1
                if result.correct_outcome:
                    total_correct += 1
        
        success_rate = total_correct / total_votes if total_votes > 0 else 0.0
        
        return AttackResult(
            attack_type=attack_type,
            mechanism=mechanism,
            total_votes=total_votes,
            correct_outcomes=total_correct,
            success_rate=success_rate
        )
    
    def run_full_mechanism_test(self, mechanism: GovernanceMechanism) -> Dict[AttackType, AttackResult]:
        """Run all 4 attack types against a single mechanism"""
        results = {}
        
        print(f"Testing mechanism: {mechanism}")
        
        for attack_type in AttackType:
            print(f"  Running {attack_type.value} attack...")
            result = self.run_attack_scenario(mechanism, attack_type)
            results[attack_type] = result
            print(f"    Success rate: {result.success_rate:.3f} ({result.correct_outcomes}/{result.total_votes})")
        
        return results
    
    def run_batch_test(self, mechanisms: List[GovernanceMechanism]) -> Dict[GovernanceMechanism, Dict[AttackType, AttackResult]]:
        """Run full tests on multiple mechanisms"""
        all_results = {}
        
        print(f"Starting batch test of {len(mechanisms)} mechanisms...")
        
        for i, mechanism in enumerate(mechanisms):
            print(f"\n=== Mechanism {i+1}/{len(mechanisms)} ===")
            mechanism_results = self.run_full_mechanism_test(mechanism)
            all_results[mechanism] = mechanism_results
        
        return all_results

# Example usage and testing
if __name__ == "__main__":
    from generator import MechanismGenerator
    
    # Test with a few mechanisms
    generator = MechanismGenerator()
    test_mechanisms = generator.generate_unique_mechanisms(3)
    
    # Run simulation
    engine = SimulationEngine()
    
    # Test single mechanism
    print("=== Testing Single Mechanism ===")
    mechanism = test_mechanisms[0]
    results = engine.run_full_mechanism_test(mechanism)
    
    print(f"\nResults Summary for mechanism:")
    print(f"  Voting: {mechanism.voting_method}, Stake: {mechanism.stake_method}")
    print(f"  Threshold: {mechanism.consensus_threshold}, Slashing: {mechanism.slashing_rate}")
    
    for attack_type, result in results.items():
        print(f"  {attack_type.value}: {result.success_rate:.3f}")
    
    # Test voting system components
    print(f"\n=== Testing Voting System Components ===")
    voting_system = VotingSystem(mechanism)
    
    # Create test agents
    scenario_gen = AttackScenarioGenerator()
    test_agents = scenario_gen.generate_whale_scenario()
    
    print(f"Created {len(test_agents)} agents")
    
    # Test a vote
    proposal = Proposal(1, 0.3)  # Bad proposal
    vote_result = voting_system.conduct_vote(test_agents, proposal)
    
    print(f"Proposal quality: {proposal.quality}")
    print(f"Proposal passed: {vote_result.passed}")
    print(f"Correct outcome: {vote_result.correct_outcome}")
    print(f"Yes power: {vote_result.yes_voting_power:.2f}")
    print(f"Total power: {vote_result.total_voting_power:.2f}")
    print(f"Agents slashed: {len(vote_result.agents_slashed)}")