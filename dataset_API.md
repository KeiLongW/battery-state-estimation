# Dataset A API

## data_set_a.py

Used for loading the dataset A CSVs into memory by the specific chunk size.

### Initialization

Initialize the Dataset A object with all data loaded into memory.

- test_types: Determine which data with the test types to load
- chunk_size: Chunk size of data loading
- lines: Determine which data with the line code to load
- charge_line: The line code represent charge data
- discharge_line: The line code represent discharge data
- base_path: Base path of the running source

```
dataset = DatasetA(
    test_types=['S'], # Empty list for getting all
    chunk_size=1000000,
    lines=[37, 40], # Empty list for getting all
    charge_line=37,
    discharge_line=40,
    base_path="./"
)
```

### prepare_data

Prepare the data for training and testing with specific test names (Call before initializing `ModelDataHandler`)

- train_names: Test names of training data
- test_names: Test nams of testing data

```
train_data_test_names = [
    '000-DM-3.0-4019-S',
    '001-DM-3.0-4019-S',
    '002-DM-3.0-4019-S',
]
test_data_test_names = [
    '003-DM-3.0-4019-S',
]
dataset.prepare_data(train_data_test_names, test_data_test_names)
```

### get_charge_data

Get all prepared testing and training charge data.

```
train_charge_cyc,train_charge_cap,test_charge_cyc,test_charge_cap = dataset.get_charge_data()
```

### get_discharge_data

Get all prepared testing and training discharge data.

```
train_discharge_cyc,train_discharge_cap,test_discharge_cyc,test_discharge_cap = dataset.get_discharge_data()
```

### get_all_test_names

Get all test names

```
test_names = dataset.get_all_test_names()
```

## model_data_handler.py

Used to construct training and testing input/output data from Dataset A object.

### Initialization

Initialize the model data handler object with the prepared Dataset A object and specify the model input columns

- dataset: The prepared Dataset A object
- x_indices: The column indices used for model data input
- scaler_type: class of scaler in sklearn.preprocessing, default=MinMaxScaler

```
mdh = ModelDataHandler(
    dataset=dataset,
    x_indices=[
        CycleCols.VOLTAGE,
        CycleCols.CURRENT,
        CycleCols.TEMPERATURE
    ],
    scaler_type=MinMaxScaler
)
```

### get_scalers

Get the scalers (MinMaxScaler) used to scale the model input data

```
scalers = mdh.get_scalers()
```

### get_discharge_whole_cycle

Get the whole cycle input/output data for SOH/SOC estimation

Data shape:

```
x: [ [[voltage, current, temperature], ...], ...]
SOH y (single step): [ [soh/last_charging_capacity, remaining_time_to_cell_end], ... ]
SOH y (multiple steps): [ [[soh/last_charging_capacity, remaining_time_to_cell_end], ...], ... ]
SOC y: [[[soc/discharging_capacity, remaining_time_to_cycle_end], ...], ...]
```

- output_capacity: Determine whether output capacity or SOH/SOC value
- multiple_output: Determine whether output single or multiple steps (always multiple for SOC)
- soh: Determine output for SOH or SOC estimation

```
# [SOH] Single output step with SOH value
train_x, train_y, test_x, test_y = mdh.get_discharge_whole_cycle(
    soh=True
)

# [SOH] Multiple output steps with SOH capacity value
train_x, train_y, test_x, test_y = mdh.get_discharge_whole_cycle(
    output_capacity=True,
    multiple_output=True,
    soh=True
)

# [SOC] Multiple output steps with SOC value
train_x, train_y, test_x, test_y = mdh.get_discharge_whole_cycle(
    multiple_output=True,
    soh=False
)
```

### get_discharge_single_step

Get single time step input/output data for SOH/SOC estimation

Data shape:

```
x: [[voltage, current, temperature], ...]
SOH y: [[soh/last_charging_capacity, remaining_time_to_cell_end], ...]
SOC y: [[soc/discharging_capacity, remaining_time_to_cycle_end], ...]
```

- output_capacity: Determine whether output capacity or SOH/SOC value
- soh: Determine output for SOH or SOC estimation

```
# [SOH] SOH capacity value
train_x, train_y, test_x, test_y = mdh.get_discharge_single_step(output_capacity=True, soh=True)

# [SOC] SOC value
train_x, train_y, test_x, test_y = mdh.get_discharge_single_step(output_capacity=False, soh=False)
```

### get_discharge_multiple_step

Get multiple time step input/output data for SOH/SOC estimation where input are voltage, current and temperature in multiple (n) steps before the target time step

Data shape:

```
x: [[[voltage, current, temperature], ...] ...]
SOH y (single step): [[soh/last_charging_capacity, remaining_time_to_cell_end], ...]
SOH y (multiple steps): [[[soh/last_charging_capacity, remaining_time_to_cell_end], ...], ...]
SOC y (single step): [[soc/discharging_capacity, remaining_time_to_cycle_end], ...]
SOC y (multiple steps): [[[soc/discharging_capacity, remaining_time_to_cycle_end], ...], ...]
(Pad zeros to begining steps)
```

- output_capacity: Determine whether output capacity or SOH/SOC value
- multiple_output: Determine whether output single or multiple steps
- soh: Determine output for SOH or SOC estimation

```
#[SOH] Multiple output steps with SOH value
train_x, train_y, test_x, test_y = mdh.get_discharge_multiple_step(
    10, # 10 previous steps
    output_capacity=False,
    multiple_output=True,
    soh=True
)

#[SOC] Single output steps with SOC value
train_x, train_y, test_x, test_y = mdh.get_discharge_multiple_step(
    10, # 10 previous steps
    output_capacity=False,
    multiple_output=False,
    soh=False
)
```
