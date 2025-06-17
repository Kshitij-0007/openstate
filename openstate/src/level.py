import pygame
import random
from .maze_generator import MazeGenerator
from .scroll import Scroll
from .tile import Tile

class MovingWall:
    def __init__(self, start_pos, end_pos, speed=0.5):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = list(start_pos)
        self.speed = speed
        self.moving_to_end = True
        self.width = 32
        self.height = 32
        self.rect = pygame.Rect(self.current_pos[0], self.current_pos[1], self.width, self.height)
        
        # Create a surface for the moving wall
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((150, 50, 50))  # Reddish color to distinguish from normal walls
    
    def update(self):
        # Calculate direction vector
        if self.moving_to_end:
            target = self.end_pos
        else:
            target = self.start_pos
        
        # Calculate direction
        dx = target[0] - self.current_pos[0]
        dy = target[1] - self.current_pos[1]
        distance = (dx**2 + dy**2)**0.5
        
        # Move towards target
        if distance > self.speed:
            self.current_pos[0] += (dx / distance) * self.speed
            self.current_pos[1] += (dy / distance) * self.speed
        else:
            # Reached target, switch direction
            self.moving_to_end = not self.moving_to_end
        
        # Update rect position
        self.rect.x = int(self.current_pos[0])
        self.rect.y = int(self.current_pos[1])
    
    def render(self, screen):
        screen.blit(self.image, self.rect)

