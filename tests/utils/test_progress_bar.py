import asyncio
import re
from typing import Any

from jkpy.utils import ProgressBar


async def test_coroutine() -> int:
    await asyncio.sleep(1)
    return 1


class TestProgressBar:
    def test_init(self) -> None:
        pb = ProgressBar(1, 2)
        assert pb.width == 1
        assert pb.cursor == 2
        assert pb._progress == 0.0
        assert pb._start is None

    # @pytest.mark.asyncio
    async def test_run_and_animate(self, capsys: Any) -> None:
        result = await ProgressBar(20, 0).run_with(test_coroutine())
        captured = capsys.readouterr()

        assert result == 1
        assert re.search(r"\[####################\] 100.0%", captured.out)
