---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
---
Overview
============

Visualizing data from neutron scattering experiments is the first step in understanding the physics. 
The scripts described in the following sections allow generation and plotting of cuts and slices
through the four dimensional single crystal inelastic datasets measured on direct geometry
neutron spectrometers at SNS (ARCS, CNCS, HYSPEC, SEQUOIA). The original implementation was done by A. Savici (ORNL) and
I. Zaliznyak (BNL) in 2019. We usedPython as the programming language,
with visualization done using Matplotlib. Data processing is done using [Mantid](https://mantidproject.org)
algorithms. Preprocessing is mostly based on [DgsReduction](https://docs.mantidproject.org/nightly/algorithms/DgsReduction-v1.html)
and [ConvertToMD](https://docs.mantidproject.org/nightly/algorithms/ConvertToMD-v1.html) algorithms. 
Data slicing is based on the [MDNorm](https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html) algorithm.

The overarching principle is to separate data description, slice description, and the presentation into different entities.
The basic workflow for the user is to create and modify three scripts. The first one describes 
the data to be processed, including some parameters that are independent of the visualization.
The second script describes the visualization parameters (slice/cut thickness, position, step size, etc.).
The main script puts everything together. It allows taking multiple slices and/or multiple datasets and 
combine them into figures and documents.


* [Data descriptions]({{ site.baseurl }}/data_description/)
* [Slice descriptions]({{ site.baseurl }}/slice_description/)
* [Main program]({{ site.baseurl }}/main/)
* [Examples]({{ site.baseurl }}/examples/)
* [Utility functions]({{ site.baseurl }}/utility/)

![HYSPEC example]({{ site.baseurl }}/images/multi_geometry_sym.png)
