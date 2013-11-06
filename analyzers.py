#!/usr/bin/env python

"""
An Analyzer class should take an Acquisition object and return a list of labels
and their resepective locations: [(10, 'A'), (8, 'B'), ...].

All analyzer class should take these values in their constructors:
    display_mode        ascii, hex, decimal

"""

import itertools
import sys

class USARTAnalyzer:
    """
    USART acquisition analyzer.

    Parameters
    ----------
    acquisition : Acquisition
        The Acquisition object to analyze.
    display_mode : str
        Should be one of 'ascii', 'hex', 'decimal'. The format to display the
        labels
    baud : int
        If None autobaud is attempted, otherwise the baudrate of the
        acquisition.
    """
    channel_names = ['RX', 'TX', 'GPIO', 'GPIO']

    def __init__(self, acquisition, display_mode, baud=None):
        self.acquisition = acquisition
        self.display_mode = display_mode
        if baud is None:
            self._autobaud()
        else:
            self.baud = baud
            self.bit_size = int(acquisition.sample_rate / self.baud)

    def _autobaud():
        min_len = sys.maxint
        fot k, g in itertools.groupby(self.acquisition[0]):
            l = len(g)
            if l < min_len:
                min_len = l
        self.bit_size = min_len

    def labels(self):
        pass
