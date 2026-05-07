================================================================================
  Distributed Adaptive Flooding for Reducing Redundancy in
  Wireless Multi-Hop Networks
================================================================================

This repository contains the implementation and experimental code for the paper
"Distributed Adaptive Flooding for Reducing Redundancy in Wireless Multi-Hop
Networks."


TABLE OF CONTENTS
--------------------------------------------------------------------------------
1. Overview
2. Requirements
3. Installation
4. Project Structure
5. Running the Experiments
6. Reproducing Paper Results
7. Understanding the Code
8. Troubleshooting


1. OVERVIEW
--------------------------------------------------------------------------------
This project implements and evaluates a delayed-decision adaptive flooding
protocol for wireless multi-hop networks. The key innovation is using local
duplicate reception counts and network density information to probabilistically
suppress redundant forwards while maintaining delivery ratio.

Key Components:
- Adaptive flooding algorithm with delayed decision-making
- Baseline flooding for comparison
- Network density sensitivity analysis
- Performance evaluation across various topologies


2. REQUIREMENTS
--------------------------------------------------------------------------------
- Python 3.8 or higher
- pywisim (Wireless network simulator)
- matplotlib (For generating plots)
- Standard libraries: random, statistics, argparse, collections, pathlib

Install dependencies using:
    pip install -r requirements.txt

Note: If pywisim is not available via pip, you may need to install it from
source or ensure it's in the parent directory as the code expects it at:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


3. INSTALLATION
--------------------------------------------------------------------------------
Step 1: Clone this repository
    git clone <your-repository-url>
    cd EE597

Step 2: Install Python dependencies
    pip install -r requirements.txt

Step 3: Verify pywisim is available
    python -c "import pywisim; print('pywisim installed successfully')"


4. PROJECT STRUCTURE
--------------------------------------------------------------------------------
EE597/
├── README.txt                          # This file
├── requirements.txt                    # Python dependencies
├── .gitignore                          # Git ignore patterns
│
├── src/                                # Source code
│   ├── adaptive_flooding.py            # Main adaptive flooding implementation
│   ├── compare_flooding.py             # Baseline vs Adaptive comparison
│   ├── plot_results.py                 # Plot delivery ratio, forwards, receptions
│   ├── plot_sensitivity.py             # Decision delay sensitivity analysis
│   └── plot_tradeoff.py                # Performance tradeoff visualization
│
├── results/                            # Generated experimental results
│   ├── delivery_ratio.png              # Delivery ratio comparison
│   ├── total_forwards.png              # Forwarding overhead comparison
│   ├── total_receptions.png            # Total receptions comparison
│   ├── tradeoff.png                    # Efficiency-delivery tradeoff
│   └── decision_delay_sensitivity.png  # Sensitivity to decision delay
│
└── paper/                              # Research paper (PDF)
    └── Distributed Adaptive Flooding for Reducing Redundancy.pdf


5. RUNNING THE EXPERIMENTS
--------------------------------------------------------------------------------

5.1 Run Single Adaptive Flooding Simulation
--------------------------------------------
Basic usage with default parameters (30 nodes, random topology):
    python src/adaptive_flooding.py

With custom parameters:
    python src/adaptive_flooding.py --nodes 50 --area 15 --tx-range 2.0 --seed 42

Available options:
    --topology {line, random}   Network topology (default: random)
    --nodes N                   Number of nodes (default: 30)
    --area SIZE                 Area size for random topology (default: 10.0)
    --tx-range RANGE           Transmission range (default: 2.2)
    --seed SEED                Random seed (default: 42)
    --source NODE              Source node ID (default: "0")
    --until TIME               Simulation time (default: 20.0)
    --verbose                  Enable detailed logging

Example outputs:
    - Topology (neighbor lists)
    - Delivery statistics
    - Per-node forwarding and reception counts


5.2 Compare Baseline vs Adaptive Flooding
------------------------------------------
Run comprehensive comparison across multiple random seeds:
    python src/compare_flooding.py

