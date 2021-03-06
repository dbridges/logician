"""
An Analyzer class should take an Acquisition object and return a list of labels
and their resepective locations and widths: [(10, 80, 'A'), (8, 80, 'B'), ...].
where 10 is the left edge, 80 is the width of the label, and 'A' is the text.

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
        return ['Ch 0', 'Ch 1', 'Ch 2', 'Ch 3']


def format_byte(value, format_type='ascii'):
    """
    Returns a string for displaying a byte value in the requested format.

    Parameters
    ----------
    value : int
        The value to format, should be 0 - 255

    format_type : str
        The display format, one of 'ascii', 'hex', 'decimal'.
    """
    format_type = format_type.lower()
    if format_type == 'ascii':
        return chr(value)
    elif format_type == 'hex':
        return hex(value)
    elif format_type == 'decimal':
        return str(value)
    else:
        raise ValueError("format_type must be 'ascii', 'hex', or 'decimal'")


class USARTAnalyzer:
    """
    USART acquisition analyzer.

    Parameters
    ----------
    acquisition : Acquisition
        The Acquisition object to analyze.
    baud : int
        If None autobaud is attempted, otherwise the baudrate of the
        acquisition.
    """
    channel_names = ['RX', 'TX', 'Ch 2', 'Ch 3']

    def __init__(self, acquisition, baud=None):
        self.acquisition = acquisition
        self.parity = None
        self.bit_count = 8
        if baud is None:
            self._autobaud()
        else:
            self.baud = baud
            self.bit_size = float(acquisition.sample_rate) / self.baud

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
        bit_size = min(rx_bit_s, tx_bit_s)
        baud = self.acquisition.sample_rate / bit_size
        # Check to see if we are close to a standard baud rate
        bauds = [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
        for b in bauds:
            if baud < b*1.2 and baud > b*0.8:
                baud = b
                break
        self.baud = baud
        self.bit_size = float(self.acquisition.sample_rate) / self.baud

    def labels(self):
        return [self._read_waveform(n)
                for n in range(len(self.acquisition))]

    def _read_waveform(self, waveform_i):
        """
        Returns the labels for the given waveform.

        Parameters
        ----------
        waveform_i : int
            The index of the wavefrom to encode.

        Returns
        -------
        List of tuples
            Returns a list of tuples in form: [(t0, 'a'), (t1, 'b'), ...],
            where t0, t1, are the float approximations of indicies of the
            center of each byte.
        """
        labels = []
        start_i = 0
        max_i = (self.acquisition.acquisition_length -
                 int(self.bit_size * self.bit_count))
        while start_i < max_i:
            while self.acquisition[waveform_i][start_i] == 0:
                start_i += 1
                if start_i >= max_i:
                    return labels
            while self.acquisition[waveform_i][start_i] == 1:
                start_i += 1
                if start_i >= max_i:
                    return labels
            # add 1 bit for start bit
            labels.append((start_i + self.bit_size,
                           self.bit_size * self.bit_count,
                           self._read_byte(waveform_i,
                                           start_i + self.bit_size)))
            start_i += int(self.bit_size * self.bit_count)
        return labels

    def _read_byte(self, waveform_i, start_pos):
        """
        Returns the value of the first byte received after start_pos.

        Parameters
        ----------
        waveform_i : int
            The index of the waveform to search in.
        start_pos : float
            The location of the leading edge of the first bit.
        """
        val = 0
        for n in range(self.bit_count):
            bit_i = int(start_pos + (n*self.bit_size + (self.bit_size / 2)))
            val += self.acquisition[waveform_i][bit_i] << n
        return val


class SPIAnalyzer:
    """
    SPI acquisition analyzer.

    Parameters
    ----------
    acquisition : Acquisition
        The Acquisition object to analyze.
    """
    channel_names = ['CLK', 'MOSI', 'MISO', 'CS']

    def __init__(self, acquisition):
        self.acquisition = acquisition

    def labels(self):
        return []


class I2CAnalyzer:
    """
    I2C acquisition analyzer.

    Parameters
    ----------
    acquisition : Acquisition
        The Acquisition object to analyze.
    """
    channel_names = ['SCL', 'SDA', 'Ch 2', 'Ch 3']

    def __init__(self, acquisition):
        self.acquisition = acquisition

    def labels(self):
        return []
