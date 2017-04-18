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
from custom_blocks.sparse_recovery import SparseRecovery
from utils import sparse_recovery as sr
import numpy as np


class qa_SparseRecovery(gr_unittest.TestCase):

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
        signal_amps = sr.amplitude_vector(high_rate, n_tones)

        # demodulator matrices
        repr_mat = sr.perm_dftmtx(high_rate)
        D = sr.chipping_matrix(high_rate)
        H = sr.acc_dump_matrix(low_rate, high_rate)
        measure_mat = np.dot(H, D)
        overall_mat = np.dot(measure_mat, repr_mat)

        # output = system * input
        y = np.dot(overall_mat, signal_amps)

        #########################
        src1 = blocks.vector_source_c(y.flatten().tolist())
        scr1_1 = blocks.stream_to_vector(8, low_rate)
        src2 = blocks.vector_source_f(np.diag(D))
        scr2_1 = blocks.stream_to_vector(4, high_rate)
        recovered = SparseRecovery(high_rate, low_rate)
        recovered_1 = blocks.vector_to_stream(8, high_rate)
        dst = blocks.vector_sink_c()

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
        print(np.dot(repr_mat, signal_amps))


if __name__ == '__main__':
    gr_unittest.run(qa_SparseRecovery, "qa_SparseRecovery.xml")
