from model import BangladeshModel

"""
    Run simulation
    Print output at terminal
"""

# ---------------------------------------------------------------

# run time 5 x 24 hours; 1 tick 1 minute
run_length = 5 * 24 * 60

# run time 1000 ticks
run_length = 10

seed = 1234567

# sim_model = BangladeshModel(seed=seed)
# sim_model_test = BangladeshModel(seed=1234, scenario=0)

probs_1 = {'A': 5, 'B': 10, 'C': 20, 'D': 40}
model_Julian = BangladeshModel(scenario_probabilities=probs_1)


# Check if the seed is set
# print("SEED " + str(sim_model._seed))
#
# # One run with given steps
for i in range(run_length):
    model_Julian.step()
