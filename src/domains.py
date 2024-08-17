# domains.py
import os
import http.client
from urllib.parse import urlparse, urljoin
from configparser import ConfigParser
from src import info, convert, silent_error

def read_urls_from_file(filename):
    """Читает URL-адреса из файла, определяя тип файла (INI или текстовый)."""
    urls = []
    try:
        with open(filename, "r") as file:
            first_line = file.readline()
            file.seek(0)  # Возвращаем указатель в начало файла

            if first_line.startswith("["):  # Проверяем, похоже ли на INI
                config = ConfigParser()
                config.read_file(file)
                urls.extend(config.get(section, key) 
                             for section in config.sections() 
                             for key in config.options(section) 
                             if not key.startswith("#"))
            else:  # Читаем как обычный текстовый файл
                urls = [url.strip() for url in file if url.strip() and not url.startswith("#")]
    except Exception as e:
        silent_error(f"Error reading URLs from file {filename}: {e}")
    return urls


def read_urls_from_env(env_var):
    """Читает URL-адреса из переменной окружения."""
    urls = os.getenv(env_var, "")
    return [url.strip() for url in urls.split() if url.strip()]


def download_file(url):
    """Загружает файл по заданному URL, используя keep-alive."""
    parsed_url = urlparse(url)
    conn = None
    try:
        if parsed_url.scheme == "https":
            conn = http.client.HTTPSConnection(parsed_url.netloc)
        else:
            conn = http.client.HTTPConnection(parsed_url.netloc)

        headers = {'User-Agent': 'Mozilla/5.0', 'Connection': 'keep-alive'}

        conn.request("GET", parsed_url.path, headers=headers)
        response = conn.getresponse()

        # Обработка редиректов
        while response.status in (301, 302, 303, 307, 308):
            location = response.getheader('Location')
            if not location:
                break
            location = urljoin(url, location) if not urlparse(location).netloc else location
            url = location
            parsed_url = urlparse(url)
            conn.request("GET", parsed_url.path, headers=headers)
            response = conn.getresponse()

        if response.status != 200:
            silent_error(f"Failed to download file from {url}, status code: {response.status}")
            return ""

        data = response.read().decode('utf-8')
        info(f"Downloaded file from {url} File size: {len(data)}")
        return data
    except Exception as e:
        silent_error(f"Error downloading file from {url}: {e}")
        return ""
    finally:
        if conn:
            conn.close()


class DomainConverter:
    """Класс для загрузки и конвертации списков доменов."""

    def __init__(self):
        """Инициализирует DomainConverter."""
        self.env_file_map = {
            "ADLIST_URLS": "./lists/adlist.ini",
            "WHITELIST_URLS": "./lists/whitelist.ini",
            "DYNAMIC_BLACKLIST": "./lists/dynamic_blacklist.txt",
            "DYNAMIC_WHITELIST": "./lists/dynamic_whitelist.txt"
        }
        self.adlist_urls = self.read_urls("ADLIST_URLS")
        self.whitelist_urls = self.read_urls("WHITELIST_URLS")

    def read_urls(self, env_var):
        """Читает URL-адреса из файла и переменной окружения."""
        file_path = self.env_file_map[env_var]
        urls = read_urls_from_file(file_path)
        urls += read_urls_from_env(env_var)
        return urls

    def process_urls(self):
        """Загружает и конвертирует списки доменов."""
        block_content = "".join(download_file(url) for url in self.adlist_urls)
        white_content = "".join(download_file(url) for url in self.whitelist_urls)

        # Чтение динамических списков
        for key, file_path in (("DYNAMIC_BLACKLIST", block_content), ("DYNAMIC_WHITELIST", white_content)):
            content = os.getenv(key, "")
            if content:
                content += content
            else:
                try:
                    with open(self.env_file_map[key], "r") as f:
                        content += f.read()
                except Exception as e:
                    silent_error(f"Error reading {key}: {e}")

        domains = convert.convert_to_domain_list(block_content, white_content)
        info(f"Processed {len(domains)} domains.")
        return domains
