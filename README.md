# Battery-state-estimation

Estimation of the State of Charge (SOC) of Lithium-ion batteries using Deep LSTMs.

## Introduction

This repository provides the implementation of deep LSTMs for SOC estimation. The experiments have been performed on two datasets: the [**LG 18650HG2 Li-ion Battery Data**](https://data.mendeley.com/datasets/cp3473x7xv/3) and the [**UNIBO Powertools Dataset**](https://doi.org/10.17632/n6xg5fzsbv.1).

### UNIBO Powertools Dataset, a novel battery dataset
The UNIBO Powertools Dataset is an original dataset that will be published along with this work. The dataset is described [here](data_description.md). We provide two scripts to load the data and prepare them (e.g. computing SOC and SOH, splitting data into time series, normalize the data, and so on). The API to use the dataset is defined [here](dataset_API.md).

## Paper
If you use this work or the UNIBO dataset, please cite our paper:

*Li-Ion Batteries State-of-Charge Estimation Using Deep LSTM at Various Battery Specifications and Discharge Cycles* [[DOI](https://doi.org/10.1145/3462203.3475878)]

```
@inproceedings{10.1145/3462203.3475878,
author = {Wong, Kei Long and Bosello, Michael and Tse, Rita and Falcomer, Carlo and Rossi, Claudio and Pau, Giovanni},
title = {Li-Ion Batteries State-of-Charge Estimation Using Deep LSTM at Various Battery Specifications and Discharge Cycles},
year = {2021},
isbn = {9781450384780},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3462203.3475878},
doi = {10.1145/3462203.3475878},
booktitle = {Proceedings of the Conference on Information Technology for Social Good},
pages = {85–90},
numpages = {6},
location = {Roma, Italy},
series = {GoodIT '21}
}
```

## Source code structure

The package *data_processing* contains the scripts that load the data from the two sets. *unibo_powertools_data.py* loads the data from the csv and compute the derived columns like the SOC one, while *model_data_handler.py* prepare the time series to be used by the neural network. *lg_dataset.py* both loads and prepares the data of the LG set.

The *experiments* directory contains the Jupyter notebooks defining the various experiments and LSTM models used. The *results* directory shows the plots of the results and the measurements like RMSE, MAE, etc.

## Quick start

### 1) Install requirements

#### Python packages

    pip install tensorflow
    pip install pandas
    pip install sklearn
    pip install scipy
    pip install plotly
    pip install jupyterlab

#### Alternatively, you can create the conda environment by

````
conda env create -f environment.yml
````

#### Let Plotly work in Jupyterlab

1) [Install node](https://nodejs.org/en/download/package-manager)


2) `jupyter labextension install jupyterlab-plotly`

### 2) Download the datasets

Download the [LG dataset](https://data.mendeley.com/datasets/cp3473x7xv/3) and put its content in the directory `battery-state-estimation/data/LG 18650HG2 Li-ion Battery Data/`

Download the [**UNIBO dataset**](https://doi.org/10.17632/n6xg5fzsbv.1) and put its content in the directory `battery-state-estimation/data/unibo-powertools-dataset/`

### 3) Run one of the notebooks

Use one of the notebooks in the *experiments* directory if you want to train your model or use one of the notebooks in the *results* directory if you want to load and use one of the pre-trained models (they will be available in the release section soon).

If you want to run the notebook on Google Colab, load the repository in your Google Drive and set to True the variable *IS_COLAB* at the top of the notebook. This will allow the notebook to find the datasets and to save the results in your Drive. 
