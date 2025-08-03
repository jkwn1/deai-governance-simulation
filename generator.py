import random
from itertools import product
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class GovernanceMechanism:
    """Represents a governance mechanism with all 7 parameters"""
    voting_method: str  # 'simple_majority', 'weighted', 'quadratic'
    stake_method: str   # 'token_based', 'reputation_based', 'hybrid', 'equal_weight', 'proof_of_work'
    slashing_method: str  # 'none', 'linear', 'exponential', 'progressive'
    consensus_threshold: float  # 0.50 to 1.0
    slashing_rate: float  # 0.0 to 0.3
    sybil_resistance: float  # 0.0 to 1.0
    max_voting_power: float  # 0.1 to 1.0 (10% to 100%)
    
    def __hash__(self):
        """Make mechanism hashable so we can track duplicates"""
        return hash((
            self.voting_method, self.stake_method, self.slashing_method,
            self.consensus_threshold, self.slashing_rate, 
            self.sybil_resistance, self.max_voting_power
        ))

class MechanismGenerator:
    def __init__(self):
        # Define all possible parameter values
        self.voting_methods = ['simple_majority', 'weighted', 'quadratic']
        
        self.stake_methods = ['token_based', 'reputation_based', 'hybrid', 
                             'equal_weight']
        
        self.slashing_methods = ['none', 'linear', 'exponential', 'progressive']
        
        # 13 consensus thresholds from 50% to 100%
        self.consensus_thresholds = [0.50, 0.51, 0.55, 0.60, 0.65, 0.70, 0.75, 
                                   0.80, 0.85, 0.90, 0.95, 0.98, 1.0]
        
        # 7 slashing rates from 0% to 30%
        self.slashing_rates = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
        
        # 9 sybil resistance values
        self.sybil_resistance_values = [0.0, 0.125, 0.25, 0.375, 0.5, 
                                       0.625, 0.75, 0.875, 1.0]
        
        # 10 max voting power values from 10% to 100%
        self.max_voting_power_values = [0.1, 0.2, 0.3, 0.4, 0.5, 
                                       0.6, 0.7, 0.8, 0.9, 1.0]
        
        self.generated_mechanisms = set()
    
    def calculate_total_possible_mechanisms(self) -> int:
        """Calculate total number of possible unique mechanisms"""
        return (len(self.voting_methods) * 
                len(self.stake_methods) * 
                len(self.slashing_methods) * 
                len(self.consensus_thresholds) * 
                len(self.slashing_rates) * 
                len(self.sybil_resistance_values) * 
                len(self.max_voting_power_values))
    
    def generate_random_mechanism(self) -> GovernanceMechanism:
        """Generate a single random mechanism"""
        mechanism = GovernanceMechanism(
            voting_method=random.choice(self.voting_methods),
            stake_method=random.choice(self.stake_methods),
            slashing_method=random.choice(self.slashing_methods),
            consensus_threshold=random.choice(self.consensus_thresholds),
            slashing_rate=random.choice(self.slashing_rates),
            sybil_resistance=random.choice(self.sybil_resistance_values),
            max_voting_power=random.choice(self.max_voting_power_values)
        )
        return mechanism
    
    def generate_unique_mechanisms(self, num_mechanisms: int) -> List[GovernanceMechanism]:
        """
        Generate a specified number of unique random mechanisms.
        Returns fewer if we can't generate enough unique ones.
        """
        mechanisms = []
        max_attempts = num_mechanisms * 10  # Prevent infinite loops
        attempts = 0
        
        total_possible = self.calculate_total_possible_mechanisms()
        print(f"Total possible unique mechanisms: {total_possible:,}")
        
        while len(mechanisms) < num_mechanisms and attempts < max_attempts:
            mechanism = self.generate_random_mechanism()
            
            # Check if this exact mechanism was already generated
            if mechanism not in self.generated_mechanisms:
                self.generated_mechanisms.add(mechanism)
                mechanisms.append(mechanism)
            
            attempts += 1
        
        if attempts >= max_attempts:
            print(f"Warning: Could only generate {len(mechanisms)} unique mechanisms "
                  f"out of {num_mechanisms} requested after {max_attempts} attempts")
        
        return mechanisms
    
    def generate_systematic_sample(self, sample_size: int) -> List[GovernanceMechanism]:
        """
        Generate a systematic sample that covers parameter space well.
        This ensures we test diverse combinations rather than just random ones.
        """
        mechanisms = []
        
        # Calculate how many mechanisms we should generate per parameter combination
        # This is a simplified systematic sampling
        total_possible = self.calculate_total_possible_mechanisms()
        
        if sample_size >= total_possible:
            # If we want more mechanisms than possible, generate all possible ones
            print("Generating all possible mechanisms...")
            for combo in product(self.voting_methods, self.stake_methods, 
                                self.slashing_methods, self.consensus_thresholds,
                                self.slashing_rates, self.sybil_resistance_values,
                                self.max_voting_power_values):
                mechanism = GovernanceMechanism(*combo)
                mechanisms.append(mechanism)
        else:
            # Generate systematic sample with some randomness
            mechanisms = self.generate_unique_mechanisms(sample_size)
        
        return mechanisms

    def generate_all_mechanisms(self) -> List[GovernanceMechanism]:
        """
        Generate every single possible mechanism combination.
        Returns all 491,400 possible mechanisms.
        """
        print("Generating all possible mechanisms... This may take a moment.")
    
        mechanisms = []
        total_count = 0
    
        for voting_method in self.voting_methods:
            for stake_method in self.stake_methods:
                for slashing_method in self.slashing_methods:
                    for consensus_threshold in self.consensus_thresholds:
                        for slashing_rate in self.slashing_rates:
                            for sybil_resistance in self.sybil_resistance_values:
                                for max_voting_power in self.max_voting_power_values:
                                    mechanism = GovernanceMechanism(
                                        voting_method=voting_method,
                                        stake_method=stake_method,
                                        slashing_method=slashing_method,
                                        consensus_threshold=consensus_threshold,
                                        slashing_rate=slashing_rate,
                                        sybil_resistance=sybil_resistance,
                                        max_voting_power=max_voting_power
                                    )
                                    mechanisms.append(mechanism)
                                    total_count += 1
                                
                                    # Progress indicator for large generation
                                    if total_count % 50000 == 0:
                                        print(f"Generated {total_count:,} mechanisms...")
    
        print(f"Successfully generated all {total_count:,} possible mechanisms")
        return mechanisms

    def generate_real_world_mechanism_classes(self) -> List[GovernanceMechanism]:
        """Generate all variations of real-world mechanism classes"""
        mechanisms = []
       
        # 1. Bittensor Class: weighted + token_based + 0.51 + 0.95 + 1.0
        # Vary: slashing_method, slashing_rate
        for slashing_method in self.slashing_methods:
            for slashing_rate in self.slashing_rates:
                mechanisms.append(GovernanceMechanism(
                    'weighted', 'token_based', slashing_method, 0.51, slashing_rate, 0.95, 1.0
                ))
       
        # 2. Gensyn Class: simple_majority + token_based + linear + 0.50 + 0.95 + 1.0  
        # Vary: slashing_rate
        for slashing_rate in self.slashing_rates:
            mechanisms.append(GovernanceMechanism(
                'simple_majority', 'token_based', 'linear', 0.50, slashing_rate, 0.95, 1.0
            ))
        
        # 3. Ocean Class: Complete mechanism (no variations)
        mechanisms.append(GovernanceMechanism(
            'weighted', 'token_based', 'none', 0.50, 0.0, 0.95, 1.0
        ))
        
        # 4. SingularityNET Class: quadratic + hybrid + 0.65 + 0.95 + 1.0
        # Vary: slashing_method, slashing_rate  
        for slashing_method in self.slashing_methods:
            for slashing_rate in self.slashing_rates:
                mechanisms.append(GovernanceMechanism(
                    'quadratic', 'hybrid', slashing_method, 0.65, slashing_rate, 0.95, 1.0
                ))
       
        return mechanisms

    def generate_mixed_with_real_world_classes(self, num_mechanisms: int) -> List[GovernanceMechanism]:
        """Generate mechanisms including all real-world class variations"""
        mechanisms = []
       
        # Add all real-world class variations
        real_world_classes = self.generate_real_world_mechanism_classes()
        mechanisms.extend(real_world_classes)
       
        print(f"Added {len(real_world_classes)} real-world class mechanisms:")
        print(f"  • Bittensor class: {4 * 7} variations (4 slashing methods × 7 slashing rates)")
        print(f"  • Gensyn class: {7} variations (1 slashing method × 7 slashing rates)")  
        print(f"  • Ocean class: {1} complete mechanism")
        print(f"  • SingularityNET class: {4 * 7} variations (4 slashing methods × 7 slashing rates)")
       
        # Fill remaining with random mechanisms
        remaining = max(0, num_mechanisms - len(real_world_classes))
        if remaining > 0:
            random_mechanisms = self.generate_unique_mechanisms(remaining)
            mechanisms.extend(random_mechanisms)
            print(f"  • Random mechanisms: {len(random_mechanisms)}")
       
        return mechanisms[:num_mechanisms]

# Example usage and testing
if __name__ == "__main__":
    generator = MechanismGenerator()
    
    # Generate 100 unique mechanisms for testing
    test_mechanisms = generator.generate_unique_mechanisms(100)
    
    print(f"Generated {len(test_mechanisms)} unique mechanisms")
    print("\nFirst 5 mechanisms:")
    for i, mechanism in enumerate(test_mechanisms[:5]):
        print(f"{i+1}: {mechanism}")
    
    # Show parameter distribution
    voting_methods_count = {}
    stake_methods_count = {}
    
    for mechanism in test_mechanisms:
        voting_methods_count[mechanism.voting_method] = voting_methods_count.get(mechanism.voting_method, 0) + 1
        stake_methods_count[mechanism.stake_method] = stake_methods_count.get(mechanism.stake_method, 0) + 1
    
    print(f"\nVoting methods distribution: {voting_methods_count}")
    print(f"Stake methods distribution: {stake_methods_count}")