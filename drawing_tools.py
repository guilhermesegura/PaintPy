import tkinter as tk
from PIL import ImageDraw, Image, ImageFont, ImageTk
from tkinter import messagebox
import peer



class DrawingTools:
    def __init__(self, canvas, pil_image, draw_context, peer):
        self.canvas = canvas
        self.pil_image = pil_image
        self.draw_context = draw_context
        self.pen_color = "#000000"
        self.pen_size = 2 # Also used for text size
        self.tool = "pen"

        self.start_x, self.start_y = None, None

        # --- For shape previews (same as before) ---
        self.temp_pil_image = None
        self.temp_draw_context = None
        self.temp_tk_image = None
        self.temp_tk_image_id = None

        # --- For text tool ---
        self.text_entry_widget = None
        self.text_entry_canvas_id = None
        self.text_font = "Arial" # Default font
        self.text_color = "#000000" # Default text color

        self.peer = peer

    def set_color(self, color):
        self.pen_color = color
        self.text_color = color # Text color also changes with pen color

    def set_size(self, size):
        self.pen_size = int(size) # Pen size also affects text size

    def set_tool(self, tool_name):
        # Clean up any active temporary tools before switching
        self._cleanup_temp_tools()

        self.tool = tool_name
        self.canvas.config(cursor="crosshair" if tool_name in ["pen", "eraser", "line", "rectangle", "circle", "text"] else "arrow")
        self.start_x, self.start_y = None, None

    def _cleanup_temp_tools(self):
        # Clean up shape preview
        if self.temp_tk_image_id:
            self.canvas.delete(self.temp_tk_image_id)
            self.temp_tk_image_id = None
        self.temp_tk_image = None
        self.temp_pil_image = None
        self.temp_draw_context = None

        # Clean up text entry widget
        if self.text_entry_widget:
            self.text_entry_widget.destroy()
            self.text_entry_widget = None
        if self.text_entry_canvas_id:
            self.canvas.delete(self.text_entry_canvas_id)
            self.text_entry_canvas_id = None


    def start_action(self, event):
        self.start_x, self.start_y = event.x, event.y

        if self.tool in ["line", "rectangle", "circle"]:
            self._cleanup_temp_tools() # Ensure no text entry or other shapes are active
            self.temp_pil_image = self.pil_image.copy()
            self.temp_draw_context = ImageDraw.Draw(self.temp_pil_image)
            # No need to create temp_tk_image_id here, it's created in perform_action

        elif self.tool == "text":
            self._cleanup_temp_tools() # Ensure no shapes are active
            # Create a Tkinter Entry widget at the clicked position
            self.text_entry_widget = tk.Entry(self.canvas, bg="lightgrey", fg=self.text_color,
                                              font=(self.text_font, self.pen_size))
            self.text_entry_canvas_id = self.canvas.create_window(event.x, event.y,
                                                                  window=self.text_entry_widget,
                                                                  anchor=tk.NW, tags="temp_text_entry")
            self.text_entry_widget.focus_set()
            # Bind Return key to finalize text
            self.text_entry_widget.bind("<Return>", self._finalize_text)
            # Bind Escape key to cancel text entry
            self.text_entry_widget.bind("<Escape>", self._cancel_text_entry)


    def apply_remote_action(self, message):
        try:
            parts = message.split(':')
            tool = parts[1].strip()
            color = parts[2]
            size = int(parts[3])
            x1 = int(parts[4])
            y1 = int(parts[5])
            x2 = parts[6]
            y2 = parts[7]
            extra_data = parts[8]
            if tool != "text":
                size = int(size)
                x2 = int(x2)
                y2 = int(y2)

            if tool == "line":

                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=size,
                                            capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([x1, y1, x2, y2], fill=color, width=size, joint="curve")

            elif tool == "rectangle":

                bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                self.draw_context.rectangle(bbox, outline=color, width=size)
                self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3],
                                             outline=color, width=size, tags="drawn_item")

            elif tool == "circle":

                bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                self.canvas.create_oval(bbox, outline=color, width=size, tags="drawn_item")
                self.draw_context.ellipse(bbox, outline=color, width=size)

            elif tool == "pen":
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=size,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([x1, y1, x2, y2], fill=color, width=size, joint="curve")

            elif tool == "eraser":

                self.canvas.create_line(x1, y1, x2, y2, fill="white", width=size * 2,
                                       capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([x1, y1, x2, y2], fill="white", width=size * 2, joint="curve")

            elif tool == "text":

                text_content = extra_data
                if text_content:
                    font_size = max(1, size)
                    try:
                        pil_font = ImageFont.truetype(self.text_font, font_size)
                    except IOError:
                        pil_font = ImageFont.load_default()

                    self.canvas.create_text(x1, y1, text=text_content, anchor=tk.NW,
                                            font=(self.text_font, font_size),  fill=color, tags="drawn_item")
                    self.draw_context.text((x1, y1), text=text_content, font=pil_font, fill=color)

        except Exception as e:
            print(f"Erro ao aplicar ação remota: {e}. Mensagem: '{message}'")


    def perform_action(self, event):
        x, y = event.x, event.y
        if self.start_x is None or self.start_y is None:
            return
        if self.tool in ["pen", "eraser"]:
            string_data = ""
            if self.tool == "pen":
                self.canvas.create_line(self.start_x, self.start_y, x, y,
                                        fill=self.pen_color, width=self.pen_size,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([self.start_x, self.start_y, x, y],
                                       fill=self.pen_color, width=self.pen_size, joint="curve")
                string_data = [self.tool, self.pen_color, str(self.pen_size), str(self.start_x), str(self.start_y), str(x), str(y), '']
                self.start_x, self.start_y = x, y
            elif self.tool == "eraser":
                self.canvas.create_line(self.start_x, self.start_y, x, y,
                                        fill="white", width=self.pen_size * 2,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                self.draw_context.line([self.start_x, self.start_y, x, y],
                                       fill="white", width=self.pen_size * 2, joint="curve")
                string_data = [self.tool, self.pen_color, str(self.pen_size), str(self.start_x), str(self.start_y), str(x), str(y), '']
                self.start_x, self.start_y = x, y
            msg = ":".join(string_data)
            self.peer.broadcast(msg)

        elif self.tool in ["line", "rectangle", "circle"]:
            if self.temp_pil_image and self.temp_draw_context:
                self.temp_pil_image = self.pil_image.copy() # Reset temp_pil_image to original base
                self.temp_draw_context = ImageDraw.Draw(self.temp_pil_image)

                bbox = [min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)]

                if self.tool == "line":
                    self.temp_draw_context.line([self.start_x, self.start_y, x, y],
                                                fill=self.pen_color, width=self.pen_size, joint="curve")
                elif self.tool == "rectangle":
                    self.temp_draw_context.rectangle(bbox, outline=self.pen_color, width=self.pen_size)
                elif self.tool == "circle":
                    self.temp_draw_context.ellipse(bbox, outline=self.pen_color, width=self.pen_size)

                if self.temp_tk_image_id:
                    self.canvas.delete(self.temp_tk_image_id)

                self.temp_tk_image = ImageTk.PhotoImage(self.temp_pil_image)
                self.temp_tk_image_id = self.canvas.create_image(0, 0, image=self.temp_tk_image, anchor=tk.NW, tags="temp_preview")
        # Text tool does not use perform_action for dragging

    def end_action(self, event):
        x, y = event.x, event.y
        string_data = ""
        if self.start_x is None or self.start_y is None: # No drawing started
            return

        if self.tool in ["pen", "eraser"]:
            pass # Handled in perform_action
        elif self.tool in ["line", "rectangle", "circle"]:
            if self.temp_tk_image_id:
                self.canvas.delete(self.temp_tk_image_id)
                self.temp_tk_image_id = None
            self.temp_tk_image = None
            self.temp_pil_image = None
            self.temp_draw_context = None

            bbox = [min(self.start_x, x), min(self.start_y, y), max(self.start_x, x), max(self.start_y, y)]

            if self.tool == "line":
                self.draw_context.line([self.start_x, self.start_y, x, y],
                                       fill=self.pen_color, width=self.pen_size, joint="curve")
                self.canvas.create_line(self.start_x, self.start_y, x, y,
                                        fill=self.pen_color, width=self.pen_size,
                                        capstyle=tk.ROUND, smooth=tk.TRUE, tags="drawn_item")
                string_data = [self.tool, self.pen_color, str(self.pen_size), str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]), '']
            elif self.tool == "rectangle":
                self.draw_context.rectangle(bbox, outline=self.pen_color, width=self.pen_size)
                self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3],
                                            outline=self.pen_color, width=self.pen_size, tags="drawn_item")
                string_data = [self.tool, self.pen_color, str(self.pen_size), str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]), '']
            elif self.tool == "circle":
                self.draw_context.ellipse(bbox, outline=self.pen_color, width=self.pen_size)
                self.canvas.create_oval(bbox[0], bbox[1], bbox[2], bbox[3],
                                        outline=self.pen_color, width=self.pen_size, tags="drawn_item")
                string_data = [self.tool, self.pen_color, str(self.pen_size), str(bbox[0]), str(bbox[1]), str(bbox[2]), str(bbox[3]), '']

            msg = ":".join(string_data)
            self.peer.broadcast(msg)

        elif self.tool == "text":
            # For text, the end_action just resets start_x, start_y.
            # The actual text drawing happens when the user presses Enter in the Entry widget.
            pass


        self.start_x, self.start_y = None, None

    def _finalize_text(self, event):
        if not self.text_entry_widget:
            return
        msg = ""
        x, y = "", ""
        text_content = self.text_entry_widget.get()
        if text_content:
            # Get the position of the entry widget on the canvas
            bbox = self.canvas.bbox(self.text_entry_canvas_id)
            if bbox:
                x, y = bbox[0], bbox[1] # Top-left corner of the text entry

                try:
                    # Load font with current size
                    font_size = max(8, self.pen_size) # Minimum font size of 8
                    pil_font = ImageFont.load_default()
                    #pil_font = ImageFont.truetype(self.text_font, font_size)
                except IOError:
                    pil_font = ImageFont.load_default()
                    print(f"Warning: Could not load font {self.text_font}. Using default.")

                # Draw text on the PIL image
                self.draw_context.text((x, y), text_content, font=pil_font, fill=self.text_color)

                # Draw text on the Tkinter canvas (approximation)
                self.canvas.create_text(x, y, text=text_content, anchor=tk.NW,
                                        font=(self.text_font, font_size), fill=self.text_color,
                                        tags="drawn_item")
                string_data = [str(self.tool), str(self.pen_color), str(font_size), str(x), str(y), '', '', str(text_content)]
                msg = ":".join(string_data)

                if self.peer:
                    self.peer.broadcast(msg)

            self._cleanup_temp_tools() # Remove the entry widget


    def _cancel_text_entry(self, event):
        self._cleanup_temp_tools() # Just remove the entry widget

    def update_image_context(self, new_pil_image, new_draw_context):
        """Updates the internal PIL image and draw context when the canvas is cleared or image is opened."""
        self.pil_image = new_pil_image
        self.draw_context = new_draw_context
        self._cleanup_temp_tools() # Clear any temporary previews or text entries

    def clear_canvas(self):
        self.canvas.delete("all")
        new_pil_image = Image.new("RGB", (self.canvas.winfo_width(), self.canvas.winfo_height()), "white")
        new_draw_context = ImageDraw.Draw(new_pil_image)
        self.update_image_context(new_pil_image, new_draw_context)

    def send_clear(self):
        msg = "clear:" + self.peer.username
        self.peer.broadcast(msg)