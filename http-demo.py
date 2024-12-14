import socket
import ssl


def https_get(host, path):
    # 创建一个 TCP 套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 使用 SSL/TLS 对套接字进行封装
    context = ssl.create_default_context()
    ssl_socket = context.wrap_socket(client_socket, server_hostname=host)

    try:
        # 连接到服务器（HTTPS 默认端口是 443）
        ssl_socket.connect((host, 443))

        # 构造 HTTP GET 请求
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        ssl_socket.sendall(request.encode())

        # 接收响应
        response = b""
        while True:
            data = ssl_socket.recv(4096)
            if not data:
                break
            response += data

        # 返回响应内容
        return response.decode()
    finally:
        ssl_socket.close()


# 使用
host = "www.google.com"
path = "/"
response = https_get(host, path)
print(response)
