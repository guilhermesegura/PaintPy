import tkinter as tk
from PIL import ImageDraw

class DrawingTools:
    def __init__(self, canvas, pil_image, draw_context):
        self.canvas = canvas
        self.pil_image = pil_image
        self.draw_context = draw_context
        self.pen_color = "black"
        self.pen_size = 2
        self.tool = "pen"  # Current active tool (pen, eraser, line, rectangle, circle)
        self.start_x, self.start_y = None, None
        self.current_drawing_id = None # To store ID of temporary shapes

    def set_color(self, color):
        self.pen_color = color

    def set_size(self, size):
        self.pen_size = int(size)

    def set_tool(self, tool_name):
        self.tool = tool_name
        self.canvas.config(cursor="crosshair" if tool_name in ["pen", "eraser", "line", "rectangle", "circle"] else "arrow")

    def start_action(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.tool in ["line", "rectangle", "circle"]:
            # Delete any previous temporary shape
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id)
            # Placeholder for the new temporary shape
            self.current_drawing_id = None

    def perform_action(self, event):
        x, y = event.x, event.y
        if self.tool == "pen":
            if self.start_x is not None and self.start_y is not None:
                self.canvas.create_line(self.start_x, self.start_y, x, y,
                                        fill=self.pen_color, width=self.pen_size,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([self.start_x, self.start_y, x, y],
                                       fill=self.pen_color, width=self.pen_size)
            self.start_x, self.start_y = x, y
        elif self.tool == "eraser":
            if self.start_x is not None and self.start_y is not None:
                # Eraser draws a white line on canvas and PIL image
                self.canvas.create_line(self.start_x, self.start_y, x, y,
                                        fill="white", width=self.pen_size * 2, # Thicker for eraser
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([self.start_x, self.start_y, x, y],
                                       fill="white", width=self.pen_size * 2)
            self.start_x, self.start_y = x, y
        elif self.tool == "line":
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id)
            self.current_drawing_id = self.canvas.create_line(self.start_x, self.start_y, x, y,
                                                               fill=self.pen_color, width=self.pen_size,
                                                               tags="temp_shape")
        elif self.tool == "rectangle":
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id)
            self.current_drawing_id = self.canvas.create_rectangle(self.start_x, self.start_y, x, y,
                                                                   outline=self.pen_color, width=self.pen_size,
                                                                   tags="temp_shape")
        elif self.tool == "circle":
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id)
            # Calculate bounding box for the circle/oval
            bbox = [min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)]
            self.current_drawing_id = self.canvas.create_oval(bbox[0], bbox[1], bbox[2], bbox[3],
                                                              outline=self.pen_color, width=self.pen_size,
                                                              tags="temp_shape")

    def end_action(self, event):
        x, y = event.x, event.y
        if self.tool == "line":
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id) # Remove temporary line
            self.canvas.create_line(self.start_x, self.start_y, x, y,
                                    fill=self.pen_color, width=self.pen_size,
                                    capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
            self.draw_context.line([self.start_x, self.start_y, x, y],
                                   fill=self.pen_color, width=self.pen_size,
                                   joint="curve") # Use joint="curve" for smooth PIL lines
        elif self.tool == "rectangle":
            bbox = [min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)]
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id) # Remove temporary rectangle
            self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3],
                                        outline=self.pen_color, width=self.pen_size, tags="drawn_item")
            self.draw_context.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]],
                                        outline=self.pen_color, width=self.pen_size)
        elif self.tool == "circle":
            if self.current_drawing_id:
                self.canvas.delete(self.current_drawing_id) # Remove temporary circle
            bbox = [min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)]
            self.canvas.create_oval(bbox[0], bbox[1], bbox[2], bbox[3],
                                   outline=self.pen_color, width=self.pen_size, tags="drawn_item")
            self.draw_context.ellipse([bbox[0], bbox[1], bbox[2], bbox[3]],
                                      outline=self.pen_color, width=self.pen_size)

        self.start_x, self.start_y = None, None
        self.current_drawing_id = None # Reset after drawing permanent shape


    def update_image_context(self, new_pil_image, new_draw_context):
        """Updates the internal PIL image and draw context when the canvas is cleared or image is opened."""
        self.pil_image = new_pil_image
        self.draw_context = new_draw_context