import json
import time
from src.requests import (
    cloudflare_gateway_request, retry, rate_limited_request, retry_config
)


@retry(**retry_config)
@rate_limited_request
def create_list(name, domains):
    """Создает новый список доменов в Cloudflare Gateway."""
    start_time = time.time()
    endpoint = "/lists"
    data = {
        "name": name,
        "description": "Ads & Tracking Domains",
        "type": "DOMAIN",
        "items": [{"value": domain} for domain in domains]
    }
    status, response = cloudflare_gateway_request("POST", endpoint, body=json.dumps(data))
    end_time = time.time()
    info(f"create_list operation took {end_time - start_time:.2f} seconds")
    return response["result"]

@retry(**retry_config)
@rate_limited_request
def update_list(list_id, remove_items, append_items):
    """Обновляет существующий список доменов в Cloudflare Gateway."""
    start_time = time.time()
    endpoint = f"/lists/{list_id}"    
    data = {
        "remove": [domain for domain in remove_items],
        "append": [{"value": domain} for domain in append_items]
    }    
    status, response = cloudflare_gateway_request("PATCH", endpoint, body=json.dumps(data))
    end_time = time.time()
    info(f"update_list operation took {end_time - start_time:.2f} seconds")
    return response["result"]

@retry(**retry_config)
def create_rule(rule_name, list_ids):
    """Создает новое правило в Cloudflare Gateway."""
    start_time = time.time()
    endpoint = "/rules"
    data = {
        "name": rule_name,
        "description": "Block Ads & Tracking",
        "action": "block",
        "traffic": " or ".join(f'any(dns.domains[*] in ${lst})' for lst in list_ids),
        "enabled": True,
    }
    status, response = cloudflare_gateway_request("POST", endpoint, body=json.dumps(data))
    end_time = time.time()
    info(f"create_rule operation took {end_time - start_time:.2f} seconds")
    return response["result"]

@retry(**retry_config)
def update_rule(rule_name, rule_id, list_ids):
    """Обновляет существующее правило в Cloudflare Gateway."""
    start_time = time.time()
    endpoint = f"/rules/{rule_id}"
    data = {
        "name": rule_name,
        "description": "Block Ads & Tracking",
        "action": "block",
        "traffic": " or ".join(f'any(dns.domains[*] in ${lst})' for lst in list_ids),
        "enabled": True,
    }
    status, response = cloudflare_gateway_request("PUT", endpoint, body=json.dumps(data))
    end_time = time.time()
    info(f"update_rule operation took {end_time - start_time:.2f} seconds")
    return response["result"]

@retry(**retry_config)
def get_lists(prefix_name):
    """Получает список списков доменов из Cloudflare Gateway."""
    status, response = cloudflare_gateway_request("GET", "/lists")
    lists = response["result"] or []
    return [l for l in lists if l["name"].startswith(prefix_name)]

@retry(**retry_config)
def get_rules(rule_name_prefix):
    """Получает список правил из Cloudflare Gateway."""
    status, response = cloudflare_gateway_request("GET", "/rules")
    rules = response["result"] or []
    return [r for r in rules if r["name"].startswith(rule_name_prefix)]

@retry(**retry_config)
@rate_limited_request
def delete_list(list_id):
    """Удаляет список доменов из Cloudflare Gateway."""
    start_time = time.time()
    endpoint = f"/lists/{list_id}"
    status, response = cloudflare_gateway_request("DELETE", endpoint)
    end_time = time.time()
    info(f"delete_list operation took {end_time - start_time:.2f} seconds")
    return response["result"]

@retry(**retry_config)
def delete_rule(rule_id):
    """Удаляет правило из Cloudflare Gateway."""
    start_time = time.time()
    endpoint = f"/rules/{rule_id}"
    status, response = cloudflare_gateway_request("DELETE", endpoint)
    end_time = time.time()
    info(f"delete_rule operation took {end_time - start_time:.2f} seconds")
    return response["result"]

@retry(**retry_config)
def get_list_items(list_id):
    """Получает элементы списка доменов из Cloudflare Gateway."""
    endpoint = f"/lists/{list_id}/items?limit=1000"
    status, response = cloudflare_gateway_request("GET", endpoint)
    items = response["result"] or []
    return [i["value"] for i in items]
