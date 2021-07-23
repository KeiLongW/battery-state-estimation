# UNIBO Powertools Dataset

The UNIBO Powertools Dataset has been collected in a laboratory test by an Italian Equipment producer. The cycling experiments are designed to analyze different cells intended for use in various cleaning equipment such as vacuum and automated floor cleaners. The vast dataset is composed of 27 batteries. The main features of the dataset are:
(1) the use of batteries from different manufacturers, (2) cells with several nominal capacities, (3) cycling is performed until the cell's end-of-life and thus data regarding the cell at different life stages are produced. Three types of tests have been conducted. (I) The standard test, where the battery was discharged at 5A current in main cycles. (II), the high current test, where the battery was discharged at 8A current in main cycles. (III), the preconditioned test, where the battery cells are stored at 45°C environments for 90 days before conducting the test. During discharge, the sampling period is 10 seconds.

# Data description

| Column               | Description                                           |
| -------------------- | ----------------------------------------------------- |
| test_name            | test identifier, see below for test name codification |
| record_id            | id of the step in the test                            |
| time                 | time elapsed since test start                         |
| step_time            | time used to perform the step                         |
| line                 | procedure code, see below                             |
| voltage              | V[V]                                                  |
| current              | I[A]                                                  |
| charging_capacity    | capacity measured during charge. During charging cicles, it represent the present capacity of the battery. It is zeroed at each charge/discharge cycle          |
| discharging_capacity | capacity measured during discharge. It is how much the battery has been discharged i.e. during discharging cicles: present_capacity = charging_capacity - discharge capacity. It is zeroed at each charge/discharge cycle       |
| wh_charging          | Wh measured during charge. It is zeroed at each discharge cycle                       |
| wh_discharging       | Wh measured during discharge. It is zeroed at each discharge cycle                    |
| temperature          | cell temperature measured using NTC sensor placed in the middle of the cell's body and attached using thermal interface material        |
| cycle_count          | charge/discharge cycle count. It goes from 0 to 100 for the main cycle and from 0 to 1000 for the resistance cycle. The two cycles are interleaved i.e. 0->100->0->1000->0->100...       |

# Battery cycling procedure

1) delivery SOC verification

    discharge at 5A until V<sub>eod</sub> (line code: 12)

2) capacity test

    CC-CV charge at 1A until cutoff=4.2V, termination at 0,05A (line code: 17)

    discharge, 0,2A (line code: 19)

3) resistance cycle

    two steps alternated:

    first step, discharge at 0,5A for 10s (line code: 29)

    second step, discharge at 5A for 1s (line code: 30)

4) main cycle

    CC-CV charge at 1.8A until cutoff=4.2V, termination at 0,1A (line code: 37)

    discharge at 5A until V<sub>eod</sub> (line code: 40)

5) repeat the main cycle (point 4) 100 times, then perform a capacity test (point 2) and a resistance cycle (point 3), redo point 5

# Test name convention

000-XW-Y.Y-AABB-T

---

000 = sample serial number

X = lecter related to cell manufacturer

W = cell type | P: powertool, M: mid power, E: e-byke

Y.Y = cell capacity e.g. 2.5Ah -> 2.5

AABB = samples delivery date (AA: week, bb: year)

T = test type | S: Standard (5A discharge), H: High Current (8A discharge), P: Pre-conditioned (90 days storing at 45C degree before testing)

# Files

*test_result.csv* contains all the records but the last one of each charge/discharge run. *test_result.csv* contains the last record of each run. A python file for loading data is available at https://github.com/KeiLongW/battery-state-estimation