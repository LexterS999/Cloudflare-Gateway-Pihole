import os
import re
from sys import exit
from src.colorlog import logger

# Constants
RATE_LIMIT_INTERVAL = 1.0
PREFIX = "AdBlock-DNS-Filters"

# Read .env variables 
def dot_env(file_path=".env"):
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    value = re.sub(r'^["\'<]*(.*?)["\'>]*$', r'\1', value)
                    env_vars[key] = value
    return env_vars

env_vars = dot_env()

# Load environment or .env variables
CF_API_TOKEN = os.getenv("CF_API_TOKEN") or env_vars.get("CF_API_TOKEN")
CF_IDENTIFIER = os.getenv("CF_IDENTIFIER") or env_vars.get("CF_IDENTIFIER")
if not CF_API_TOKEN or not CF_IDENTIFIER:
    raise Exception("Missing Cloudflare credentials")
if CF_API_TOKEN == "your CF_API_TOKEN value" or CF_IDENTIFIER == "your CF_IDENTIFIER value":
    raise Exception("Please provide valid values for CF_API_TOKEN and CF_IDENTIFIER")

# Compile regex patterns
replace_pattern = re.compile(
    r"(^([0-9.]+|[0-9a-fA-F:.]+)\s+|^(\|\||@@\|\||\*\.|\*))"
)
domain_pattern = re.compile(
    r"^([a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?\.)*"
    r"[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?$"
)
ip_pattern = re.compile(
    r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
)
ids_pattern = re.compile(
    r"\$(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})"
)

# Logging functions
def error(message):
    logger.error(message)
    exit(1)

def silent_error(message):
    logger.warning(message)

def info(message):
    logger.info(message)
