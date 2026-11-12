import ttkbootstrap as tb
from tkinter import Canvas
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import heapq
import json

rows = 50
columns = 50
cell_size = 15
map_width = columns * cell_size
map_height = rows * cell_size




stairs = {(0,11,49): (1,11,49),(1,11,49): (0, 11, 49)}

with open("locations.json", "r") as f:
    locations = json.load(f)

locations = {
    name: tuple(coords)
    for name, coords in locations.items()}

with open("settings.json", "r") as f:
    settings = json.load(f)

line_colour = settings["line_colour"]
line_width = settings["line_width"]

if settings["grid_visible"] == True:
    grid_state = "gray"
else:
    grid_state = ""
print(line_colour,line_width,grid_state)

obstacle_colours = [(207, 196, 179),(225, 212, 187),(0, 0, 0)]
corridor_colours = [(255, 255, 255)]

def is_obstacle(pixel):
    r, g, b = pixel
    for colour in obstacle_colours:
        cr, cg, cb = colour

        if (abs(r - cr) <= 10 and abs(g - cg) <= 10) and abs(b - cb) <= 10:
            return True

    return False

def is_corridor(pixel):
    r, g, b = pixel
    for colour in corridor_colours:
        cr, cg, cb = colour
        if (abs(r - cr) <= 10 and abs(g - cg) <= 10 and abs(b - cb) <= 10):
            return True

    return False
floor_images = []

for file_location in settings["floor_images"]:
    image = Image.open(file_location).convert("RGB")
    image = image.resize((map_width, map_height))
    floor_images.append(image)



def create_grid(image):
    grid = []

    cell_width = image.width / columns
    cell_height = image.height / rows

    for row in range(rows):
        grid_row = []
        for column in range(columns):
            start_x = int(column * cell_width)
            end_x = int((column + 1) * cell_width)
            start_y = int(row * cell_height)
            end_y = int((row + 1) * cell_height)

            obstacle_pixels = 0
            corridor_pixels = 0
            total_pixels = 0

            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    pixel = image.getpixel((x, y))
                    total_pixels += 1

                    if is_obstacle(pixel):
                        obstacle_pixels += 1

                    if is_corridor(pixel):
                        corridor_pixels += 1

            if total_pixels > 0:
                obstacle_percentage = (obstacle_pixels / total_pixels) * 100
                corridor_percentage = (corridor_pixels / total_pixels) * 100
            else:
                obstacle_percentage = 0
                corridor_percentage = 0

            if corridor_percentage >= 20:
                grid_row.append(0)
            elif obstacle_percentage >= 20:
                grid_row.append(1)
            else:
                grid_row.append(0)

        grid.append(grid_row)

    return grid


grid = []

for image in floor_images:
    grid.append(create_grid(image))


def dijkstra(start, finish):
    previous = {}
    distances = {start: 0}
    queue = [(0, start)]

    for floor, row, column in (start, finish):
        if not (0 <= floor < len(grid)):
            return None
        if not (0 <= row < rows and 0 <= column < columns):
            return None

        if grid[floor][row][column] == 1:
            return None

    while queue:
        current_distance, current = heapq.heappop(queue)

        if current_distance > distances[current]:
            continue

        if current == finish:
            break

        floor, row, column = current

        neighbours = [
            (floor, row - 1, column),
            (floor, row + 1, column),
            (floor, row, column - 1),
            (floor, row, column + 1),
            (floor, row - 1, column - 1),
            (floor, row - 1, column + 1),
            (floor, row + 1, column - 1),
            (floor, row + 1, column + 1)
        ]
        if current in stairs:
            neighbours.append(stairs[current])


        for neighbour in neighbours:
            f, r, c = neighbour

            if not (0 <= f < len(grid)):
                continue

            if r < 0 or r >= rows:
                continue

            if c < 0 or c >= columns:
                continue

            if grid[f][r][c] == 1:
                continue
            if f!= floor:
                movement_cost = 1

            elif r != row and c != column:
                if grid[floor][row][c] == 1:
                    continue

                if grid[floor][r][column] == 1:
                    continue

                movement_cost = 1.414
            else:
                movement_cost = 1

            new_distance = current_distance + movement_cost

            if new_distance < distances.get(neighbour, float("inf")):
                distances[neighbour] = new_distance
                previous[neighbour] = current

                heapq.heappush(queue, (new_distance, neighbour))

    if finish not in distances:
        return None
    path = []
    current = finish
    while current != start:
        path.append(current)
        current = previous[current]

    path.append(start)
    path.reverse()
    return distances[finish], path



root = tb.Window(themename=settings["theme"])
root.minsize(1000, 850)
root.title("School Pathfinder")

root.geometry("1000x850")
main_page = tb.Frame(root)
main_page.pack(fill="both", expand=True)


map_images = []

for image in floor_images:
    map_images.append(ImageTk.PhotoImage(image))


