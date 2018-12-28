from collections import OrderedDict
from itertools import product
from typing import FrozenSet, List, MutableMapping, Optional, Tuple

import zarr

from .constants import Coordinates, Extras, Indices
from .tile import Tile


# TODO this API is tied closely enough to starfish that it should live in starfish
# Maybe that's the TileSetData API...
class TileSet(object):

    def __init__(
            self,
            dimensions: FrozenSet[str],
            shape: MutableMapping[str, int],
            extras: Optional[MutableMapping] = None,
            default_tile_shape: Tuple[int]=None,  # Used by the writer, not used by this class
            # default_tile_format=None,  # TODO probably never used for zarr
    ) -> None:
        """TileSet contains all references to the Tiles of a field of view, and is sufficient to
        construct an ImageStack in-memory.

        Parameters
        ==========
        dimensions : FrozenSet[str]
        """

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

        # we know the order of the axis that are in the archive, and we stored that in an
        # ordered dict above, so can use this information to build all the tile indices for
        # each FoV
        ordered_numeric_tile_indices = product(
            range(shape[Indices.ROUND]), range(shape[Indices.CH]), range(shape[Indices.Z])
        )
        for r, c, z in ordered_numeric_tile_indices:
            tileset.add_tile(Tile.from_zarr(zarr_array, r, c, z))

        return tileset

    # TODO this method isn't needed -- it can live in ImageStack
    @classmethod
    def from_imagestack(cls, imagestack):
        """This function is used to serialize imagestack using a user-selected back-end"""

        tileset = cls(
            dimensions=frozenset((
                Indices.ROUND,
                Indices.CH,
                Indices.Z,
                Indices.Y,
                Indices.X,
            )),
            shape={
                Indices.ROUND: imagestack.num_rounds,
                Indices.CH: imagestack.num_chs,
                Indices.Z: imagestack.num_zlayers,
                Indices.Y: imagestack.shape[Indices.Y],
                Indices.X: imagestack.shape[Indices.X],
            },
            extras=imagestack._tile_data.extras,
        )
        for round_ in range(imagestack.num_rounds):
            for ch in range(imagestack.num_chs):
                for zlayer in range(imagestack.num_zlayers):
                    # TODO why is this necessary?
                    tilekey = TileKey(round=round_, ch=ch, z=zlayer)
                    extras: dict = imagestack._tile_data[tilekey]

                    tile_indices = {
                        Indices.ROUND: round_,
                        Indices.CH: ch,
                        Indices.Z: zlayer,
                    }

                    coordinates: MutableMapping[Coordinates, Tuple[Number, Number]] = dict()
                    x_coordinates = imagestack.tile_coordinates(tile_indices, Coordinates.X)
                    y_coordinates = imagestack.tile_coordinates(tile_indices, Coordinates.Y)
                    z_coordinates = imagestack.tile_coordinates(tile_indices, Coordinates.Z)

                    coordinates[Coordinates.X] = x_coordinates
                    coordinates[Coordinates.Y] = y_coordinates
                    if z_coordinates[0] != np.nan and z_coordinates[1] != np.nan:
                        coordinates[Coordinates.Z] = z_coordinates

                    tile = Tile(
                        coordinates=coordinates,
                        indices=tile_indices,
                        extras=extras,
                    )
                    tile.numpy_array, _ = imagestack.get_slice(
                        indices={Indices.ROUND: round_, Indices.CH: ch, Indices.Z: zlayer}
                    )
                    tileset.add_tile(tile)

    # TODO this class _is_ needed and should be factored out of the class in starfish
    def write_zarr(self):

        if tile_opener is None:
            def tile_opener(tileset_path, tile, ext):
                tile_basename = os.path.splitext(tileset_path)[0]
                if Indices.Z in tile.indices:
                    zval = tile.indices[Indices.Z]
                    zstr = "-Z{}".format(zval)
                else:
                    zstr = ""
                return open(
                    "{}-H{}-C{}{}.{}".format(
                        tile_basename,
                        tile.indices[Indices.ROUND],
                        tile.indices[Indices.CH],
                        zstr,
                        ext,
                    ),
                    "wb")

        if not filepath.endswith('.json'):
            filepath += '.json'
        Writer.write_to_path(
            tileset,
            filepath,
            pretty=True,
            tile_opener=tile_opener,
            tile_format=tile_format)