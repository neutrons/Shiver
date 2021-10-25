---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
---

Visualizing data from neutron scattering experiments is the first step in understanding the physics. 
The scripts described in the following sections allow generation and plotting of cuts and slices
through the four dimensional single crystal inelastic datasets measured on direct geometry
neutron spectrometers at SNS (ARCS, CNCS, HYSPEC, SEQUOIA). The programming language used
is Python, with visualization done using Matplotlib. Data processing is done using [Mantid](https://mantidproject.org)
algorithms. Preprocessing is mostly based on [DgsReduction](https://docs.mantidproject.org/nightly/algorithms/DgsReduction-v1.html)
and [ConvertToMD](https://docs.mantidproject.org/nightly/algorithms/ConvertToMD-v1.html) algorithms. 
Data slicing is based on the [MDNorm](https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html) algorithm.

The basic workflow for the user is to create and modify three scripts. The first one describes 
the data to be processed, including some parameters that are independent of teh visualization.
The second script describes the visualization parameters (slice/cut thickness, position, step size, etc.).
The main script puts everything together. It allows taking multiple slices and/or multiple datasets and 
combine them into figures and documents.

```python
def test():
    pass
```
