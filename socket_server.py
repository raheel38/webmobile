import os
import socket
from datetime import datetime

class SocketServer:
    def __init__(self):
        self.buf_size = 1024  # 버퍼 크기 설정
        with open('./response.bin', 'rb') as file:
            self.RESPONSE = file.read()  # 응답 파일 읽기

        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        """디렉토리 생성"""
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def run(self, ip, port):
        """서버 실행"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server\n")

        try:
            while True:
                # 클라이언트 요청 대기
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)
                print(f"Request message from {req_addr}...\n")

                # 데이터 수신
                data = b""
                while True:
                    try:
                        packet = clnt_sock.recv(self.buf_size)
                        if not packet:
                            break
                        data += packet
                    except socket.timeout:
                        break

                # ---- 실습 1: 요청 데이터를 .bin 파일로 저장 ----
                timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                filename = f"{self.DIR_PATH}/{timestamp}.bin"
                with open(filename, "wb") as f:
                    f.write(data)
                print(f"Saved request data to {filename}")

                # ---- 실습 2: multipart 이미지 저장 ----
                if b"Content-Type: image" in data:
                    try:
                        header, image_data = data.split(b"\r\n\r\n", 1)
                        if b"\r\n--" in image_data:
                            image_data = image_data.split(b"\r\n--", 1)[0]
                        img_filename = f"{self.DIR_PATH}/{timestamp}.jpeg"
                        with open(img_filename, "wb") as img:
                            img.write(image_data)
                        print(f"Saved image to {img_filename}")
                    except Exception as e:
                        print("Image parsing failed:", e)

                # ---- 응답 전송 ----
                clnt_sock.sendall(self.RESPONSE)

               
                clnt_sock.close()

        except KeyboardInterrupt:
            print("\nStop the server...")

        # 서버 소켓 닫기
        self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8080)
