from .metplus import MetplusOutput, MetplusRunner, PointStatRunner
from pathlib import Path
import iris
from iris.cube import Cube, CubeList

def run_metplus(
    cube: Cube,
    *,
    config_file: str | Path | None = None,
    config: dict[str, str] | None = None,
) -> MetplusOutput:
    """
    Run METplus on a cube and return the results as a named tuple of pandas DataFrames.

    No default config is provided.

    Arguments:
    ----------
    cube : Cube
        The input cube to be processed by METplus.
    config_file : str|Path|None
        The path to the METplus configuration file.
    config : dict[str, str] | None
        The METplus configuration as a dictionary.

    Returns
    -------
    MetplusOutput
        The output of the METplus processing.
    """
    runner = MetplusRunner(config_file, config)
    return runner.run(cube)


def point_stat(
    cube: Cube,
    *,
    config_file: str | Path | None = None,
    config: dict[str, str] | None = None,
) -> MetplusOutput:
    """
    Run point_stat on a cube and return the results as a named tuple of pandas DataFrames.

    Recommended minimum config settings:
    * ``POINT_STAT_OBS_INPUT_DIR``
    * ``POINT_STAT_OBS_INPUT_TEMPLATE``
    * ``OBS_VAR1_NAME``
    * ``FCST/OBS/BOTH_LEVELS``
    
    Arguments:
    ----------
    cube : Cube
        The input cube to be processed by METplus point_stat.
    config_file : str|Path|None
        The path to the METplus configuration file.
    config : dict[str, str] | None
        The METplus configuration as a dictionary.

    Returns
    -------
    MetplusOutput
        The output of the METplus point_stat processing.

    See also
    --------
    https://metplus.readthedocs.io/en/latest/Users_Guide/wrappers.html#pointstat
    https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/point-stat.html
    """
    runner = PointStatRunner(config_file, config)
    return runner.run(cube)


def filter_stat(
    metplus_output: MetplusOutput,
    line_type: str,
    metric: str,
    reduce_coordinates: str|None = None,
) -> CubeList:
    """
    Filter the METplus output based on the line type and metric.

    Arguments:
    ----------
    metplus_output : MetplusOutput
        The output of the METplus processing.
    line_type : str
        The line type to filter by.
    metric : str
        The metric to filter by.
    reduce_coordinates : str|None
        The coordinates to reduce during filtering.

    Returns
    -------
    CubeList
        The filtered METplus output.
    """
    # Placeholder for filtering the METplus output
    data = metplus_output[line_type][metric]
    cube = iris.pandas.as_cube(data)
    return CubeList([cube])