import ttkbootstrap as tb
from tkinter import Canvas
from PIL import Image, ImageTk
import heapq
import json

ROWS = 50
COLUMNS = 50
CELL_SIZE = 15
MAP_WIDTH = COLUMNS * CELL_SIZE
MAP_HEIGHT = ROWS * CELL_SIZE

with open("locations.json", "r") as f:
    locations = json.load(f)

locations = {
    name: tuple(coords)
    for name, coords in locations.items()
}

obstacle_colours = [
    (207, 196, 179),
    (225, 212, 187),
    (0, 0, 0)
]

corridor_colours = [
    (255, 255, 255)
]

OBSTACLE_PERCENTAGE = 25
def is_obstacle(pixel):

    r, g, b = pixel

    for colour in obstacle_colours:

        cr, cg, cb = colour

        if (
            abs(r - cr) <= 10
            and abs(g - cg) <= 10
            and abs(b - cb) <= 10
        ):
            return True

    return False

def is_corridor(pixel):

    r, g, b = pixel

    for colour in corridor_colours:

        cr, cg, cb = colour

        if (
            abs(r - cr) <= 10
            and abs(g - cg) <= 10
            and abs(b - cb) <= 10
        ):
            return True

    return False

image = Image.open("example.png").convert("RGB")

image = image.resize(
    (MAP_WIDTH, MAP_HEIGHT)
)


original_width = image.width
original_height = image.height

cell_width = original_width / COLUMNS
cell_height = original_height / ROWS

grid = []


for row in range(ROWS):

    grid_row = []

    for column in range(COLUMNS):

        start_x = int(column * cell_width)
        end_x = int((column + 1) * cell_width)

        start_y = int(row * cell_height)
        end_y = int((row + 1) * cell_height)

        total_pixels = 0
        obstacle_pixels = 0
        corridor_pixels = 0

        for y in range(start_y, end_y):

            for x in range(start_x, end_x):

                pixel = image.getpixel((x, y))

                total_pixels += 1

                if is_obstacle(pixel):
                    obstacle_pixels += 1

                if is_corridor(pixel):
                    corridor_pixels += 1

        if total_pixels > 0:

            obstacle_percentage = (
                obstacle_pixels / total_pixels
            ) * 100

            corridor_percentage = (
                corridor_pixels / total_pixels
            ) * 100

        else:

            obstacle_percentage = 0
            corridor_percentage = 0


        if corridor_percentage >= 25:

            grid_row.append(0)

        elif obstacle_percentage >= OBSTACLE_PERCENTAGE:

            grid_row.append(1)

        else:

            grid_row.append(0)


    grid.append(grid_row)

def dijkstra(start, end):

    queue = [
        (0, 0, start)
    ]

    distances = {
        start: (0, 0)
    }

    previous = {}
    directions = {}


    while queue:

        current_distance, turns, current = heapq.heappop(queue)

        row, column = current

        if current not in distances:
            continue

        if (
            current_distance,
            turns
        ) != distances[current]:

            continue

        if current == end:
            break

        neighbours = [

            (row - 1, column),
            (row + 1, column),
            (row, column - 1),
            (row, column + 1),
            (row - 1, column - 1),
            (row - 1, column + 1),
            (row + 1, column - 1),
            (row + 1, column + 1)
        ]


        for neighbour in neighbours:

            r, c = neighbour
            if r < 0 or r >= ROWS:
                continue

            if c < 0 or c >= COLUMNS:
                continue
            if grid[r][c] == 1:
                continue

            if r != row and c != column:

                if grid[row][c] == 1:
                    continue

                if grid[r][column] == 1:
                    continue

            movement_cost = 1

            new_distance = (
                current_distance
                + movement_cost
            )


            new_direction = (
                r - row,
                c - column
            )


            new_turns = turns

            if current in directions:

                old_direction = directions[current]

                if old_direction != new_direction:

                    new_turns += 1
            new_score = (
                new_distance,
                new_turns
            )
            if (
                neighbour not in distances
                or new_score < distances[neighbour]
            ):

                distances[neighbour] = new_score

                previous[neighbour] = current

                directions[neighbour] = new_direction

                heapq.heappush(
                    queue,
                    (
                        new_distance,
                        new_turns,
                        neighbour
                    )
                )

    if (
        start != end
        and end not in previous
    ):

        return []
    path = []

    current = end


    while current != start:

        path.append(current)

        current = previous[current]


    path.append(start)

    path.reverse()

    return path

root = tb.Window(
    themename="darkly"
)

root.title(
    "School Pathfinder"
)

root.geometry(
    "1000x750"
)

map_image = ImageTk.PhotoImage(image)

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
    width=MAP_WIDTH,
    height=MAP_HEIGHT,
    bg="white"
)

canvas.pack()

def draw_grid():

    canvas.delete("all")

    canvas.create_image(
        0,
        0,
        anchor="nw",
        image=map_image
    )

    for row in range(ROWS):

        for column in range(COLUMNS):

            x1 = column * CELL_SIZE
            y1 = row * CELL_SIZE

            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

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


    for i in range(len(path) - 1):

        row1, column1 = path[i]
        row2, column2 = path[i + 1]


        x1 = (
            column1 * CELL_SIZE
            + CELL_SIZE / 2
        )

        y1 = (
            row1 * CELL_SIZE
            + CELL_SIZE / 2
        )


        x2 = (
            column2 * CELL_SIZE
            + CELL_SIZE / 2
        )

        y2 = (
            row2 * CELL_SIZE
            + CELL_SIZE / 2
        )


        canvas.create_line(
            x1,
            y1,
            x2,
            y2,
            fill="lime",
            width=4
        )
def draw_locations():

    for name, (row, column) in locations.items():

        x = (
            column * CELL_SIZE
            + CELL_SIZE / 2
        )

        y = (
            row * CELL_SIZE
            + CELL_SIZE / 2
        )


        canvas.create_oval(
            x - 6,
            y - 6,
            x + 6,
            y + 6,
            fill="blue",
            outline="white",
            width=1
        )


def calculate_path():

    start_name = start_box.get()
    end_name = end_box.get()


    if not start_name or not end_name:
        return


    if start_name == end_name:
        return


    start = locations[start_name]
    end = locations[end_name]

    path = dijkstra(
        start,
        end
    )

    draw_grid()

    draw_path(path)

    draw_locations()

tb.Button(
    control_frame,
    text="Calculate Path",
    command=calculate_path,
    bootstyle="success"
).pack(
    side="left",
    padx=10
)

draw_grid()

draw_locations()

root.mainloop()