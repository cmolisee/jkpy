from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from jkpy.callbacks import run_application


class TestRunApplication:
    def test_run_application(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        mock_menu_model = MagicMock()
        mock_menu_view = MagicMock()

        mock_handler_chain = MagicMock()
        mock_handler_chain.return_value = True

        mock_create_chain: MagicMock = mocker.patch("jkpy.handlers.Handlers.create_chain")
        mock_create_chain.return_value = mock_handler_chain

        with pytest.raises(SystemExit) as excinfo:
            run_application(model=mock_menu_model, view=mock_menu_view)

        # assert a newline is printed to console
        captured = capsys.readouterr()
        assert captured.out == "\n"
        assert captured.err == ""

        # ensure exit with success
        assert excinfo.value.code == 0

    def test_run_application_exception(
        self,
        mocker: MockerFixture,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        mock_create_chain = mocker.patch("jkpy.handlers.Handlers.create_chain")
        mock_create_chain.side_effect = Exception("test")

        with pytest.raises(SystemExit) as excinfo:
            run_application(model={}, view={})

        # assert a newline is printed to console
        captured = capsys.readouterr()
        assert "Exception: test" in captured.out
        assert captured.err == ""

        # ensure exit with error
        assert excinfo.value.code == 1
