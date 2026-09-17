from typing import Any

import pandas as pd
import pytest


@pytest.fixture
def sample_obs_dataframe() -> tuple[pd.DataFrame, pd.DataFrame]:
    # Sample observation data
    obs_data: dict[str, Any] = {
        "station_id": ["S1", "S2", "S1"],
        "valid": pd.to_datetime(
            ["2023-01-01T00:00", "2023-01-01T01:00", "2023-01-01T02:00"]
        ),
        "prepbufr_type": ["A", "B", "A"],
        "var_name": ["TMP", "DPT", "TMP"],
        "units": ["K", "K", "K"],
        "height": [10, 20, 10],
        "level": [1000, 900, 500],
        "value": [273.15, 275.15, 224.15],
        "QC": ["good", "bad", "good"],
    }
    obs_df = pd.DataFrame(obs_data)

    # Sample station metadata
    stations_data: dict[str, Any] = {
        "station_id": ["S1", "S2"],
        "latitude": [40.0, 41.0],
        "longitude": [-75.0, -76.0],
        "elevation_asl": [100, 200],
    }
    stations_df = pd.DataFrame(stations_data)

    return obs_df, stations_df
