# Shiver

Create and activate conda environment for shiver development

```bash
conda env create
# or
mamba env create

conda activate shiver
```

Install shiver (in editable mode) and start application

```bash
python -m pip install -e .

shiver
```

To start shiver from within the Mantid workbench, start
`mantidworkbench` then run the following in the `IPython` console

```python
from shiver import Shiver
s=Shiver()
s.show()
```

[![CI](https://github.com/neutrons/Shiver/actions/workflows/actions.yml/badge.svg?branch=next)](https://github.com/neutrons/Shiver/actions/workflows/actions.yml)
[![codecov](https://codecov.io/gh/neutrons/shiver/branch/next/graph/badge.svg?token=J1ZNHXF6Ml)](https://codecov.io/gh/neutrons/shiver)