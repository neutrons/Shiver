---
layout: default
---
* TOC
{:toc}

# Refine lattice parameters and orientation (UB matrix)

Sometimes the sample orientation or the lattice parameters are incorrect. In version 1.0.0 of
Shiver we introduced an experimental way to adjust these values.

![Shiver wrong UB]({{ site.baseurl }}/images/Shiver-wrongUB.png)

Click on the event workspace and select `Refine sample parameters`. The histogram
parameters will be prepopulated with some default values, to create a 3D view.

![Shiver refine UB parameters]({{ site.baseurl }}/images/Shiver-refineUB-parameters.png)

Once the histogram is created, a new tab is opened:

![Shiver refine UB tab]({{ site.baseurl }}/images/Shiver-refineUB-tab.png)

On the left hand side there is an embedded [Mantid slice viewer](https://docs.mantidproject.org/nightly/workbench/sliceviewer.html).
The center area is reserved for the list of peaks to be used for refinement. The right hand
side is used for plotting selected peaks and for controlling the refinement process.

To populate the peaks list, there are two options. The recommended procedure
is to click on `Populate Peaks` button. Then in the slice viewer just click on the desired
pek position. It will be marked with a red X. Do not worry if you did not clicked exactly
in the center. If possible, click on several non-coplanar peaks. If you use more peaks
you have a chance for a better refinement. An alternative way is to use `Predict Peaks`.
This will try to use all integer coordinates for peaks, so the list of peaks might be very long.

Clicking on any peak in the list will display the slices along the projection view directions:

![Shiver refine UB peak view]({{ site.baseurl }}/images/Shiver-refineUB-centering.png)

In the peaks list, select the peak you want to re-center. You can click one `Select All` and
manually deselect the few you don't need. Click on `Recenter` button.

The alignment usually happens on Bragg peaks at integer position. For all the peaks
used in the refinement one needs to set the `H`, `K`, `L` values to the expected ones. If the orientation
and lattice parameters are relatively good, one can just round these values to the neares integers.
Use the `Round HKL` button.

You are now ready for refinement. If there are peaks only in a single plane, one can easily just refine the
orientation. Use `Refine orientation only` button. Otherwise, one can use the `Refine` option. If you 
know the lattice type please use it.

![Shiver refine UB ready for refinement]({{ site.baseurl }}/images/Shiver-refineUB-ready.png)

Once you clink on the `Refine` or `Refine orientation only` buttons, Shiver will try to get a better UB
matrix, and will re-histogram the workspace.

![Shiver refine UB refinement check]({{ site.baseurl }}/images/Shiver-refineUB-check.png)

Check that everything is fine, using the Slice Viewer. If you are happy, ckick `Close`. The new UB
matrix is attached to the MDEvent workspace. For future use, in the main window use the workspace
context menu to save the dataset with the current orientation. If you are unhappy with the results,
click `Undo`

## Suggestions

 * Be mindful of memory and speed, when creating the 3D workspace. It is advisable to limit the ranges
 of the momentum dimensions.
 * Use linear scaling with `1.5-Inetrquartile Range` for best views of Bragg peaks.
 * It might be useful to do the refinement in steps, starting with orientation only.
