from collections import OrderedDict
from itertools import product
from typing import FrozenSet, List, Mapping, Optional

import zarr

from .constants import Extras, Indices
from .tile import Tile


# this thing should contain the data for an FoV, and needs to operate with TileSetData from
# starfish

# TODO this API is tied closely enough to starfish that it should live in starfish
# Maybe that's the TileSetData API...
class TileSet(object):

    def __init__(
            self,
            dimensions: FrozenSet[str],
            shape: Mapping[str, int],
            extras: Optional[Mapping] = None
            # default_tile_shape: Tuple[int]=None,
            # default_tile_format=None,  # TODO probably never used for zarr
    ) -> None:
        """TileSet Constructor"""

        self.dimensions = dimensions
        self.shape = shape
        self.extras = extras
        self._tiles: List[Tile] = []

        # Mandatory API, not used by the zarr image format
        self.default_tile_shape = None

        # # Leaving these here for now. Not needed for reading, might be needed for writing.
        # self.default_tile_format = None
        # self._discrete_dimensions = set()

    def validate(self):
        raise NotImplementedError()

    def add_tile(self, tile):
        self._tiles.append(tile)

    def tiles(self, filter_fn=lambda _: True):
        """
        Return the tiles in this tileset.  If a filter_fn is provided, only the tiles for which
        filter_fn returns True are returned.
        """
        return list(filter(filter_fn, self._tiles))

    def get_dimension_shape(self, dimension_name):
        return self.shape[dimension_name]

    @classmethod
    def from_zarr(cls, zarr_array: zarr.core.Array) -> "TileSet":
        """A tileset is stored as a zarr array, broken up into chunks."""
        # TODO get rid of this hardcoding
        shape = OrderedDict((
            (Indices.ROUND, zarr_array.shape[0]),
            (Indices.CH, zarr_array.shape[1]),
            (Indices.Z, zarr_array.shape[2]),
            (Indices.Y, zarr_array.shape[3]),
            (Indices.X, zarr_array.shape[4]),
        ))

        tileset = cls(
            dimensions=frozenset((Indices.ROUND, Indices.CH, Indices.Z, Indices.Y, Indices.X)),
            shape=shape,
            extras=zarr_array.attrs.get(Extras.FOVS, None)
        )

        # add the tiles to the TileSet

        # we know the order of the axis that are in the archive, and we stored that in an
        # ordered dict above, so can use this information to build all the tile indices for
        # each FoV
        ordered_numeric_tile_indices = product(
            range(shape[Indices.ROUND]), range(shape[Indices.CH]), range(shape[Indices.Z])
        )
        for r, c, z in ordered_numeric_tile_indices:
            tileset.add_tile(Tile.from_zarr(zarr_array, r, c, z))

        return tileset
