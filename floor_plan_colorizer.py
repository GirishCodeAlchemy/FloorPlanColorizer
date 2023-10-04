import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont


class FloorPlanColorizer:
    def __init__(self, floor_plan_file_path):
        # Initialize instance variables
        self.input_file_name = os.path.splitext(os.path.basename(floor_plan_file_path))[0]
        self.output_file_prefix = f"output/{self.input_file_name}"
        self.load_floor_plan(floor_plan_file_path)

    def load_floor_plan(self, floor_plan_file_path):
        # Load and preprocess the floor plan
        floor_plan_text = self.read_floor_plan_from_file(floor_plan_file_path)
        self.floor_plan = self.preprocess_floor_plan(floor_plan_text)
        self.width = len(self.floor_plan[0])
        self.height = len(self.floor_plan)
        self.room_colors = {}
        self.used_colors = set()

    def read_floor_plan_from_file(self, floor_plan_file_path):
        # Read the floor plan from a file
        with open(floor_plan_file_path, 'r') as file:
            return file.read()

    def preprocess_floor_plan(self, floor_plan_text):
        # Preprocess the floor plan text and return a 2D array
        floor_plan_lines = floor_plan_text.strip().split('\n')
        max_width = max(len(line) for line in floor_plan_lines)
        floor_plan = [[' ' if x >= len(line) else line[x] for x in range(max_width)] for line in floor_plan_lines]
        return floor_plan

    def find_rooms(self):
        rooms = []
        visited = set()

        for y in range(self.height):
            for x in range(self.width):
                if self.floor_plan[y][x] == ' ' and (x, y) not in visited:
                    room = self.explore_room(x, y, visited)
                    visited.update(room)
                    rooms.append(room)
        return rooms

    def explore_room(self, x, y, visited):
        room = set()
        stack = [(x, y)]

        while stack:
            x, y = stack.pop()
            room.add((x, y))

            visited.add((x, y))  # Mark the cell as visited

            neighbors = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            for nx, ny in neighbors:
                if 0 <= nx < self.width and 0 <= ny < self.height \
                        and self.floor_plan[ny][nx] != '#' and (nx, ny) not in visited:
                    if self.is_door(nx, ny):
                        visited.add((nx, ny))  # Mark the door as visited
                    else:
                        stack.append((nx, ny))

        return room

    def is_door(self, x, y):
        try:
            # Check if a space (' ') is a door by verifying it is surrounded by two walls ('#')
            # in the same direction
            horizontal = (self.floor_plan[y][x - 1] == '#' and self.floor_plan[y][x + 1] == '#')
            vertical = (self.floor_plan[y - 1][x] == '#' and self.floor_plan[y + 1][x] == '#')
            return horizontal or vertical
        except IndexError:
            return False

    def colorize(self):
        rooms = self.find_rooms()
        for room in rooms:
            color = self.generate_random_color()
            self.room_colors[color] = room

    def generate_random_color(self):
        while True:
            color = tuple(random.randint(0, 255) for _ in range(3))
            if color not in self.used_colors and color != (0, 0, 0) and color != (255, 255, 255):
                self.used_colors.add(color)
                return color

    def get_room_color(self, x, y):
        for color, room in self.room_colors.items():
            if (x, y) in room:
                return color
        return (255, 255, 255)

    def render_to_text(self):
        with open(f"{self.output_file_prefix}_output.txt", 'w') as output_file:
            for y in range(self.height):
                for x in range(self.width):
                    cell = self.floor_plan[y][x]
                    if cell == '#':
                        output_file.write('#')
                    else:
                        color = self.get_room_color(x, y)
                        output_file.write(f'#{color[0]:02X}{color[1]:02X}{color[2]:02X}')
                output_file.write('\n')

            output_file.write(f"Number of rooms: {len(self.room_colors)}")
            print(f"{self.input_file_name} -- > Number of rooms: {len(self.room_colors)}")

    def render_to_image(self):
        cell_size = 20
        image_width = self.width * cell_size
        image_height = self.height * cell_size

        img = Image.new('RGB', (image_width, image_height), 'white')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        for y in range(self.height):
            for x in range(self.width):
                cell = self.floor_plan[y][x]
                if cell == '#':
                    draw.rectangle([(x * cell_size, y * cell_size),
                                    ((x + 1) * cell_size, (y + 1) * cell_size)],
                                    fill='white')
                    center_x = (x * cell_size + (x + 0.5) * cell_size) // 2
                    center_y = (y * cell_size + (y + 0.5) * cell_size) // 2
                    text_color = 'black'
                    draw.text((center_x, center_y), '#', fill=text_color, font=font)
                else:
                    color = self.get_room_color(x, y)
                    draw.rectangle([(x * cell_size, y * cell_size),
                                    ((x + 1) * cell_size, (y + 1) * cell_size)],
                                    fill=color)

        img.save(f"{self.output_file_prefix}_output.png", "PNG")
        img.close()

    def render_to_image_with_colorized_output(self):
        cell_size = 20
        image_width = self.width * cell_size * 4
        image_height = self.height * cell_size + 20

        img = Image.new('RGB', (image_width, image_height), 'white')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()

        for y in range(self.height):
            for x in range(self.width):
                cell = self.floor_plan[y][x]
                x_left = x + self.width // 2
                if cell == '#':
                    draw.rectangle([(x_left * cell_size, y * cell_size),
                                    ((x_left + 1) * cell_size, (y + 1) * cell_size)],
                                    fill='white')
                    center_x = (x_left * cell_size + (x_left + 0.5) * cell_size) // 2
                    center_y = (y * cell_size + (y + 0.5) * cell_size) // 2
                    text_color = 'black'
                    draw.text((center_x, center_y), '#', fill=text_color, font=font)


        # Render the colorized floor plan on the right side of the image
        for y in range(self.height):
            for x in range(self.width):
                cell = self.floor_plan[y][x]
                x_output = x + self.width * 2.8  # Adjust the x coordinate to move it to the right
                if cell == '#':
                    draw.rectangle([(x_output * cell_size, y * cell_size),
                                    ((x_output + 1) * cell_size, (y + 1) * cell_size)],
                                    fill='white')
                    center_x = (x_output * cell_size + (x_output + 0.5) * cell_size) // 2
                    center_y = (y * cell_size + (y + 0.5) * cell_size) // 2
                    text_color = 'black'
                    draw.text((center_x, center_y), '#', fill=text_color, font=font)
                else:
                    color = self.get_room_color(x, y)
                    draw.rectangle([(x_output * cell_size, y * cell_size),
                                    ((x_output + 1) * cell_size, (y + 1) * cell_size)],
                                    fill=color)

        # Add an arrow between the two images
        arrow_length = 20
        arrow_start = (self.width * 2 * cell_size, (image_height // 2))
        arrow_end = (self.width * 2 * cell_size + arrow_length, image_height // 2)
        draw.line([arrow_start, arrow_end], fill='black', width=4)
        draw.line([(arrow_end[0] - 5, arrow_end[1] - 5), arrow_end, (arrow_end[0] - 5, arrow_end[1] + 5)],
                  fill='black', width=2)

        # Add the number of rooms as text to the image
        num_rooms_text = f"Number of rooms: {len(self.room_colors)}"
        text_color = 'black'
        draw.text(((image_width//2) - 3, image_height - 20), num_rooms_text, fill=text_color, font=font)
        img.save(f"{self.output_file_prefix}_input_output.png", "PNG")
        img.show()
        img.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python floor_plan_colorizer.py <input_file_path>")
        sys.exit(1)

    input_floor_plan_file = sys.argv[1]
    # input_floor_plan_file = "input/sample_floor_plan.txt"
    colorizer = FloorPlanColorizer(input_floor_plan_file)
    colorizer.colorize()
    colorizer.render_to_text()
    colorizer.render_to_image()
    colorizer.render_to_image_with_colorized_output()