class Level:
    def __init__(self, level_number, screen_width, screen_height):
        self.level_number = level_number
        self.tile_size = 32
        
        # Calculate grid dimensions based on screen size
        self.grid_width = screen_width // self.tile_size
        self.grid_height = screen_height // self.tile_size
        
        # Actual pixel dimensions
        self.width = self.grid_width * self.tile_size
        self.height = self.grid_height * self.tile_size
        
        # Moving maze elements
        self.moving_walls = []
        
        # Generate the level
        self.generate_level()
        
        # Load tile images (placeholders)
        self.tile_images = {
            Tile.EMPTY: pygame.Surface((self.tile_size, self.tile_size)),
            Tile.WALL: pygame.Surface((self.tile_size, self.tile_size)),
            Tile.HIDE_SPOT: pygame.Surface((self.tile_size, self.tile_size)),
            Tile.EXIT: pygame.Surface((self.tile_size, self.tile_size))
        }
        
        # Set placeholder colors
        self.tile_images[Tile.EMPTY].fill((50, 50, 50))  # Dark gray
        self.tile_images[Tile.WALL].fill((100, 100, 100))  # Gray
        self.tile_images[Tile.HIDE_SPOT].fill((0, 100, 0))  # Dark green
        self.tile_images[Tile.EXIT].fill((255, 215, 0))  # Gold
    
    def generate_level(self):
        # Create maze generator
        maze_gen = MazeGenerator(self.grid_width, self.grid_height)
        self.grid = maze_gen.generate_maze()
        
        # Create walls list for collision detection
        self.walls = []
        self.hide_spots = []
        
        # Process the grid to create game objects
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == Tile.WALL:
                    self.walls.append(pygame.Rect(
                        x * self.tile_size, 
                        y * self.tile_size, 
                        self.tile_size, 
                        self.tile_size
                    ))
                elif self.grid[y][x] == Tile.HIDE_SPOT:
                    self.hide_spots.append(pygame.Rect(
                        x * self.tile_size, 
                        y * self.tile_size, 
                        self.tile_size, 
                        self.tile_size
                    ))
        
        # Place player start position (always in top-left area)
        start_x, start_y = self.find_empty_position(1, 1, 3, 3)
        # Adjust to center of tile and make sure player is smaller than tile
        self.player_start_pos = (
            start_x * self.tile_size + (self.tile_size - 24) // 2,
            start_y * self.tile_size + (self.tile_size - 24) // 2
        )
        
        # Place exit (always in bottom-right area)
        exit_x, exit_y = self.find_empty_position(
            self.grid_width - 4, 
            self.grid_height - 4, 
            self.grid_width - 1, 
            self.grid_height - 1
        )
        self.grid[exit_y][exit_x] = Tile.EXIT
        self.exit_rect = pygame.Rect(
            exit_x * self.tile_size,
            exit_y * self.tile_size,
            self.tile_size,
            self.tile_size
        )
        
        # Place scrolls (3-5 based on level)
        num_scrolls = 3 + min(2, self.level_number // 3)
        self.scrolls = []
        for _ in range(num_scrolls):
            scroll_x, scroll_y = self.find_empty_position(2, 2, self.grid_width - 3, self.grid_height - 3)
            # Center the scroll in the tile
            scroll_pos = (
                scroll_x * self.tile_size + (self.tile_size - 16) // 2,
                scroll_y * self.tile_size + (self.tile_size - 16) // 2
            )
            self.scrolls.append(Scroll(scroll_pos))
        
        # Create moving maze elements (more with higher levels)
        self.create_moving_walls()
        
        # Create guard patrol routes and guards
        self.create_guards()
    
    def create_moving_walls(self):
        # Number of moving walls increases with level
        num_moving_walls = min(self.level_number, 5)  # Cap at 5 moving walls
        
        for _ in range(num_moving_walls):
            # Find a suitable position for the moving wall
            wall_x, wall_y = self.find_empty_position(4, 4, self.grid_width - 5, self.grid_height - 5)
            
            # Find a suitable end position (in one of four directions)
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            random.shuffle(directions)
            
            end_x, end_y = None, None
            for dx, dy in directions:
                # Try to find a valid end position in this direction
                for distance in range(3, 6):  # Moving distance of 3-5 tiles
                    test_x = wall_x + dx * distance
                    test_y = wall_y + dy * distance
                    
                    # Check if position is valid
                    if (0 <= test_x < self.grid_width and 
                        0 <= test_y < self.grid_height and 
                        self.grid[test_y][test_x] == Tile.EMPTY):
                        
                        # Check if path is clear
                        path_clear = True
                        for i in range(1, distance):
                            check_x = wall_x + dx * i
                            check_y = wall_y + dy * i
                            if self.grid[check_y][check_x] != Tile.EMPTY:
                                path_clear = False
                                break
                        
                        if path_clear:
                            end_x, end_y = test_x, test_y
                            break
                
                if end_x is not None:
                    break
            
            # If we found a valid end position, create the moving wall
            if end_x is not None:
                # Convert to pixel coordinates
                start_pos = (wall_x * self.tile_size, wall_y * self.tile_size)
                end_pos = (end_x * self.tile_size, end_y * self.tile_size)
                
                # Create moving wall with random speed
                speed = 0.3 + (random.random() * 0.4)  # Speed between 0.3 and 0.7
                moving_wall = MovingWall(start_pos, end_pos, speed)
                self.moving_walls.append(moving_wall)
                
                # Mark the path as special in the grid (for rendering)
                for i in range(distance + 1):
                    path_x = wall_x + dx * i
                    path_y = wall_y + dy * i
                    if 0 <= path_x < self.grid_width and 0 <= path_y < self.grid_height:
                        # Don't overwrite existing special tiles
                        if self.grid[path_y][path_x] == Tile.EMPTY:
                            # We don't need a special tile type, just mark it visually
                            pass
    
    def find_empty_position(self, min_x, min_y, max_x, max_y):
        attempts = 0
        while attempts < 100:  # Prevent infinite loop
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            if self.grid[y][x] == Tile.EMPTY:
                return x, y
            attempts += 1
        
        # Fallback if no empty position found
        return min_x, min_y
    
    def create_guards(self):
        # Number of guards increases with level, but at a slower rate
        num_guards = 1 + min(2, self.level_number // 3)
        self.guards = []
        
        # Keep track of player start area to avoid placing guards there
        player_safe_zone_x = self.player_start_pos[0] // self.tile_size
        player_safe_zone_y = self.player_start_pos[1] // self.tile_size
        safe_zone_radius = 5  # Tiles away from player start
        
        for _ in range(num_guards):
            # Find a suitable position for the guard that's not near the player start
            guard_x, guard_y = None, None
            attempts = 0
            
            while attempts < 50:  # Limit attempts to prevent infinite loop
                temp_x, temp_y = self.find_empty_position(2, 2, self.grid_width - 3, self.grid_height - 3)
                
                # Check if this position is far enough from player start
                distance = abs(temp_x - player_safe_zone_x) + abs(temp_y - player_safe_zone_y)
                if distance > safe_zone_radius:
                    guard_x, guard_y = temp_x, temp_y
                    break
                
                attempts += 1
            
            # If we couldn't find a good position, use the last one anyway
            if guard_x is None:
                guard_x, guard_y = self.find_empty_position(2, 2, self.grid_width - 3, self.grid_height - 3)
            
            # Create a patrol route
            patrol_points = self.create_patrol_route(guard_x, guard_y)
            
            # Randomize guard speed based on level, but keep it manageable
            base_speed = 0.7  # Base speed for level 1
            speed_multiplier = 1.0 + (self.level_number * 0.03)  # Slower increase per level
            speed_multiplier = min(1.3, speed_multiplier)  # Cap at 1.3x
            
            # Create the guard with centered position
            from .guard import Guard
            guard_pos = (
                guard_x * self.tile_size + (self.tile_size - 24) // 2,
                guard_y * self.tile_size + (self.tile_size - 24) // 2
            )
            guard = Guard(guard_pos, patrol_points, speed_multiplier)
            self.guards.append(guard)
    
    def create_patrol_route(self, start_x, start_y):
        # Create a simple patrol route with 2-3 points (reduced from 2-4)
        num_points = random.randint(2, 3)
        
        # Center patrol points in tiles
        start_pos = (
            start_x * self.tile_size + (self.tile_size - 24) // 2,
            start_y * self.tile_size + (self.tile_size - 24) // 2
        )
        patrol_points = [start_pos]
        
        current_x, current_y = start_x, start_y
        for _ in range(num_points - 1):
            # Try to find a valid patrol point
            for attempt in range(20):  # Limit attempts
                # Choose a random direction and distance
                direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                
                # Shorter patrol routes (3-4 instead of 3-6)
                distance = random.randint(3, 4)
                
                new_x = current_x + direction[0] * distance
                new_y = current_y + direction[1] * distance
                
                # Check if the new point is valid
                if (0 <= new_x < self.grid_width and 
                    0 <= new_y < self.grid_height and 
                    self.grid[new_y][new_x] == Tile.EMPTY):
                    
                    # Check if path is clear
                    path_clear = True
                    for i in range(distance):
                        check_x = current_x + direction[0] * i
                        check_y = current_y + direction[1] * i
                        if self.grid[check_y][check_x] != Tile.EMPTY and self.grid[check_y][check_x] != Tile.HIDE_SPOT:
                            path_clear = False
                            break
                    
                    if path_clear:
                        # Center the patrol point in the tile
                        patrol_pos = (
                            new_x * self.tile_size + (self.tile_size - 24) // 2,
                            new_y * self.tile_size + (self.tile_size - 24) // 2
                        )
                        patrol_points.append(patrol_pos)
                        current_x, current_y = new_x, new_y
                        break
        
        # If we couldn't create enough points, just use what we have
        if len(patrol_points) < 2:
            # Add a second point nearby
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dx, dy in directions:
                new_x, new_y = start_x + dx * 2, start_y + dy * 2
                if (0 <= new_x < self.grid_width and 
                    0 <= new_y < self.grid_height and 
                    self.grid[new_y][new_x] == Tile.EMPTY):
                    patrol_pos = (
                        new_x * self.tile_size + (self.tile_size - 24) // 2,
                        new_y * self.tile_size + (self.tile_size - 24) // 2
                    )
                    patrol_points.append(patrol_pos)
                    break
        
        return patrol_points
    
    def update_moving_elements(self):
        # Update all moving walls
        for wall in self.moving_walls:
            wall.update()
            
        # Update the walls list to include current positions of moving walls
        # First, filter out any moving walls from the previous frame
        self.walls = [wall for wall in self.walls if not any(
            wall.x == moving_wall.rect.x and wall.y == moving_wall.rect.y 
            for moving_wall in self.moving_walls
        )]
        
        # Then add the current positions of moving walls
        for moving_wall in self.moving_walls:
            self.walls.append(moving_wall.rect)
    
    def render(self, screen):
        # Render the grid
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                tile_type = self.grid[y][x]
                screen.blit(
                    self.tile_images[tile_type],
                    (x * self.tile_size, y * self.tile_size)
                )
        
        # Render scrolls
        for scroll in self.scrolls:
            scroll.render(screen)
        
        # Render moving walls
        for wall in self.moving_walls:
            wall.render(screen)
        
        # Render guards
        for guard in self.guards:
            guard.render(screen)
