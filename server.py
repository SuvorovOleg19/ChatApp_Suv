import socket
import threading
import logging
from datetime import datetime
from config import load_config

# Настройка логирования
logging.basicConfig(
    filename="server.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# Хранение подключений: {имя_пользователя: сокет}
clients = {}
lock = threading.Lock()


def send_message(sender, message, recipient=None):
    """Отправка сообщения конкретному клиенту или всем"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {sender}: {message}"

    with lock:
        if recipient:
            if recipient in clients:
                clients[recipient].send(full_message.encode())
            else:
                clients[sender].send(f"Пользователь {recipient} не найден.".encode())
        else:
            for client, conn in clients.items():
                if client != sender:
                    conn.send(full_message.encode())

def handle_client(conn, addr):
    """Обработка клиента"""
    conn.send("Введите ваше имя: ".encode())
    name = conn.recv(1024).decode().strip()

    with lock:
        clients[name] = conn

    print(f"{name} подключился с {addr}.")

    try:
        while True:
            message = conn.recv(1024).decode()
            if message == "/exit":
                break

            if message.startswith("@"):
                recipient, msg = message[1:].split(" ", 1)
                send_message(name, msg, recipient)
            else:
                send_message(name, message)
    except Exception as e:
        logging.error(f"Ошибка у клиента {name}: {e}")
    finally:
        with lock:
            del clients[name]
        conn.close()
        print(f"{name} отключился.")

def start_tcp_server(host, port):
    """Запуск TCP сервера"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"TCP сервер запущен на {host}:{port}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()


def start_udp_server(host, port):
    """Запуск UDP сервера"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"UDP сервер запущен на {host}:{port}")

    while True:
        try:
            message, client_address = server_socket.recvfrom(1024)
            message = message.decode()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[UDP] {timestamp} от {client_address}: {message}")
        except Exception as e:
            logging.error(f"Ошибка UDP: {e}")

def main():
    config = load_config()
    host = config["host"]
    tcp_port = config["tcp_port"]
    udp_port = config["udp_port"]

    threading.Thread(target=start_tcp_server, args=(host, tcp_port), daemon=True).start()
    threading.Thread(target=start_udp_server, args=(host, udp_port), daemon=True).start()

    print("Сервер работает. Нажмите Ctrl+C для завершения.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Завершение работы сервера.")

if __name__ == "__main__":
    main()
