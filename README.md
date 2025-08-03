# Fair and Manipulation-Resistant Governance for Decentralized AI Systems

Agent-based simulation framework for systematically testing governance mechanisms against adversarial attacks in decentralized artificial intelligence networks.

## Repository Contents

### Core Simulation Framework
- `generator.py`: Governance mechanism configuration generation across 7 parameters
- `simulation.py`: Agent-based simulation engine with attack scenario modeling
- `pipeline.py`: Batch testing framework for large-scale mechanism evaluation
- `agents.py`: Agent behavior implementations (honest, collusion, whale, sybil, bias)

### Results Datasets
- `Ranking.csv`: Top 150 performing mechanisms with parameter configurations
- `Real World Ranking.csv`: Performance analysis of real-world platform mechanisms

## Parameters Tested

The simulation varies seven governance parameters:
- **Voting methods**: Simple majority, weighted, quadratic
- **Stake methods**: Token-based, reputation-based, hybrid, equal weight  
- **Slashing approaches**: None, linear, exponential, progressive
- **Consensus thresholds**: 50% to 100% (13 values)
- **Slashing rates**: 0% to 30% (7 values)
- **Sybil resistance**: 0% to 100% (9 values)
- **Max voting power**: 10% to 100% (10 values)

## Attack Scenarios

Each mechanism faces four adversarial conditions:
- **Collusion**: 8 coordinating agents + 42 honest agents
- **Whale attacks**: 4 high-stake agents + 46 normal agents
- **Sybil attacks**: 10 fake identities + 40 honest agents  
- **Bias attacks**: 5 systematic + 5 emotional bias agents + 40 honest agents

## Usage

Run the complete simulation:
```bash
python3 pipeline.py --num_mechanisms -1 --output results
