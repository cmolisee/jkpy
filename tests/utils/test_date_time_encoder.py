import datetime
import json

from jkpy.utils import DateTimeEncoder

# tuple - input, expect
CASES = [
    ({}, "{}"),
    ({"key": "value"}, '{"key": "value"}'),
    ({"key": ["one", "two"]}, '{"key": ["one", "two"]}'),
    ({"key": datetime.datetime(2026, 3, 11, 0, 0, 0, 0)}, '{"key": "2026-03-11T00:00:00"}'),
    (
        [
            datetime.datetime(2026, 3, 11, 0, 0, 0, 0),
            datetime.datetime(2026, 4, 11, 0, 0, 0, 0),
            datetime.datetime(2026, 5, 11, 0, 0, 0, 0),
        ],
        '["2026-03-11T00:00:00", "2026-04-11T00:00:00", "2026-05-11T00:00:00"]',
    ),
]


class TestDateTimeEncoder:
    def test_encode(self) -> None:
        for input_obj, expect in CASES:
            result = json.dumps(input_obj, cls=DateTimeEncoder)
            assert result == expect, f"Expected: {expect!r}; Receieved: {result!r}"
