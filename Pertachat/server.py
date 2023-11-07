import socket
import threading

class ServerChat:
    def __init__(self, host, port, max_clients=5):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.usersocket = {}
        self.usernames = set()

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print("Server is listening for incoming client...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        client_socket.send("zSilakan masukkan username Anda: ".encode())
        username = client_socket.recv(1024).decode()
        while username in self.usernames:
            client_socket.send("zUsername ini sudah digunakan, silakan pilih yang lain: ".encode())
            username = client_socket.recv(1024).decode()

        self.clients[client_socket] = username
        self.usersocket[username] = client_socket
        self.usernames.add(username)

        client_socket.send(f"wSelamat datang di ruang obrolan, {username}!\n".encode())
        client_socket.send(f"O{','.join(self.usernames)}".encode())
        for c in self.clients.keys():
            if c != client_socket:
                c.send(f"o{username}".encode())

        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                # Kirim pesan pribadi atau semua klien yang terhubung
                if data.startswith("@"):
                    splitted = data.split(' ')
                    curr_username = splitted[0][1:]
                    if curr_username in self.usernames:
                        pesan = ' '.join(splitted[1:])
                        self.usersocket[curr_username].send(
                            f"d{username} (pribadi): {pesan}".encode())
                else:
                    for c in self.clients.keys():
                        if c != client_socket:
                            c.send(f"n{self.clients[client_socket]}: {data}".encode())
            except Exception as e:
                print(e)
                del self.clients[client_socket]
                del self.usersocket[username]
                self.usernames.remove(username)
                client_socket.close()
                for c in self.clients.keys():
                    c.send(f"o{username}".encode())  # Mengirim daftar pengguna yang terhubung
                break

HOST = 'localhost'
PORT = 8000
MAX_CLIENTS = 5
server = ServerChat(HOST, PORT, MAX_CLIENTS)
server.start()