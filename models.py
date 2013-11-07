#!usr/bin/env python

"""
This file contains the general data storage classes used throughout Logician.
"""

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
        else:
            raise TypeError('Invalid data type')
        self.sample_rate = sample_rate
        self.dt = 1.0 / sample_rate
        self.channel_count = len(self.data)
        self.acquisition_length = len(self.data[0])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def csv_string(self):
        out_string = '#sample_rate=%d' % self.sample_rate
        for row in zip(*self.data):
            out_string += str(row)[1:-1].replace(' ', '')
            out_string += '\n'
        return out_string


class AnalyzerCommand:
    """
    Simple class to hold analyzer commands and create appropriate command bytes
    to be sent to the firmware.
    """
    def __init__(self, sample_rate=1e6, sample_count=4000,
                 trigger_type=0, trigger_channel=0):
        sp = int(1.0 / sample_rate / 1e-6)
        self.command_bytes = \
            [0x01,                              # Command
             (sp & 0x00FF), (sp >> 8),          # Sample Period (us)
             (sample_count & 0x00FF), (sample_count >> 8),
             trigger_type, trigger_channel]
        self.command_bytes = (''.join([chr(x) for x in self.command_bytes]) +
                              ' '*(64 - len(self.command_bytes)))

