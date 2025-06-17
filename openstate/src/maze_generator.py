import random
from .tile import Tile

class MazeGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[Tile.WALL for _ in range(width)] for _ in range(height)]
    
    def generate_maze(self):
        # Use a randomized depth-first search algorithm to generate the maze
        # Start with a grid full of walls
        
        # Make sure the grid has odd dimensions for a proper maze
        width_odd = self.width if self.width % 2 == 1 else self.width - 1
        height_odd = self.height if self.height % 2 == 1 else self.height - 1
        
        # Pick a random starting cell (must be odd coordinates)
        start_x = random.randrange(1, width_odd, 2)
        start_y = random.randrange(1, height_odd, 2)
        self.grid[start_y][start_x] = Tile.EMPTY
        
        # Initialize the stack with the starting cell
        stack = [(start_x, start_y)]
        
        # Continue until the stack is empty
        while stack:
            current_x, current_y = stack[-1]
            
            # Get unvisited neighbors
            neighbors = self.get_unvisited_neighbors(current_x, current_y)
            
            if neighbors:
                # Choose a random neighbor
                next_x, next_y = random.choice(neighbors)
                
                # Remove the wall between the current cell and the chosen neighbor
                self.grid[next_y][next_x] = Tile.EMPTY
                
                # Also remove the wall in between if they're not adjacent
                wall_x = (current_x + next_x) // 2
                wall_y = (current_y + next_y) // 2
                self.grid[wall_y][wall_x] = Tile.EMPTY
                
                # Push the neighbor to the stack
                stack.append((next_x, next_y))
            else:
                # Backtrack
                stack.pop()
        
        # Add some hiding spots (bushes, shadows, etc.)
        self.add_hiding_spots()
        
        # Make sure there are enough paths by removing some walls
        self.create_additional_paths()
        
        # Create some open areas for better gameplay
        self.create_open_areas()
        
        return self.grid
    
    def get_unvisited_neighbors(self, x, y):
        neighbors = []
        
        # Check in all four directions with a distance of 2 (to create walls in between)
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]  # Up, Right, Down, Left
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check if the neighbor is within bounds and is a wall (unvisited)
            if (1 <= nx < self.width - 1 and 
                1 <= ny < self.height - 1 and 
                self.grid[ny][nx] == Tile.WALL):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def add_hiding_spots(self):
        # Add hiding spots randomly throughout the maze
        num_hiding_spots = (self.width * self.height) // 15  # About 6-7% of the grid
        
        for _ in range(num_hiding_spots):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            # Only place hiding spots in empty spaces
            if self.grid[y][x] == Tile.EMPTY:
                self.grid[y][x] = Tile.HIDE_SPOT
    
    def create_additional_paths(self):
        # Remove some walls to create additional paths
        # This makes the maze easier to navigate
        num_walls_to_remove = (self.width * self.height) // 20  # About 5% of the grid
        
        for _ in range(num_walls_to_remove):
            # Pick a random wall that's not on the border
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            if self.grid[y][x] == Tile.WALL:
                # Check if removing this wall connects two separate paths
                # Count empty neighbors
                empty_neighbors = 0
                if self.grid[y-1][x] == Tile.EMPTY: empty_neighbors += 1
                if self.grid[y+1][x] == Tile.EMPTY: empty_neighbors += 1
                if self.grid[y][x-1] == Tile.EMPTY: empty_neighbors += 1
                if self.grid[y][x+1] == Tile.EMPTY: empty_neighbors += 1
                
                # If it has at least 2 empty neighbors, remove it
                if empty_neighbors >= 2:
                    self.grid[y][x] = Tile.EMPTY
    
    def create_open_areas(self):
        # Create a few open areas by removing clusters of walls
        num_open_areas = max(2, self.width * self.height // 100)
        
        for _ in range(num_open_areas):
            # Pick a random center point for the open area
            center_x = random.randint(3, self.width - 4)
            center_y = random.randint(3, self.height - 4)
            
            # Determine size of open area (2-3 tiles radius)
            radius = random.randint(2, 3)
            
            # Clear walls in this area
            for y in range(center_y - radius, center_y + radius + 1):
                for x in range(center_x - radius, center_x + radius + 1):
                    if (0 < x < self.width - 1 and 0 < y < self.height - 1):
                        # Don't remove all walls - keep some for structure
                        if self.grid[y][x] == Tile.WALL and random.random() < 0.7:
                            self.grid[y][x] = Tile.EMPTY
