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

More Thoughts
=============
Mimicing the full TileSet API is not necessary with zarr-backing, since it knows how to produce
xarrays directly from its chunks. The concept of a TileSet is kinda zarr-internal. To me this says
that the starfish API should really be something like "return me an xarray or something that can
become an xarray". Any other complexity we've got in the codebase should go live in the format
library (zarr/slicedimage).

Looking at zarr, it supports any storage class that implements a mutable mapping over chunks.
We could write a TIFF backend, for example, in which 2d-TIFF files serve as the chunks. This could
look very similar to the existing SpaceTx-Format and might use part of slicedimage as the back-end.
If we inserted zarr in this way, it may help us to separate concerns about format vs library in
starfish.

Writing ImageStacks in Starfish is very closely tied to the SpaceTx-Format specification; it might
be a good idea to factor out code that relates specifically to slicedimage into slicedimage. It
feels like the right balance is that TileSet is an object that lives in starfish and exposes the
minimum API needed to construct an ImageStack. That feels *much* more minimal than what exists
there right now. Conversely, leaving this object in starfish means we could also have a
to_tileset() method that creates a TileSet from the ImageStack.

The downside of this is that I don't have a great sense of how to separate the backing of the
TileSet from starfish. The zarr approach of specifying its API using a standard python ABC is a
nice trick that I'd love to implement everywhere.

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
