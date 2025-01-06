import argparse
import warnings

from source.agent_simulator import AgentSimulator
def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Process event log parameters')
    
    # File paths
    parser.add_argument('--log_path', help='Path to single log file, which is split into train and test')
    parser.add_argument('--train_path', help='Path to training log file')
    parser.add_argument('--test_path', help='Path to test log file')
    
    # Column names
    parser.add_argument('--case_id', help='Case ID column name')
    parser.add_argument('--activity_name', help='Activity name column')
    parser.add_argument('--resource_name', help='Resource column name')
    parser.add_argument('--end_timestamp', help='End timestamp column name')
    parser.add_argument('--start_timestamp', help='Start timestamp column name')
    
    # Hyperparameters
    parser.add_argument('--extr_delays', type=bool, default=False, help='Enable delay extraction')
    parser.add_argument('--central_orchestration', type=bool, default=False, help='Enable central orchestration')

    # Simulation parameters
    parser.add_argument('--num_simulations', type=int, default=10, help='Number of simulations to run')
    
    args = parser.parse_args()
    return args

if __name__ == "__main__":

    # Start a timer 
    import time
    start_time = time.time()

    warnings.filterwarnings("ignore")
    args = parse_arguments()
    


    # Process arguments
    train_and_test = not bool(args.log_path)
    column_names = {
        args.case_id: 'case_id',
        args.activity_name: 'activity_name',
        args.resource_name: 'resource',
        args.end_timestamp: 'end_timestamp',
        args.start_timestamp: 'start_timestamp'
    }
    
    # Set paths
    PATH_LOG = args.train_path if train_and_test else args.log_path
    PATH_LOG_test = args.test_path
    
    # Feature flags
    discover_extr_delays = discover_delays = args.extr_delays
    central_orchestration = args.central_orchestration
    determine_automatically = not central_orchestration

    params = {
        'discover_extr_delays': discover_extr_delays,
        'discover_parallel_work': False,
        'central_orchestration': central_orchestration,
        'determine_automatically': determine_automatically,
        'PATH_LOG': PATH_LOG,
        'PATH_LOG_test': PATH_LOG_test,
        'train_and_test': train_and_test,
        'column_names': column_names,
        'num_simulations': 5
    }

    simulator = AgentSimulator(params)
    simulator.execute_pipeline()

    # Stop the timer
    end_time = time.time()
    elapsed_time = end_time - start_time

    # Convert elapsed time into hours, minutes, and seconds
    hours = int(elapsed_time // 3600)
    minutes = int((elapsed_time % 3600) // 60)
    seconds = int(elapsed_time % 60)

    # Format the timestamp
    timestamp = f"Elapsed time: {hours}h {minutes}min {seconds}s"

    # Print the timestamp
    print(timestamp)

    # Save the timestamp to a text file
    file_name = "elapsed_time.txt"
    with open(f"simulated_data/BPIC_2012_W/main_results/{file_name}", "w") as file:
        file.write(timestamp)



    