#!/usr/bin/env python3
"""
Problema 1: Sockets básicos - Servidor
Objetivo: Crear un servidor TCP que acepte una conexión y intercambie mensajes básicos
"""

import socket

# TODO: Definir la dirección y puerto del servidor
HOST = "localhost"
PORT = 9000

# TODO: Crear un socket TCP/IP
# AF_INET: socket de familia IPv4
# SOCK_STREAM: socket de tipo TCP (orientado a conexión)
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# TODO: Enlazar el socket a la dirección y puerto especificados
servidor.bind((HOST, PORT))

# TODO: Poner el socket en modo escucha
servidor.listen() #pone al servidor en espera de conexiones
print("Servidor a la espera de conexiones ...")


# El parámetro define el número máximo de conexiones en cola
# TODO: Aceptar una conexión entrante
conn, direccion = servidor.accept()
# accept() bloquea hasta que llega una conexión
# conn: nuevo socket para comunicarse con el cliente
# addr: dirección y puerto del cliente

print(f"Conexión realizada por {HOST}")

# TODO: Recibir datos del cliente (hasta 1024 bytes)
datos = conn.recv(1024)
# TODO: Enviar respuesta al cliente (convertida a bytes)
conn.sendall(b"Hola! "+ datos) #la "b" indica binario, y asi es como se manda  
# sendall() asegura que todos los datos sean enviados

# TODO: Cerrar la conexión con el cliente
conn.close()
