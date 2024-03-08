import pandas as pd
import math
import random
import matplotlib.pyplot as plt
import numpy as np
from model import BangladeshModel

"""
    Run all functions needed, output at main.py
"""

# ---------------------------------------------------------------
def run_simulation_main():
    def run_simulation_batch(seed, run_length, probs):
        model = BangladeshModel(seed=seed, scenario_probabilities=probs)
        for i in range(run_length):
            model.step()
        bridges_data = [{"unique_id": bridge.unique_id,
                         'condition': bridge.condition,
                         "name": bridge.name,
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
    ]

    # Set your seeds and run length
    seeds = range(1, 10)  # Seeds for each scenario
    run_length = 1  #run length

    # Run all scenarios
    all_scenario_results = run_all_scenarios(seeds, run_length, scenarios)

    # Process results (the rest of your provided code)
    all_results = all_scenario_results['Scenario_1'][1].copy()
    all_results = all_results[['unique_id', 'name', 'condition']]

    for scenario in all_scenario_results:
        for iteration in all_scenario_results[scenario]:
            for index, row in all_scenario_results[scenario][iteration].iterrows():
                all_results.loc[index, f'delay_time_{scenario}_{iteration}'] = row.delay_time
                all_results.loc[index, f'breaks_down_{scenario}_{iteration}'] = row.breaks_down

    delay_time_columns = all_results.filter(regex='^delay_time_').columns

    all_results['total_delay_time'] = all_results[delay_time_columns].sum(axis=1)

    # Select columns that start with 'breaks_down_'
    breaks_down_columns = all_results.filter(regex='^breaks_down_').columns

    # Count how often True appears in the breaks_down columns for each row
    all_results['total_breakdowns'] = all_results[breaks_down_columns].apply(lambda x: x.value_counts().get(True, 0),
                                                                             axis=1)

    # adjust display so that dataframe is better visible
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_colwidth', 20)
    # print the results
    return all_results[['unique_id', 'name','condition', 'total_delay_time', 'total_breakdowns']] # Show the result for the new columns)

def clean_file(roads, bmms):
    # Filter the 'roads' DataFrame for rows where the 'road' column is 'N1'
    n1_roads = roads[roads['road'] == 'N1']
    n1_roads = n1_roads[(n1_roads['lon'] >= 90.44) & (n1_roads['lon'] <= 91.851) &
                        (n1_roads['lat'] >= 22.363) & (n1_roads['lat'] <= 23.711)]

    # Generate an ID sequence starting from 1
    n1_roads['id'] = range(1, len(n1_roads) + 1)

    # Set model_type to 'link' for all rows
    n1_roads['model_type'] = 'link'

    # Generate 'name' as "Link" + id as string
    n1_roads['name'] = ['Link ' + str(id) for id in n1_roads['id']]

    # Calculate 'length' as difference between this row's 'chainage' and the next row's 'chainage'
    # Shift(-1) moves the chainage up by one row to subtract, fillna(0) to handle the last item
    n1_roads['length'] = (n1_roads['chainage'].shift(-1) - n1_roads['chainage']).fillna(0)

    # Selecting the columns needed for the empty DataFrame
    n1_roads_final = n1_roads[['road', 'id', 'model_type', 'name', 'lat', 'lon', 'length', 'chainage']]

    # Filter BMMS data for road 'N1'
    bmms_n1 = bmms[bmms['road'] == 'N1'].copy()
    bmms_n1 = bmms_n1[(bmms_n1['lon'] >= 90.44) & (bmms_n1['lon'] <= 91.851) &
                      (bmms_n1['lat'] >= 22.363) & (bmms_n1['lat'] <= 23.711)]

    bmms_n1 = bmms_n1[~bmms_n1['name'].str.contains(r"\(R\)", na=False)]
    bmms_n1 = bmms_n1[~bmms_n1['name'].str.contains("right", case=False, na=False)]
    bmms_n1 = bmms_n1[~bmms_n1['name'].str.contains("RIGHT", case=False, na=False)]
    bmms_n1 = bmms_n1[~bmms_n1['name'].str.contains(r"\( R \)", na=False)]

    # Set up for new entries
    bmms_n1['model_type'] = 'bridge'
    # bmms_n1['name'] = ['Bridge ' + str(i+1) for i in range(bmms_n1.shape[0])]
    bmms_n1['id'] = range(n1_roads_final['id'].max() + 1, n1_roads_final['id'].max() + 1 + bmms_n1.shape[0])
    bmms_n1['chainage'] = bmms_n1['km']  # Use 'km' as 'chainage'
    bmms_n1['length'] = bmms_n1['length'] / 1000

    # Select and rename columns to match the format of n1_roads_final_with_chainage
    bmms_n1_formatted = bmms_n1[['road', 'id', 'model_type', 'name', 'lat', 'lon', 'chainage', 'length', 'condition']]

    # Combine the dataframes and sort by chainage
    combined_df = pd.concat([n1_roads_final, bmms_n1_formatted], ignore_index=True).sort_values(by='chainage')

    combined_df.iloc[0, 2] = 'source'
    combined_df.iloc[-1, combined_df.columns.get_loc('model_type')] = 'sink'
    combined_df.reset_index(drop=True, inplace=True)
    count = 1
    for index, row in combined_df.iterrows():
        combined_df.iloc[index, 1] = count
        count += 1

    # add together the links
    length = 0
    rows_to_add = []  # List to accumulate rows
    last_row = None

    # Initialize the DataFrame
    n1_combined = pd.DataFrame(columns=['road', "id", 'model_type', 'name', 'length', 'condition'])

    for index, row in combined_df.iterrows():
        if row['model_type'] == 'source':
            rows_to_add.append({'road': row['road'], 'id': row['id'], 'model_type': row['model_type'],
                                'name': row['name'], 'length': row['length'], 'condition': row['condition']})
            length = 0  # Reset length after adding the combined link
        elif row['model_type'] == 'link':
            length += row['length']
        elif row['model_type'] in ['bridge', 'sink']:
            if last_row is not None and last_row['model_type'] == 'link':
                # Add the previous link with the new length
                rows_to_add.append(
                    {'road': last_row['road'], 'id': last_row['id'], 'model_type': last_row['model_type'],
                     'name': last_row['name'], 'length': length, 'condition': last_row['condition']})
            # Now add the current row (bridge or sink)
            rows_to_add.append({'road': row['road'], 'id': row['id'], 'model_type': row['model_type'],
                                'name': row['name'], 'length': row['length'], 'condition': row['condition']})
            length = 0  # Reset length after adding the combined link
        last_row = row

    # Once the loop is complete, add all accumulated rows to n1_combined
    n1 = pd.concat([n1_combined, pd.DataFrame(rows_to_add)], ignore_index=True)

    duplicates_df = bmms_n1[bmms_n1.duplicated('km', keep=False)]

    # Assuming duplicates_df is your DataFrame

    # Convert 'condition' to a numerical value for averaging
    condition_mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5}
    n1['condition_num'] = n1['condition'].map(condition_mapping)

    # add together the links
    amount = 0
    condition_sum = 0
    rows_to_add = []  # List to accumulate rows
    last_row = None

    # Initialize the DataFrame
    n1_new = pd.DataFrame(columns=['road', "id", 'model_type', 'name', 'length', 'condition', 'condition_num'])
    for index, row in n1.iterrows():
        if last_row is not None:
            if row['model_type'] == 'bridge':
                amount += 1
                condition_sum += row['condition_num']
            if row['model_type'] != 'bridge' and last_row['model_type'] != 'bridge':
                rows_to_add.append({'road': row['road'], 'id': row['id'], 'model_type': row['model_type'],
                                    'name': row['name'], 'length': row['length'], 'condition': row['condition'],
                                    'condition_num': row['condition_num']})
                amount = 0
                condition_sum = 0
            if row['model_type'] != 'bridge' and last_row['model_type'] == 'bridge':
                rows_to_add.append(
                    {'road': last_row['road'], 'id': last_row['id'], 'model_type': last_row['model_type'],
                     'name': last_row['name'], 'length': last_row['length'],
                     'condition': last_row['condition'], 'condition_num': condition_sum / amount})
                amount = 0
                condition_sum = 0
                rows_to_add.append({'road': row['road'], 'id': row['id'], 'model_type': row['model_type'],
                                    'name': row['name'], 'length': row['length'], 'condition': row['condition'],
                                    'condition_num': row['condition_num']})
        else:
            rows_to_add.append({'road': row['road'], 'id': row['id'], 'model_type': row['model_type'],
                                'name': row['name'], 'length': row['length'], 'condition': row['condition'],
                                'condition_num': row['condition_num']})
        last_row = row

    n1_new = pd.concat([n1_new, pd.DataFrame(rows_to_add)], ignore_index=True)

    for index, row in n1_new.iterrows():
        if pd.isna(row['condition_num']) == False:
            n1_new.iloc[index, 6] = math.ceil(n1_new.iloc[index, 6])
    condition_mapping = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    n1_new['condition'] = n1_new['condition_num'].map(condition_mapping)
    n1_new
    n1_new['id'] = range(1, len(n1_new) + 1)
    for index, row in n1_new.iterrows():
        if row['model_type'] != 'bridge':
            n1_new.iloc[index, 3] = row['model_type'] + ' ' + str(row['id'])
        else:
            n1_new.iloc[index, 3] = n1_new.iloc[index, 3] + ' ' + str(row['id'])

    n1_new['lat'] = random.randrange(1, 10)
    n1_new['lon'] = random.randrange(1, 10)
    for index, row in n1_new.iterrows():
        n1_new.iloc[index, 7] = random.randrange(1, 10)
        n1_new.iloc[index, 8] = random.randrange(1, 10)
    n1_new['length'] = n1_new['length'] * 1000

    n1_new.to_csv('../data/n1_model.csv', index=False)
    return n1_new