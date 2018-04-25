# TensorWow library
A pure Python + NumPy implementation of the foundations needed to build CNNs

Contains intentional and unintentional flaws.

## Set up
**Note**: Cython extension for `im2col` does not help the performance (about 10x slower).
Inside your virtual environment, compile the Cython extensions:

```bash
cd tensorwow
python setup.py build_ext --inplace
```