---
layout: default
---
* TOC
{:toc}

# Sample parameters

This dialog box allows setting/ modifying the lattice parameters and sample orientation
(the UB matrix). There are two ways to specify these:
 * The `a`, `b`, `c`, `alpha`, `beta`, `gamma` are the lattice parameters. When the goniometer
 angles are all zero, the orientation vector `u = (ux, uy, uz)` points along the beam,
 and the `v = (vx, vy, vz)` vector is in the horizontal plane, not necessarily perpendicular to `u`,
 in a way that the cross product points upward.
 * The `UB` matrix. A good explanation can be found in the [Mantid concepts page](https://docs.mantidproject.org/nightly/concepts/Lattice.html)
 
One can also load these parameters from the raw file, a processed nexus file, or an ISAW UB matrix file.
 
![Shiver UB setup]({{ site.baseurl }}/images/Shiver-UB.png)


# Polarization options

For polarized neutron experiments, it is useful to label the data with the polarization state:

![Shiver UB setup]({{ site.baseurl }}/images/Shiver-polarization_opt.png)

The state it used as a suggestion when [selecting data]({{ site.baseurl }}/GUI/main_window/#selecting-data).

If both polarization states are selected in the main window, the `Flipping ratio`
and `Flipping ratio sample log` parameters are passed to the
[FlippingRatioCorrectionMD](https://docs.mantidproject.org/nightly/algorithms/FlippingRatioCorrectionMD-v1.html) algorithm, so in the end one ends up with flipping ratio corrected histograms.

For the HYSPEC instrument, when using the supermirror polarization analyser, the neutron will be deflected by
a small amount, the `PSDA` (polarization supermirror deflection angle). This needs to be
taken in consideration when generating the MD event data. By default, this
value is taken from the file, so leave this field empty. If you want to override, `0.0` is unpolarized,
and `-1.3` is for the polarized state.


# Advanced reduction options

When generating multi-dimensional event data sets, there are some advanced options available:

![Shiver UB setup]({{ site.baseurl }}/images/Shiver-advanced_reduction.png)

 * In addition to the mask file in the [Generate]({{ site.baseurl }}/GUI/generate) tab, one can mask
 additional detectors. Each line in the `Mask Bank, Tube, Pixel` is used independently. So in the example
 in the figure, tubes 1, 2, and 3 in the first bank are masked, followed by masking pixels 1 to 8 and 121
 to 128 in every bank, in every tube.
 * The `Emin` and `Emax` define the energy transfer range, in meV. The default values
 are -0.95 and +0.95 times the incident energy
 * The pulses with low proton charge can be filtered out using the `Apply filter bad pulses`
 flag, where neutrons coming from pulses with charge less than `Lower cutoff (%)` of the median
 pulse charge will be ignored
 * One can subtract a time independent background. If `Instrument default` option is used, there is no such
 subtraction for ARCS or SEQUOIA instruments. For CNCS and HYSPEC, a range is calculated based
 on incident energy. One can override this behavior by selecting `Yes`, in which case one must
 specify the range manually, or `No`.
 * By default, the sample rotation angle is obtained from the `phi`, `chi`, and `omega` logs in the file.
 If not present, or incorrect, one can specify a different sample log name that contains the rotation
 around the vertical axis, using the `Goniometer` field.
 * The `Additional dimensions` is not currently used in the main histogramming part, but it can be in
 a script. This field specifies the name of an additional dimension in the dataset, such as
 sample temperature. The value associated with each event is the average value in the original file
 (no filtering is taking place)
 
