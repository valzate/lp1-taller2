import socket
import threading

HOST = "localhost"
PORT = 9004
BUFFER_SIZE = 1024

def receive_messages(sock): #HILO PARA RECIBIR MENSAJES DEL SERVIDOR
    while True:
        try:
            message = sock.recv(BUFFER_SIZE).decode()
            if not message:
                break
            print(message)
        except:
            print("Conexión cerrada por el servidor.")
            break
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("Conectado al servidor.")
    
    #HILO PARA RECIBIR MENSAJES
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
     
    #Eviar mensajes al servidor
    while True:
        message = input()
        if message.lower() == "/exit":
            break
        client.send(message.encode())
if __name__ == "__main__":
    start_client()                   