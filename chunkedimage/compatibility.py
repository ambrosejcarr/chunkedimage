from typing import Optional
from itertools import product
from collections import defaultdict

from starfish import Experiment
import zarr


def from_spacetx_format(store: str, overwrite: Optional[bool] = True) -> zarr.hierarchy.Group:
    """Create a Zarr version of SpaceTx-Format from BaristaSeq data to test this library

    Parameters
    ==========
    store : str
        folder to back the created zarr archive
    overwrite: Optional[Bool]
        if True, overwrite any zarr array previously stored in the `store` directory. (Default True)

    Returns
    =======
    zarr.hierarchy.Group :
        the root of the zarr archive created from the passed experiment
    """

    exp = Experiment.from_json(
        "https://d2nhj9g34unfro.cloudfront.net/browse/formatted/20181028/"
        "BaristaSeq/cropped_formatted/experiment.json"
    )

    def add_coordinates(array: zarr.hierarchy.Group, start: int=0):
        """Add coordinates to an FOV"""
        coordinates = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
        ordered_numeric_tile_indices = product(
            range(array.shape[0]), range(array.shape[1]), range(array.shape[2])
        )
        for r, c, z in ordered_numeric_tile_indices:
            coordinates[r][c][z] = {
                'zc': (0.0 + start, 0.01 + start),
                'yc': (0.0 + start, 10.0 + start),
                'xc': (0.0 + start, 10.0 + start)
            }
        array.attrs['tile_coordinates'] = coordinates
        return array

    def create_fov(root: zarr.hierarchy.Group, fov_name: str, overwrite: bool, start: int) -> None:
        fov = root.create_group(name=fov_name, overwrite=overwrite)
        for stack_type in si_fov.image_types:
            data = si_fov[stack_type]
            arr = fov.array(
                name=stack_type,
                data=data.xarray.values,
                chunks=(1, 1, 1, *data.raw_shape[-2:]),
                overwrite=overwrite)
            add_coordinates(arr, start=start)

    # get the first FOV from the SpaceTx BaristaSeq dataset
    for fov_name, si_fov in exp.items():
        break

    # create the root of the zarr archive
    root: zarr.hierarchy.Group = zarr.group(store=store, overwrite=overwrite)

    # make two FOVs from the test datasets. They will have the same data
    create_fov("fov_000", root, overwrite=True, start=0)
    create_fov("fov_001", root, overwrite=True, start=10)

    return root

