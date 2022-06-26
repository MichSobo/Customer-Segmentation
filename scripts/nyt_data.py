import io
import sys
import shutil
import pathlib

import requests
import numpy as np
import pandas as pd

if sys.version_info > (3, 7):
    import zipfile
else:
    import zipfile37 as zipfile

unpacked_foldername = '/dds_datasets/'
unpacked_zip_filename = 'dds_ch2_nyt.zip'


def retrieve(source_filepath, destination_folderpath):
    """Download dataset and unpack it."""

    def cleanup():
        try:
            shutil.rmtree(destination_folderpath + unpacked_foldername)
        except OSError as e:
            print(f'Folder: {e.filename}, Error: {e.strerror}')

    r = requests.get(source_filepath)
    assert r.status_code == requests.codes.ok

    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(destination_folderpath)

    # The top archive contains another ZIP file with data
    z = zipfile.ZipFile(
        destination_folderpath + unpacked_foldername + unpacked_zip_filename)
    z.extractall(destination_folderpath)

    # Remove temporary folder
    cleanup()


def summarize(data_filepath):
    def q25(x):
        """Return the 1st quartile of x collection."""
        return x.quantile(0.25)

    def q75(x):
        """Return the 3rd quartile of x collection."""
        return x.quantile(0.75)

    # Read and parse the CSV data file
    data = pd.read_csv(
        data_filepath,
        dtype={'Gender': 'category'}
    )

    # Categorize user ages
    data['Age_Group'] = pd.cut(
        data['Age'],
        bins=[-1, 0, 17, 24, 34, 44, 54, 64, 120],
        labels=['Unknown', '1-17', '18-24', '25-34', '35-44', '45-54', '55-64',
                '65+']
    )
    # data.drop('Age', axis='columns', inplace=True)

    # Create click-through rate feature
    data['CTR'] = data['Clicks'] / data['Impressions']

    # Remove redundant entries
    data.dropna(subset=['CTR'], inplace=True)

    try:
        data.drop(data[data['CTR'] > 1].index.values, inplace=True)
    except TypeError:
        pass  # no entries exceeded the value of 1

    # Make the final description
    compressed_data = data.groupby(
        by=['Age_Group', 'Gender'])[['CTR', 'Clicks']].agg(
            ['mean', 'std', q25, 'median', q75, 'max', 'sum']
    )
    return compressed_data


def traverse(source_folderpath, collect):
    def get_file_number(filename):
        """Extract the sequence number from a data file name."""
        return int(filename.name[3:-4]) - 1

    for filename in pathlib.Path(source_folderpath).glob('nyt*.csv'):
        collect(summarize(filename.absolute()), get_file_number(filename))
