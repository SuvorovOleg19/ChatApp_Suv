import socket
import threading

def receive_messages(client_socket):
    """Получает и отображает сообщения от сервера"""
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(message)
    except Exception as e:
        print(f"Ошибка при получении сообщения: {e}")
    finally:
        client_socket.close()

def start_client(host="127.0.0.1", port=12345):
    """Запускает клиента"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    # Поток для получения сообщений
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    try:
        while True:
            message = input()
            client_socket.sendall(message.encode())
    except KeyboardInterrupt:
        print("Отключение от сервера...")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
