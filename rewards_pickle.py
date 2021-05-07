import pickle
import os

total_mapping_reward = 0.8
performance_evaluation_reward = 0.2
verification_parameters_reward = 0.5
verification_of_data_dependence_reward = 0.5
verification_of_source_reward = 0.10
verification_of_actuator_reward = 0.10
latency_reward = 0.10
verification_degree_reward = 0.10
suc_and_prede_parameters = 0.10





rewards_vector01 = [total_mapping_reward,verification_parameters_reward,verification_of_data_dependence_reward,
                  verification_of_source_reward,verification_of_actuator_reward,latency_reward,
                  verification_degree_reward,suc_and_prede_parameters,performance_evaluation_reward]


total_mapping_reward = 0.5
performance_evaluation_reward = 0.5
verification_parameters_reward = 0.9
verification_of_data_dependence_reward = 0.1
verification_of_source_reward = 0.10
verification_of_actuator_reward = 0.10
latency_reward = 0.10
verification_degree_reward = 0.10
suc_and_prede_parameters = 0.10


rewards_vector02 = [total_mapping_reward,verification_parameters_reward,verification_of_data_dependence_reward,
                  verification_of_source_reward,verification_of_actuator_reward,latency_reward,
                  verification_degree_reward,suc_and_prede_parameters,performance_evaluation_reward]



total_mapping_reward = 0.5
performance_evaluation_reward = 0.5
verification_parameters_reward = 0.1
verification_of_data_dependence_reward = 0.9
verification_of_source_reward = 0.10
verification_of_actuator_reward = 0.10
latency_reward = 0.10
verification_degree_reward = 0.10
suc_and_prede_parameters = 0.10


rewards_vector03 = [total_mapping_reward,verification_parameters_reward,verification_of_data_dependence_reward,
                  verification_of_source_reward,verification_of_actuator_reward,latency_reward,
                  verification_degree_reward,suc_and_prede_parameters,performance_evaluation_reward]





rewards_vector = [rewards_vector01, rewards_vector02, rewards_vector03]

# rewards_vector = [rewards_vector03]
try:
    os.mkdir('rewards_folder')
except:
    pass

with open(os.path.join('rewards_folder', 'rewards_vector'), 'wb') as f:
    pickle.dump(rewards_vector, f, protocol=-1)

