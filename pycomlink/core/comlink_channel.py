# ----------------------------------------------------------------------------
# Name:         comlink_channel
# Purpose:      Class that represents one channel of a CML, holding the
#               TX and RX data as well as info on frequency
#               and polarization.
#
# Authors:      Christian Chwala
#
# Created:      24.02.2016
# Copyright:    (c) Christian Chwala 2016
# Licence:      The MIT License
# ----------------------------------------------------------------------------


import pandas as pd
import copy


class ComlinkChannel(object):
    """A class for holding CML channel data and metadata"""

    #
    # !!! Many of the subclassing things need pandas >=0.17 !!!
    #

    # According to the pandas docs this is necessary to have
    # additional attributes
    # _metadata = ['f_GHz', 'pol', 'atpc', 'id',
    #             'sampling_type', 'temporal_resolution',]

    def __init__(self, *args, **kwargs):
        """

        Parameters
        ----------

        data: pandas.DataFrame, or everything that DataFrame.__init__() digests

        index: list, np.array, or everything that DataFrame.__init__() digest

        rx: list or np.array

        tx: list or np.array

        rx_min: list or np.array

        rx_max: list or np.array

        f_GHz: float

        pol: str {'h', 'v', 'H', 'V'}

        atpc: boolean

        """
        f_GHz = kwargs.pop('f_GHz', None)
        pol = kwargs.pop('pol', None)
        atpc = kwargs.pop('atpc', None)

        data = kwargs.pop('data', None)

        t = kwargs.pop('t', None)
        rx = kwargs.pop('rx', None)
        tx = kwargs.pop('tx', None)
        rx_min = kwargs.pop('rx_min', None)
        rx_max = kwargs.pop('rx_max', None)

        # TODO: If this is not supplied we should maybe derive it somehow
        self.sampling_type = None

        # Parse the different data relevant kwargs to a DataFrame
        # and add it back to the kwargs so that we can pass this
        # then on to the pandas.DataFrame.__init__() below
        kwargs['data'] = self._parse_kwargs_to_dataframe(
            data=data, t=t, rx=rx, tx=tx, rx_min=rx_min, rx_max=rx_max)

        # super(ComlinkChannel, self).__init__(*args, **kwargs)
        self._df = kwargs.pop('data')

        # TODO: Sanely parse metadata
        self.f_GHz = f_GHz

    def __eq__(self):
        pass

    def __getitem__(self, key):
        new_cml_ch = self.__copy__()
        new_cml_ch._df = self._df.__getitem__(key)
        return new_cml_ch

    def __len__(self):
        return len(self._df)

    def __str__(self, *args, **kwargs):
        print 'f_GHz: ', self.f_GHz
        print self._df.__str__()

    def __getattr__(self, item):
        try:
            return self._df.__getattr__(item)
        except:
            raise AttributeError('Neither \'ComlinkChannel\' nor its \'DataFrame\', '
                                 'has the attribute \'%s\'' % item)

    def __copy__(self):
        cls = self.__class__
        new_cml_ch = cls.__new__(cls)
        new_cml_ch.__dict__.update(self.__dict__)
        return new_cml_ch

    def __deepcopy__(self):
        new_cml_ch = self.__copy__()
        new_cml_ch._df = copy.deepcopy(self._df)
        return new_cml_ch

    def _repr_html_(self):
        print 'f_GHz: ', self.f_GHz
        return self._df._repr_html_()

    def copy(self):
        return self.__deepcopy__()
        #return copy.deepcopy(self)

    def resample(self, *args, **kwargs):
        inplace = kwargs.pop('inplace', False)

        if inplace:
            self._df = self._df.resample(*args, **kwargs)
        elif not inplace:
            new_cml_ch = copy.copy(self)
            new_cml_ch._df = self._df.resample(*args, **kwargs)
            return new_cml_ch
        else:
            raise ValueError('`inplace` must be either True or False')

    def _parse_kwargs_to_dataframe(self, data, t, rx, tx, rx_min, rx_max):
        # The case where only `t` and `rx` are supplied
        if ((data is None) and
                (tx is None) and
                (rx is not None) and
                (t is not None)):
            if (rx_min is not None) or (rx_max is not None):
                raise ValueError('`rx_min` and `rx_max` must not be supplied '
                                 'if `rx` is supplied')
            return pd.DataFrame(index=t, data={'rx': rx})

        # The case where `data` has been supplied.
        # We check that `data` is a DataFrame below.
        elif data is not None:
            if ((tx is not None) or (rx is not None) or
                    (rx_min is not None) or (rx_max is not None) or
                    (t is not None)):
                raise ValueError('`rx`, `tx`, `rx_min`, `rx_max`  and  `t` '
                                 'must not be supplied if `data` is supplied')
            if isinstance(data, pd.DataFrame):
                # `data` is what we want, so return it
                return data

            else:
                raise ValueError('`data` must be a pandas.DataFrame')

        else:
            raise ValueError('Could not parse the supplied arguments')