import socket
import threading
import logging
from datetime import datetime
from cryptography.fernet import Fernet
from config import load_config

# Настройка логирования
logging.basicConfig(
    filename="server.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Глобальные переменные
clients = {}
lock = threading.Lock()
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)


def send_message(sender, message, recipient=None):
    """Отправка сообщения определенному клиенту или всем"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"[{timestamp}] {sender}: {message}"

    # Логирование в зашифрованном виде
    encrypted_message = cipher.encrypt(full_message.encode())
    with open("chat.log", "ab") as log_file:
        log_file.write(encrypted_message + b"\n")

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


def broadcast_udp(message, udp_socket, udp_port):
    """Широковещательная отправка по UDP"""
    broadcast_address = "255.255.255.255"  # Используйте широковещательный адрес
    try:
        udp_socket.sendto(message.encode(), (broadcast_address, udp_port))
    except Exception as e:
        logging.error(f"Ошибка при отправке UDP сообщения: {e}")



def handle_client(conn, addr, udp_socket, udp_port):
    """Обработка клиента"""
    conn.send("Введите ваше имя: ".encode())
    name = conn.recv(1024).decode().strip()

    with lock:
        clients[name] = conn

    print(f"{name} подключился с {addr}.")
    conn.send(f"Добро пожаловать, {name}! Введите /users для списка пользователей.".encode())

    try:
        while True:
            message = conn.recv(1024).decode()
            if message == "/exit":
                break
            elif message == "/users":
                user_list = ", ".join(clients.keys())
                conn.send(f"Подключенные пользователи: {user_list}".encode())
            elif message.startswith("@"):
                recipient, msg = message[1:].split(" ", 1)
                send_message(name, msg, recipient)
            elif message.startswith("!broadcast "):
                msg = message[len("!broadcast "):]
                broadcast_udp(f"{name}: {msg}", udp_socket, udp_port)
            else:
                send_message(name, message)
    except Exception as e:
        logging.error(f"Ошибка у клиента {name}: {e}")
    finally:
        with lock:
            del clients[name]
        conn.close()
        print(f"{name} отключился.")


def start_tcp_server(host, tcp_port, udp_socket, udp_port):
    """Запуск TCP сервера"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, tcp_port))
    server_socket.listen(5)
    print(f"TCP сервер запущен на {host}:{tcp_port}")

    while True:
        conn, addr = server_socket.accept()
        threading.Thread(
            target=handle_client, args=(conn, addr, udp_socket, udp_port), daemon=True
        ).start()


def start_udp_server(host, udp_port):
    """Запуск UDP сервера"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server_socket.bind((host, udp_port))
    print(f"UDP сервер запущен на {host}:{udp_port}")
    return server_socket


def main():
    config = load_config()
    host = config.get("host", socket.gethostbyname(socket.gethostname()))
    tcp_port = config["tcp_port"]
    udp_port = config["udp_port"]

    udp_socket = start_udp_server(host, udp_port)
    threading.Thread(
        target=start_tcp_server, args=(host, tcp_port, udp_socket, udp_port), daemon=True
    ).start()

    print("Сервер работает. Нажмите Ctrl+C для завершения.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Завершение работы сервера.")
        udp_socket.close()


if __name__ == "__main__":
    main()
