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
        self.root.resizable(True, True)


        self.drawing_tools = DrawingTools(None, peer)  # Canvas is None initially
        self.ui = PaintUI(root, self.drawing_tools, peer)

        # Now that UI has created the canvas, pass it to drawing_tools
        self.drawing_tools.canvas = self.ui.canvas
        self.drawing_tools.set_tool("pen")  # Set initial tool


def main(peer=None):
    print("Starting Paint App")
    root = tk.Tk()
    app_instance = PaintApp(root, peer)
    if peer:
        peer.drawingTools = app_instance.drawing_tools
    root.mainloop()
    print("Terminou a main")

if __name__ == "__main__":
    main()