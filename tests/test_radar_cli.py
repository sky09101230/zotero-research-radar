from argparse import Namespace

from omegaconf import OmegaConf

from zotero_arxiv_daily import radar_cli


def test_doctor_reports_missing_environment_variable(tmp_path, monkeypatch):
    config = OmegaConf.create(
        {
            "zotero": {"user_id": "${oc.env:RADAR_TEST_MISSING}", "api_key": "key"},
            "executor": {"source": ["arxiv"]},
        }
    )
    monkeypatch.setattr(radar_cli, "load_config", lambda *args: config)
    args = Namespace(config_dir="config", config_name="default", overrides=[], output=tmp_path / "report.json")

    assert radar_cli.doctor(args) == 1
