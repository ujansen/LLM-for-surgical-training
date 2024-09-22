import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

control_metrics_forcep, control_metrics_driver = [], []
experiment_metrics_forcep, experiment_metrics_driver = [], []

# Create a figure and axis object
control_group = [3, 4, 7, 9, 11, 13, 14, 16, 17, 18]
experiment_group = list(set(np.arange(1, 21)) - set(control_group))

control_files, experiment_files = [], []
for group in os.listdir('./Recordings/Novices'):
    group_path = os.path.join('./Recordings/Novices', group)
    for participant in os.listdir(group_path):
        participant_path = os.path.join(group_path, participant)
        files = []
        if int(participant_path.split('ID_')[1]) in control_group:
            for recording in os.listdir(participant_path):
                recording_path = os.path.join(participant_path, recording)
                for file in os.listdir(recording_path):
                    if file.endswith('.csv'):
                        files.append(os.path.join(recording_path, file))
            control_files.append(files)
        else:
            for recording in os.listdir(participant_path):
                recording_path = os.path.join(participant_path, recording)
                for file in os.listdir(recording_path):
                    if file.endswith('.csv'):
                        files.append(os.path.join(recording_path, file))
            experiment_files.append(files)

metric_roles = ['Any = DriverTipToDriver', 'Any = ForcepTipToForcep',
                'LeftTool = ForcepTipToForcep, RightTool = DriverTipToDriver',
                'LeftTool = DriverTipToDriver, RightTool = ForcepTipToForcep']

for control_recordings in control_files:
    metrics_forcep, metrics_driver = [], []
    for man_file in control_recordings:
        df = pd.read_csv(man_file)
        df = df[(df['MetricName'] == 'Bimanual Dexterity: Translational & Rotational') &
                df['MetricRoles'].isin(metric_roles)]
        metrics_forcep.append(float(df.iloc[0]['MetricValue'].split('\t')[0]))
        metrics_driver.append(float(df.iloc[0]['MetricValue'].split('\t')[1]))
    control_metrics_driver.append(metrics_driver)
    control_metrics_forcep.append(metrics_forcep)


for experiment_recordings in experiment_files:
    metrics_forcep, metrics_driver = [], []
    for man_file in experiment_recordings:
        df = pd.read_csv(man_file)
        df = df[(df['MetricName'] == 'Bimanual Dexterity: Translational & Rotational') &
                df['MetricRoles'].isin(metric_roles)]
        if df['MetricRoles'].values[0].startswith('LeftTool = F'):
            metrics_forcep.append(float(df.iloc[0]['MetricValue'].split('\t')[0]))
            metrics_driver.append(float(df.iloc[0]['MetricValue'].split('\t')[1]))
        else:
            metrics_forcep.append(float(df.iloc[0]['MetricValue'].split('\t')[1]))
            metrics_driver.append(float(df.iloc[0]['MetricValue'].split('\t')[0]))
    experiment_metrics_driver.append(metrics_driver)
    experiment_metrics_forcep.append(metrics_forcep)


control_metrics_forcep, control_metrics_driver = (np.mean(np.array(control_metrics_forcep), axis=0),
                                                  np.mean(np.array(control_metrics_driver), axis=0))
experiment_metrics_forcep, experiment_metrics_driver = (np.mean(np.array(experiment_metrics_forcep), axis=0),
                                                        np.mean(np.array(experiment_metrics_driver), axis=0))


x = [1, 2, 3, 4, 5]
plt.plot(x, control_metrics_forcep, marker='o', color='blue', linestyle='-', label='Control (Translational)')
plt.plot(x, control_metrics_driver, marker='o', color='red', linestyle='-', label='Control (Rotational)')
plt.plot(x, experiment_metrics_forcep, marker='o', color='orange', linestyle='-', label='Experiment (Translational)')
plt.plot(x, experiment_metrics_driver, marker='o', color='green', linestyle='-', label='Experiment (Rotational)')

# Add labels and title
plt.xlabel('Trial', fontsize=10)
plt.xticks(x, fontsize=12)
plt.ylabel('Bimanual Dexterity', fontsize=10)
plt.title('Average Bimanual Dexterity of Control vs Experiment across trials', fontsize=12)

# Add legend
plt.legend()

# Customize ticks and grid
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.grid(True, linestyle='--', alpha=0.8)

# Show plot
plt.show()
