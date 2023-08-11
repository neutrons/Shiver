Deployments
===========

.. _deploy:

Branches
--------

The repository contains three main-permanent branches:

* `next <https://github.com/neutrons/Shiver/tree/next>`_

This is the central branch that all other branches are created by
``e.g., git checkout -b <feature_branch> next``

* `main <https://github.com/neutrons/Shiver/tree/main>`_

No development allowed in this branch. The branch is a result of the next branch
(for production release). The next branch is merged into this one manually.
When you put the tag (without rc suffix), this should be updated from
next manually; more on tags in the `Tags`_ section.

* `qa <https://github.com/neutrons/Shiver/tree/qa>`_

No development allowed in this branch. The branch is a results of the next branch
(for the qa release). The next branch is merged into this one manually. When
you put the tag (with rc suffix), this should be updated from next manually;
more on tahs in the `Tags`_ section.

Code Contribution
-----------------

After creating a temporary branch from *next* locally, developers can make
changes to the code. Before commiting-pushing any changes on the remote
repository:

1. Run pre-commit manually: ``pre-commit run --all-files`` and/or set it
before each commit ``pre-commit install``

2. Run all tests (including your newly created ones, if necessary) within
``pytest`` to ensure everything passes.


.. note:: Additional Information Regarding Mantid

    Some mantid algorithms/concepts used in the project: `ConvertToMD <https://docs.mantidproject.org/nightly/algorithms/ConvertToMD-v1.html>`_,
    `MDNorm <https://docs.mantidproject.org/nightly/algorithms/MDNorm-v1.html>`_ and ``Workspace`` dimensionality.

    In ``SHIVER``, ``mantid`` algorithms are executed asynchronously using the ``AlgorithmManager``.
    This allows the progress bar to be displayed, while waiting for the algorithm completion, and
    the GUI to be responsive.

.. _Tags:

Tags
----

The branches: ``qa`` and ``main`` need to be approved with the latest code
from ``next``. After approval, we assign a tag as follows:

From command line on the corresponding branch ``(main/qa)``:

.. code-block:: sh

    git tag <tag>
    git push origin -tags <branch name>

Click `here <https://code.ornl.gov/sns-hfir-scse/neutron-data-project-docs/-/blob/next/docs/standards/maturity.rst>`_
for more information.
