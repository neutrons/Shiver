---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: default
---
Overview
============

Visualizing data from neutron scattering experiments is the first step in understanding the physics. 
The program described in the following sections allow generation and plotting of cuts and slices,
through the four dimensional single crystal inelastic datasets, measured on direct geometry
neutron spectrometers at SNS (ARCS, CNCS, HYSPEC, SEQUOIA). 

The original implementation was done by A. Savici (ORNL) and
I. Zaliznyak (BNL) in 2019. We used Python as the programming language,
with visualization done using Matplotlib.
Data processing is done using [Mantid](https://mantidproject.org) algorithms. 
The new graphical user interface is based on QtPy. 

For direct geometry spectroscopy in single crystal experiments, it is advantageous to transform
all the raw data to an intermediate muti-dimensional event workspace.
 Preprocessing is mostly based on [DgsReduction](https://docs.mantidproject.org/nightly/algorithms/DgsReduction-v1.html)
and [ConvertToMD](https://docs.mantidproject.org/nightly/algorithms/ConvertToMD-v1.html) algorithms. 
Data slicing is based on the [MDNorm](https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html) algorithm.


* [Installation and availability]({{ site.baseurl }}/install/)
* [Graphical user interface]({{ site.baseurl }}/GUI/)
* [Scripting]({{ site.baseurl }}/Scripting/)
* [Future plans]({{ site.baseurl }}/future/)
* [References]({{ site.baseurl }}/references/)
![HYSPEC example]({{ site.baseurl }}/images/multi_geometry_sym.png)