control_frame = tb.Frame(main_page)

control_frame.pack(pady=15)

tb.Label(control_frame,text="Start:").pack(side="left",padx=5)


start_box = tb.Combobox(control_frame,values=list(locations.keys()),state="readonly",width=20)

start_box.pack(side="left",padx=5)


tb.Label(control_frame,text="Destination:").pack(side="left",padx=5)


end_box = tb.Combobox(control_frame,values=list(locations.keys()),state="readonly",width=20)

end_box.pack(side="left",padx=5)

def show_coordinates(event):
    column = event.x // cell_size
    row = event.y // cell_size
    selected_floor = floor_box.current()
    coordinates_label.config(text=f"Coordinates: Floor {selected_floor}, Row {row}, Column {column}")


canvas = Canvas(main_page,width=map_width,height=map_height,bg="white")
canvas.pack()

coordinates_label = tb.Label(main_page, text="Coordinates: Floor 0, Row 0, Column 0")
coordinates_label.pack(pady=5)

canvas.bind("<Motion>", show_coordinates)

def draw_grid():


    selected_floor = floor_box.current()
    canvas.delete("all")
    canvas.create_image(0,0,anchor="nw",image=map_images[selected_floor])

    for row in range(rows):

        for column in range(columns):

            x1 = column * cell_size
            y1 = row * cell_size

            x2 = x1 + cell_size
            y2 = y1 + cell_size

            canvas.create_rectangle(x1,y1,x2,y2,fill="",outline=grid_state,width=1)

def draw_path(path):

    if not path:
        return

    selected_floor = floor_box.current()
    for i in range(len(path) - 1):
        floor1, row1, column1 = path[i]
        floor2, row2, column2 = path[i + 1]

        if floor1 != selected_floor:
            continue
        if floor1 != floor2:
            continue

        x1 = (column1 * cell_size + cell_size / 2)
        y1 = (row1 * cell_size+ cell_size / 2)
        x2 = (column2 * cell_size+ cell_size / 2)
        y2 = (row2 * cell_size+ cell_size / 2)

        canvas.create_line(x1,y1,x2,y2,fill=line_colour,width=line_width)
def draw_locations():
    selected_location = floor_box.current()
    for name, (floor, row, column) in locations.items():
        if floor != selected_location:
            continue
        x = column * cell_size + cell_size / 2
        y = row * cell_size + cell_size / 2


        canvas.create_oval(x - 6,y - 6,x + 6,y + 6,fill="blue",outline="white",width=1)


def calculate_path():
    global current_path
    start_name = start_box.get()
    end_name = end_box.get()


    if not start_name or not end_name:
        return


    if start_name == end_name:
        return


    start = locations[start_name]
    end = locations[end_name]

    result = dijkstra(start,end)

    draw_grid()
    if result is None:
        draw_locations()
        return
    distance, path = result
    current_path = path
    draw_path(path)
    draw_locations()
    print(distance)
current_path = []

def redraw_floor(event=None):
    draw_grid()
    draw_path(current_path)
    draw_locations()


def open_settings():
    main_page.pack_forget()
    settings_page.pack(fill="both", expand=True)

def open_main_page():
    settings_page.pack_forget()
    main_page.pack(fill="both", expand=True)

def change_theme(event=None):
    selected_theme = theme_box.get()
    root.style.theme_use(selected_theme)

def toggle_grid():
    global grid_state
    if grid_state == "":
        grid_state = "gray"
    else:
        grid_state = ""
    draw_grid()

def change_line_colour(event=None):
    global line_colour
    line_colour = color_box.get()

def change_line_width(value):
    global line_width
    line_width = float(value)
    redraw_floor()

def floor_names():
    names = []
    for i in range(len(floor_images)):
        if i == 0:
            names.append("Ground Floor")
        else:
            names.append(f"Floor {i}")
    return names

def save_location():
    with open("locations.json", "w") as f:
        json.dump(locations, f, indent=4)
def add_location():
    name = location_name_box.get()
    floor = location_floor_box.current()

    try:
        row = int(location_row_box.get())
        column = int(location_column_box.get())
    except ValueError:
        messagebox.showerror("Error", "Row and Column must be integers.")
        return
    locations[name] = (floor, row, column)
    save_location()

    start_box["values"] = list(locations.keys())
    end_box["values"] = list(locations.keys())

    location_name_box.delete(0, "end")
    location_row_box.delete(0, "end")
    location_column_box.delete(0, "end")

    redraw_floor()



def add_floor():
    file_path = filedialog.askopenfilename(filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])

    if not file_path:
        return
    try:
        image = Image.open(file_path).convert("RGB")
        image = image.resize((map_width, map_height))
    except (OSError, ValueError) as e:
        messagebox.showerror("Error", f"Failed to open image: {e}")
        return

    floor_images.append(image)
    grid.append(create_grid(image))
    map_images.append(ImageTk.PhotoImage(image))

    settings["floor_images"].append(file_path)

    floor_box["values"] = floor_names()

    save_settings()

