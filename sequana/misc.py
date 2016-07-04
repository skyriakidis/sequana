# -*- coding: utf-8 -*-
#
#  This file is part of Sequana software
#
#  Copyright (c) 2016 - Sequana Development Team
#
#  File author(s):
#      Thomas Cokelaer <thomas.cokelaer@pasteur.fr>
#      Dimitri Desvillechabrol <dimitri.desvillechabrol@pasteur.fr>, 
#          <d.desvillechabrol@gmail.com>
#
#  Distributed under the terms of the 3-clause BSD license.
#  The full license is in the LICENSE file, distributed with this software.
#
#  website: https://github.com/sequana/sequana
#  documentation: http://sequana.readthedocs.io
#
##############################################################################
"""misc utilities"""
import numpy as np

def wget(link, output):
    """Retrieve a file from internet.

    :param str link: a valid URL
    :param str output: the output filename

    .. warning:: no sanity check of any kind for now
    """
    try:
        from urllib import urlretrieve
    except:
        from urllib.request import urlretrieve
    urlretrieve(link, filename=output)

def findpos(seq, chr):
    N = len(chr)
    for i, dummy in enumerate(seq):
        if seq[i:i+N] == chr:
            yield i


def moving_average(data, n):
        """Compute moving average

        :param n: window's size.

        """
        ret = np.cumsum(data, dtype=float)
        ret[n:] = ret[n:] - ret[:-n]
        ma = ret[n - 1:] / n
        return ma

