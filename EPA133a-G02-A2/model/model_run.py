import pandas as pd

from model import BangladeshModel

"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------
def run_simulation_batch(seed, run_length, probs):
    model = BangladeshModel(seed=seed, scenario_probabilities=probs)
    for i in range(run_length):
        model.step()
    bridges_data = [{"unique_id": bridge.unique_id,
                     "delay_time": bridge.delay_time,
                     "breaks_down": bridge.breaks_down} for bridge in model.bridges]
    return pd.DataFrame(bridges_data)

def run_simulation_for_scenario(seeds, run_length, probs):
    batch_results = {}
    for seed in seeds:
        df_bridge = run_simulation_batch(seed, run_length, probs)
        batch_results[seed] = df_bridge
    return batch_results

def run_all_scenarios(seeds, run_length, scenarios):
    all_scenario_results = {}
    for scenario_index, probs in enumerate(scenarios, start=1):
        print(f"Running scenario {scenario_index} with probabilities {probs}")
        scenario_results = run_simulation_for_scenario(seeds, run_length, probs)
        all_scenario_results[f"Scenario_{scenario_index}"] = scenario_results
    return all_scenario_results

# Define your scenarios
scenarios = [
    {'A': 0, 'B': 0, 'C': 0, 'D': 0},  # Scenario 0
    {'A': 0, 'B': 0, 'C': 0, 'D': 5},  # Scenario 1
    {'A': 0, 'B': 0, 'C': 0, 'D': 10},  # Scenario 2
    {'A': 0, 'B': 0, 'C': 5, 'D': 10},  # Scenario 3
    {'A': 0, 'B': 0, 'C': 10, 'D': 20},  # Scenario 4
    {'A': 0, 'B': 5, 'C': 10, 'D': 20},  # Scenario 5
    {'A': 0, 'B': 10, 'C': 20, 'D': 40},  # Scenario 6
    {'A': 5, 'B': 10, 'C': 20, 'D': 40},  # Scenario 7
    {'A': 10, 'B': 20, 'C': 40, 'D': 80},  # Scenario 8
    # Add more scenarios as needed
]

# Set your seeds and run length
seeds = range(1, 11)  # 10 seeds for each scenario
run_length = 5 * 24 * 60  # Example run length

# Run all scenarios
all_scenario_results = run_all_scenarios(seeds, run_length, scenarios)



# bridges_data = []  # Use a different name to avoid confusion with the 'bridges' variable inside the loop
# for bridge in model_Julian.bridges:
#     # Append a dictionary for each bridge to the list
#     bridges_data.append({
#         'unique_id': bridge.unique_id,
#         'delay_time': bridge.delay_time,
#         'breaks_down': bridge.breaks_down
#     })
#
# # Directly create a DataFrame from the list of dictionaries
# df_bridge = pd.DataFrame(bridges_data, columns=['unique_id', 'delay_time', 'breaks_down'])
# for index, row in df_bridge.iterrows():
#     print(row)
