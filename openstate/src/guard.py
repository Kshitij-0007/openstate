import pygame
import math
import random

class Guard:
    def __init__(self, start_pos, patrol_points, speed_multiplier=1.0):
        self.x, self.y = start_pos
        # Make guard smaller than tile size
        self.width = 24
        self.height = 24
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Patrol properties
        self.patrol_points = patrol_points
        self.current_point = 0
        self.base_speed = 0.6  # Even slower speed for better gameplay
        self.speed = self.base_speed * speed_multiplier
        
        # Vision properties
        self.vision_range = 100  # Reduced vision range
        self.vision_angle = 70  # Narrower angle for more balanced gameplay
        self.direction = 0  # 0 = right, 90 = down, 180 = left, 270 = up
        
        # Add pause at patrol points
        self.pause_timer = 0
        self.pause_duration = 60  # Frames to pause at each patrol point
        
        # Animation properties
        self.animation_frame = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        
        # Alert state
        self.is_alerted = False
        self.alert_timer = 0
        
        # Pursuit state
        self.is_pursuing = False
        self.pursuit_timer = 0
        self.pursuit_duration = 180  # Frames to pursue player (3 seconds at 60 FPS)
        self.pursuit_target = None
        self.original_position = start_pos
        self.returning_to_patrol = False
        
        # Load guard images (placeholder)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 0, 0))  # Red placeholder
    
    def update(self, level, player=None):
        if self.is_pursuing and player:
            # Pursue the player
            self.pursue_player(player, level)
        elif self.returning_to_patrol:
            # Return to original patrol route
            self.return_to_patrol()
        elif not self.is_alerted:
            self.patrol()
        else:
            self.alert_timer -= 1
            if self.alert_timer <= 0:
                self.is_alerted = False
        
        # Update animation
        self.update_animation()
    
    def pursue_player(self, player, level):
        # Update pursuit timer
        self.pursuit_timer -= 1
        if self.pursuit_timer <= 0:
            # Stop pursuing and return to patrol
            self.is_pursuing = False
            self.returning_to_patrol = True
            return
        
        # Calculate direction to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Move towards player with increased speed (1.5x normal speed)
        pursuit_speed = self.speed * 1.5
        if distance > pursuit_speed:
            # Check if path to player is blocked
            if not self.is_line_of_sight_blocked(player, level):
                self.x += (dx / distance) * pursuit_speed
                self.y += (dy / distance) * pursuit_speed
                
                # Update direction for vision cone
                if abs(dx) > abs(dy):  # Moving more horizontally
                    if dx > 0:
                        self.direction = 0  # Right
                    else:
                        self.direction = 180  # Left
                else:  # Moving more vertically
                    if dy > 0:
                        self.direction = 90  # Down
                    else:
                        self.direction = 270  # Up
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def return_to_patrol(self):
        # Get the nearest patrol point
        nearest_point = 0
        min_distance = float('inf')
        
        for i, point in enumerate(self.patrol_points):
            dx = point[0] - self.x
            dy = point[1] - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < min_distance:
                min_distance = distance
                nearest_point = i
        
        # Move towards the nearest patrol point
        target_x, target_y = self.patrol_points[nearest_point]
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.speed:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
            # Update direction for vision cone
            if abs(dx) > abs(dy):  # Moving more horizontally
                if dx > 0:
                    self.direction = 0  # Right
                else:
                    self.direction = 180  # Left
            else:  # Moving more vertically
                if dy > 0:
                    self.direction = 90  # Down
                else:
                    self.direction = 270  # Up
        else:
            # Reached patrol point, resume normal patrol
            self.returning_to_patrol = False
            self.current_point = nearest_point
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def patrol(self):
        # Check if guard is pausing at a patrol point
        if self.pause_timer > 0:
            self.pause_timer -= 1
            return
            
        # Get target point
        target_x, target_y = self.patrol_points[self.current_point]
        
        # Calculate direction to target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Move towards target if not already there
        if distance > self.speed:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
            # Update direction for vision cone (in degrees, clockwise from right)
            if abs(dx) > abs(dy):  # Moving more horizontally
                if dx > 0:
                    self.direction = 0  # Right
                else:
                    self.direction = 180  # Left
            else:  # Moving more vertically
                if dy > 0:
                    self.direction = 90  # Down
                else:
                    self.direction = 270  # Up
        else:
            # Reached target point, pause before moving to next one
            self.pause_timer = self.pause_duration
            self.current_point = (self.current_point + 1) % len(self.patrol_points)
        
        # Update rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def detect_player(self, player, level):
        # Don't detect if player is hidden
        if player.is_hidden:
            return False
        
        # Calculate distance to player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if player is within vision range
        if distance <= self.vision_range:
            # Calculate angle to player (in degrees, clockwise from right)
            angle = math.degrees(math.atan2(dy, dx))
            if angle < 0:
                angle += 360
                
            # Check if player is within vision angle
            angle_diff = abs((angle - self.direction) % 360)
            if angle_diff <= self.vision_angle / 2 or angle_diff >= 360 - self.vision_angle / 2:
                # Check if there's a wall blocking the view
                if not self.is_line_of_sight_blocked(player, level):
                    # Add reaction delay - only alert if player is in sight for a while
                    self.is_alerted = True
                    self.alert_timer = 30  # Alert for 30 frames
                    
                    # Start pursuing the player
                    self.is_pursuing = True
                    self.pursuit_timer = self.pursuit_duration
                    self.pursuit_target = (player.rect.centerx, player.rect.centery)
                    
                    # Return true immediately for detection - we'll handle the game over in game.py
                    return True
        
        return False
    
    def is_line_of_sight_blocked(self, player, level):
        # Check if there's a wall between guard and player
        start_x, start_y = self.rect.center
        end_x, end_y = player.rect.center
        
        # Use Bresenham's line algorithm to check points along the line
        points = self.get_line_points(start_x, start_y, end_x, end_y)
        
        # Check each point for collision with walls
        for x, y in points:
            # Create a small rect at this point
            point_rect = pygame.Rect(x, y, 1, 1)
            
            # Check if this point collides with any wall
            for wall in level.walls:
                if wall.colliderect(point_rect):
                    return True  # Line of sight is blocked
        
        return False  # No walls blocking the line of sight
    
    def get_line_points(self, x0, y0, x1, y1):
        """Bresenham's Line Algorithm to get all points on a line"""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                if x0 == x1:
                    break
                err -= dy
                x0 += sx
            if e2 < dx:
                if y0 == y1:
                    break
                err += dx
                y0 += sy
                
        return points
    
    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= 60 * self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # 4 frames of animation
    
    def render(self, screen):
        # Change color based on state (for placeholder)
        if self.is_pursuing:
            self.image.fill((255, 0, 0))  # Bright red when pursuing
        elif self.is_alerted:
            self.image.fill((255, 255, 0))  # Yellow when alerted
        elif self.returning_to_patrol:
            self.image.fill((255, 165, 0))  # Orange when returning to patrol
        else:
            self.image.fill((200, 0, 0))  # Dark red normally
        
        screen.blit(self.image, self.rect)
        
        # Draw vision cone (simplified)
        if not self.is_pursuing:
            # Create a semi-transparent surface for the vision cone
            vision_surface = pygame.Surface((self.vision_range * 2, self.vision_range * 2), pygame.SRCALPHA)
            
            # Calculate start and end angles for the vision cone
            start_angle = math.radians(self.direction - self.vision_angle / 2)
            end_angle = math.radians(self.direction + self.vision_angle / 2)
            
            # Draw the vision cone as a pie slice
            pygame.draw.arc(vision_surface, (255, 0, 0, 50), 
                           (0, 0, self.vision_range * 2, self.vision_range * 2),
                           start_angle, end_angle, self.vision_range)
            
            # Draw lines from center to edge of cone
            center = (self.vision_range, self.vision_range)
            for angle in [start_angle, end_angle]:
                end_x = center[0] + math.cos(angle) * self.vision_range
                end_y = center[1] + math.sin(angle) * self.vision_range
                pygame.draw.line(vision_surface, (255, 0, 0, 100), center, (end_x, end_y), 2)
            
            # Blit the vision cone centered on the guard
            screen.blit(vision_surface, 
                       (self.rect.centerx - self.vision_range, 
                        self.rect.centery - self.vision_range))
