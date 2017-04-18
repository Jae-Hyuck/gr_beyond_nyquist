import numpy as np
import math
import scipy.linalg as la

import matlab.engine
eng = matlab.engine.start_matlab()
eng.addpath('utils/sparsify_0_5/GreedLab')


def amplitude_vector(high_rate, n_tones):
    y = np.zeros(high_rate)
    shuffle = np.random.permutation(high_rate)
    y[shuffle[0:n_tones]] = 1
    y = y * np.exp(1j * np.random.rand(high_rate) * 2 * math.pi)
    return(y)


def perm_dftmtx(size):
    dftmtx = np.fft.fft(np.eye(size))
    F = dftmtx / math.sqrt(size)
    shift_idx = np.roll(np.arange(size), size//2-1)
    return F[shift_idx, :]


def chipping_matrix(size):
    return np.diagflat(np.sign(np.random.rand(1, size) - 0.5))


def acc_dump_matrix(low_rate, high_rate):
    scale = high_rate // low_rate
    block = np.ones([1, scale])
    blocks = [block] * low_rate
    return la.block_diag(*blocks)


def run(low_rate_samples, chipping_seq, high_rate, low_rate):

    assert high_rate % low_rate == 0

    # demodulator matrices
    repr_mat = perm_dftmtx(high_rate)
    D = np.diagflat(chipping_seq)
    H = acc_dump_matrix(low_rate, high_rate)
    measure_mat = np.dot(H, D)
    overall_mat = np.dot(measure_mat, repr_mat)

    # reconstruction
    overall_mat_matlab = matlab.double(list(overall_mat.flatten('F')),
                                       size=overall_mat.shape,
                                       is_complex=True)
    y_matlab = matlab.double(list(low_rate_samples),
                             size=(low_rate, 1),
                             is_complex=True)
    coef = eng.greed_gp(y_matlab, overall_mat_matlab, overall_mat.shape[1])
    coef = np.array(coef._real) + 1j * np.array(coef._imag)
    high_rate_samples = np.dot(repr_mat, coef)

    return high_rate_samples


# toy example
if __name__ == '__main__':
    # parameters
    n_tones = 5
    low_rate = 32
    high_rate = 128
    assert high_rate % low_rate == 0

    # signal
    signal_amps = amplitude_vector(high_rate, n_tones)

    # demodulator matrices
    repr_mat = perm_dftmtx(high_rate)
    D = chipping_matrix(high_rate)
    H = acc_dump_matrix(low_rate, high_rate)
    measure_mat = np.dot(H, D)
    overall_mat = np.dot(measure_mat, repr_mat)

    # output = system * input
    y = np.dot(overall_mat, signal_amps)

    # reconstruction
    overall_mat_matlab = matlab.double(list(overall_mat.flatten('F')),
                                       size=overall_mat.shape,
                                       is_complex=True)
    y_matlab = matlab.double(list(y),
                             size=(low_rate, 1),
                             is_complex=True)
    coef = eng.greed_gp(y_matlab, overall_mat_matlab, overall_mat.shape[1])
    coef = np.array(coef._real) + 1j * np.array(coef._imag)

    # compare
    print(np.dot(repr_mat, signal_amps))
    print(np.dot(repr_mat, coef))
