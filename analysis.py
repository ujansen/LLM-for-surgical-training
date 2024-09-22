import numpy as np
import pandas as pd
from scipy.stats import ttest_ind, shapiro
import os

METRICS = ["Elapsed Time", "Path Length", "Average Velocity", "Bimanual Dexterity: Translational & Rotational",
           "Motion Smoothness", "Path Inefficiency", "Rotational Actions", "Rotation Total", "Translational Actions"]
NUM_EXPERIMENTS = 5


class GatherRecordingMetrics:
    def __init__(self, control_directory, experiment_directory, num_participants=10):
        self._control_directory = control_directory
        self._experiment_directory = experiment_directory
        self._metrics = METRICS
        self._num_participants = num_participants
        self._average_metrics_control_mean, self._average_metrics_control_std = self._gather_metric_value('Control')
        self._average_metrics_experiment_mean, self._average_metrics_experiment_std = self._gather_metric_value(
            'Experiment')
        self._conduct_t_test()
        # self._statistically_significant_metrics = self._conduct_t_test()
        # self._changed_control, self._changed_experiment = self._find_change('Control'), self._find_change('Experiment')
        # self._investigate_change()

    def _gather_metric_value(self, directory):
        average_metrics_mean, average_metrics_std = [], []
        if directory == 'Control':
            for participant in os.listdir(self._control_directory):
                metric_files = []
                for recording in os.listdir(os.path.join(self._control_directory, participant)):
                    if recording.endswith('_5'):
                        recording_path = os.path.join(self._control_directory, participant, recording)
                        for file in os.listdir(recording_path):
                            if file.endswith('.csv'):
                                metric_file = os.path.join(recording_path, file)
                                metric_files.append(metric_file)
                    else:
                        continue
                average_metrics_mean.append(self._find_average_metrics(metric_files)[0])
                average_metrics_std.append(self._find_average_metrics(metric_files)[1])
        else:
            for participant in os.listdir(self._experiment_directory):
                metric_files = []
                for recording in os.listdir(os.path.join(self._experiment_directory, participant)):
                    if recording.endswith('_5'):
                        recording_path = os.path.join(self._experiment_directory, participant, recording)
                        for file in os.listdir(recording_path):
                            if file.endswith('.csv'):
                                metric_file = os.path.join(recording_path, file)
                                metric_files.append(metric_file)
                    else:
                        continue
                average_metrics_mean.append(self._find_average_metrics(metric_files)[0])
                average_metrics_std.append(self._find_average_metrics(metric_files)[1])

        return average_metrics_mean, average_metrics_std

    def _find_change(self, directory):
        metric_roles = ['Any = DriverTipToDriver', 'Any = ForcepTipToForcep',
                        'LeftTool = ForcepTipToForcep, RightTool = DriverTipToDriver',
                        'LeftTool = DriverTipToDriver, RightTool = ForcepTipToForcep']

        if directory == 'Control':
            folder = self._control_directory
        else:
            folder = self._experiment_directory

        participants = []
        for participant in os.listdir(folder):
            metric_files = []
            metrics = {}
            for recording in os.listdir(os.path.join(folder, participant)):
                if recording.endswith('_1') or recording.endswith('_5'):
                    recording_path = os.path.join(folder, participant, recording)
                    for file in os.listdir(recording_path):
                        if file.endswith('.csv'):
                            metric_file = os.path.join(recording_path, file)
                            metric_files.append(metric_file)
                else:
                    continue
            for metric in self._metrics:
                values_per_metric = []
                for file in metric_files:
                    df = pd.read_csv(file)
                    df = df[df['MetricRoles'].isin(metric_roles)]
                    row = df[df['MetricName'] == metric]
                    row_values = row['MetricValue'].values
                    if 'Bimanual' in metric:
                        row_values = row_values[0].split('\t')
                        if row['MetricRoles'].values[0].startswith('LeftTool = Dr'):
                            row_values = [row_values[1], row_values[0]]
                    else:
                        row_values = [row_values[1], row_values[0]]
                    values_per_metric.append(row_values)
                metrics[metric] = values_per_metric
            participants.append(metrics)

        return participants

    # def _investigate_change(self):
    #     for metric in self._metrics:
    #         print(f"Metric: {metric}")
    #         max_control_forcep_change, max_control_driver_change = 0, 0
    #         max_experiment_forcep_change, max_experiment_driver_change = 0, 0
    #         (changed_forcep_control, changed_driver_control,
    #          changed_driver_experiment, changed_forcep_experiment) = [], [], [], []
    #         for i in range(self._num_participants):
    #             # print("Control group:")
    #             change_forcep_control = (float(self._changed_control[i][metric][1][0]) -
    #                                      float(self._changed_control[i][metric][0][0]))
    #             change_driver_control = (float(self._changed_control[i][metric][1][1]) -
    #                                      float(self._changed_control[i][metric][0][1]))
    #             # print(f"Forcep change: {change_forcep_control}")
    #             # print(f"Driver change: {change_driver_control}")
    #             #
    #             # print("Experiment group:")
    #             change_forcep_experiment = (float(self._changed_experiment[i][metric][1][0]) -
    #                                         float(self._changed_experiment[i][metric][0][0]))
    #             change_driver_experiment = (float(self._changed_experiment[i][metric][1][1]) -
    #                                         float(self._changed_experiment[i][metric][0][1]))
    #             # print(f"Forcep change: {change_forcep_experiment}")
    #             # print(f"Driver change: {change_driver_experiment}\n")
    #             if abs(change_forcep_control) > max_control_forcep_change:
    #                 max_control_forcep_change = abs(change_forcep_control)
    #                 changed_forcep_control = [float(self._changed_control[i][metric][0][0]),
    #                                           float(self._changed_control[i][metric][1][0])]
    #
    #             if abs(change_driver_control) > max_control_driver_change:
    #                 max_control_driver_change = abs(change_driver_control)
    #                 changed_driver_control = [float(self._changed_control[i][metric][0][1]),
    #                                           float(self._changed_control[i][metric][1][1])]
    #
    #             if abs(change_forcep_experiment) > max_experiment_forcep_change:
    #                 max_experiment_forcep_change = abs(change_forcep_experiment)
    #                 changed_forcep_experiment = [float(self._changed_experiment[i][metric][0][0]),
    #                                              float(self._changed_experiment[i][metric][1][0])]
    #                 # changed_forcep_control = [float(self._changed_control[i][metric][0][0]),
    #                 #                           float(self._changed_control[i][metric][1][0])]
    #
    #             if abs(change_driver_experiment) > max_experiment_driver_change:
    #                 max_experiment_driver_change = abs(change_driver_experiment)
    #                 changed_driver_experiment = [float(self._changed_experiment[i][metric][0][1]),
    #                                              float(self._changed_experiment[i][metric][1][1])]
    #                 # changed_driver_control = [float(self._changed_control[i][metric][0][1]),
    #                 #                           float(self._changed_control[i][metric][1][1])]
    #
    #         print("Maximum Changes:")
    #         print("Forcep:")
    #         # print(f"Control: {max_control_forcep_change}")
    #         print(f"Control Values: {changed_forcep_control[1] - changed_forcep_control[0]}")
    #         # print(f"Experiment: {max_experiment_forcep_change}")
    #         print(f"Experiment Values: {changed_forcep_experiment[1] - changed_forcep_experiment[0]}\n")
    #
    #         print("Driver:")
    #         # print(f"Control: {max_control_driver_change}")
    #         print(f"Control Values: {changed_driver_control[1] - changed_driver_control[0]}")
    #         # print(f"Experiment: {max_experiment_driver_change}")
    #         print(f"Experiment Values: {changed_driver_experiment[1] - changed_driver_experiment[0]}\n")

    def _find_average_metrics(self, metric_files):
        metric_roles = ['Any = DriverTipToDriver', 'Any = ForcepTipToForcep',
                        'LeftTool = ForcepTipToForcep, RightTool = DriverTipToDriver',
                        'LeftTool = DriverTipToDriver, RightTool = ForcepTipToForcep']

        average_metrics_mean = {k: [] for k in self._metrics}
        average_metrics_std = {k: [] for k in self._metrics}

        for metric in self._metrics:
            values_per_metric = []
            for file in metric_files:
                df = pd.read_csv(file)
                df = df[df['MetricRoles'].isin(metric_roles)]
                row = df[df['MetricName'] == metric]
                row_values = row['MetricValue'].values
                if 'Bimanual' in metric:
                    row_values = row_values[0].split('\t')
                    if row['MetricRoles'].values[0].startswith('LeftTool = Dr'):
                        row_values = [row_values[1], row_values[0]]
                else:
                    row_values = [row_values[1], row_values[0]]
                values_per_metric.append(row_values)

            average_metrics_mean[metric] = [np.mean([float(arr[0]) for arr in values_per_metric]),
                                            np.mean([float(arr[1]) for arr in values_per_metric])]
            average_metrics_std[metric] = [np.std([float(arr[0]) for arr in values_per_metric]),
                                           np.std([float(arr[1]) for arr in values_per_metric])]

        return average_metrics_mean, average_metrics_std

    @staticmethod
    def _calculate_cohens_d(group1, group2):
        mean_diff = np.mean(group1) - np.mean(group2)
        n1, n2 = len(group1), len(group2)
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
        return mean_diff / pooled_std

    def _conduct_t_test(self):
        alpha = 0.15
        metrics = []
        for metric in self._metrics:

            control_mean_forcep = [self._average_metrics_control_mean[i][metric][0] for i in
                                   range(len(self._average_metrics_control_mean))]
            control_mean_driver = [self._average_metrics_control_mean[i][metric][1] for i in
                                   range(len(self._average_metrics_control_mean))]

            experiment_mean_forcep = [self._average_metrics_experiment_mean[i][metric][0] for i in
                                      range(len(self._average_metrics_experiment_mean))]
            experiment_mean_driver = [self._average_metrics_experiment_mean[i][metric][1] for i in
                                      range(len(self._average_metrics_experiment_mean))]

            # _, p_value_forcep_control = shapiro(control_mean_forcep)
            # _, p_value_driver_control = shapiro(control_mean_driver)
            # _, p_value_forcep_experiment = shapiro(experiment_mean_forcep)
            # _, p_value_driver_experiment = shapiro(experiment_mean_driver)

            # print(p_value_forcep_control)
            # print(p_value_driver_control)
            # print(p_value_forcep_experiment)
            # print(p_value_driver_experiment)

            # t_stat_forcep, p_value_forcep = ttest_ind(control_mean_forcep, experiment_mean_forcep)
            # t_stat_driver, p_value_driver = ttest_ind(control_mean_driver, experiment_mean_driver)
            #
            # if p_value_driver < alpha or p_value_forcep < alpha:
            #     metrics.append(metric)
            # print(f"Metric: {metric}")
            # print(f"Forcep - t-statistic = {t_stat_forcep}, p-value = {p_value_forcep}")
            # print(f"Driver - t-statistic = {t_stat_driver}, p-value = {p_value_driver}")
            # print("\n")

        return metrics


gather = GatherRecordingMetrics('./Recordings/Novices/Control',
                                './Recordings/Novices/Experiment')
