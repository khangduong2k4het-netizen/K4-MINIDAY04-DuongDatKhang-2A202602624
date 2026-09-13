import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw-data')


def search_product_catalog(category: str, max_price: int = 999999999999) -> List[Dict[str, Any]]:
    """Lọc danh mục và giá tối đa từ dữ liệu JSON."""
    try:
        with open(os.path.join(RAW_DATA_DIR, 'product_catalog.json'), encoding='utf-8') as f:
            products = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return [{'error': f'Không thể đọc catalog: {exc}'}]
    return [p for p in products if p['category'].lower() == category.strip().lower()
            and p['price_vnd'] <= max_price]


def submit_support_ticket(customer_name: str, issue_description: str,
                          priority: str = 'medium') -> Dict[str, Any]:
    """Thêm ticket mới, giữ lại toàn bộ ticket hiện có."""
    priority = priority.strip().lower()
    if not customer_name.strip() or not issue_description.strip():
        return {'error': 'Cần tên khách hàng và mô tả vấn đề.'}
    if priority not in ('low', 'medium', 'high'):
        return {'error': 'Mức ưu tiên phải là low, medium hoặc high.'}
    path = os.path.join(RAW_DATA_DIR, 'support_tickets.json')
    try:
        tickets = []
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                tickets = json.load(f)
        now = datetime.now(timezone(timedelta(hours=7)))
        seq = len(tickets) + 1
        used_ids = {t['ticket_id'] for t in tickets}
        ticket_id = f'TK-{now:%Y%m%d}-{seq:03d}'
        while ticket_id in used_ids:
            seq += 1
            ticket_id = f'TK-{now:%Y%m%d}-{seq:03d}'
        ticket = dict(ticket_id=ticket_id, customer_name=customer_name.strip(),
                      issue_description=issue_description.strip(), priority=priority,
                      status='open', created_at=now.isoformat(), category='general')
        tickets.append(ticket)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(tickets, f, indent=2, ensure_ascii=False)
    except (OSError, json.JSONDecodeError) as exc:
        return {'error': f'Không thể lưu ticket: {exc}'}
    return {**ticket, 'message': f'Ticket {ticket_id} đã được tạo thành công.'}


TOOL_DEFINITIONS = [
    {
        'name': 'search_product_catalog',
        'description': 'Tra cứu sản phẩm Vingroup theo danh mục và giá tối đa.',
        'parameters': {
            'type': 'object',
            'properties': {
                'category': {'type': 'string', 'enum': ['xe_dien', 'du_lich'],
                             'description': 'Danh mục xe điện hoặc du lịch.'},
                'max_price': {'type': 'integer', 'minimum': 0,
                              'description': 'Giá tối đa bằng VNĐ.'},
            },
            'required': ['category'], 'additionalProperties': False,
        },
    },
    {
        'name': 'submit_support_ticket',
        'description': 'Tạo và lưu yêu cầu hỗ trợ khách hàng.',
        'parameters': {
            'type': 'object',
            'properties': {
                'customer_name': {'type': 'string', 'minLength': 1,
                                  'description': 'Tên khách hàng cung cấp.'},
                'issue_description': {'type': 'string', 'minLength': 1,
                                      'description': 'Nội dung cần hỗ trợ.'},
                'priority': {'type': 'string', 'enum': ['low', 'medium', 'high'],
                             'default': 'medium', 'description': 'Mức ưu tiên.'},
            },
            'required': ['customer_name', 'issue_description'], 'additionalProperties': False,
        },
    },
]

TOOL_MAP = {'search_product_catalog': search_product_catalog,
            'submit_support_ticket': submit_support_ticket}
