---
layout: default
---

* TOC
{:toc}

The overarching principle is to separate data description, slice description, and the presentation into different entities.
The basic workflow for the user is to create and modify three scripts. The first one describes 
the data to be processed, including some parameters that are independent of the visualization.
The second script describes the visualization parameters (slice/cut thickness, position, step size, etc.).
The main script puts everything together. It allows taking multiple slices and/or multiple datasets and 
combine them into figures and documents.

* [Data descriptions]({{ site.baseurl }}/Scripting/data_description/)
* [Slice descriptions]({{ site.baseurl }}/Scripting/slice_description/)
* [Main program]({{ site.baseurl }}/Scripting/main/)
* [Examples]({{ site.baseurl }}/Scripting/examples/)
* [Utility functions]({{ site.baseurl }}/Scripting/utility/)
