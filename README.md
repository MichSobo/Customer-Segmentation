# Customer-Segmentation

## Description

The program was written to conduct a data analysis study using simulated observations about advertisements recorded on
the New York Times home page in May 2012.

There are 31 CSV files in the dataset, one per each day of the month. There is a certain naming convention that the
files follow, i.e. `nyt<DD>.csv`, where the `<DD>` stands for the day.

A single line in each input file corresponds to a single user.

## Usage

The starting point for the program execution is a configuration file.
The default path to the file is `config.json`, but it can be changed using command-line arguments.

There are a few steps that take place during program execution: retrieving data, visualization, saving output.
All of these actions would be performed by default, unless a proper command-line argument is used.