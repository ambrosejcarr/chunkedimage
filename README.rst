Chunkedimage
============

This repository represents my attempts to understand how slicedimage works by generalizing
``starfish.Experiment`` to read from data stored in Zarr format. This repository contains
a haphazardly constructed prototype that at present is able to *read* data from a ``.zarr``
formatted experiment file from a *local filesystem*.

Further commits will be made as time permits that:

1. Enable reading from s3 in a listable (public) directory
2. Enable writing to the chunkedimage-modified SpaceTx-Format
3. Enable dask backing of zarr-formatted ImageStacks

If we decide anything here is actually useful, additional work would be needed to:

1. Think up a way to make the zarr translation of SpaceTx-Format self-describing.
2. add cryptographic data checks -- zarr supports these for arrays, which is probably adequate for our purposes
3. make some issues about discoverability of groups or
4. add caching support to zarr

A list of modifications to the SpaceTx format made in support of this exercise are in
``specification/index.rst``. That file also contains some notes on slicedimage, now that I
understand a bit better how things work.

Installation
============

Installation is a bit fragile, as I haven't uploaded this repository to pypi yet. 

install this repository

::

    git clone https://github.com/ambrosejcarr/chunkedimage.git
    cd chunkedimage
    pip3 install -e .

install the ``ajc-zarr`` branch of ``starfish``

::

    cd starfish
    git checkout ajc-zarr
    pip3 install -e .


Download the ``baristaseq.zarr`` data

::

    aws s3 sync s3://spacetx.starfish.data.public/browse/zarr/baristaseq.zarr starfish/notebooks/baristaseq.zarr


run the test in starfish

::

    pytest starfish/test/experiment/test_experiment.py::test_experiment_from_zarr
