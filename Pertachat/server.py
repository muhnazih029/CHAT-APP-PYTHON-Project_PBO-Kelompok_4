import time
import socket
import threading
import subprocess
import tkinter as tk

class ServerChat:
    def __init__(self):
        self.host = 'localhost'
        self.port = 8000
        self.max_clients = 5
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.usersocket = {}
        self.usernames = set()

    def get_current_client_count(self):
        return len(self.clients)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print("Server is listening for incoming client...")
        while True:
            try:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()
            except Exception as e:
                print(e)
                break

    def stop_server(self):
        self.server_socket.close()
        print("Server stopped.")
    
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
                        
                elif data.startswith("i"):
                    # Menerima data gambar
                    image_size = int(data[1:])
                    image_data = client_socket.recv(image_size)
                    image_filename = f"received_image_{int(time.time())}.png"

                    with open(image_filename, 'wb') as image_file:
                        image_file.write(image_data)

                    # Kirim path gambar ke semua klien
                    for c in self.clients.keys():
                        message = f"i{image_filename} sent by {username}"
                        c.send(message.encode())
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

class Client:
    def __init__(self):
        self.server = ServerChat()
        self.root = tk.Tk()
        self.root.title("Client Controller")
        self.root.protocol("WM_DELETE_WINDOW", self.on_end_server)
        self.max_clients = 5
        self.current_clients = 0
        self.process = None
        self.server_running = False

    def on_button_click(self):
        if self.current_clients < self.max_clients:
            self.process = subprocess.Popen(['python', 'client.py'])
            self.current_clients += 1
            self.status_label.config(text=f"Current Clients: {self.current_clients}/{self.max_clients}")
            if self.current_clients >= self.max_clients:
                self.disable_button()

    def disable_button(self):
        self.button.config(state=tk.DISABLED)

    def on_end_server(self):
        self.server.stop_server()
        # self.disable_button()
        self.server_running = False
        self.root.destroy()

    def start_server(self):
        if not self.server_running:
            self.server_running = True
            self.server.start()
    
    def start_server_thread(self):
        server_thread = threading.Thread(target=self.start_server)
        server_thread.start()

    def run_gui(self):
        label = tk.Label(self.root, text="Client Controller")
        label.pack()

        self.server_on = tk.Button(self.root, text="Start Server", command=klien.start_server_thread)
        self.server_on.pack()

        self.button = tk.Button(self.root, text="Add Client", command=self.on_button_click)
        self.button.pack()

        self.end_server_button = tk.Button(self.root, text="End Server", command=self.on_end_server)
        self.end_server_button.pack()

        self.status_label = tk.Label(self.root, text=f"Current Clients: {self.current_clients}/{self.max_clients}")
        self.status_label.pack()
        
        self.root.mainloop()

if __name__ == "__main__":
    klien = Client()
    klien.run_gui()