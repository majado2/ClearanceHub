from io import BytesIO
from typing import Iterable

from openpyxl import Workbook


def _get_value(item, key):
    if isinstance(item, dict):
        return item.get(key)
    return getattr(item, key, None)


def requests_to_excel(requests: Iterable[object]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Requests"

    headers = [
        "ID",
        "Type",
        "Employee ID",
        "Submitted By",
        "Status",
        "Card Request Type",
        "Request Date",
        "Created At",
        "Updated At",
    ]
    ws.append(headers)

    for req in requests:
        ws.append(
            [
                _get_value(req, "id"),
                _get_value(req, "request_type"),
                _get_value(req, "employee_id"),
                _get_value(req, "submitted_by_employee_id"),
                _get_value(req, "status"),
                _get_value(req, "card_request_type"),
                _get_value(req, "request_date"),
                _get_value(req, "created_at"),
                _get_value(req, "updated_at"),
            ]
        )

    stream = BytesIO()
    wb.save(stream)
    return stream.getvalue()
