from jkpy.utils import Ansi


class TestAnsi:
    def test_from_code(self) -> None:
        assert Ansi.from_code("\x1b[1;2A") == "SHIFT+UP"
        assert Ansi.from_code("a") == "a"

    def test_up(self) -> None:
        assert Ansi.up(5) == "\x1b[5F"

    def test_right(self) -> None:
        assert Ansi.right(3) == "\x1b[3C"

    def test_overwrite(self) -> None:
        assert Ansi.overwrite() == "\x1b[K"

    def test_erase_line(self) -> None:
        assert Ansi.erase_line() == "\x1b[2K"

    def test_to_col(self) -> None:
        assert Ansi.to_col(6) == "\x1b[6G"
