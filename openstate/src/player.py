import pygame
import random

class Player:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        # Make the ninja smaller than the maze tiles
        self.width = 24
        self.height = 24
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Movement properties
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 2  # Reduced speed for better control
        
        # State properties
        self.facing_right = True
        self.is_crouching = False
        self.is_hidden = False
        
        # Animation properties
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.animation_timer = 0
        
        # Load player images (placeholder)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 0, 255))  # Blue placeholder
    
    def handle_event(self, event):
        # We'll handle movement in the update method using key states
        pass
    
    def update(self, level):
        # Update position with collision detection
        self.move_with_collision(level)
        
        # Check if player is in a hiding spot
        self.check_hiding(level)
        
        # Update animation
        self.update_animation()
    
    def move_with_collision(self, level):
        # Store original position for collision resolution
        original_x = self.rect.x
        original_y = self.rect.y
        
        # Move horizontally
        self.x += self.vel_x
        self.rect.x = int(self.x)
        
        # Check for horizontal collisions
        for wall in level.walls:
            if self.rect.colliderect(wall):
                if self.vel_x > 0:  # Moving right
                    self.rect.right = wall.left
                elif self.vel_x < 0:  # Moving left
                    self.rect.left = wall.right
                self.x = self.rect.x
        
        # Move vertically
        self.y += self.vel_y
        self.rect.y = int(self.y)
        
        # Check for vertical collisions
        for wall in level.walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0:  # Moving down
                    self.rect.bottom = wall.top
                elif self.vel_y < 0:  # Moving up
                    self.rect.top = wall.bottom
                self.y = self.rect.y
        
        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = self.rect.x
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.x = self.rect.x
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.y = self.rect.y
        elif self.rect.bottom > level.height:
            self.rect.bottom = level.height
            self.y = self.rect.y
    
    def check_hiding(self, level):
        self.is_hidden = False
        if self.is_crouching:
            for hide_spot in level.hide_spots:
                if self.rect.colliderect(hide_spot):
                    self.is_hidden = True
                    break
    
    def update_animation(self):
        self.animation_timer += 1
        if self.animation_timer >= 60 * self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # 4 frames of animation
    
    def render(self, screen):
        # Change color based on state (for placeholder)
        if self.is_hidden:
            self.image.fill((100, 100, 100))  # Gray when hidden
        elif self.is_crouching:
            self.image.fill((0, 100, 255))  # Light blue when crouching
        else:
            self.image.fill((0, 0, 255))  # Blue normally
        
        screen.blit(self.image, self.rect)
