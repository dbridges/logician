"""
An Analyzer class should take an Acquisition object and return a list of labels
and their resepective locations: [(10, 'A'), (8, 'B'), ...].

All analyzer class should take these values in their constructors:
    display_mode        ascii, hex, decimal

"""

from itertools import groupby


def labels(protocol):
    if protocol.lower() == 'usart':
        return USARTAnalyzer.channel_names
    elif protocol.lower() == 'spi':
        return SPIAnalyzer.channel_names
    elif protocol.lower() == 'i2c':
        return I2CAnalyzer.channel_names
    else:
        return ['Channel 0', 'Channel 1', 'Channel 2', 'Channel 3']


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
    channel_names = ['RX', 'TX', 'Channel 2', 'Channel 3']

    def __init__(self, acquisition, display_mode, baud=None):
        self.acquisition = acquisition
        self.display_mode = display_mode
        if baud is None:
            self._autobaud()
        else:
            self.baud = baud
            self.bit_size = int(acquisition.sample_rate / self.baud)

    def _autobaud(self):
        """
        Attempts to find the size of 1 bit in the acquired data by looking for
        the shortest number of continuous values.

        Notes
        -----
        This algorithim may be inaccurate if the data does not contain isolated
        bits. For example if the decimal value 51 (0b00110011) was transmited
        the calculated autobaud would be inaccurate by a factor of two.
        """
        # Find smallest length of continuous values, this is
        rx_bit_s = min([len(list(g)) for k, g in groupby(self.acquisition[0])])
        tx_bit_s = min([len(list(g)) for k, g in groupby(self.acquisition[1])])
        self.bit_size = min(rx_bit_s, tx_bit_s)

    def labels(self):
        pass


class SPIAnalyzer:
    """
    SPI acquisition analyzer.

    Parameters
    ----------
    acquisition : Acquisition
        The Acquisition object to analyze.
    display_mode : str
        Should be one of 'ascii', 'hex', 'decimal'. The format to display the
        labels
    """
    channel_names = ['CLK', 'MOSI', 'MISO', 'CS']

    def __init__(self, acquisition, display_mode):
        self.acquisition = acquisition
        self.display_mode = display_mode


class I2CAnalyzer:
    """
    I2C acquisition analyzer.

    Parameters
    ----------
    acquisition : Acquisition
        The Acquisition object to analyze.
    display_mode : str
        Should be one of 'ascii', 'hex', 'decimal'. The format to display the
        labels
    """
    channel_names = ['SCL', 'SDA', 'Channel 2', 'Channel 3']

    def __init__(self, acquisition, display_mode):
        self.acquisition = acquisition
        self.display_mode = display_mode
