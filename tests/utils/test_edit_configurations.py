import pytest
from pytest_mock import MockerFixture

from jkpy.callbacks import edit_configurations


class TestEditConfigurations:
    def test_edit_configurations(
        self, mocker: MockerFixture, capsys: pytest.CaptureFixture[str]
    ) -> None:
        mock_menu_model_run = mocker.patch("jkpy.mvc.menu.MenuController.run")
        mock_menu_model_run.return_value = print("test")

        edit_configurations()

        captured = capsys.readouterr()
        assert captured.out == "test\n"
        assert captured.err == ""

    def test_edit_configurations_keyboardinterrupt(self, mocker: MockerFixture) -> None:
        mocker.patch("jkpy.mvc.menu.MenuController.run", side_effect=KeyboardInterrupt)

        with pytest.raises(SystemExit) as execinfo:
            edit_configurations()

        assert execinfo.value.code == 0

    def test_edit_configurations_exception(self) -> None:
        # Raises an exception because termios module is not mocked
        with pytest.raises(SystemExit) as execinfo:
            edit_configurations()

        assert execinfo.value.code == 1
