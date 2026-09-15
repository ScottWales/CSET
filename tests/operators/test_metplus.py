from unittest.mock import MagicMock, patch
import pytest
import subprocess
from textwrap import dedent
from iris.cube import Cube
from CSET.operators.metplus.metplus import MetplusOutput, MetplusRunner
from CSET.operators.metplus import point_stat, run_metplus
from pathlib import Path
import pandas

@pytest.fixture
def sample_obs(tmp_path: Path) -> Path:
    sample_ascii = tmp_path / "sample_obs.txt"
    # Type Station Valid Lat Lon Elev VarName Level Height QC Value
    sample_ascii.write_text(dedent("""\
    ADPSFC 0000 20220921_0300 3.0 361.9 0.0 TMP Z2 NA NA 273.15
    """))
    sample_nc = tmp_path / "sample_obs.nc"

    subprocess.run(["ascii2nc", str(sample_ascii), str(sample_nc)], check=True)
    return sample_nc


def test_run_metplus():
    """
    Test the run_metplus function with a mock cube and configuration.
    """
    mock_cube = MagicMock(spec=Cube)
    mock_config = {
        "config_key": "config_value"
    }

    with patch("CSET.operators.metplus.subprocess.run") as mock_subprocess_run, patch("CSET.operators.metplus.iris.save"):
        output = run_metplus(mock_cube, config=mock_config)
        mock_subprocess_run.assert_called_once()

    assert isinstance(output, MetplusOutput)


def test_metplus_runner_default_config(cube: Cube):
    runner = MetplusRunner(config={"config_key": "config_value"})

    config = runner.generate_default_config(cube)
    assert config["LOOP_BY"] == "INIT"
    assert config["INIT_BEG"] == "20220921T0300Z"
    assert config["INIT_END"] == "20220921T0300Z"
    assert config["VALID_BEG"] == "20220921T0300Z"
    assert config["VALID_END"] == "20220921T0500Z"
    assert config["LEAD_SEQ"] == "0S, 3600S, 7200S"


def test_metplus_runner():
    mock_cube = MagicMock(spec=Cube)
    runner = MetplusRunner(config={"config_key": "config_value"})

    with patch("CSET.operators.metplus.subprocess.run") as mock_subprocess_run, patch("CSET.operators.metplus.iris.save"):
        output = runner.run(mock_cube)
        mock_subprocess_run.assert_called_once()
        cmd = mock_subprocess_run.call_args[0][0]
        assert cmd[0] == "run_metplus"
        assert cmd[1].endswith("default.conf")
        assert cmd[2].endswith("config.conf")
        assert cmd[3].endswith("override.conf")

    assert isinstance(output, MetplusOutput)


def test_point_stat(cube: Cube, sample_obs: Path):
    config = {
        "POINT_STAT_OBS_INPUT_TEMPLATE": str(sample_obs),
        "OBS_VAR1_NAME": "TMP",
        "OBS_VAR1_LEVELS": "Z2",
    }
    output = point_stat(cube, config=config)
    assert isinstance(output, MetplusOutput)


def test_metplus_output_integration(cube: Cube, sample_obs: Path):
    config = {
        "POINT_STAT_OBS_INPUT_TEMPLATE": str(sample_obs),
        "OBS_VAR1_NAME": "TMP",
        "OBS_VAR1_LEVELS": "Z2",
    }
    output = point_stat(cube, config=config)
    assert "CNT" in output.data
    assert isinstance(output["CNT"], pandas.DataFrame)


def test_metplus_output_load(tmp_path: Path):
    sample = tmp_path / "sample_cnt.txt"
    headers = "VERSION MODEL DESC FCST_LEAD FCST_VALID_BEG FCST_VALID_END OBS_LEAD OBS_VALID_BEG OBS_VALID_END FCST_VAR FCST_UNITS FCST_LEV OBS_VAR OBS_UNITS OBS_LEV OBTYPE VX_MASK INTERP_MTHD INTERP_PNTS FCST_THRESH OBS_THRESH COV_THRESH ALPHA LINE_TYPE TOTAL FBAR FBAR_NCL FBAR_NCU FBAR_BCL FBAR_BCU FSTDEV FSTDEV_NCL FSTDEV_NCU FSTDEV_BCL FSTDEV_BCU OBAR OBAR_NCL OBAR_NCU OBAR_BCL OBAR_BCU OSTDEV OSTDEV_NCL OSTDEV_NCU OSTDEV_BCL OSTDEV_BCU PR_CORR PR_CORR_NCL PR_CORR_NCU PR_CORR_BCL PR_CORR_BCU SP_CORR KT_CORR RANKS FRANK_TIES ORANK_TIES ME ME_NCL ME_NCU ME_BCL ME_BCU ESTDEV ESTDEV_NCL ESTDEV_NCU ESTDEV_BCL ESTDEV_BCU MBIAS MBIAS_BCL MBIAS_BCU MAE MAE_BCL MAE_BCU MSE MSE_BCL MSE_BCU BCMSE BCMSE_BCL BCMSE_BCU RMSE RMSE_BCL RMSE_BCU E10 E10_BCL E10_BCU E25 E25_BCL E25_BCU E50 E50_BCL E50_BCU E75 E75_BCL E75_BCU E90 E90_BCL E90_BCU EIQR EIQR_BCL EIQR_BCU MAD MAD_BCL MAD_BCU ANOM_CORR ANOM_CORR_NCL ANOM_CORR_NCU ANOM_CORR_BCL ANOM_CORR_BCU ME2 ME2_BCL ME2_BCU MSESS MSESS_BCL MSESS_BCU RMSFA RMSFA_BCL RMSFA_BCU RMSOA RMSOA_BCL RMSOA_BCU ANOM_CORR_UNCNTR ANOM_CORR_UNCNTR_BCL ANOM_CORR_UNCNTR_BCU SI SI_BCL SI_BCU"
    headers = headers.split()
    record = ['x','x','x','0','20210101_0000','20210101_0000','0','20210101_0000','20210101_0000','TMP','C','Z2','TMP','Z2','C','ADPSFC','FULL','NEAREST','1','NA','NA','NA','NA','CNT']
    record.extend(['NA'] * (len(headers) - len(record)))  # Extend the record to match the number of columns in the header
    sample.write_text(" ".join(headers) + "\n" + " ".join(record))
    output = MetplusOutput(tmp_path)

    assert "CNT" in output.data
    assert isinstance(output["CNT"], pandas.DataFrame)
    assert len(output["CNT"]) == 1

    assert output["CNT"].iloc[0]["FBAR"] == "CNT"