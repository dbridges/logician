#!/usr/bin/env python

import csv

import models

def read_csv(fname):
    with open(fname, 'rb') as f:
        reader = csv.reader(f)
        header = next(reader)
        sample_rate = int(header[0].split('=')[-1])
        data = [[int(d) for d in row] for row in reader
                if len(row) != 1]
    return models.Acquisition(zip(*data), sample_rate)

