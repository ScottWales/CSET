"""
Common column definitions for observation dataframes and station metadata.

Observations should provide at least these columns so they can be converted to MET format

Observations can include the station information directly in the observation dataframe or reference it through a separate station metadata dataframe.
"""

from cf_units import Unit  # type: ignore
from iris.coords import AuxCoord, DimCoord  # type: ignore
from iris.cube import Cube, CubeList  # type: ignore
from pandas import DataFrame
from typing import cast
import numpy as np

obs_dataframe_columns = [
    "prepbufr_type",
    "station_id",
    "valid",
    "var_name",
    "units",
    "level",
    "height",
    "QC",
    "value",
]

obs_station_columns = [
    "station_id",
    "latitude",
    "longitude",
    "elevation_asl",
]


def normalise_obs_dataframe(
    obs: DataFrame, stations: DataFrame | None
) -> tuple[DataFrame, DataFrame]:
    """
    Check the columns of the obs dataframe and split out stations if needed.

    Args:
        obs (DataFrame): Observation dataframe containing at least the columns defined in `obs_dataframe_columns`.
        stations (DataFrame | None): Station metadata dataframe containing at least the columns defined in `obs_station_columns`. If None, station information will be extracted from the observation dataframe.

    Returns
    -------
        tuple[DataFrame, DataFrame]: Normalised observation and station dataframes.
    """
    
    if stations is None:
        stations = obs[obs_station_columns].drop_duplicates().reset_index(drop=True)

    if set(obs_dataframe_columns) - set(obs.columns):
        raise ValueError(
            "Observation DataFrame is missing required columns: "
            f"{set(obs_dataframe_columns) - set(obs.columns)}"
        )
    if set(obs_station_columns) - set(stations.columns):
        raise ValueError(
            "Station DataFrame is missing required columns: "
            f"{set(obs_station_columns) - set(stations.columns)}"
        )

    return obs, stations


def obs_dataframe_to_point_cube(obs: DataFrame, stations: DataFrame) -> CubeList:
    """Convert an observation dataframe to point cubes.

    Args:
        obs (DataFrame): Observation dataframe containing at least the columns defined in `obs_dataframe_columns`.
        stations (DataFrame): Station metadata dataframe containing at least the columns defined in `obs_station_columns`.

    Returns
    -------
        CubeList: A list of point cube representations of the observations.
    """
    obs, stations = normalise_obs_dataframe(obs, stations)
    stations = stations.set_index("station_id")

    cubes = CubeList()
    for var_name, df in obs.groupby("var_name"):
        assert isinstance(var_name, str)

        # Uniqueness checks
        if len(df["prepbufr_type"].unique()) > 1:
            raise AttributeError(
                "Multiple prepbufr_type values found for the same variable."
            )
        if len(df["units"].unique()) > 1:
            raise AttributeError("Multiple units values found for the same variable.")

        data = df.pivot(
            columns=["station_id", "height", "level"], index="valid", values="value"
        )
        time_unit = Unit("hours since 1970-01-01 00:00:00")
        times = time_unit.date2num(data.index.to_pydatetime())  # type: ignore

        station_ids = data.columns.get_level_values("station_id")
        heights = data.columns.get_level_values("height")
        levels = data.columns.get_level_values("level")

        lats = stations.loc[station_ids, "latitude"]
        lons = stations.loc[station_ids, "longitude"]
        elevs = stations.loc[station_ids, "elevation_asl"]

        dims: list[tuple[DimCoord, int]] = [
            (DimCoord(cast(np.ndarray[tuple[int]], times), var_name="time", units=time_unit), 0),
        ]
        aux: list[tuple[AuxCoord, int|None]] = [
            (AuxCoord(station_ids, var_name="station"), 1),
            (AuxCoord(heights, var_name="height", units="m"), 1),
            (AuxCoord(levels, var_name="level", units="hPa"), 1),
            (AuxCoord(lats, var_name="latitude", units="degrees"), 1),
            (AuxCoord(lons, var_name="longitude", units="degrees"), 1),
            (AuxCoord(elevs, var_name="station_elevation_asl", units="m"), 1),
            (AuxCoord(df["prepbufr_type"].iloc[0], var_name="prepbufr_type"), None),
        ]

        cube = Cube(
            data=data.values,
            var_name=var_name,
            units=df["units"].iloc[0],
            dim_coords_and_dims=dims,
            aux_coords_and_dims=aux,
        )
        cubes.append(cube)  # type: ignore
    return cubes
