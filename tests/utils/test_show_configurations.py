from datetime import datetime
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from jkpy.callbacks import show_configurations


class TestShowConfiguration:
    mock_config = {
        "email": "test@gmail.com",
        "token": "abc123",
        "path": "/path",
        "members": ["member1", "member2"],
        "teams": ["team1", "team2"],
        "statuses": ["status1", "status2"],
        "labels": ["label1", "label2"],
        "ignore_labels": ["ignore1"],
        "host": "https://host.com/",
        "start": datetime.today(),
        "end": None,
    }

    def test_show_configuration(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        expected_output = "\nshape: (11, 2)\n┌────────────────────────┬────────────────────────────┐\n│ key                    ┆ value                      │\n│ ---                    ┆ ---                        │\n│ str                    ┆ str                        │\n╞════════════════════════╪════════════════════════════╡\n│ \x1b[32memail\x1b[0m         ┆ \x1b[32mtest@gmail.com\x1b[0m    │\n│ \x1b[32mtoken\x1b[0m         ┆ \x1b[32mabc123\x1b[0m            │\n│ \x1b[32mpath\x1b[0m          ┆ \x1b[32m/path\x1b[0m             │\n│ \x1b[32mmembers\x1b[0m       ┆ \x1b[32mmember1,member2\x1b[0m   │\n│ \x1b[32mteams\x1b[0m         ┆ \x1b[32mteam1,team2\x1b[0m       │\n│ …                      ┆ …                          │\n│ \x1b[32mlabels\x1b[0m        ┆ \x1b[32mlabel1,label2\x1b[0m     │\n│ \x1b[32mignore_labels\x1b[0m ┆ \x1b[32mignore1\x1b[0m           │\n│ \x1b[32mhost\x1b[0m          ┆ \x1b[32mhttps://host.com/\x1b[0m │\n│ \x1b[32mstart\x1b[0m         ┆ \x1b[32m2026-03-25\x1b[0m        │\n│ \x1b[32mend\x1b[0m           ┆ \x1b[32m\x1b[0m                  │\n└────────────────────────┴────────────────────────────┘\n"
        mock_menu_model = MagicMock()
        mock_menu_model.get_configs = lambda: self.mock_config

        mock_input_confirm = mocker.patch("jkpy.mvc.input.Input.confirm")
        mock_input_confirm.return_value = True

        show_configurations(model=mock_menu_model)

        # assert all output is captured
        captured = capsys.readouterr()
        assert captured.out == expected_output
        assert captured.err == ""

    def test_show_configuration_with_stop(
        self,
        mocker: MockerFixture,
    ) -> None:
        mock_menu_model = MagicMock()
        mock_stop_call = MagicMock()

        mock_menu_model.get_configs = lambda: self.mock_config
        mock_menu_model.stop = mock_stop_call

        mock_input_confirm = mocker.patch("jkpy.mvc.input.Input.confirm")
        mock_input_confirm.return_value = False

        show_configurations(model=mock_menu_model)

        mock_stop_call.assert_called()

    def test_show_configuration_exception(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            show_configurations()

        assert excinfo.value.code == 1
