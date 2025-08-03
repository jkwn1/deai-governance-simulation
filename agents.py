import random
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class AgentType(Enum):
    HONEST = "honest"
    COLLUSION = "collusion"
    WHALE = "whale"
    SYBIL = "sybil"
    EMOTIONAL_BIAS = "emotional_bias"
    SYSTEMATIC_BIAS = "systematic_bias"

@dataclass
class Agent:
    """Represents an agent in the governance system"""
    agent_id: int
    agent_type: AgentType
    stake: float  # tokens/reputation/computational power
    original_stake: float = None # to track how much has been slashed
    amount_slashed: float = None  # total amount slashed so far
    honesty_threshold: float = None  # for honest agents (x value between 0.5-0.7)
    
    def __post_init__(self):
        self.original_stake = self.stake
        self.amount_slashed = 0.0
    
    def get_effective_stake(self) -> float:
        """Get current stake after slashing"""
        return max(0.0, self.stake - self.amount_slashed)
    
    def apply_slashing(self, slash_amount: float):
        """Apply slashing to this agent"""
        self.amount_slashed += slash_amount
        # Ensure we don't go below zero
        if self.amount_slashed > self.stake:
            self.amount_slashed = self.stake
    
    def vote_on_proposal(self, proposal_quality: float) -> bool:
        """
        Return True for YES vote, False for NO vote
        Based on agent type and proposal quality
        """
        if self.agent_type == AgentType.HONEST:
            return self._honest_vote(proposal_quality)
        elif self.agent_type == AgentType.COLLUSION:
            return self._collusion_vote(proposal_quality)
        elif self.agent_type == AgentType.WHALE:
            return self._whale_vote(proposal_quality)
        elif self.agent_type == AgentType.SYBIL:
            return self._sybil_vote(proposal_quality)
        elif self.agent_type == AgentType.EMOTIONAL_BIAS:
            return self._emotional_bias_vote(proposal_quality)
        elif self.agent_type == AgentType.SYSTEMATIC_BIAS:
            return self._systematic_bias_vote(proposal_quality)
        else:
            raise ValueError(f"Unknown agent type: {self.agent_type}")
    
    def _honest_vote(self, quality: float) -> bool:
        """Honest agent voting logic"""
        x = self.honesty_threshold
        
        if quality > x:
            return True  # Always vote YES
        elif 0.4 < quality < x:
            probability = quality / x
            return random.random() < probability
        elif quality < 0.4:
            probability = (quality - 0.2) / (x + 0.5)
            # Ensure probability doesn't go negative
            probability = max(0.0, probability)
            return random.random() < probability
        else:  # quality == 0.5 or quality == x
            if quality == 0.4:
                probability = (quality - 0.2) / (x + 0.5)
                probability = max(0.0, probability)
                return random.random() < probability
            else:  # quality == x
                return True
    
    def _collusion_vote(self, quality: float) -> bool:
        """Collusion agent voting logic - tries to vote incorrectly"""
        correct_vote = quality >= 0.5
        
        if 0.4 < quality < 0.6:
            # Always vote incorrectly
            return not correct_vote
        elif (0.35 < quality <= 0.4) or (0.6 <= quality < 0.65):
            # Vote incorrectly 50% of the time
            if random.random() < 0.5:
                return not correct_vote
            else:
                return correct_vote
        else:
            # Outside manipulation range, vote correctly
            return correct_vote
    
    def _whale_vote(self, quality: float) -> bool:
        """Whale agent voting logic - same as collusion"""
        return self._collusion_vote(quality)
    
    def _sybil_vote(self, quality: float) -> bool:
        """Sybil agent voting logic"""
        correct_vote = quality >= 0.5
        
        if 0.4 < quality < 0.6:
            # Always vote incorrectly
            return not correct_vote
        else:
            # Outside manipulation range, vote correctly
            return correct_vote
    
    def _emotional_bias_vote(self, quality: float) -> bool:
        """Emotional bias agent - votes incorrectly 50% of the time"""
        correct_vote = quality >= 0.5
        
        if random.random() < 0.5:
            return not correct_vote
        else:
            return correct_vote
    
    def _systematic_bias_vote(self, quality: float) -> bool:
        """Systematic bias agent - always votes incorrectly"""
        correct_vote = quality >= 0.5
        return not correct_vote

