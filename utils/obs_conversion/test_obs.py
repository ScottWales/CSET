# type: ignore

from .obs import obs_dataframe_to_point_cube
from pandas import DataFrame
from iris.cube import Cube


def test_obs_dataframe_to_point_cube(sample_obs_dataframe: tuple[DataFrame, DataFrame]):
    obs, stations = sample_obs_dataframe

    cubes = obs_dataframe_to_point_cube(obs, stations)
    assert len(cubes) == 2

    tmp: Cube = cubes.extract_cube("TMP")  # type: ignore
    assert tmp.shape == (2, 2)
    assert tmp.coord("time").cell(0).point.strftime("%Y-%m-%dT%H:%M") == "2023-01-01T00:00"
    assert tmp.coord("time").cell(1).point.strftime("%Y-%m-%dT%H:%M") == "2023-01-01T02:00"
    assert tmp.coord("station").cell(0).point == "S1"
    assert tmp.coord("prepbufr_type").cell(0).point == "A"
    