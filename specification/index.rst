ChunkedImage Specification
==========================

Chunkedimage requires some amendments to the slicedimage specification that stem a difference in how
zarr represents "Tiles". In slicedimage/SpaceTx-Format, Tiles are first class structures that have
associated attributes. In zarr, arrays are first class structures, and their chunks do not get their
own attrs objects. We could go the {"tiles": [<tile_data>]} route from slicedimage, but the below
implementation supports random access, instead of sequential list-based access.

As such, this zarr-based prototype does not strictly adhere to SpaceTx-Format. The following (poorly
thought-out) modifications have been made:

Coordinates
-----------
Coordinates of each (round, channel, z) image chunk must be defined. Because zarr stores attrs for
each array, not each chunk, the attrs for the array must be slightly more complex than the
slicedimage case.

the chunkedimage backend stores chunk coordinates as::

    Dict[
        round, Dict[
            channel, Dict[
                z, Dict[
                    z: Tuple[int, int],
                    y: Tuple[int, int],
                    x: Tuple[int, int]
                ]
            ]
        ]
    ]

These coordinates are stored in the ``Array.attrs`` mapping under the ``tile_coordinates`` key. in
the future flexibility may be added for FoV-level coordinates. This type of storage, due to the
json serialization requirement, is a pain. If there are better ways to store these data, this
structure has room for improvement.


Extras
------

the chunkedimage backend stores chunk extras as::

    Dict[
        round, Dict[
            channel, Dict[
                z, Any
            ]
        ]
    ]

These coordinates are stored in ``Array.attrs`` under the ``tile_extras`` key.
In the future flexibility may be added for FoV-level extras. This type of storage, due to the
json serialization requirement, is a pain. If there are better ways to store these data, this
structure has room for improvement.

Notes from the exercise
=======================

The main point of this was to try to generalize our backend and to try to better understand
slicedimage. Slicedimage is really slick! I had a few thoughts on potential refactorings that might
make it clearer for a new user to pick up, or to support someone who wants to implement a new
backend. These ideas might be useful to contemplate when we're thinking about documenting the
objects in starfish and slicedimage that support SpaceTx Format.


Notes on Starfish and SpaceTx-Format
------------------------------------
- It's not clear what the conformance tests are for Experiment, TileSetData, TileSet, and Tile
  implementations that need to pass for a new backend to be valid.
- Related, it would be good to specify what API a TileSet and Tile need to expose for Starfish to
  function
- The SpaceTx-Format is probably *over-specified* as it stands; there are many implementations that
  *could* represent the format, but spec'd out as JSON it's limited to exactly our implementation.
- I found the notion of a slicedimage.Collection confusing; it took me a while to realize that
  it matches the FOV_manifest, an *optional* part of our spec.


Notes on slicedimage
--------------------
- I found the "Reader" system unclear. It was challenging to reverse engineer because at each
  stage I needed to switch between starfish and slicedimage to understand the API specification.
  I took the path of eliminating the reader and adding a bunch of from_zarr() methods that take as
  arguments the zarr group that represents the object that matches the part of the spec they
  represent. The pairs are: (experiment, zarr_root), (fov, zarr_group), (tileset, zarr_array),
  (tile, (zarr_array, chunk indices)). Because chunks aren't first-class objects,
  my quick implementation makes some gross nested dicts to build the necessary attrs for them.
- Another thing I would change about the way the slicedimage classes function is that it's very easy
  at present to use the constructor of the TileSet and Tile to make a non-functional object. For
  example, filling the array future is done in Reader, but that really feels like something that
  should be done in a classmethod, and the future passed to the constructor. Objects created by the
  constructor should always be functional!
- I haven't looked at the writer system yet but I have a feeling I'd struggle there, too.
- It's not clear that tile_shape refers only to the x-y coordinates. We might contemplate changing
  it to include the whole shape (or at least z) for future compatibility with n-d chunking.
