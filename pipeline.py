import time
import json
import csv
import multiprocessing as mp
import argparse
from typing import List, Dict, Any, Tuple
from dataclasses import asdict

from generator import MechanismGenerator, GovernanceMechanism
from simulation import SimulationEngine, AttackType, AttackResult
from agents import AttackScenarioGenerator

def test_single_mechanism(mechanism: GovernanceMechanism) -> Tuple[GovernanceMechanism, Dict[AttackType, AttackResult]]:
    """Test a single mechanism - designed for multiprocessing"""
    engine = SimulationEngine()
    results = {}
    
    for attack_type in AttackType:
        result = engine.run_attack_scenario(mechanism, attack_type)
        results[attack_type] = result
    
    return mechanism, results

class GovernancePipeline:
    """Main pipeline to generate mechanisms and run break-tests with multiprocessing"""
    
    def __init__(self, num_processes: int = None):
        self.generator = MechanismGenerator()
        self.num_processes = num_processes or mp.cpu_count()
        
    def run_pipeline(self, num_mechanisms: int, output_file: str = None) -> Dict[str, Any]:
        """
        Main pipeline function with multiprocessing:
        1. Generate mechanisms (including real-world classes)
        2. Run break-tests on each (in parallel)
        3. Collect and return results
        """
        print(f"🚀 Starting governance mechanism break-test pipeline")
        print(f"📊 Testing {num_mechanisms} mechanisms")
        print(f"🔄 Using {self.num_processes} processes for parallel execution")
        print(f"🎯 Each mechanism will face 4 attack types × 30 instances × 20 rounds = 2,400 votes")
        print(f"📈 Total votes to simulate: {num_mechanisms * 2400:,}")
        
        start_time = time.time()
        
        # Step 1: Generate mechanisms including real-world classes
        print(f"\n⚙️  Generating {num_mechanisms} mechanisms (including real-world classes)...")
        mechanisms = self.generator.generate_mixed_with_real_world_classes(num_mechanisms)
        
        print(f"✅ Generated {len(mechanisms)} mechanisms")
        
        # Step 2: Run break-tests in parallel
        print(f"\n🔥 Running break-tests with {self.num_processes} parallel processes...")
        
        with mp.Pool(processes=self.num_processes) as pool:
            results_list = pool.map(test_single_mechanism, mechanisms)
        
        # Convert list of tuples back to dictionary
        all_results = dict(results_list)
        
        # Step 3: Process and save results
        summary = self._create_summary(all_results)
        
        # Step 4: Save results if requested
        if output_file:
            self._save_results(all_results, summary, output_file)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n🎉 Pipeline completed in {duration:.2f} seconds")
        print(f"📊 Results summary:")
        print(f"   • Mechanisms tested: {len(all_results)}")
        print(f"   • Total votes simulated: {summary['total_votes']:,}")
        print(f"   • Average success rate: {summary['average_success_rate']:.3f}")
        print(f"   • Best mechanism success rate: {summary['best_success_rate']:.3f}")
        print(f"   • Worst mechanism success rate: {summary['worst_success_rate']:.3f}")
        
        return {
            'mechanisms': mechanisms,
            'results': all_results,
            'summary': summary,
            'duration': duration
        }
    
    def _create_summary(self, all_results: Dict[GovernanceMechanism, Dict[AttackType, AttackResult]]) -> Dict[str, Any]:
        """Create summary statistics from all results"""
        
        total_votes = 0
        total_correct = 0
        mechanism_scores = []
        
        for mechanism, attack_results in all_results.items():
            mechanism_total_votes = 0
            mechanism_correct = 0
            
            # Aggregate across all attack types for this mechanism
            for attack_type, result in attack_results.items():
                mechanism_total_votes += result.total_votes
                mechanism_correct += result.correct_outcomes
            
            # Calculate mechanism success rate
            mechanism_success_rate = mechanism_correct / mechanism_total_votes if mechanism_total_votes > 0 else 0
            mechanism_scores.append(mechanism_success_rate)
            
            total_votes += mechanism_total_votes
            total_correct += mechanism_correct
        
        return {
            'total_mechanisms': len(all_results),
            'total_votes': total_votes,
            'total_correct': total_correct,
            'average_success_rate': total_correct / total_votes if total_votes > 0 else 0,
            'best_success_rate': max(mechanism_scores) if mechanism_scores else 0,
            'worst_success_rate': min(mechanism_scores) if mechanism_scores else 0,
        }
    
    def _save_results(self, all_results: Dict[GovernanceMechanism, Dict[AttackType, AttackResult]], 
                     summary: Dict[str, Any], output_file: str):
        """Save results as CSV files with rankings"""
        base_name = output_file.split('.')[0]
        
        # Step 1: Create mechanism performance data
        mechanism_data = []
        real_world_mechanisms = []
        
        for mechanism, attack_results in all_results.items():
            # Calculate overall score and individual attack scores
            total_votes = sum(result.total_votes for result in attack_results.values())
            total_correct = sum(result.correct_outcomes for result in attack_results.values())
            overall_score = total_correct / total_votes if total_votes > 0 else 0
            
            mechanism_info = {
                'mechanism': mechanism,
                'overall_score': overall_score,
                'collusion_score': attack_results[AttackType.COLLUSION].success_rate,
                'whale_score': attack_results[AttackType.WHALE].success_rate,
                'sybil_score': attack_results[AttackType.SYBIL].success_rate,
                'bias_score': attack_results[AttackType.BIAS].success_rate,
            }
            
            mechanism_data.append(mechanism_info)
            
            # Check if this is a real-world mechanism class
            if self._is_real_world_mechanism(mechanism):
                real_world_mechanisms.append(mechanism_info)
        
        # Step 2: Sort all mechanisms by overall score (descending)
        mechanism_data.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Step 3: Save top 150 mechanisms
        top_150_file = f"{base_name}_top_150.csv"
        self._save_top_150_csv(mechanism_data[:150], top_150_file)
        
        # Step 4: Sort real-world mechanisms and add top 150 rankings
        real_world_mechanisms.sort(key=lambda x: x['overall_score'], reverse=True)
        
        # Add top 150 rankings to real-world mechanisms
        top_150_scores = {mech['overall_score']: i+1 for i, mech in enumerate(mechanism_data[:150])}
        for rw_mech in real_world_mechanisms:
            rw_mech['top_150_rank'] = top_150_scores.get(rw_mech['overall_score'], None)
        
        # Step 5: Save real-world mechanisms ranking
        real_world_file = f"{base_name}_real_world_ranking.csv"
        self._save_real_world_csv(real_world_mechanisms, real_world_file)
        
        print(f"💾 Results saved:")
        print(f"   • Top 150 mechanisms: {top_150_file}")
        print(f"   • Real-world mechanism ranking: {real_world_file}")
    
    def _is_real_world_mechanism(self, mechanism: GovernanceMechanism) -> bool:
        """Check if mechanism belongs to a real-world class"""
        # Bittensor class
        if (mechanism.voting_method == 'weighted' and 
            mechanism.stake_method == 'token_based' and 
            mechanism.consensus_threshold == 0.51 and 
            mechanism.sybil_resistance == 0.95 and 
            mechanism.max_voting_power == 1.0):
            return True
        
        # Gensyn class
        if (mechanism.voting_method == 'simple_majority' and 
            mechanism.stake_method == 'token_based' and 
            mechanism.slashing_method == 'linear' and
            mechanism.consensus_threshold == 0.50 and 
            mechanism.sybil_resistance == 0.95 and 
            mechanism.max_voting_power == 1.0):
            return True
        
        # Ocean class
        if (mechanism.voting_method == 'weighted' and 
            mechanism.stake_method == 'token_based' and 
            mechanism.slashing_method == 'none' and
            mechanism.consensus_threshold == 0.50 and 
            mechanism.slashing_rate == 0.0 and
            mechanism.sybil_resistance == 0.95 and 
            mechanism.max_voting_power == 1.0):
            return True
        
        # SingularityNET class
        if (mechanism.voting_method == 'quadratic' and 
            mechanism.stake_method == 'hybrid' and 
            mechanism.consensus_threshold == 0.65 and 
            mechanism.sybil_resistance == 0.95 and 
            mechanism.max_voting_power == 1.0):
            return True
        
        return False
    
    def _save_top_150_csv(self, top_mechanisms: List[Dict], filename: str):
        """Save top 150 mechanisms to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = [
                'rank', 'overall_score', 'collusion_score', 'whale_score', 'sybil_score', 'bias_score',
                'voting_method', 'stake_method', 'slashing_method', 'consensus_threshold', 
                'slashing_rate', 'sybil_resistance', 'max_voting_power'
            ]
            writer.writerow(header)
            
            # Data rows
            for i, mech_data in enumerate(top_mechanisms):
                mechanism = mech_data['mechanism']
                row = [
                    i + 1,  # rank
                    round(mech_data['overall_score'], 4),
                    round(mech_data['collusion_score'], 4),
                    round(mech_data['whale_score'], 4),
                    round(mech_data['sybil_score'], 4),
                    round(mech_data['bias_score'], 4),
                    mechanism.voting_method,
                    mechanism.stake_method,
                    mechanism.slashing_method,
                    mechanism.consensus_threshold,
                    mechanism.slashing_rate,
                    mechanism.sybil_resistance,
                    mechanism.max_voting_power
                ]
                writer.writerow(row)
    
    def _save_real_world_csv(self, real_world_mechanisms: List[Dict], filename: str):
        """Save real-world mechanism ranking to CSV"""
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Header
            header = [
                'real_world_rank', 'overall_score', 'collusion_score', 'whale_score', 'sybil_score', 'bias_score',
                'top_150_rank', 'voting_method', 'stake_method', 'slashing_method', 'consensus_threshold', 
                'slashing_rate', 'sybil_resistance', 'max_voting_power'
            ]
            writer.writerow(header)
            
            # Data rows
            for i, mech_data in enumerate(real_world_mechanisms):
                mechanism = mech_data['mechanism']
                row = [
                    i + 1,  # real_world_rank
                    round(mech_data['overall_score'], 4),
                    round(mech_data['collusion_score'], 4),
                    round(mech_data['whale_score'], 4),
                    round(mech_data['sybil_score'], 4),
                    round(mech_data['bias_score'], 4),
                    mech_data['top_150_rank'] if mech_data['top_150_rank'] else '',  # top_150_rank
                    mechanism.voting_method,
                    mechanism.stake_method,
                    mechanism.slashing_method,
                    mechanism.consensus_threshold,
                    mechanism.slashing_rate,
                    mechanism.sybil_resistance,
                    mechanism.max_voting_power
                ]
                writer.writerow(row)

def main():
    """Command line interface for the pipeline"""
    parser = argparse.ArgumentParser(description='Governance Mechanism Break-Test Pipeline')
    parser.add_argument('--num_mechanisms', type=int, default=1000, 
                       help='Number of mechanisms to test (use -1 for all possible)')
    parser.add_argument('--num_processes', type=int, default=None,
                       help='Number of CPU processes to use (default: auto-detect)')
    parser.add_argument('--output', type=str, default='governance_results',
                       help='Output file base name')
    
    args = parser.parse_args()
    
    # Handle "all mechanisms" case
    num_mechanisms = 393120 if args.num_mechanisms == -1 else args.num_mechanisms
    
    # Create and run pipeline
    pipeline = GovernancePipeline(num_processes=args.num_processes)
    
    results = pipeline.run_pipeline(
        num_mechanisms=num_mechanisms,
        output_file=args.output
    )
    
    print(f"\n🎯 Analysis complete! Check the CSV files for detailed rankings.")

if __name__ == "__main__":
    main()