import socket

HOST = "127.0.0.1"
PORT = 8080

proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy.connect((HOST, PORT))

# Petición HTTP simple
request = b"""GET http://oracle.com/ HTTP/1.1\r
Host: oracle.com\r
\r
"""

proxy.send(request)

response = proxy.recv(4096)
print("Respuesta recibida:\n")
print(response.decode(errors="ignore"))

proxy.close()
