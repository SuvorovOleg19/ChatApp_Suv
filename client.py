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

def listen_udp(udp_port):
    """Прослушивание UDP сообщений"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("", udp_port))  # Привязываемся к любому доступному адресу и указанному порту
    print(f"UDP слушает на порту {udp_port}")
    while True:
        try:
            message, addr = udp_socket.recvfrom(1024)
            print(f"Получено UDP сообщение: {message.decode()}")
        except Exception as e:
            print(f"Ошибка при получении UDP сообщения: {e}")
            break

def main():
    host = input("Введите адрес сервера (или оставьте пустым для автоматического): ")
    tcp_port = int(input("Введите TCP порт сервера: "))
    udp_port = int(input("Введите UDP порт сервера: "))  # Добавьте ввод UDP порта

    if not host:
        host = socket.gethostbyname(socket.gethostname())

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, tcp_port))

        # Запуск потока для прослушивания TCP сообщений
        threading.Thread(target=listen_for_messages, args=(client_socket,), daemon=True).start()

        # Запуск потока для прослушивания UDP сообщений
        threading.Thread(target=listen_udp, args=(udp_port,), daemon=True).start()

        print("Введите сообщения, !broadcast для UDP, @user для приватных сообщений, /exit для выхода.")
        while True:
            message = input()
            if message == "/exit":
                client_socket.send(message.encode())
                break
            client_socket.send(message.encode())


if __name__ == "__main__":
    main()
