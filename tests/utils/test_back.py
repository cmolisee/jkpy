from unittest.mock import MagicMock

import pytest

from jkpy.callbacks import back


class TestBack:
    def test_back(
        self,
    ) -> None:
        mock_menu_model = MagicMock()
        mock_menu_model.is_running = True

        back(model=mock_menu_model)

        assert not mock_menu_model.is_running

    def test_back_exception(self) -> None:
        with pytest.raises(SystemExit) as excinfo:
            back()

        assert excinfo.value.code == 1
