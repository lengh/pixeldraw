import tkinter as tk
from tkinter import filedialog, colorchooser
from PIL import Image, ImageDraw
import json



def refresh_miniature_ui():
    for idx, layer in enumerate(layers):
        if layer == active_layer:
            layer.miniature_canvas.config(bg="cyan")
        else:
            layer.miniature_canvas.config(bg="white")
        layer.miniature_canvas.grid(row=0, column=idx)

# Added this function to paint the canvas with the alternating grays
def paint_alternating_bg(canvas, width, height, cell_size):
    colors = ["#D3D3D3", "#A0A0A0"]
    for i in range(0, width, cell_size * 2):  # Increment by 2 * cell_size for each iteration
        for j in range(0, height, cell_size):
            if (j // cell_size) % 2 == 0:  # Only alternate colors on even rows
                canvas.create_rectangle(i, j, i+cell_size, j+cell_size, fill=colors[0], outline="")
                canvas.create_rectangle(i + cell_size, j, i+2*cell_size, j+cell_size, fill=colors[1], outline="")
            else:  # Reverse colors on odd rows
                canvas.create_rectangle(i, j, i+cell_size, j+cell_size, fill=colors[1], outline="")
                canvas.create_rectangle(i + cell_size, j, i+2*cell_size, j+cell_size, fill=colors[0], outline="")


class Layer:
    def __init__(self, root, display_canvas, miniature_frame, width, height, update_layer_visibility_func, cell_size=20):
        self.cell_size = cell_size
        self.root = root
        self.canvas = tk.Canvas(root, width=width, height=height, bg=None)
        self.display_canvas = display_canvas
        self.data = {}
        self.update_layer_visibility = update_layer_visibility_func
        self.create_miniature(miniature_frame, len(layers))

    def draw_pixel(self, x, y, color):
        self.data[(x, y)] = color
        self.display_canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=color, outline="grey", tags="pixel")
        self.update_miniature()

    def hide(self):
        self.canvas.place_forget()

    def show(self):
        self.canvas.place(x=0, y=0)

    def draw_on_display(self):
        for (x, y), color in self.data.items():
            self.display_canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, fill=color, outline="grey", tags="pixel")

    def create_miniature(self, frame, layer_count):
        self.miniature_canvas = tk.Canvas(frame, width=100, height=75, bg="white", bd=2, relief="ridge", cursor="hand2")
        self.miniature_canvas.grid(row=0, column=layer_count)
        self.miniature_canvas.bind("<Button-1>", self.on_miniature_click)
        self.miniature_canvas.bind("<ButtonRelease-1>", self.on_miniature_release)
        self.miniature_canvas.bind("<B1-Motion>", self.on_miniature_drag)

    def update_layer_visibility():
        display_canvas.delete("pixel")
        if show_all_layers.get():
            for i, layer in enumerate(layers):
                if i <= layers.index(active_layer):
                    layer.draw_on_display()
        else:
            active_layer.draw_on_display()
        create_grid(display_canvas, active_layer.cell_size)    

    def on_miniature_drag(self, event):
        global active_layer
        widget_under_cursor = self.root.winfo_containing(event.x_root, event.y_root)

        # Check if the widget_under_cursor is a child of miniature_frame
        if widget_under_cursor not in miniature_frame.winfo_children():
            return

        if widget_under_cursor == self.miniature_canvas:
            return

        target_idx = miniature_frame.winfo_children().index(widget_under_cursor)
        self_idx = miniature_frame.winfo_children().index(self.miniature_canvas)
        if target_idx != self_idx:
            # Swap layers in the 'layers' list
            layers[self_idx], layers[target_idx] = layers[target_idx], layers[self_idx]
            
            # Update the display order of miniatures
            refresh_miniature_ui()
            update_layer_visibility()

    def on_miniature_release(self, event):
        global active_layer
        widget_under_cursor = self.root.winfo_containing(event.x_root, event.y_root)
        if widget_under_cursor != self.miniature_canvas:
            self.miniature_canvas.config(bg="white")
            return
        if self != active_layer:
            active_layer = self
            self.update_layer_visibility_func()

    def update_miniature(self):
        self.miniature_canvas.delete("all")
        for (x, y), color in self.data.items():
            self.miniature_canvas.create_rectangle(x/8, y/8, (x + self.cell_size)/8, (y + self.cell_size)/8, fill=color, outline="grey")

    def on_miniature_click(self, event):
        global active_layer
        if self != active_layer:
            active_layer = self
            self.update_layer_visibility_func()
            refresh_miniature_ui() 


    def export_layer(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            with open(filename, 'w') as file:
                json.dump(self.data, file)

    def import_layer(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            with open(filename, 'r') as file:
                self.data = json.load(file)
                for (x, y), color in self.data.items():
                    self.draw_pixel(int(x), int(y), color)

    
def create_grid(canvas, cell_size=20):
    canvas.delete("grid_line")
    for x in range(0, canvas.winfo_width(), cell_size):
        canvas.create_line(x, 0, x, canvas.winfo_height(), fill="grey", tags="grid_line")
    for y in range(0, canvas.winfo_height(), cell_size):
        canvas.create_line(0, y, canvas.winfo_width(), y, fill="grey", tags="grid_line")


def export_as_image(layers, width, height):
    # Ignore the background when exporting
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if filename:
        image = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(image)
        for layer in layers:
            for (x, y), color in layer.data.items():
                draw.rectangle([x, y, x + layer.cell_size, y + layer.cell_size], fill=color)
        image.save(filename)



def main():
    global active_layer, layers, miniature_frame
    root = tk.Tk()
    current_tool = tk.StringVar(value="pen")
    root.title("Pixel Art Creator with Layers")

    # Creating the top button frame
    top_container = tk.Frame(root)
    top_container.pack(pady=10)

    def choose_color():
        color = colorchooser.askcolor(title="Choose a color")[1]
        if color:
            chosen_color.set(color)

    btn_choose_color = tk.Button(top_container, text="Choose Color", command=choose_color)
    btn_choose_color.pack(side="left", padx=10)

    def add_new_layer():
        new_layer = Layer(root, display_canvas, miniature_frame, width, height, update_layer_visibility)
        layers.append(new_layer)
        change_active_layer(1)
        update_layer_visibility()

    btn_new_layer = tk.Button(top_container, text="New Layer", command=add_new_layer)
    btn_new_layer.pack(side="left", padx=10)

    btn_prev_layer = tk.Button(top_container, text="Previous Layer", command=lambda: change_active_layer(-1))
    btn_prev_layer.pack(side="left", padx=10)

    btn_next_layer = tk.Button(top_container, text="Next Layer", command=lambda: change_active_layer(1))
    btn_next_layer.pack(side="left", padx=10)

    btn_export_img = tk.Button(top_container, text="Export Image", command=lambda: export_as_image(layers, width, height))
    btn_export_img.pack(side="left", padx=10)

    def update_layer_visibility():
        display_canvas.delete("pixel")
        if show_all_layers.get():
            for i, layer in enumerate(layers):
                if i <= layers.index(active_layer):
                    layer.draw_on_display()
        else:
            active_layer.draw_on_display()
        create_grid(display_canvas, active_layer.cell_size)

    show_all_layers = tk.BooleanVar(value=False)
    chk_show_all_layers = tk.Checkbutton(top_container, text="Show All Previous Layers", variable=show_all_layers, command=update_layer_visibility)
    chk_show_all_layers.pack(side="left", padx=10)

    width, height = 800, 600
    chosen_color = tk.StringVar(value="black")
    display_canvas = tk.Canvas(root, width=width, height=height, bg='#D3D3D3')
    display_canvas.pack(pady=20)


    bottom_container = tk.Frame(root)
    bottom_container.pack(pady=10)
     # Tool frame
    tool_frame = tk.Frame(bottom_container)
    tool_frame.pack(side="left", padx=10)

    # Create buttons for each tool
    btn_pen = tk.Radiobutton(tool_frame, text="Pen", variable=current_tool, value="pen")
    btn_pen.pack(side="left", padx=5)
    
    btn_selector = tk.Radiobutton(tool_frame, text="Selector", variable=current_tool, value="selector")
    btn_selector.pack(side="left", padx=5)
    
    btn_eraser = tk.Radiobutton(tool_frame, text="Eraser", variable=current_tool, value="eraser")
    btn_eraser.pack(side="left", padx=5)
    
    btn_bucket = tk.Radiobutton(tool_frame, text="Bucket", variable=current_tool, value="bucket")
    btn_bucket.pack(side="left", padx=5)

    
    
    miniature_frame = tk.Frame(bottom_container)
    miniature_frame.pack(side="left", padx=10)

    layers = []

    

    first_layer = Layer(root, display_canvas, miniature_frame, width, height, update_layer_visibility)
    layers.append(first_layer)
    active_layer = layers[0]
    first_layer.miniature_canvas.config(bg="cyan")

    def on_canvas_click_or_drag(event, color="black"):
        if current_tool.get() == "pen":
            cell_size = active_layer.cell_size
            x, y = event.x - event.x % cell_size, event.y - event.y % cell_size
            active_layer.draw_pixel(x, y, color)
            update_layer_visibility()
        elif current_tool.get() == "eraser":
            cell_size = active_layer.cell_size
            x, y = event.x - event.x % cell_size, event.y - event.y % cell_size
            # Remove from the data dict and refresh
            active_layer.data.pop((x, y), None)
            update_layer_visibility()

    def bind_events_to_active_layer():
        display_canvas.bind("<Button-1>", lambda event: on_canvas_click_or_drag(event, color=chosen_color.get()))
        display_canvas.bind("<B1-Motion>", lambda event: on_canvas_click_or_drag(event, color=chosen_color.get()))

    def on_canvas_click_or_drag(event, color="black"):
        cell_size = active_layer.cell_size
        x, y = event.x - event.x % cell_size, event.y - event.y % cell_size
        active_layer.draw_pixel(x, y, color)
        update_layer_visibility()

    bind_events_to_active_layer()
    paint_alternating_bg(display_canvas, width, height, first_layer.cell_size)

    def change_active_layer(direction):
        global active_layer
        idx = layers.index(active_layer)
        idx = (idx + direction) % len(layers)
        active_layer = layers[idx]
        update_layer_visibility()
        refresh_miniature_ui()

    root.mainloop()

if __name__ == "__main__":
    main()