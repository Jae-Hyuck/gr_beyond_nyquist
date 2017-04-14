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

from gnuradio import gr, gr_unittest
from gnuradio import blocks
from custom_blocks.L1Recovery import L1Recovery
from utils.my_recovery import amplitude_vector, perm_dftmtx, chipping_matrix, acc_dump_matrix
import numpy as np


class qa_L1Recovery (gr_unittest.TestCase):

    def setUp(self):
        self.tb = gr.top_block()

    def tearDown(self):
        self.tb = None

    def test_001_t(self):
        # parameters
        n_tones = 5
        low_rate = 32
        high_rate = 128
        assert high_rate % low_rate == 0

        # signal
        s = amplitude_vector(high_rate, n_tones)

        # demodulator matrices
        F = perm_dftmtx(high_rate)
        F = F.real
        D = chipping_matrix(high_rate)
        H = acc_dump_matrix(low_rate, high_rate)
        M = np.dot(H, D)
        Phi = np.dot(M, F)

        s = s.real
        # output = system * input
        y = np.dot(Phi, s)

        #########################
        src1 = blocks.vector_source_f(y.flatten().tolist())
        scr1_1 = blocks.stream_to_vector(4, low_rate)
        src2 = blocks.vector_source_f(np.diag(D))
        scr2_1 = blocks.stream_to_vector(4, high_rate)
        recovered = L1Recovery(high_rate, low_rate)
        recovered_1 = blocks.vector_to_stream(4, high_rate)
        dst = blocks.vector_sink_f()

        # set up fg
        self.tb.connect(src1, scr1_1)
        self.tb.connect(scr1_1, (recovered, 0))
        self.tb.connect(src2, scr2_1)
        self.tb.connect(scr2_1, (recovered, 1))
        self.tb.connect(recovered, recovered_1)
        self.tb.connect(recovered_1, dst)
        self.tb.run()
        # check data

        result_data = dst.data()
        print(result_data)

        # ground truth
        print(np.dot(F, s))


if __name__ == '__main__':
    gr_unittest.run(qa_L1Recovery, "qa_L1Recovery.xml")
