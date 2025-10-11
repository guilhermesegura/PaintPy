import socket
import threading
import json
import tkinter as tk
from PIL import Image, ImageDraw
from drawing_tools import DrawingTools
from ui import PaintUI  # sua UI original

class Server:
    def __init__(self, host="0.0.0.0", port=8080, drawing_tools=None):
        self.host = host
        self.port = port
        self.clients = []
        self.drawing_tools = drawing_tools
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f"[*] Servidor escutando em {self.host}:{self.port}")
        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while True:
            client_socket, addr = self.sock.accept()
            self.clients.append(client_socket)
            print(f"[+] Cliente conectado: {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                msg = data.decode()
                try:
                    msg_obj = json.loads(msg)
                    if self.drawing_tools:
                        self.drawing_tools.apply_message(msg_obj)
                    self.broadcast(msg, sender=client_socket)
                except:
                    print(msg)  # chat
        except:
            pass
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
            print("[SERVIDOR] Cliente desconectado")

    def broadcast(self, message, sender=None):
        for c in self.clients:
            if c != sender:
                try:
                    c.send(message.encode())
                except:
                    pass


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Paint Servidor")
    root.geometry("800x600")
    root.resizable(False, False)

    # PIL Image
    pil_image = Image.new("RGB", (800, 600), "white")
    draw = ImageDraw.Draw(pil_image)

    # DrawingTools sem nada ainda
    drawing_tools = DrawingTools(None, pil_image, draw)

    server = Server(port=8080, drawing_tools=drawing_tools)

    # UI
    ui = PaintUI(root, drawing_tools)
    drawing_tools.canvas = ui.canvas

    root.mainloop()