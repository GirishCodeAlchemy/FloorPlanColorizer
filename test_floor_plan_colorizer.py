import os
import unittest

from floor_plan_colorizer import FloorPlanColorizer  # Import the FloorPlanColorizer class


class TestFloorPlanColorizer(unittest.TestCase):
    def setUp(self):
        # Create a sample floor plan file for testing
        self.sample_floor_plan_file = "input/floor_plan_1.txt"
        # Create an instance of FloorPlanColorizer using the sample floor plan file
        self.colorizer = FloorPlanColorizer(self.sample_floor_plan_file)
        self.colorizer.colorize()

    def tearDown(self):
        # Clean up: remove the sample floor plan file
        # os.remove(self.sample_floor_plan_file)
        pass

    def test_read_floor_plan_from_file(self):
        expected_floor_plan = [
            "##########",
            "#   #    #",
            "#   #    #",
            "## #### ##",
            "#        #",
            "#        #",
            "##########",
        ]
        self.assertEqual(self.colorizer.floor_plan, [list(row) for row in expected_floor_plan])

    def test_find_rooms(self):
        # Test the find_rooms method
        rooms = self.colorizer.find_rooms()
        self.assertTrue(len(rooms) > 0)

    def test_explore_room(self):
        # Test the explore_room method
        room = self.colorizer.explore_room(2, 2, set())
        self.assertIn((2, 2), room)

    def test_is_door(self):
        # Test the is_door method
        self.assertTrue(self.colorizer.is_door(7, 3))
        self.assertFalse(self.colorizer.is_door(1, 2))
        self.assertFalse(self.colorizer.is_door(100, 200))

    def test_generate_random_color(self):
        # Test the generate_random_color method
        color = self.colorizer.generate_random_color()
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)

    def test_get_room_color(self):
        # Test the get_room_color method
        color = self.colorizer.get_room_color(2, 2)
        self.assertIsInstance(color, tuple)
        self.assertEqual(len(color), 3)

    def test_render_to_text(self):
        # Test the render_to_text method
        output_file = f"{self.colorizer.output_file_prefix}_output.txt"

        self.colorizer.render_to_text()
        with open(output_file, "r") as f:
            read_data = f.read().strip().endswith("Number of rooms: 3")
            self.assertTrue(read_data)

    def test_render_to_image(self):
        # Test the render_to_image method
        self.colorizer.render_to_image()
        self.assertTrue(os.path.isfile(f"{self.colorizer.output_file_prefix}_output.png"))


    def test_render_to_image_with_colorized_output(self):
        # Test the render_to_image_with_colorized_output method
        self.colorizer.render_to_image_with_colorized_output()
        self.assertTrue(os.path.isfile(f"{self.colorizer.output_file_prefix}_output.png"))

    def test_various_floor_plans(self):

        input_folder = os.path.abspath("input/")
        # List all files in the input folder with complete paths
        input_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

        for floor_plan in input_files:
            colorizer = FloorPlanColorizer(floor_plan)
            colorizer.colorize()
            colorizer.render_to_text()
            colorizer.render_to_image()
            colorizer.render_to_image_with_colorized_output()
            self.assertTrue(os.path.isfile(f"{colorizer.output_file_prefix}_output.txt"))
            self.assertTrue(os.path.isfile(f"{colorizer.output_file_prefix}_output.png"))
            self.assertTrue(os.path.isfile(f"{colorizer.output_file_prefix}_input_output.png"))
