from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from jkpy.callbacks import setter_prompt


class TestSetterPrompt:
    MOCK_CONFIG = {
        "email": "test@gmail.com",
        "token": "abc123",
        "path": "/path",
        "members": ["member1", "member2"],
        "teams": ["team1", "team2"],
        "statuses": ["status1", "status2"],
        "labels": ["label1", "label2"],
        "ignore_labels": ["ignore1"],
        "host": "https://host.com/",
    }

    def test_setter_prompt_host_path_token(
        self,
        mocker: MockerFixture,
    ) -> None:
        mock_menu_model = MagicMock()
        mock_set_configs = MagicMock()
        mock_menu_model.get_configs = lambda: self.MOCK_CONFIG
        mock_menu_model.set_configs = mock_set_configs

        for key in ["host", "path", "token"]:
            mock_input_confirm = mocker.patch("jkpy.mvc.input.Input.text")
            mock_input_confirm.return_value = f"{key}-test"
            setter_prompt(model=mock_menu_model, key=key)

            mock_set_configs.assert_called_with({key: f"{key}-test"})
            mock_set_configs.reset_mock()

    def test_setter_prompt_members_labels_statuses_teams_ignorelabels(
        self,
        mocker: MockerFixture,
    ) -> None:
        mock_menu_model = MagicMock()
        mock_set_configs = MagicMock()
        mock_menu_model.get_configs = lambda: self.MOCK_CONFIG
        mock_menu_model.set_configs = mock_set_configs

        for key in ["members", "labels", "statuses", "teams", "ignore_labels"]:
            mock_input_confirm = mocker.patch("jkpy.mvc.input.Input.text")
            mock_input_confirm.return_value = f"{key}-a,{key}-b"
            setter_prompt(model=mock_menu_model, key=key)

            mock_set_configs.assert_called_with({key: [f"{key}-a", f"{key}-b"]})
            mock_set_configs.reset_mock()

    def test_setter_prompt_remove(
        self,
        mocker: MockerFixture,
    ) -> None:
        mock_menu_model = MagicMock()
        mock_set_configs = MagicMock()
        mock_menu_model.get_configs = lambda: self.MOCK_CONFIG
        mock_menu_model.set_configs = mock_set_configs

        for key in [
            "remove_labels",
            "remove_members",
            "remove_statuses",
            "remove_teams",
            "remove_ignore_labels",
        ]:
            mock_input_confirm = mocker.patch("jkpy.mvc.options.Options.multiselect")
            mock_input_confirm.return_value = [key]
            setter_prompt(model=mock_menu_model, key=key)

            mock_set_configs.assert_called_with({key.replace("remove_", ""): [key]})
            mock_set_configs.reset_mock()

    def test_setter_prompt_invalid_key(
        self,
    ) -> None:
        mock_menu_model = MagicMock()
        mock_set_configs = MagicMock()
        mock_menu_model.get_configs = lambda: self.MOCK_CONFIG
        mock_menu_model.set_configs = mock_set_configs

        setter_prompt(model=mock_menu_model, key="this_key_does_not_exist")
        mock_set_configs.assert_not_called()

    def test_setter_prompt_exception(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            setter_prompt()

        assert excinfo.value.code == 1
