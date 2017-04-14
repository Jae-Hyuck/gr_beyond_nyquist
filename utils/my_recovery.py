import numpy as np
import math
import scipy.linalg as la
from sklearn.linear_model import OrthogonalMatchingPursuit


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
    repr_mat = repr_mat.real
    D = np.diagflat(chipping_seq)
    H = acc_dump_matrix(low_rate, high_rate)
    measure_mat = np.dot(H, D)
    overall_mat = np.dot(measure_mat, repr_mat)

    # reconstruction
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=10)
    omp.fit(overall_mat, low_rate_samples)
    coef = omp.coef_
    high_rate_samples = np.dot(repr_mat, coef)

    return high_rate_samples


if __name__ == '__main__':
    # parameters
    n_tones = 5
    low_rate = 32
    high_rate = 128
    assert high_rate % low_rate == 0

    # signal
    signal_amps = amplitude_vector(high_rate, n_tones)
    signal_amps = signal_amps.real

    # demodulator matrices
    repr_mat = perm_dftmtx(high_rate)
    repr_mat = repr_mat.real
    D = chipping_matrix(high_rate)
    H = acc_dump_matrix(low_rate, high_rate)
    measure_mat = np.dot(H, D)
    overall_mat = np.dot(measure_mat, repr_mat)

    # output = system * input
    y = np.dot(overall_mat, signal_amps)

    # reconstruction
    omp = OrthogonalMatchingPursuit()  # (n_nonzero_coefs=n_tones)
    omp.fit(overall_mat, y)
    coef = omp.coef_

    # compare
    print(np.dot(repr_mat, signal_amps))
    print(np.dot(repr_mat, coef))
