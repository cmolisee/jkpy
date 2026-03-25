from unittest.mock import MagicMock

import pytest

from jkpy.callbacks import exit_application


class TestExitApplication:
    def test_exit_applications(self) -> None:
        mock_menu_model = MagicMock()
        mock_stop = MagicMock()
        mock_menu_model.stop = mock_stop

        exit_application(model=mock_menu_model)

        mock_stop.assert_called_once()

    def test_edit_configurations_exception(self) -> None:
        with pytest.raises(SystemExit) as execinfo:
            exit_application()

        assert execinfo.value.code == 1