def change_floor():
    selected_floor = floor_box.current()
    file_path = filedialog.askopenfilename(filetypes=[("Image File", "*.png;*.jpg;*.jpeg")])

    if not file_path:
        return
    try:
        image = Image.open(file_path).convert("RGB")
        image = image.resize((map_width, map_height))
    except (OSError, ValueError) as e:
        messagebox.showerror("Error", f"Failed to open image: {e}")
        return

    floor_images[selected_floor] = image
    grid[selected_floor] = create_grid(image)
    map_images[selected_floor] = ImageTk.PhotoImage(image)

    settings["floor_images"][selected_floor] = file_path

    current_path.clear()
    save_settings()
    redraw_floor()

def save_settings():
    settings["theme"] = root.style.theme_use()
    settings["grid_visible"] = grid_state == "gray"
    settings["line_colour"] = line_colour
    settings["line_width"] = line_width

    with open("settings.json", "w") as f:
        json.dump(settings, f, indent=4)

settings_page = tb.Frame(root)
header_frame = tb.Frame(settings_page)
header_frame.pack(fill="x", pady=10)

tb.Label(header_frame, text="Settings", font=("Arial", 16)).pack(padx=10,side="left")
tb.Button(header_frame, text="Back", command=open_main_page, bootstyle="info").pack(side="right", padx=10)

theme_frame = tb.Frame(settings_page)
theme_frame.pack(pady=10)

tb.Label(theme_frame, text="Select Theme:").pack(pady=10,side ="left",padx=10)
theme_box = tb.Combobox(theme_frame, values=root.style.theme_names(), state="readonly")
theme_box.set(root.style.theme_use())
theme_box.bind("<<ComboboxSelected>>", change_theme)
theme_box.pack(pady=10,side ="left",padx=10)

grid_frame = tb.Frame(settings_page)
grid_frame.pack(pady=10)

tb.Label(grid_frame, text="Toggle Grid:").pack(pady=10,side ="left",padx=10)
tb.Button(grid_frame, text="Toggle Grid", command=toggle_grid, bootstyle="primary").pack(pady=10,side ="left",padx=10)

line_frame = tb.Frame(settings_page)
line_frame.pack(pady=10)

tb.Label(line_frame, text="Line Color:").pack(pady=10,side ="left",padx=10)
color_box = tb.Combobox(line_frame, values=["lime", "red", "blue","white","black","pink","yellow"], state="readonly")
color_box.set(line_colour)
color_box.bind("<<ComboboxSelected>>", change_line_colour)
color_box.pack(pady=10,side ="left",padx=10)

tb.Label(line_frame, text="Line Width:").pack(pady=10,side ="left",padx=10)
width_box = tb.Scale(line_frame, from_=1, to=10, orient="horizontal", command=change_line_width).pack(pady=10,side ="left",padx=10)

location_frame = tb.Frame(settings_page)
location_frame.pack(pady=10)

tb.Label(location_frame, text="Location Name:").pack(pady=10,side ="left")
location_name_box = tb.Entry(location_frame)
location_name_box.pack(pady=10,side ="left",padx=10)

tb.Label(location_frame, text="Floor:").pack(pady=10,side ="left")
location_floor_box = tb.Combobox(location_frame, values=floor_names(), state="readonly")
location_floor_box.pack(pady=10,side ="left",padx=10)

tb.Label(location_frame, text="Row:").pack(pady=10,side ="left")
location_row_box = tb.Entry(location_frame)
location_row_box.pack(pady=10,side ="left",padx=10)

tb.Label(location_frame, text="Column:").pack(pady=10,side ="left")
location_column_box = tb.Entry(location_frame)
location_column_box.pack(pady=10,side ="left")

tb.Button(location_frame, text="Add Location", command=add_location, bootstyle="primary").pack(pady=10,side ="left",padx=10)

tb.Button(settings_page, text="Add floor image", command=add_floor, bootstyle="primary").pack(pady=10,padx=10)
tb.Button(settings_page, text="Change floor image", command=change_floor, bootstyle="primary").pack(pady=10,padx=10)

tb.Button(settings_page, text="Save Settings", command=save_settings, bootstyle="success").pack(pady=10,padx=10)

tb.Button(control_frame,text="Calculate Path",command=calculate_path,bootstyle="success").pack(side="left",padx=10)
floor_box = tb.Combobox(control_frame, values=floor_names(),state="readonly")
floor_box.current(0)
floor_box.pack(side="left",padx=10)
floor_box.bind("<<ComboboxSelected>>", redraw_floor)
tb.Button(control_frame,text="Settings",command=open_settings,bootstyle="info").pack(side="left",padx=10)
draw_grid()

draw_locations()

root.mainloop()