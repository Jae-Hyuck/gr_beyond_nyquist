# gr_beyond_nyquist
Toy Implementation of Beyond Nyquist using GNU Radio.

### Run
```sh
$ cd gr_beyond_nyquist
$ export GRC_BLOCKS_PATH=./custom_blocks:$GRC_BLOCKS_PATH
$ gnuradio-companion beyond_nyquist.grc
```

### References
- Tropp, J.A., Laska, J.N., Duarte, M.F., Romberg, J.K., Baraniuk, R.G., "Beyond Nyquist: Efficient Sampling of Sparse Bandlimited Signals", IEEE Transactions on Information Theory, vol.56, no.1, pp.520-544, Jan. 2010.
- https://github.com/stemblab/beyond-nyquist - An implementation by MATLAB
