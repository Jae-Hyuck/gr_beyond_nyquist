#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2017 <+YOU OR YOUR COMPANY+>.
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#

import numpy as np
from gnuradio import gr
from utils import sparse_recovery as sr


class SparseRecovery(gr.sync_block):
    """
    docstring for block
    """
    def __init__(self, high_rate, low_rate):
        self.high_rate = high_rate
        self.low_rate = low_rate
        gr.sync_block.__init__(
            self,
            name='SparseRecovery',
            in_sig=[(np.complex64, low_rate), (np.float32, high_rate)],
            out_sig=[(np.complex64, high_rate)])

    def work(self, input_items, output_items):
        low_rate_sample = input_items[0]
        chipping_seq = input_items[1]
        out = output_items[0]

        n = low_rate_sample.shape[0]
        for i in range(n):
            out[i, :] = sr.run(low_rate_sample[i], chipping_seq[i],
                               self.high_rate, self.low_rate)

        return len(output_items[0])
