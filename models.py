"""
This file contains the general data storage classes used throughout Logician.
"""
import csv
from collections import OrderedDict

VALID_CHANNEL_COUNTS = [4]


class Acquisition:
    """
    The acqusition object contains data from all of the acquired channels.

    Parameters
    ----------
    data : array or bytes or str
        Array of form [[1, 0, 0, ...], [0, 0, 1, ...], ...]
        or bytes of data.
        If data is bytes, channel_count must be provided.

    samplerate : int
        The acquisition rate in Samples / sec.
    """
    def __init__(self, data, sample_rate=1, channel_count=None):
        if isinstance(data, list):
            if len(data) not in VALID_CHANNEL_COUNTS:
                raise ValueError('data must have length %s'
                                 % str(VALID_CHANNEL_COUNTS))
            l = len(data[0])
            for channel in data:
                if len(channel) != l:
                    raise ValueError('All channels must be have same length.')
            self.data = data
        elif isinstance(data, bytes):
            if channel_count not in VALID_CHANNEL_COUNTS:
                raise ValueError('Invalid number of channels.')
            # Convert byte string to list of 1's and 0's. If there are 4
            # channels each byte should have 2 4 channel samples in it. The MSB
            # is the 4th channel of the least recent sample.
            sep_channel_data = [f(c) for c in data
                                for f in (lambda x: ord(x) >> 4,
                                          lambda x: ord(x) & 0x0F)]
            unpacked_data = [[int(i) for i in list(bin(d)[2:].zfill(4))]
                             for d in sep_channel_data]
            self.data = zip(*unpacked_data)
            self.data.reverse()
        elif isinstance(data, str) or isinstance(data, unicode):
            self.load_csv_file(data)
            return
        else:
            raise TypeError('Invalid data type')
        self.sample_rate = sample_rate

    @property
    def dt(self):
        return 1.0 / self.sample_rate

    @property
    def acquisition_length(self):
        return len(self.data[0])

    @property
    def channel_count(self):
        return len(self.data)

    def csv_string(self):
        out_string = '#sample_rate=%d' % self.sample_rate
        for row in zip(*self.data):
            out_string += str(row)[1:-1].replace(' ', '')
            out_string += '\n'
        return out_string

    def load_csv_file(self, fname):
        with open(fname, 'rb') as f:
            reader = csv.reader(f)
            header = next(reader)
            sample_rate = int(header[0].split('=')[-1])
            data = [[int(d) for d in row] for row in reader
                    if len(row) != 1]
        self.data = zip(*data)
        self.sample_rate = sample_rate

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)


class AnalyzerCommand:
    """
    Simple class to hold analyzer commands and create appropriate command bytes
    to be sent to the firmware.
    """
    sample_counts = OrderedDict((('200K', 200000),
                                 ('100K', 100000),
                                 ('50K', 50000),
                                 ('10K', 10000),
                                 ('2K', 2000)))
    sample_rates = OrderedDict((('1 MS/s', 1000000),
                                ('500 KS/s', 500000),
                                ('200 KS/s', 200000),
                                ('100 KS/s', 10000)))

    def __init__(self, sample_rate=1e6, sample_count=64000,
                 trigger_type=0, trigger_channel=0):
        sp = int(1.0 / sample_rate / 1e-6)
        self.sample_count = sample_count
        self.sample_rate = sample_rate
        sample_count /= 1000
        self.command_bytes = \
            [0x01,                              # Command
             (sp & 0x00FF), (sp >> 8),          # Sample Period (us)
             (sample_count & 0x00FF), (sample_count >> 8),
             trigger_type, trigger_channel]
        self.command_bytes = (''.join([chr(x) for x in self.command_bytes]) +
                              ' '*(64 - len(self.command_bytes)))