This script will:
    - Run 20 simulations with different random seeds
    - Compare baseline flooding vs adaptive flooding
    - Report mean and standard deviation for:
        * Delivery ratio
        * Total forwards (overhead)
        * Total receptions (network load)

Expected runtime: 1-2 minutes


5.3 Generate Performance Plots
-------------------------------
Generate delivery ratio, forwards, and receptions plots:
    python src/plot_results.py

Generate sensitivity analysis plot:
    python src/plot_sensitivity.py

Generate efficiency-delivery tradeoff plot:
    python src/plot_tradeoff.py

All plots will be saved to the results/ directory.


6. REPRODUCING PAPER RESULTS
--------------------------------------------------------------------------------

To fully reproduce the results from the paper, follow these steps:

Step 1: Run Baseline vs Adaptive Comparison
    python src/compare_flooding.py > comparison_output.txt

Step 2: Generate All Plots
    python src/plot_results.py
    python src/plot_sensitivity.py
    python src/plot_tradeoff.py

Step 3: Review Results
    - Check results/ directory for generated PNG files
    - Compare with figures in the paper (paper/ directory)

Step 4: Experiment with Different Network Densities
    # Dense network (higher tx-range)
    python src/adaptive_flooding.py --tx-range 2.5 --area 10

    # Medium network
    python src/adaptive_flooding.py --tx-range 2.0 --area 12

    # Sparse network (lower tx-range)
    python src/adaptive_flooding.py --tx-range 1.5 --area 15


Key Parameters from Paper:
---------------------------
- Default: 30 nodes, area=15, tx_range=1.8
- Dense scenario: area=10, tx_range=2.5
- Medium scenario: area=12, tx_range=2.0
- Sparse scenario: area=15, tx_range=1.5
- Decision delay: 0.45s (configurable in code)
- Jitter: 0.10s


7. UNDERSTANDING THE CODE
--------------------------------------------------------------------------------

7.1 adaptive_flooding.py
------------------------
- FloodNode class: Implements the adaptive flooding protocol
    * DECISION_DELAY: Time to wait before making forward decision (0.45s)
    * JITTER: Random jitter added to decision delay (0.10s)
    * _forward_prob(): Calculates forwarding probability based on:
        - Node degree (network density)
        - Duplicate reception count
    * _decide_forward(): Makes probabilistic forwarding decision
    * on_receive(): Handles incoming messages, buffers and schedules decisions
    * flood(): Initiates a flood from this node

7.2 compare_flooding.py
-----------------------
- BaselineNode: Simple flooding (forward first copy immediately)
- AdaptiveNode: Delayed-decision adaptive flooding
- run_once(): Single simulation run
- summarize(): Compute statistics across multiple runs

7.3 Plotting Scripts
--------------------
- plot_results.py: Visualizes delivery ratio, forwards, receptions
- plot_sensitivity.py: Shows impact of decision delay parameter
- plot_tradeoff.py: Efficiency vs delivery ratio tradeoff


8. TROUBLESHOOTING
--------------------------------------------------------------------------------

Problem: "ModuleNotFoundError: No module named 'pywisim'"
Solution:
    - Ensure pywisim is installed or in parent directory
    - Check sys.path configuration in the scripts
    - Install from source if necessary

Problem: Plots not displaying
Solution:
    - Make sure matplotlib is installed: pip install matplotlib
    - If running headless, plots will be saved but not displayed
    - Comment out plt.show() if you only want saved files

Problem: Low delivery ratio in sparse networks
Solution:
    - This is expected behavior
    - Increase tx_range or decrease area size to improve connectivity
    - Check topology output to verify network is connected

Problem: Different results than paper
Solution:
    - Verify you're using the same parameters (seeds, network size, tx_range)
    - Random seed affects topology; use same seeds for reproducibility
    - Check pywisim version compatibility


================================================================================
For questions or issues, please refer to the paper or contact the authors.
================================================================================
