#!/usr/bin/env python

"""Convert BOM rain data from JIVE to MET point observation format."""

import argparse
import re
from pathlib import Path

import pandas
import xarray
from pandas import DataFrame

from .met import save_obs_dataframe_as_met


def bom_jive_to_obs_dataframe(jive_file: Path) -> DataFrame:
    """Convert BOM JIVE NetCDF file to observation dataframe."""
    ds = xarray.open_dataset(jive_file)  # type: ignore
    precip_accum = ds["lwe_thickness_of_precipitation_amount"]
    units = precip_accum.attrs["units"]
    df = precip_accum.to_dataframe().reset_index()
    df = df.rename(
        columns={
            "station_number": "station_id",
            "time": "valid",
            "lwe_thickness_of_precipitation_amount": "value",
        }
    )
    df["prepbufr_type"] = "ADPSFC"
    df["var_name"] = "APCP"
    df["units"] = units
    df["height"] = 0
    method = precip_accum.attrs["cell_methods"]
    match = re.match(r"time: sum \(interval: (\d+)h\)", method)
    if match is None:
        raise AttributeError("Unable to determine precipitation accumulation interval")
    df["level"] = match.group(1)
    df["QC"] = "0"

    print(df.head())

    return df


def bom_jive_stations(stations_file: Path) -> DataFrame:
    """Convert station list to obs dataframe."""
    df = pandas.read_csv(stations_file)

    mapping = {
        "station_number": "station_id",
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude",
        "STN_HT": "elevation_asl",
    }

    return df.rename(columns=mapping)


def main():
    """CLI for converting BOM rain data from JIVE to MET format."""
    parser = argparse.ArgumentParser(
        description="Convert BOM rain data from JIVE to MET point observation format."
    )
    parser.add_argument(
        "input_files", nargs="+", type=Path, help="Path to the JIVE NetCDF file"
    )
    parser.add_argument(
        "--stations",
        "-s",
        type=Path,
        required=True,
        help="Path to the stations CSV file",
    )
    parser.add_argument(
        "--output", "-o", type=Path, required=True, help="Path to the output CSV file"
    )
    parser.add_argument(
        "--format",
        choices=["netcdf", "ascii"],
        default="netcdf",
        help="Output format for the converted data",
    )
    args = parser.parse_args()

    df = pandas.concat(
        [bom_jive_to_obs_dataframe(jive_file) for jive_file in args.input_files]
    )
    stations = bom_jive_stations(args.stations)

    save_obs_dataframe_as_met(df, stations, output=args.output, format=args.format)


if __name__ == "__main__":
    main()
