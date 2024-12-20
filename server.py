import socket
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Хранение подключений: {имя_пользователя: сокет}
clients = {}

def broadcast(sender_name, receiver_name, message):
    """Отправляет сообщение указанному получателю"""
    if receiver_name in clients:
        try:
            full_message = f"[{sender_name} -> {receiver_name}]: {message}"
            clients[receiver_name].sendall(full_message.encode())
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения: {e}")
    else:
        logging.warning(f"Получатель '{receiver_name}' не найден.")

def handle_client(client_socket):
    """Обрабатывает подключение клиента"""
    try:
        # Получаем имя пользователя
        client_socket.sendall("Введите свое имя: ".encode())
        user_name = client_socket.recv(1024).decode().strip()
        if user_name in clients:
            client_socket.sendall("Имя занято. Подключитесь снова.".encode())
            client_socket.close()
            return

        clients[user_name] = client_socket
        logging.info(f"Подключен пользователь: {user_name}")
        client_socket.sendall("Вы подключены. Можете отправлять сообщения.".encode())

        while True:
            # Ожидаем сообщение в формате "получатель: сообщение"
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break

            if ":" not in data:
                client_socket.sendall("Неверный формат сообщения. Используйте 'получатель: сообщение'.".encode())
                continue

            receiver_name, message = data.split(":", 1)
            receiver_name = receiver_name.strip()
            message = message.strip()

            if receiver_name == "":  # Если поле пустое
                client_socket.sendall("Укажите получателя.".encode())
            else:
                broadcast(user_name, receiver_name, message)

    except Exception as e:
        logging.error(f"Ошибка в обработке клиента: {e}")
    finally:
        logging.info(f"Отключен пользователь: {user_name}")
        if user_name in clients:
            del clients[user_name]
        client_socket.close()

def start_server(host="127.0.0.1", port=12345):
    """Запускает сервер"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    logging.info(f"Сервер запущен на {host}:{port}")

    try:
        while True:
            client_socket, _ = server_socket.accept()
            threading.Thread(target=handle_client, args=(client_socket,), daemon=True).start()
    except KeyboardInterrupt:
        logging.info("Сервер остановлен вручную")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
