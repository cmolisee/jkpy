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
        mock_menu_model = MagicMock()
        mock_menu_model.get_configs = lambda: self.mock_config

        mock_input_confirm = mocker.patch("jkpy.mvc.input.Input.confirm")
        mock_input_confirm.return_value = True

        show_configurations(model=mock_menu_model)

        captured = capsys.readouterr()
        # assert values excluding statuses to avoid issues with truncated captured output
        for sub in [
            "test@gmail.com",
            "abc123",
            "/path",
            "member1",
            "member2",
            "team1",
            "team2",
            "label1",
            "label2",
            "ignore1",
            "https://host.com/",
        ]:
            assert sub in captured.out
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
