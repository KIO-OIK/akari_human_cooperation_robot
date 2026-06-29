import socket
import time

HOST = "0.0.0.0"
PORT = 6000     #ポート番号（数字）

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = "aaaaaa"
            if not data:
                break
            conn.sendall(data.encode())
            time.sleep(1)