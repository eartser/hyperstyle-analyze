# Hyperskill statistics analysis

Test task for JetBrains Research Hyperstyle team for project "Large Scale Analysis of Code Quality". Represents some intresting statistics of collected from Hyperskill platform data.

## Installation

Simply clone the repository and run the following command:

`pip install -r requirements.txt`

## Collecting data

All observed data is already collected and stored in [output](https://github.com/eartser/hyperstyle-analyze/tree/main/output) folder. At most 10000 items of every object were got by running [run_data_collection.py](https://github.com/hyperskill/hyperstyle-analyze/blob/main/analysis/src/python/data_collection/run_data_collection.py) script as follows:

```
python3 run_data_collection.py hyperskill step --output ../../../../output --count 10000
python3 run_data_collection.py hyperskill track --output ../../../../output --count 10000
python3 run_data_collection.py hyperskill project --output ../../../../output --count 10000
python3 run_data_collection.py hyperskill topic --output ../../../../output --count 10000
```

For more detailed information on collecting data from Hyperskill read [here](https://github.com/hyperskill/hyperstyle-analyze/tree/main/analysis/src/python/data_collection).

## Data analysis

The entire analysis of the obtained data with comments and visualization is located in [jupyter notebook](https://github.com/eartser/hyperstyle-analyze/blob/main/Hyperskill_statistics_analyze.ipynb). To correctly display the analysis results, start the notebook and run all cells.
