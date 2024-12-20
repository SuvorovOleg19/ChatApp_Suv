import socket
import threading


def listen_for_messages(sock):
    """Прослушивание сообщений от сервера"""
    while True:
        try:
            message = sock.recv(1024).decode()
            print(message)
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            break


def main():
    host = input("Введите адрес сервера (или оставьте пустым для автоматического): ")
    port = int(input("Введите TCP порт сервера: "))

    if not host:
        host = socket.gethostbyname(socket.gethostname())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))

        threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

        print("Введите сообщения, !broadcast для UDP, @user для приватных сообщений, /exit для выхода.")
        while True:
            message = input()
            if message == "/exit":
                client_socket.send(message.encode())
                break
            client_socket.send(message.encode())


if __name__ == "__main__":
    main()