class AgentFactory:
    """Factory class for creating different types of agents"""
    
    def __init__(self):
        self.agent_counter = 0
    
    def _get_next_id(self) -> int:
        """Get next unique agent ID"""
        self.agent_counter += 1
        return self.agent_counter
    
    def create_honest_agent(self) -> Agent:
        """Create an honest agent with stake 5-10 and honesty threshold 0.5-0.7"""
        return Agent(
            agent_id=self._get_next_id(),
            agent_type=AgentType.HONEST,
            stake=random.uniform(5, 10),
            honesty_threshold=random.uniform(0.4, 0.8)
        )
    
    def create_collusion_agent(self) -> Agent:
        """Create a collusion agent with stake 5-10"""
        return Agent(
            agent_id=self._get_next_id(),
            agent_type=AgentType.COLLUSION,
            stake=random.uniform(5, 10)
        )
    
    def create_whale_agent(self) -> Agent:
        """Create a whale agent with stake 50-200"""
        return Agent(
            agent_id=self._get_next_id(),
            agent_type=AgentType.WHALE,
            stake=random.uniform(50, 200)
        )
    
    def create_sybil_agent(self) -> Agent:
        """Create a sybil agent with stake 1"""
        return Agent(
            agent_id=self._get_next_id(),
            agent_type=AgentType.SYBIL,
            stake=1.0
        )
    
    def create_emotional_bias_agent(self) -> Agent:
        """Create an emotional bias agent with stake 5-10"""
        return Agent(
            agent_id=self._get_next_id(),
            agent_type=AgentType.EMOTIONAL_BIAS,
            stake=random.uniform(5, 10)
        )
    
    def create_systematic_bias_agent(self) -> Agent:
        """Create a systematic bias agent with stake 5-10"""
        return Agent(
            agent_id=self._get_next_id(),
            agent_type=AgentType.SYSTEMATIC_BIAS,
            stake=random.uniform(5, 10)
        )

class AttackScenarioGenerator:
    """Generates agent populations for different attack scenarios"""
    
    def __init__(self):
        self.factory = AgentFactory()
    
    def generate_collusion_scenario(self) -> List[Agent]:
        """Generate 8 colluding agents + 42 honest agents"""
        agents = []
        
        # 8 collusion agents
        for _ in range(8):
            agents.append(self.factory.create_collusion_agent())
        
        # 42 honest agents
        for _ in range(42):
            agents.append(self.factory.create_honest_agent())
        
        return agents
    
    def generate_whale_scenario(self) -> List[Agent]:
        """Generate 4 whale agents + 46 honest agents"""
        agents = []
        
        # 4 whale agents
        for _ in range(4):
            agents.append(self.factory.create_whale_agent())
        
        # 46 honest agents
        for _ in range(46):
            agents.append(self.factory.create_honest_agent())
        
        return agents
    
    def generate_sybil_scenario(self) -> List[Agent]:
        """Generate 10 sybil agents + 40 honest agents"""
        agents = []
        
        # 10 sybil agents (all controlled by same person, same goals)
        for _ in range(10):
            agents.append(self.factory.create_sybil_agent())
        
        # 40 honest agents
        for _ in range(40):
            agents.append(self.factory.create_honest_agent())
        
        return agents
    
    def generate_bias_scenario(self) -> List[Agent]:
        """Generate 5 emotional + 5 systematic bias agents + 40 honest agents"""
        agents = []
        
        # 5 emotional bias agents
        for _ in range(5):
            agents.append(self.factory.create_emotional_bias_agent())
        
        # 5 systematic bias agents
        for _ in range(5):
            agents.append(self.factory.create_systematic_bias_agent())
        
        # 40 honest agents
        for _ in range(40):
            agents.append(self.factory.create_honest_agent())
        
        return agents
    
    def reset_factory(self):
        """Reset the agent factory counter for fresh scenarios"""
        self.factory = AgentFactory()

# Example usage and testing
if __name__ == "__main__":
    generator = AttackScenarioGenerator()
    
    # Test each scenario
    print("=== Collusion Scenario ===")
    collusion_agents = generator.generate_collusion_scenario()
    print(f"Total agents: {len(collusion_agents)}")
    agent_types = {}
    for agent in collusion_agents:
        agent_types[agent.agent_type.value] = agent_types.get(agent.agent_type.value, 0) + 1
    print(f"Agent distribution: {agent_types}")
    
    print("\n=== Whale Scenario ===")
    whale_agents = generator.generate_whale_scenario()
    print(f"Total agents: {len(whale_agents)}")
    agent_types = {}
    total_stake = 0
    for agent in whale_agents:
        agent_types[agent.agent_type.value] = agent_types.get(agent.agent_type.value, 0) + 1
        total_stake += agent.stake
    print(f"Agent distribution: {agent_types}")
    print(f"Total stake in system: {total_stake:.2f}")
    
    # Test voting behavior
    print("\n=== Testing Voting Behavior ===")
    test_agent = generator.factory.create_honest_agent()
    print(f"Honest agent threshold: {test_agent.honesty_threshold:.3f}")
    
    test_qualities = [0.3, 0.45, 0.55, 0.65, 0.8]
    for quality in test_qualities:
        vote = test_agent.vote_on_proposal(quality)
        print(f"Quality {quality}: Vote {'YES' if vote else 'NO'}")
    
    # Test slashing
    print(f"\nBefore slashing - Stake: {test_agent.get_effective_stake():.2f}")
    test_agent.apply_slashing(2.0)
    print(f"After slashing 2.0 - Stake: {test_agent.get_effective_stake():.2f}")