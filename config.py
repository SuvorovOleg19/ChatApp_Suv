import json
import socket
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def load_config(config_file="config.json"):
    """Загружает конфигурацию из файла или создает значения по умолчанию."""
    default_config = {
        "host": socket.gethostbyname(socket.gethostname()),  # Автоматическое определение хоста
        "tcp_port": 12345,
        "udp_port": 12346,
    }

    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
            # Если каких-то ключей нет в конфиге, используем значения по умолчанию
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
    except FileNotFoundError:
        logging.warning("Файл конфигурации не найден. Используются значения по умолчанию.")
        return default_config
    except json.JSONDecodeError:
        logging.error("Ошибка в формате файла конфигурации. Используются значения по умолчанию.")
        return default_config
