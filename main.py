import os
import sys
import json
import argparse
sys.path.append(os.path.abspath('scripts'))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nyt_data import *


def select_stats_unregistered(df, file_num):
    summary_data['CTR'][file_num] = df['CTR']['mean'][('Unknown', '0')]
    summary_data['Clicks'][file_num] = df['Clicks']['sum'][('Unknown', '0')]


def save_stats(df, file_num):
    """Save DataFrame into parquet file"""
    target_filename = 'nyt_summary_' + str(file_num + 1) + '.parquet'

    df.columns = ['_'.join(column).rstrip('_') for column in df.columns.values]
    df.to_parquet(os.path.join(settings['results_folderpath'], target_filename))


if len(sys.argv) > 1:
    # Get command-line options
    parser = argparse.ArgumentParser(
        description='Get some customer data and process it.'
    )
    parser.add_argument('-cfg', '--config', default='config.json',
                        help='path to the configuration file (default: config.json)')
    parser.add_argument('-o', '--option', default='all',
                        choices=['retrieve', 'visualize', 'save', 'all'],
                        help='action to run (default: all)')
    args = parser.parse_args()

    config_filepath = args.config
    run_option = args.option
else:
    # Set a default path to the configuration file
    config_filepath = 'config.json'

    # Set run options to all by default
    run_option = 'all'

# Read configuration file
global settings
with open(config_filepath) as f:
    settings = json.load(f)

# Create raw data folder if not exists
os.makedirs(settings['raw_folderpath'], exist_ok=True)

# Create results folder if not exists
os.makedirs(settings['results_folderpath'], exist_ok=True)

if run_option in ('retrieve', 'all'):
    # Download and unpack the dataset to
    retrieve(settings)
    print('Raw data files were successfully retrieved.')

if run_option in ('visualize', 'all'):
    # Traverse raw data files
    summary_data = dict()
    summary_data.setdefault('CTR', np.empty(31))
    summary_data.setdefault('Clicks', np.empty(31))

    traverse(settings['raw_folderpath'], select_stats_unregistered)
    print('Raw data files were successfully processed.')


    # Make plots of CTR and total clicks over time
    df = pd.DataFrame(summary_data)

    fix, ax = plt.subplots(nrows=2, ncols=1)

    df['CTR'].plot(
        title='Click-through rate over one month',
        ax=ax[0],
        figsize=(8, 9),
        xticks=[]
    )
    df['Clicks'].plot(
        title='Total clicks over one month',
        ax=ax[1],
        figsize=(8, 9),
        xticks=range(0, 31, 2)
    )
    plt.show()

if run_option in ('save', 'all'):
    # Save processed results
    traverse(settings['raw_folderpath'], save_stats)
