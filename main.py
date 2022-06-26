import os
import sys
import json
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
    df.to_parquet(os.path.join('results', target_filename))


config_filepath = 'config.json'

# Read configuration file
global settings
with open(config_filepath) as f:
    settings = json.load(f)

# Download and unpack the dataset to
destination_folderpath = 'raw_data'
retrieve(repo_url + file_url, destination_folderpath)
print('Raw data files were successfully retrieved.')

# Process a single file
data = summarize(os.path.join(destination_folderpath, 'nyt1.csv'))

# Traverse raw data files
summary_data = dict()
summary_data.setdefault('CTR', np.empty(31))
summary_data.setdefault('Clicks', np.empty(31))

traverse(destination_folderpath, select_stats_unregistered)
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

# Save processed results
traverse('raw_data', save_stats)
