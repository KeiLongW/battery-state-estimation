import numpy as np
import pandas as pd
import logging
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

DATA_PATH = 'data/LG 18650HG2 Li-ion Battery Data/LG_HG2_Original_Dataset_McMasterUniversity_Jan_2020/'

class LgData():
    def __init__(self, base_path="./"):
        self.path = base_path + DATA_PATH
        self.logger = logging.getLogger()

    def get_discharge_whole_cycle(self, train_names, test_names, output_capacity=False, scale_test=False, output_time=False):
        train = self._get_data(train_names, output_capacity, output_time)
        test = self._get_data(test_names, output_capacity, output_time)
        train, test = self._scale_x(train, test, scale_test=scale_test)        
        return (train, test)
        
    def _get_data(self, names, output_capacity, output_time=False):
        cycles = []
        for name in names:
            cycle = pd.read_csv(self.path + name + '.csv', skiprows=30)
            cycle.columns = ['Time Stamp','Step','Status','Prog Time','Step Time','Cycle',
                            'Cycle Level','Procedure','Voltage','Current','Temperature','Capacity','WhAccu','Cnt','Empty']
            cycle = cycle[(cycle["Status"] == "TABLE") | (cycle["Status"] == "DCH")]

            max_discharge = abs(min(cycle["Capacity"]))
            cycle["SoC Capacity"] = max_discharge + cycle["Capacity"]
            cycle["SoC Percentage"] = cycle["SoC Capacity"] / max(cycle["SoC Capacity"])
            x = cycle[["Voltage", "Current", "Temperature"]].to_numpy()

            if output_time:
                cycle['Prog Time'] = cycle['Prog Time'].apply(self._time_string_to_seconds)
                cycle['Time in Seconds'] = cycle['Prog Time'] - cycle['Prog Time'][0]

            if output_capacity:
                if output_time:
                    y = cycle[["SoC Capacity", "Time in Seconds"]].to_numpy()
                else:
                    y = cycle[["SoC Capacity"]].to_numpy()
            else:
                if output_time:
                    y = cycle[["SoC Percentage", "Time in Seconds"]].to_numpy()
                else:
                    y = cycle[["SoC Percentage"]].to_numpy()

            if np.isnan(np.min(x)) or np.isnan(np.min(y)):
                self.logger.info("There is a NaN in cycle " + name + ", removing row")
                x = x[~np.isnan(x).any(axis=1)]
                y = y[~np.isnan(y).any(axis=1)].reshape(-1, y.shape[1])

            cycles.append((x, y))

        return cycles

    def _time_string_to_seconds(self, input_string):
        time_parts = input_string.split(':')
        second_parts = time_parts[2].split('.')
        return timedelta(hours=int(time_parts[0]), 
            minutes=int(time_parts[1]), 
            seconds=int(second_parts[0]), 
            microseconds=int(second_parts[1])).total_seconds()

    def _scale_x(self, train, test, scale_test=False):
        for index_feature in range(len(train[0][0][0])):
            feature_min = min([min(cycle[0][:,index_feature]) for cycle in train])
            feature_max = max([max(cycle[0][:,index_feature]) for cycle in train])
            for i in range(len(train)):
                train[i][0][:,index_feature] = (train[i][0][:,index_feature]-feature_min)/(feature_max-feature_min)
            if scale_test:
                for i in range(len(test)):
                    test[i][0][:,index_feature] = (test[i][0][:,index_feature]-feature_min)/(feature_max-feature_min)

        return train, test


    #################################
    #
    # get_stateful_cycle
    #
    #################################
    def get_stateful_cycle(self, cycles, pad_num = 0, steps = 100):
        max_lenght = max(max(len(cycle[0]) for cycle in cycles[0]), max(len(cycle[0]) for cycle in cycles[1]))
        train_x, train_y = self._to_padded_cycle(cycles[0], pad_num, max_lenght)
        test_x, test_y = self._to_padded_cycle(cycles[1], pad_num, max_lenght)
        train_x = self._split_cycle(train_x, steps)
        train_y = self._split_cycle(train_y, steps)
        test_x = self._split_cycle(test_x, steps)
        test_y = self._split_cycle(test_y, steps)
        self.logger.info("Train x: %s, train y: %s | Test x: %s, test y: %s" %
                         (train_x.shape, train_y.shape, test_x.shape, test_y.shape))
        return (train_x, train_y, test_x, test_y)

    def _to_padded_cycle(self, cycles, pad_num, max_lenght):
        x_length = len(cycles[0][0][0])
        y_length = len(cycles[0][1][0])
        x = np.full((len(cycles), max_lenght, x_length), pad_num, dtype=float)
        y = np.full((len(cycles), max_lenght, y_length), pad_num, dtype=float)
        for i, cycle in enumerate(cycles):
            x[i, :cycle[0].shape[0]] = cycle[0]
            y[i, :cycle[1].shape[0]] = cycle[1]
        return x, y

    def _split_cycle(self, cycles, steps):
        features = cycles.shape[2]
        time_steps = cycles.shape[1]
        new_cycles = np.empty((0, time_steps//steps, steps, features), float)
        for cycle in cycles:
            new_cycle = np.empty((0, steps, features), float)
            for i in range(0, len(cycle) - steps, steps):
                next_split = np.array(cycle[i:i + steps]).reshape(1, steps, features)
                new_cycle = np.concatenate((new_cycle, next_split))
            new_cycles = np.concatenate((new_cycles, new_cycle.reshape(1, time_steps//steps, steps, features)))
        return new_cycles


    #################################
    #
    # get_discharge_multiple_step
    #
    #################################
    def get_discharge_multiple_step(self, cycles, steps):
        train_x, train_y = self._split_to_multiple_step(cycles[0], steps)
        test_x, test_y = self._split_to_multiple_step(cycles[1], steps)
        self.logger.info("Train x: %s, train y: %s | Test x: %s, test y: %s" %
                         (train_x.shape, train_y.shape, test_x.shape, test_y.shape))
        return (train_x, train_y, test_x, test_y)

    def _split_to_multiple_step(self, cycles, steps):
        x_length = len(cycles[0][0][0])
        y_length = len(cycles[0][1][0])
        x = np.empty((0, steps, x_length), float)
        y = np.empty((0, steps, y_length), float)
        for cycle in cycles:
            for i in range(0, len(cycle[0]) - steps, steps):
                next_x = np.array(cycle[0][i:i + steps]).reshape(1, steps, x_length)
                next_y = np.array(cycle[1][i:i + steps]).reshape(1, steps, y_length)
                x = np.concatenate((x, next_x))
                y = np.concatenate((y, next_y))
        return x, y

    def keep_only_y_end(self, y, step, is_stateful=False):
        if is_stateful:
            return y[:,:,[-1]]
        else:
            return y[:,[-1]]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    train_names = [
        '25degC/551_LA92', 
        '25degC/551_Mixed1', 
        '25degC/551_Mixed2', 
        '25degC/551_UDDS', 
        #'25degC/551_US06', 
        #'25degC/552_Mixed3',
        #
        #'25degC/552_Mixed7', 
        #'25degC/552_Mixed8', 


        #'0degC/589_LA92', 
        #
        #'0degC/589_UDDS', 
        #'0degC/589_US06', 
        #'0degC/590_Mixed4',
        #'0degC/590_Mixed6', 
        #'0degC/590_Mixed7',
        #'0degC/590_Mixed8',


        #'10degC/567_Mixed1', 
        #'10degC/567_Mixed2', 
        #'10degC/571_Mixed4',
        #'10degC/571_Mixed5', 
        #'10degC/571_Mixed6',
        #'10degC/571_Mixed7',
        #
        #'10degC/582_LA92',


        #'40degC/556_Mixed2',
        #'40degC/556_UDDS', 
        #'40degC/556_US06',
        #'40degC/557_Mixed3',
        #'40degC/562_Mixed4', 
        #'40degC/562_Mixed5',
        #'40degC/562_Mixed6',
        #
        #'40degC/562_Mixed8',


        #'n10degC/596_LA92',
        #'n10degC/596_UDDS', 
        #'n10degC/601_Mixed1',
        #'n10degC/601_Mixed2',
        #'n10degC/601_US06', 
        #'n10degC/602_Mixed4',
        #'n10degC/602_Mixed5',
        #'n10degC/604_Mixed3',


        #'n20degC/610_LA92', 
        #'n20degC/610_Mixed1',
        #'n20degC/610_Mixed2',
        #'n20degC/610_UDDS',
        #'n20degC/610_US06', 
        #
        #'n20degC/611_Mixed4',
        #'n20degC/611_Mixed5',
        #
        #'n20degC/611_Mixed8',
        ]
    test_names = [
        '25degC/552_Mixed4', 
        '25degC/552_Mixed5', 
        '25degC/552_Mixed6', 


        #'0degC/589_Mixed1', 
        #'0degC/589_Mixed2',


        #'10degC/571_Mixed8',
        #'10degC/576_UDDS',


        #'40degC/556_LA92', 
        #'40degC/556_Mixed1',
        #
        #'40degC/562_Mixed7',


        #'n10degC/604_Mixed6',
        #'n10degC/604_Mixed7',
        #'n10degC/604_Mixed8',


        #'n20degC/611_Mixed3',
        #
        #'n20degC/611_Mixed6',
        #'n20degC/611_Mixed7',
        ]

    stateful_config = True
    steps = 300

    lg_data = LgData()
    cycles = lg_data.get_discharge_whole_cycle(train_names, test_names)
    print("Train/Test %d" % len(cycles))
    print("Train cycles: %d" % len(cycles[0]))
    print("x/y %d" % len(cycles[0][0]))
    print("time_steps: %d" % len(cycles[0][0][0]))
    print("x features: %d" % len(cycles[0][0][0][0]))

    if not stateful_config:
        train_x, train_y, test_x, test_y = lg_data.get_discharge_multiple_step(cycles, steps)

        train_y = lg_data.keep_only_y_end(train_y, steps)
        test_y = lg_data.keep_only_y_end(test_y, steps)

        display_x = train_x.reshape(train_x.shape[0]*train_x.shape[1], train_x.shape[2])
        display_y = train_y.reshape(train_y.shape[0]*train_y.shape[1], train_y.shape[2])
    else:
        train_x, train_y, test_x, test_y = lg_data.get_stateful_cycle(cycles, steps = steps)

        display_x = train_x.reshape(train_x.shape[0]*train_x.shape[1]*train_x.shape[2], train_x.shape[3])
        display_y = train_y.reshape(train_y.shape[0]*train_y.shape[1]*train_y.shape[2], train_y.shape[3])


    fig = go.Figure()
    fig.add_trace(go.Scatter(y=display_x[:,0],
                        mode='lines', name='Voltage'))
    fig.add_trace(go.Scatter(y=display_x[:,1],
                        mode='lines', name='Current'))
    fig.add_trace(go.Scatter(y=display_x[:,2],
                        mode='lines', name='Temperature'))
    fig.update_layout(title='X Data',
                    xaxis_title='Step',
                    yaxis_title='X',
                    width=1400,
                    height=600)
    fig.show()

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=display_y[:,0],
                        mode='lines', name='SoC'))
    fig.update_layout(title='Y Data',
                    xaxis_title='Step',
                    yaxis_title='SoC',
                    width=1400,
                    height=600)
    fig.show()