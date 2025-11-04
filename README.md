# ProbabilityBasedEventLogGenerator

Code related to the implementation of the paper "An Experimental Comparison of Alternative Methods for Event-Log Augmentation"

The code has been developed and tested on both Windows 11 and Linux 24.04 LTS with a Python 3.10.2 environment. All simulations were executed on a workstation equipped with a 12th Gen Intel Core i7 processor and 32 GB RAM.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Event Log Generation](#event-log-generation)
- [Metrics Calculation](#metrics-calculation)
- [Case Studies](#case-studies)
- [Output Structure](#output-structure)

## Installation

### Prerequisites

- Python 3.10.2 or compatible version
- Virtual environment (recommended)

### Setup

1. Create a virtual Python environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) For alternative techniques comparison:
   - Create folders for each alternative technique (RIMS, DSIM, SIMOD, AgentSimulator)
   - Fill them with experiments from:
     - [Zenodo records](https://zenodo.org/records/5734443)
     - [Google Drive folder](https://drive.google.com/drive/folders/1gmO8ULxtBxqShXnBeEUhBLOy97KYlVI2)

## Project Structure

```
ProbabilityBasedEventLogGenerator/
├── run_simulations.py          # Main script for event log generation
├── LogDistanceMeasuresSim.ipynb # Jupyter notebook for metrics calculation
├── EventLogGenerator.py         # Core event log generator class
├── src/                         # Source modules
│   ├── gen_seq_utils.py        # Sequence generation utilities
│   ├── gen_res_utils.py        # Resource generation utilities
│   ├── gen_time_utils.py       # Time distribution utilities
│   ├── eventlog_utils.py        # Event log utilities
│   └── ...
├── data/                        # Input event logs (XES format)
│   ├── bpi12/
│   ├── bpi17/
│   ├── Consulta/
│   └── ...
└── simulations/                 # Generated simulation outputs
    ├── bpi12/
    ├── bpi17/
    └── ...
```

## Event Log Generation

### Overview

The `run_simulations.py` script generates synthetic event logs using a probability-based approach. It processes training logs, learns patterns, and generates new traces that follow the discovered distributions.

### Usage

```bash
python3 run_simulations.py
```

### Configuration

The script supports multiple case studies. Edit the `case_studies` list and configuration parameters in the script:

```python
case_studies = [
    'Purchasing',
    'Production',
    'Consulta',
    'bpi12',
    'bpi17',
    'sepsis',
    'bpi19',
    'rtf',
]

N_SIM = 1  # Number of simulations to run
k = 1      # Prefix length for probability calculations
```

### Parameters

For each case study, you can configure:

- **`path_log`**: Path to the original event log file (XES format)
- **`save_split_to`**: Directory to save train/test split logs
- **`save_simulations_to`**: Directory to save generated simulations
- **`label_data_attributes`**: List of data attributes to consider during generation (empty list `[]` to ignore)
- **`k`**: Prefix length parameter for conditional probability calculations

### Workflow

1. **Load Event Log**: Imports the original event log from XES format
2. **Split Data**: Creates train/test split (80/20) with temporal ordering
3. **Initialize Generator**: Creates `EventLogGenerator` instance that:
   - Learns prefix-based activity transition probabilities
   - Discovers resource calendars and assignments
   - Computes arrival time distributions
   - Computes execution time distributions
   - Optionally handles data attributes
4. **Generate Simulations**: For each simulation:
   - Generates `N=len(test_log)*8` traces
   - Starts from the test log's first timestamp
   - Saves to CSV format: `sim_{i}_{k}.csv`
5. **Record Execution Time**: Saves execution time to `execution_time.txt`

### Output

Generated simulations are saved in the `simulations/{case_study}/` directory:
- `sim_0.csv`, `sim_1.csv`, ... - Generated event logs
- `execution_time.txt` - Execution time statistics

### Example

```python
# For bpi12 case study
if case_study == 'bpi12':
    path_log = 'data/bpi12/bpi12w.xes'
    save_split_to = 'data/bpi12'
    save_simulations_to = 'simulations/bpi12'
    label_data_attributes = []  # Empty = ignore attributes
    k = 1
```

## Metrics Calculation

### Overview

The `LogDistanceMeasuresSim.ipynb` Jupyter notebook calculates various distance metrics between real and simulated event logs to evaluate the quality of generated logs.

### Usage

1. Open the notebook:
   ```bash
   jupyter notebook LogDistanceMeasuresSim.ipynb
   ```

2. Configure the case study and approach:
   ```python
   case_study = case_studies[4]  # Select case study
   our_approach = True           # True = our approach, False = SOTA
   approach = 'SIMOD' if Sota else None  # SOTA approach name
   ```

3. Run cells sequentially to compute metrics.

### Supported Metrics

The notebook calculates the following distance measures:

1. **Generated Attributes Distribution Distance** (`emd_attributes`)
   - Earth Mover's Distance for data attributes
   - Requires specifying attribute names in `attr_names` parameter

2. **Control-flow Log Distance** (`control_flow_log_distance`)
   - Measures structural similarity of process flows
   - Based on trace alignments

3. **N-Gram Distribution Distance** (`n_gram_distribution_distance`)
   - Compares activity sequence patterns
   - Configurable n-gram length (default: 3)

4. **Absolute Event Distribution Distance** (`absolute_event_distribution_distance`)
   - Compares timestamp distributions
   - Discretizes by hour (configurable)

5. **Case Arrival Distribution Distance** (`case_arrival_distribution_distance`)
   - Measures similarity of case arrival patterns
   - Temporal distribution comparison

6. **Circadian Event Distribution Distance** (`circadian_event_distribution_distance`)
   - Hour-of-day event distribution patterns
   - Considers both start and end timestamps

7. **Resource-Based Circadian Event Distribution Distance** (`resource_based_circadian_event_distribution_distance`)
   - Circadian patterns per resource
   - Resource-specific temporal analysis

8. **Relative Event Distribution Distance** (`relative_event_distribution_distance`)
   - Relative timing between events
   - Temporal ordering similarity

9. **Cycle Time Distribution Distance** (`cycle_time_distribution_distance`)
   - Case duration distribution comparison
   - Binned by time intervals (default: 1 hour)

### Workflow

1. **Load Logs**: 
   - Real log: `data/{case_study}/logTest.xes`
   - Simulated log: `simulations/{case_study}/sim_0.csv` (our approach) or SOTA paths

2. **Data Preprocessing**:
   - Convert lifecycle transitions to start/end format if needed
   - Standardize column names
   - Convert timestamps to datetime objects

3. **Compute Metrics**: Run each metric calculation cell

4. **Save Results**: Metrics are saved to `simulations/{case_study}/metrics.pkl`

### Output

- **Metrics Dictionary**: Saved as pickle file containing all computed distances
- **Console Output**: Prints each metric value during computation

### Example Output

```
case study is bpi12 for approach None, with our approach True and Sota False
emd_attributes nan
control_flow_log_distance 0.5878994838548787
n_gram_distribution_distance 0.9762775141946022
absolute_event_distribution_distance 79222.95631580324
case_arrival_distribution_distance 227.30366492146598
circadian_event_distribution_distance 4.130469247980372
resource_based_circadian_event_distribution_distance 8.168591247366653
relative_event_distribution_distance 79435.52090004024
cycle_time_distribution_distance 62797.13089005235
```

## Case Studies

The project supports the following case studies:

1. **BPI Challenge 2012** (`bpi12`)
   - Financial process
   - Path: `data/bpi12/bpi12w.xes`

2. **BPI Challenge 2017** (`bpi17`)
   - Loan application process
   - Path: `data/bpi17/bpi17w.xes`

3. **Consulta** (`Consulta`)
   - Healthcare consultation process
   - Path: `data/Consulta/ConsultaDataMining201618.xes`

4. **Production** (`Production`)
   - Manufacturing process
   - Path: `data/Production/production.xes`

5. **Purchasing** (`Purchasing`)
   - Procurement process
   - Path: `data/Purchasing/PurchasingExample.xes`

6. **Sepsis** (`sepsis`)
   - Healthcare process
   - Path: `data/sepsis/sepsis.xes`

7. **BPI Challenge 2019** (`bpi19`)
   - Purchase-to-pay process
   - Path: `data/bpi19/bpi19.xes`

8. **RTF** (`rtf`)
   - Road traffic fine process
   - Path: `data/rtf/rtf.xes`

## Output Structure

### Event Log Generation Output

```
simulations/{case_study}/
├── sim_0.csv              # Generated simulation 0
├── sim_1.csv              # Generated simulation 1
├── ...
└── execution_time.txt     # Execution time statistics
```

### Metrics Output

```
simulations/{case_study}/
└── metrics.pkl            # Pickle file with all distance metrics
```

### Generated Log Format

CSV files contain the following columns:
- `case:concept:name` - Case identifier
- `concept:name` - Activity name
- `time:timestamp` - Event end timestamp
- `start:timestamp` - Event start timestamp (if available)
- `org:resource` - Resource identifier (if available)
- Additional data attributes (if configured)

## Notes

- Ensure input event logs are in XES format
- The generator uses temporal train/test split (80/20) to maintain chronological order
- Execution time is recorded for each case study
- Metrics calculation may take significant time for large logs
- Some metrics (e.g., Work in Progress Distance) are computationally intensive and may be commented out

## Troubleshooting

1. **Import Errors**: Ensure all dependencies are installed via `requirements.txt`
2. **File Not Found**: Check that case study data files exist in the `data/` directory
3. **Memory Issues**: For large logs, consider reducing `N_SIM` or the number of generated traces
4. **Metrics Calculation Time**: Some metrics are computationally expensive; consider using smaller log samples for testing

## License

See LICENSE file for details.

## Citation

If you use this code, please cite the paper:
"An Experimental Comparison of Alternative Methods for Event-Log Augmentation"
