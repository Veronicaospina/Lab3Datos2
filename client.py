import socket
from Crypto.Hash import SHA3_512

SERVER_IP_ADDRESS = '192.168.0.13'
SERVER_PORT = 8081

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP_ADDRESS, SERVER_PORT))

data = client_socket.recv(2048)
credentials = data.decode("utf-8")
username, salt, pwd = credentials.split(',')
print("credentials", credentials)
found = False
while True:
    try:
        data = client_socket.recv(1024)
        password = data.decode("iso-8859-1")
        print("Probando contraseña: ", password)
        # Perform SHA3_512 hashing
        for pepper in range(256):
            hasher = SHA3_512.new()
            hasher.update(bytes(password, 'utf-8'))
            hasher.update(pepper.to_bytes(1, 'big'))
            hasher.update(bytes.fromhex(salt))
            hashed_password = hasher.hexdigest()

            # Send response to the server if a match is found
            if hashed_password == pwd:
                print(f"Encontrada, es esta: {password} en pepper: {pepper}")
                client_socket.sendall(b"True")
                client_socket.sendall(bytes(f"{pepper}", "utf-8"))
                found = True
                break
        if found is False:
            client_socket.sendall(b"False")
        else:
            break
    except Exception as exe:
        client_socket.close()
        break
