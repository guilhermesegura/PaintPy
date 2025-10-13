import tkinter as tk
from ui import PaintUI
from drawing_tools import DrawingTools
from PIL import Image, ImageDraw

app_instance = None

class PaintApp:
    def __init__(self, root, peer):
        self.root = root
        self.root.title("Advanced Paint App")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Initialize PIL image and draw context (will be updated by UI on canvas setup)
        # These are placeholders until the canvas size is known
        initial_pil_image = Image.new("RGB", (1, 1), "white")
        initial_draw_context = ImageDraw.Draw(initial_pil_image)

        self.drawing_tools = DrawingTools(None, initial_pil_image, initial_draw_context,
                                          peer)  # Canvas is None initially
        self.ui = PaintUI(root, self.drawing_tools, peer)

        # Now that UI has created the canvas, pass it to drawing_tools
        self.drawing_tools.canvas = self.ui.canvas
        self.drawing_tools.set_tool("pen")  # Set initial tool


def main(peer):
    print("Starting Paint App")
    root = tk.Tk()
    app_instance = PaintApp(root, peer)
    peer.drawingTools = app_instance.drawing_tools
    root.mainloop()
    print("Terminou a main")