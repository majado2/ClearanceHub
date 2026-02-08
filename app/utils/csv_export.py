import csv
from io import StringIO
from typing import Any, Iterable


def _format_value(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, (list, tuple, set)):
        return ",".join(str(item) for item in value)
    return str(value)


def requests_to_csv(rows: Iterable[dict], headers: list[str]) -> bytes:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([_format_value(row.get(key)) for key in headers])
    return buffer.getvalue().encode("utf-8-sig")
