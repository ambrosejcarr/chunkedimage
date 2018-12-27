from typing import Any, Mapping, Tuple

import numpy as np
import zarr

from .constants import Coordinates, Extras, Indices
from .types import Number


# TODO a lot of this API is _required_ by starfish and should live there.
# In a zarr world, I think a Tile is eventually generalized as a chunk, however for now these
# are one and the same
class Tile(object):
    def __init__(
        self,
        zarr_array: zarr.core.Array,
        coordinates: Mapping[str, Tuple[Number, Number]],
        indices: Mapping[str, int],
        tile_shape: Tuple[int, int],  # Note: x, y shape ONLY (not documented!)
        extras: Mapping[str, Any],
        # sha256=None,
    ) -> None:

        self.coordinates = coordinates
        self.indices = indices
        self.tile_shape = tile_shape  # is always chunk size in zarr.
        self.extras = extras

        # Tiles set a future for lazy-loading of the numpy array
        self._numpy_array = None
        self._zarr_array = zarr_array

        # sha256 must be type int
        # self.sha256 = sha256

    def _array_future(self) -> np.ndarray:
        return self._zarr_array[
            self.indices[Indices.ROUND],
            self.indices[Indices.CH],
            self.indices[Indices.Z]
        ]

    @property
    def numpy_array(self) -> np.ndarray:
        if self._numpy_array is None:
            self._numpy_array = self._array_future()
        return self._numpy_array

    @numpy_array.setter
    def numpy_array(self, numpy_array):
        self._numpy_array = numpy_array

    # # TODO may need to bring back this complexity once we go delve into ImageStack some more.
    # # this is likely important for cases where data is ejected.
    # def set_source_fh_contextmanager(self, source_fh_contextmanager, tile_format):
    #     """
    #     Provides a tile with a callable, which should yield a context manager that returns a
    #     file-like object.  If the  tile data is requested, the context manager is invoked and the
    #     data is read from the returned file-like object.  It is possible that the context manager
    #     is never invoked.
    #     """
    #     self._source_fh_contextmanager = source_fh_contextmanager
    #     self._numpy_array = None
    #     self.tile_format = tile_format

    def write(self, dst_fh, tile_format):
        """
        Write the contents of this tile out to a given file handle.
        """
        # TODO implement

        # self._load()
        # tile_format.writer_func(dst_fh, self._numpy_array)

        raise NotImplementedError

    @classmethod
    def from_zarr(cls, zarr_array: zarr.core.Array, r: int, c: int, z: int) -> "Tile":

        # TODO make order self-describing in zarr
        coordinates = zarr_array.attrs[Coordinates.TILES][str(r)][str(c)][str(z)]
        indices = {Indices.ROUND: r, Indices.CH: c, Indices.Z: z}
        # TODO consider refactoring ImageStack to allow non-singleton sizes of r, c, and z.
        tile_shape = zarr_array.shape[-2:]  # TODO remove this hardcoding.
        try:
            extras = zarr_array.attrs[Extras.TILES][r][c][z]
        except KeyError:
            extras = None

        return cls(
            zarr_array=zarr_array,
            coordinates=coordinates,
            indices=indices,
            extras=extras,
            tile_shape=tile_shape
        )
