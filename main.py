import tkinter as tk
from ui import PaintUI
from drawing_tools import DrawingTools
from PIL import Image, ImageDraw

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Paint App")
        self.root.geometry("1200x800")

        # Initialize PIL image and draw context (will be updated by UI on canvas setup)
        # These are placeholders until the canvas size is known
        initial_pil_image = Image.new("RGB", (1, 1), "white")
        initial_draw_context = ImageDraw.Draw(initial_pil_image)

        self.drawing_tools = DrawingTools(None, initial_pil_image, initial_draw_context) # Canvas is None initially
        self.ui = PaintUI(root, self.drawing_tools)

        # Now that UI has created the canvas, pass it to drawing_tools
        self.drawing_tools.canvas = self.ui.canvas
        self.drawing_tools.set_tool("pen") # Set initial tool

if __name__ == "__main__":
    root = tk.Tk()
    app = PaintApp(root)
    root.mainloop()