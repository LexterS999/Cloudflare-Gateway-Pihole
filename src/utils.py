import re
from src import ids_pattern

def split_domain_list(domains, chunk_size):
    """Разбивает список доменов на части заданного размера."""
    for i in range(0, len(domains), chunk_size):
        yield domains[i:i + chunk_size]

def safe_sort_key(list_item):
    """Функция для безопасной сортировки элементов списка по имени, извлекая число из имени."""
    match = re.search(r'\d+', list_item["name"])
    return int(match.group()) if match else float('inf')

def extract_list_ids(rule):
    """Извлекает ID списков из правила Cloudflare."""
    if not rule or not rule.get('traffic'):
        return set()
    return set(ids_pattern.findall(rule['traffic']))
