import json


def load_config(config_file="config.json"):
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Конфигурационный файл не найден. Укажите адрес и порт вручную.")
        host = input("Введите хост (например, 127.0.0.1): ")
        tcp_port = int(input("Введите TCP порт (например, 12345): "))
        udp_port = int(input("Введите UDP порт (например, 12346): "))
        return {"host": host, "tcp_port": tcp_port, "udp_port": udp_port}
