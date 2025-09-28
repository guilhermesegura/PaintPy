import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

class PaintUI:
    def __init__(self, root, drawing_tools):
        self.root = root
        self.drawing_tools = drawing_tools
        self.canvas = None
        self.photo_image = None # To keep a reference to the PhotoImage to prevent garbage collection

        self._setup_toolbar()
        self._setup_canvas()
        self._bind_events()

    def _setup_toolbar(self):
        self.toolbar = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        # Color picker button
        self.color_button = tk.Button(self.toolbar, text="Color", command=self._choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Pen size slider
        self.size_label = tk.Label(self.toolbar, text="Size:")
        self.size_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.size_slider = tk.Scale(self.toolbar, from_=1, to=20, orient=tk.HORIZONTAL,
                                    command=lambda s: self.drawing_tools.set_size(s))
        self.size_slider.set(self.drawing_tools.pen_size)
        self.size_slider.pack(side=tk.LEFT, padx=5, pady=5)

        # Separator
        tk.Frame(self.toolbar, width=1, bg="grey", height=30).pack(side=tk.LEFT, padx=10)

        # Tool buttons
        self.pen_button = tk.Button(self.toolbar, text="Pen", command=lambda: self.drawing_tools.set_tool("pen"))
        self.pen_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.eraser_button = tk.Button(self.toolbar, text="Eraser", command=lambda: self.drawing_tools.set_tool("eraser"))
        self.eraser_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.line_button = tk.Button(self.toolbar, text="Line", command=lambda: self.drawing_tools.set_tool("line"))
        self.line_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.rect_button = tk.Button(self.toolbar, text="Rectangle", command=lambda: self.drawing_tools.set_tool("rectangle"))
        self.rect_button.pack(side=tk.LEFT, padx=2, pady=5)

        self.circle_button = tk.Button(self.toolbar, text="Circle", command=lambda: self.drawing_tools.set_tool("circle"))
        self.circle_button.pack(side=tk.LEFT, padx=2, pady=5)

        # Separator
        tk.Frame(self.toolbar, width=1, bg="grey", height=30).pack(side=tk.LEFT, padx=10)

        # Clear button
        self.clear_button = tk.Button(self.toolbar, text="Clear", command=self._clear_canvas)
        self.clear_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Save button
        self.save_button = tk.Button(self.toolbar, text="Save", command=self._save_image)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Open button
        #self.open_button = tk.Button(self.toolbar, text="Open", command=self._open_image)
        #self.open_button.pack(side=tk.LEFT, padx=5, pady=5)

    def _setup_canvas(self):
        self.canvas = tk.Canvas(self.root, bg="white", bd=5, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        # Ensure the canvas size is properly determined before creating the initial PIL image
        self.canvas.update_idletasks() # Update layout to get actual dimensions

        # Initialize PIL image and draw context for drawing_tools
        initial_width = max(1, self.canvas.winfo_width())
        initial_height = max(1, self.canvas.winfo_height())
        self.drawing_tools.pil_image = Image.new("RGB", (initial_width, initial_height), "white")
        self.drawing_tools.draw_context = ImageDraw.Draw(self.drawing_tools.pil_image)


    def _bind_events(self):
        self.canvas.bind("<Button-1>", self.drawing_tools.start_action)
        self.canvas.bind("<B1-Motion>", self.drawing_tools.perform_action)
        self.canvas.bind("<ButtonRelease-1>", self.drawing_tools.end_action)
        self.root.bind("<Configure>", self._on_resize) # Handle window resizing

    def _on_resize(self, event):
        # Resize the PIL image when the canvas size changes
        new_width = self.canvas.winfo_width()
        new_height = self.canvas.winfo_height()

        if new_width > 0 and new_height > 0 and (new_width != self.drawing_tools.pil_image.width or new_height != self.drawing_tools.pil_image.height):
            # Create a new blank image of the new size
            new_pil_image = Image.new("RGB", (new_width, new_height), "white")
            new_draw_context = ImageDraw.Draw(new_pil_image)

            # Redraw existing canvas content onto the new PIL image
            self._redraw_canvas_to_pil(new_draw_context)

            # Update drawing_tools with the new image and context
            self.drawing_tools.update_image_context(new_pil_image, new_draw_context)


    def _redraw_canvas_to_pil(self, target_draw_context):
        # This is a simplified approach. A more robust solution would store drawing commands
        # rather than redrawing from the canvas objects.
        # For basic lines and shapes, we can iterate through canvas items.
        for item_id in self.canvas.find_all():
            if "drawn_item" in self.canvas.gettags(item_id):
                item_type = self.canvas.type(item_id)
                coords = self.canvas.coords(item_id)
                fill_color = self.canvas.itemcget(item_id, "fill")
                outline_color = self.canvas.itemcget(item_id, "outline")
                width = int(self.canvas.itemcget(item_id, "width"))

                if item_type == "line":
                    target_draw_context.line(coords, fill=fill_color, width=width)
                elif item_type == "rectangle":
                    target_draw_context.rectangle(coords, outline=outline_color, width=width)
                elif item_type == "oval": # Circles are drawn as ovals
                    target_draw_context.ellipse(coords, outline=outline_color, width=width)


    def _choose_color(self):
        color_code = colorchooser.askcolor(title="Choose pen color")
        if color_code[1]: # color_code[1] is the hex code
            self.drawing_tools.set_color(color_code[1])

    def _clear_canvas(self):
        self.canvas.delete("all")
        # Reset the PIL image as well
        new_pil_image = Image.new("RGB", (self.canvas.winfo_width(), self.canvas.winfo_height()), "white")
        new_draw_context = ImageDraw.Draw(new_pil_image)
        self.drawing_tools.update_image_context(new_pil_image, new_draw_context)


    def _save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                  filetypes=[("PNG files", "*.png"),
                                                             ("JPEG files", "*.jpg"),
                                                             ("All files", "*.*")])
        if file_path:
            try:
                # Get the current drawing from the PIL image managed by drawing_tools
                img_to_save = self.drawing_tools.pil_image

                # If canvas size changed, ensure PIL image matches for saving
                if img_to_save.width != self.canvas.winfo_width() or img_to_save.height != self.canvas.winfo_height():
                    # Create a temporary image of the correct canvas size
                    temp_img = Image.new("RGB", (self.canvas.winfo_width(), self.canvas.winfo_height()), "white")
                    temp_draw = ImageDraw.Draw(temp_img)
                    self._redraw_canvas_to_pil(temp_draw)
                    img_to_save = temp_img

                img_to_save.save(file_path)
                messagebox.showinfo("Save Image", "Image saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save image: {e}")

    def _open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp"),
                                                          ("All files", "*.*")])
        if file_path:
            try:
                img_pil = Image.open(file_path)
                self.canvas.delete("all") # Clear current canvas

                # Resize image to fit the current canvas dimensions
                canvas_width = self.canvas.winfo_width()
                canvas_height = self.canvas.winfo_height()
                img_pil = img_pil.resize((canvas_width, canvas_height), Image.LANCZOS)

                # Update PIL image and draw context in drawing_tools
                new_draw_context = ImageDraw.Draw(img_pil)
                self.drawing_tools.update_image_context(img_pil, new_draw_context)

                # Convert PIL image to Tkinter PhotoImage and display
                self.photo_image = ImageTk.PhotoImage(img_pil) # Store reference
                self.canvas.create_image(0, 0, image=self.photo_image, anchor=tk.NW, tags="drawn_item")
                messagebox.showinfo("Open Image", "Image opened successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open image: {e}")