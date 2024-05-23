import math
import socket
import threading
from _thread import *
from typing import List, NoReturn
from collections import deque

IP_ADDRESS = '192.168.0.13'
PORT = 8081
MAX_CLIENTS = 100000
LIST_OF_CLIENTS: List["socket.socket"] = []

# Creamos el objeto socket
SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

username, salt, pwd = ('veronicaospina', '9511a3d63335ccd41b5b2cbc6655e882',
                       '34261cfce8a950d926fadf1fe004c07829b95f7ce3edfb7bf231cfbd3207c30a5b2e558bbf41e9f9038d9e27c49131acfa79a8f5fe52bec232a34131561b181e')

# Abre el archivo de texto en modo de lectura
with open('rockyou.txt', 'r', encoding='iso-8859-1') as file:
    # Lee todas las líneas del archivo
    lines = file.readlines()
possible = [line.strip() for line in lines]

amount_of_passwords = len(possible)
batch_amount = math.ceil(amount_of_passwords / 500)
processed_batches = 0
pending_to_process = deque()
batch_lock = threading.Lock()

def get_new_batch():
    with batch_lock:
        global processed_batches
        start_index = processed_batches * batch_amount
        end_index = min(start_index + batch_amount, amount_of_passwords)
        batch = possible[start_index:end_index]
        processed_batches += 1
        return batch

def get_pending_batch():
    with batch_lock:
        if not pending_to_process:
            return None
        else:
            return pending_to_process.pop()


def client_thread(client_socket: "socket.socket") -> NoReturn:
    while True:
        batch = get_pending_batch()
        if batch is None:
            batch = get_new_batch()
            print("Procesando nuevo lote de contraseñas....")
        else:
            print("Procesando batch pendiente")
        index = 0
        response = False
        try:
            client_socket.sendall(bytes(f"{username},{salt},{pwd}", 'utf-8'))
            for password in batch:
                if password == "":
                    password = "Seguro"
                client_socket.sendall(bytes(password, 'iso-8859-1'))
                data = client_socket.recv(1024)
                response = data == b"True"
                if response:
                    pepp = client_socket.recv(1024)
                    pepper = pepp.decode("utf-8")
                    print(f"Contraseña encontrada: {password}")
                    print(f"Pepper fue: {pepper}")
                    cerrar_clientes()
                    cerrar_clientes()
                index += 1
        except Exception as exe:
            if not response:
                pending_to_process.append(batch[index:len(batch)])
                client_socket.close()
                remove(client_socket)
            break


def cerrar_clientes() -> None:
    for client in LIST_OF_CLIENTS:
        client.close()


def remove(client_socket: "socket.socket") -> None:
    if client_socket in LIST_OF_CLIENTS:
        LIST_OF_CLIENTS.remove(client_socket)


# Configuramos el socket para reutilizar la dirección
SERVER_SOCKET.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Asociamos el socket con la dirección y el puerto
SERVER_SOCKET.bind((IP_ADDRESS, PORT))
# Configuramos el socket para escuchar conexiones entrantes
SERVER_SOCKET.listen(MAX_CLIENTS)

print(f'El servidor ha iniciado en {IP_ADDRESS}:{PORT} y esta escuchando...')

while True:
    client_socket, client_address = SERVER_SOCKET.accept()
    LIST_OF_CLIENTS.append(client_socket)
    print(client_address[0], 'connected')
    start_new_thread(client_thread, (client_socket,))