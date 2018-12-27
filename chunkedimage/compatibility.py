from typing import Optional

from starfish import Experiment
import zarr


def from_slicedimage(
    slicedimage_experiment: str, store: str, overwrite: Optional[bool] = True
) -> zarr.hierarchy.Group:
    """
    Parameters
    ==========
    slicedimage_experiment : str
        name of a SpaceTx-Format experiment that adheres to SpaceTx-Format and is loadedable by
        starfish
    store : str
        folder to back the created zarr archive
    overwrite: Optional[Bool]
        if True, overwrite any zarr array previously stored in the `store` directory

    Returns
    =======
    zarr.hierarchy.Group :
        the root of the zarr archive created from the passed experiment
    """
    exp = Experiment.from_json(slicedimage_experiment)

    root: zarr.hierarchy.Group = zarr.create_group(store=store, overwrite=overwrite)

    for fov_name, si_fov in exp.items():
        fov = root.create_group(name=fov_name, overwrite=overwrite)
        for stack_type in si_fov.image_types:
            data = si_fov[stack_type]
            fov.array(
                name=stack_type,
                data=data.xarray.values,
                chunks=(1, 1, 1, *data.raw_shape[-2:])  # unpack y, x shapes
            )

    return root
