---
layout: default
---

* TOC
{:toc}

Conda install
=============

The Shiver program is available as a conda package. In a terminal type 
`conda install -c neutrons shiver` for the latest stable release
 or
`conda install -c "neutrons/label/rc" shiver` for the release candidate.

Source code install
===================

The code is available on [Github](https://github.com/neutrons/Shiver). 
Please follow installation instructions on that page.

Availability on analysis.sns.gov
================================

GUI
---

To start the graphical user interface, in a terminal type `shiver` (for main release) or `shiver --qa` (for testing branch). This will open the shiver main window:

![Main Shiver GUI]({{ site.baseurl }}/images/Shiver-main.png)

Alternatively, one can start the Mantid workbench within the appropriate conda environment 
`mantidworkbench --env=shiver` or `mantidworkbench --env=shive-qa`, 
then navigate in the menu to `Interfaces`>`Direct`>`Shiver`.

![Launching Shiver from Mantid]({{ site.baseurl }}/images/Shiver-mantid.png)


Scripting
---------

The original version of the scripting is available in the `/SNS/groups/dgs/DGS_SC_scripts`.
One needs to have Mantid in their Python path. The simplest way is to use `mantidpython`, or
run the scripts from withing the Mantid workbench.



