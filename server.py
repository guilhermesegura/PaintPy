import tkinter as tk
from ui import PaintUI
from drawing_tools import DrawingTools
from PIL import Image, ImageDraw
import socket
import threading

HOST = '?'
PORT = 0
KEEPALIVE_ = 15.0  # segundos permitidos sem keepalive antes da desconexão


if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()