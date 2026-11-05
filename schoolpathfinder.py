import ttkbootstrap as tb
from tkinter import Canvas
from PIL import Image, ImageTk
import heapq
import json

rows = 50
columns = 50
cell_size = 15
map_width = columns * cell_size
map_height = rows * cell_size

stairs = {(0,1,10): (1,1,10),(1,1,10): (0, 1, 10)}

with open("locations.json", "r") as f:
    locations = json.load(f)

locations = {
    name: tuple(coords)
    for name, coords in locations.items()}

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

ground_image = Image.open("example.png").convert("RGB")
first_image = Image.open("example2.png").convert("RGB")

ground_image = ground_image.resize((map_width, map_height))
first_image = first_image.resize((map_width, map_height))


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


grid = create_grid(ground_image),create_grid(first_image)


def dijkstra(start, finish):
    previous = {}
    distances = {start: 0}
    queue = [(0, start)]

    # Validate start and finish
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



root = tb.Window(
    themename="darkly"
)

root.title(
    "School Pathfinder"
)

root.geometry(
    "1000x750"
)
map_images = [ImageTk.PhotoImage(ground_image),ImageTk.PhotoImage(first_image)]


control_frame = tb.Frame(root)

control_frame.pack(
    pady=15
)

tb.Label(control_frame,text="Start:").pack(side="left",padx=5)


start_box = tb.Combobox(
    control_frame,
    values=list(locations.keys()),
    state="readonly",
    width=20
)

start_box.pack(
    side="left",
    padx=5
)


tb.Label(
    control_frame,text="Destination:"
).pack(side="left",padx=5)


end_box = tb.Combobox(
    control_frame,values=list(locations.keys()),
    state="readonly",
    width=20
)

end_box.pack(
    side="left",
    padx=5
)
canvas = Canvas(
    root,
    width=map_width,
    height=map_height,
    bg="white"
)

canvas.pack()

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

            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="",
                outline="gray",
                width=1
            )

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

        canvas.create_line(x1,y1,x2,y2,fill="lime",width=4)
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

tb.Button(control_frame,text="Calculate Path",command=calculate_path,bootstyle="success").pack(side="left",padx=10)
floor_box = tb.Combobox(control_frame, values=["Ground Floor","First Floor"],state="readonly")
floor_box.current(0)
floor_box.pack(side="left",padx=10)
floor_box.bind("<<ComboboxSelected>>", redraw_floor)
draw_grid()

draw_locations()

root.mainloop()