import socket
import threading
import tkinter as tk
from PIL import Image, ImageTk
import sys
from datetime import datetime
from tkinter import filedialog

global receive_thread
global stop_thread

# Define constants for the client
HOST = 'localhost'
PORT = 8000

class Client:
    def __init__(self) :
        self.usernames_set = set()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message(self, event = None):
        message = self.input_field.get()
        if len(self.usernames_set) == 0:
            root.title(f'Chat - {message}') 
        self.input_field.delete(0, tk.END)
        self.client_socket.send(message.encode())
        self.add_message(message, 'me')
    
    def send_pic(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if file_path:
            # self.display_image(file_path, 'me')
            with open(file_path, 'rb') as file:
                image_data = file.read()
                self.client_socket.send(f"i{len(image_data)}".encode())
                self.client_socket.send(image_data)
        return file_path

    def send(self, msg, is_sent=False):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.insert(tk.END, '\n ', "right")
        self.chat_window.window_create(tk.END, window=tk.Label(self.chat_window, fg="#000000", text=msg, wraplength=200, font=("Arial", 10), bg="lightblue", bd=4, justify="left"))
        self.chat_window.insert(tk.END, '\n ', "left")
        self.chat_window.config(foreground="#0000CC", font=("Helvetica", 9))
        self.chat_window.yview(tk.END)
    
    def insert_emoji(self, x):
        self.input_field.insert(tk.END, x.widget['text'])
    
    def on_listbox_double_click(self, event):
        # Get the selected item from the listbox
        selection = self.online_clients_listbox.get(
            self.online_clients_listbox.curselection())

        # Perform the desired action, e.g. print the selected item
        self.input_field.delete(0, tk.END)
        self.input_field.insert(tk.END, f"@{selection} ")
        self.input_field.focus_set()
    
class ChatBox(Client):
    def __init__(self):
        super().__init__()
        self.client_socket.connect((HOST, PORT))
        self.chat_frame = tk.Frame(root)
        self.chat_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.chat_frame.configure(bg="#2E3440")

        self.online_clients_frame = tk.Frame(self.chat_frame)
        self.online_clients_frame.pack(side=tk.RIGHT, padx=10)
        self.online_clients_frame.configure(bg="#2E3440")
    
        self.scrollbar = tk.Scrollbar(self.chat_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.chat_window = tk.Text(self.chat_frame, height=20, width=50,
                            yscrollcommand=self.scrollbar.set, wrap="word")
        self.chat_window.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.scrollbar.config(command=self.chat_window.yview)

        self.chat_window.tag_config('user', foreground='#88C0D0')
        self.chat_window.tag_config('server', foreground='#8FBCBB')
        self.chat_window.tag_config('small', font=("Helvetica", 7))
        self.chat_window.tag_config('greycolour', foreground="#D8DEE9")
        self.chat_window.tag_config("me", justify="right")
        self.chat_window.tag_config("others", justify="left")
        self.chat_window.tag_config("system", justify="center")
        self.chat_window.tag_config("right", justify="right")
        self.chat_window.tag_config("small", font=("Helvetica", 7))
        self.chat_window.tag_config("colour", foreground="#D8DEE9")

        self.chat_window.configure(state=tk.DISABLED)
        self.chat_window.configure(background='black')

        self.input_frame = tk.Frame(root)
        self.input_frame.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.input_frame.configure(bg="#2E3440")

        self.input_field = tk.Entry(self.input_frame, width=40)
        self.input_field.bind("<Return>", self.send_message)
        self.input_field.pack(side=tk.LEFT)

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.LEFT)
        self.send_button.configure(bg="#D8DEE9", fg="#2E3440")

        self.clear_chat_button = tk.Button(self.input_frame, text="Clear Chat", command=self.clear_chat)
        self.clear_chat_button.pack(side=tk.LEFT)
        self.clear_chat_button.configure(bg="#D8DEE9", fg="#2E3440")
        
        self.open_file = tk.Button(self.input_frame, text="Image", command=self.send_pic)
        self.open_file.pack(side=tk.LEFT)
        self.open_file.configure(bg="#D8DEE9", fg="#2E3440")
        
        self.emotbro = tk.Button(self.input_frame, text="Emoji", command=self.toggle_emojis)
        self.emotbro.pack(side=tk.LEFT)
        self.emotbro.configure(bg="#D8DEE9", fg="#2E3440")

        self.online_clients_label = tk.Label(self.online_clients_frame, text="Online Clients:")
        self.online_clients_label.pack(side=tk.TOP)
        self.online_clients_label.configure(bg="#2E3440", fg="#D8DEE9")

        self.online_clients_listbox = tk.Listbox(self.online_clients_frame, height=20, width=20)
        self.online_clients_listbox.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.online_clients_listbox.configure(bg="#4C566A", fg="#D8DEE9", highlightbackground="#81A1C1",
                                        highlightcolor="#81A1C1", selectbackground="#81A1C1", selectforeground="#D8DEE9")
        
        self.online_clients_listbox.bind("<Double-Button-1>", self.on_listbox_double_click)
        
        self.emoji_data = [('emojis/u0001f44a.png', '\U0001F44A'), ('emojis/u0001f44c.png', '\U0001F44C'), ('emojis/u0001f44d.png', '\U0001F44D'),
                      ('emojis/u0001f4a6.png', '\U0001F4A6'), ('emojis/u0001f4a9.png', '\U0001F4A9'), ('emojis/u0001f4af.png', '\U0001F4AF'), ('emojis/u0001f595.png', '\U0001F595'), ('emojis/u0001f600.png', '\U0001F600'), ('emojis/u0001f602.png', '\U0001F602'), ('emojis/u0001f603.png', '\U0001F603'), ('emojis/u0001f605.png', '\U0001F605'), ('emojis/u0001f606.png', '\U0001F606'), ('emojis/u0001f608.png', '\U0001F608'), ('emojis/u0001f60d.png', '\U0001F60D'), ('emojis/u0001f60e.png', '\U0001F60E'), ('emojis/u0001f60f.png', '\U0001F60F'), ('emojis/u0001f610.png', '\U0001F610'), ('emojis/u0001f618.png', '\U0001F618'), ('emojis/u0001f61b.png', '\U0001F61B'), ('emojis/u0001f61d.png', '\U0001F61D'), ('emojis/u0001f621.png', '\U0001F621'), ('emojis/u0001f624.png', '\U0001F621'), ('emojis/u0001f642.png', '\U0001F642'), ('emojis/u0001f64f.png', '\U0001F64F')]
        
        self.emoji_x_pos = 405
        self.emoji_y_pos = 230
        self.emojis_visible = False
        self.arremoji = []
        self.arrimg = []

    def display_image(self, image_path, sender):
        self.chat_window.config(state=tk.NORMAL)

        img_position = ""
        tags = ""

        match sender:
            case 'others':
                img_position = "left"
                tags = 'others'
            case 'system':
                img_position = "center"
                tags = 'system'
            case 'me':
                img_position = "right"
                tags = 'me'
        
        self.chat_window.insert(tk.END, '\n ', img_position)
        self.chat_window.insert(tk.END, self.get_time_formatted(),('small', 'greycolour', img_position))
        self.chat_window.insert(tk.END, ' ', img_position)

        self.chat_window.config(state=tk.DISABLED)
        global photo
        image = Image.open(image_path)
        image = image.resize((200, 200), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        self.chat_window.image_create(tk.END, image=photo)
        self.arrimg.append(photo)
        self.chat_window.insert(tk.END, '\n', "center")
        self.chat_window.tag_add(tags, "end-2l", "end-1c")
        self.chat_window.yview(tk.END)
    
    def show_emoji(self):
        for Emoji in self.emoji_data:
            self.emojis = Image.open(Emoji[0])
            self.emojis = self.emojis.resize((20, 20), Image.LANCZOS)
            self.emojis = ImageTk.PhotoImage(self.emojis)

            self.emoji_unicode = Emoji[1]
            self.emoji_label = tk.Label(root, image=self.emojis, text=self.emoji_unicode, bg="#194548", cursor="hand2")
            self.emoji_label.image = self.emojis
            self.emoji_label.place(x=self.emoji_x_pos, y=self.emoji_y_pos)
            self.emoji_label.bind('<Button-1>', lambda x: self.insert_emoji(x))
            self.emoji_label.pack(side=tk.LEFT)
            

            self.emoji_x_pos += 25
            self.cur_index = self.emoji_data.index(Emoji)
            if (self.cur_index + 1) % 6 == 0:
                self.emoji_y_pos += 25
                self.emoji_x_pos = 405
            self.arremoji.append(self.emoji_label)
    
    def toggle_emojis(self):
        if self.emojis_visible:
            for emoji in self.arremoji:
                emoji.pack_forget()
            self.emojis_visible = False
        else:
            self.show_emoji()
            self.emojis_visible = True
    
    def receive_messages(self):
        while True:
            try:
                if stop_thread == True:
                    sys.exit(0)
                    break

                data = self.client_socket.recv(1024).decode()
                # print (data)
                
                if not data:
                    break

                msg_type = data[0]
                msg = data[1:]
                img = data[0]
                # print (msg_type)
                # print (msg)

                if msg_type == 'o':
                    if msg in self.usernames_set:
                        self.add_message(f"{msg} has just left the room", 'system')
                        self.usernames_set.remove(msg)
                    else:
                        self.add_message(f"{msg} has just joined the room", 'system')
                        self.usernames_set.add(msg)
                    self.update_online_clients(self.usernames_set)
                elif msg_type == 'O':
                    curr_online_users = msg.split(',')
                    self.usernames_set.update(curr_online_users)
                    self.update_online_clients(curr_online_users)               

                elif msg_type in ['z', 'w']:
                    self.add_message(msg, 'system')
                elif img == 'i':
                    # self.display_image(msg, 'system')
                    if 'sent by' in msg:
                        sender_info = msg.split('sent by ')
                        if len(sender_info) == 2:
                            sender_name = sender_info[1]
                            image_path = sender_info[0]
                            pesan = f"{sender_name} mengirim gambar"
                            self.add_message(pesan, 'system')
                            self.display_image(image_path, 'system')
                else:
                    self.add_message(msg, 'others')
            except Exception as e:
                print(f"error {e}")
                self.client_socket.close()
                break

    def clear_chat(self):
        self.chat_window.config(state=tk.NORMAL)
        self.chat_window.delete('1.0', tk.END)
        self.chat_window.config(state=tk.DISABLED)

    def on_closing(self):
        self.client_socket.close()
        sys.exit(0)
        
    def get_time_formatted(self):
        return datetime.now().strftime("%a %I-%M %p \n")
    
    def add_message(self, msg, sender):
        self.chat_window.config(state=tk.NORMAL)

        fa = "#13f252"
        bg_color = "black"
        text_position = ""
        tags = ""
        text_direction = tk.LEFT

        match sender:
            case 'others':
                text_position = "left"
                fa = "#13f252"
                tags = 'others'
            case 'system':
                text_position = "center"
                fa = "#ffffff"
                tags = 'system'
                text_direction = tk.CENTER
            case 'me':
                text_position = "right"
                fa = "#fc541c"
                tags = 'me'
        
        self.chat_window.insert(tk.END, '\n ', text_position)
        self.chat_window.insert(tk.END, self.get_time_formatted(),('small', 'greycolour', text_position))
        self.chat_window.insert(tk.END, ' ', text_position)

        self.chat_window.config(state=tk.DISABLED)
        
        message = tk.Label(self.chat_window, fg=fa, text=msg, wraplength=200, font=("Arial", 10), bg=bg_color, bd=4, justify=text_direction, relief="flat", anchor="center")

        self.chat_window.window_create(tk.END, window=message)
        self.chat_window.insert(tk.END, '\n', "center")
        self.chat_window.tag_add(tags, "end-2l", "end-1c")
        self.chat_window.config(foreground="#0000CC", font=("Helvetica", 9))
        self.chat_window.yview(tk.END)

    def update_online_clients(self, online_clients):
        # Clear the current list of online clients
        self.online_clients_listbox.delete(0, tk.END)

        # Add each online client to the listbox
        for client in online_clients:
            self.online_clients_listbox.insert(tk.END, client)
            
root = tk.Tk()
root.configure(bg="#2E3440")
root.title('Chat')

app = ChatBox()

stop_thread = False
receive_thread = threading.Thread(target=app.receive_messages)
receive_thread.start()

root.protocol("WM_DELETE_WINDOW", app.on_closing)

tk.mainloop()