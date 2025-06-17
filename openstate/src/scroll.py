import pygame
import math

class Scroll:
    def __init__(self, position):
        self.x, self.y = position
        self.width = 16
        self.height = 16
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Animation properties
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.animation_timer = 0
        self.hover_offset = 0
        self.hover_speed = 0.05
        
        # Load scroll image (placeholder)
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((255, 255, 0))  # Yellow placeholder
    
    def update(self):
        # Update hover animation
        self.hover_offset = math.sin(pygame.time.get_ticks() * self.hover_speed) * 3
        
        # Update animation
        self.animation_timer += 1
        if self.animation_timer >= 60 * self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4  # 4 frames of animation
    
    def render(self, screen):
        # Apply hover effect
        hover_rect = self.rect.copy()
        hover_rect.y += int(self.hover_offset)
        
        screen.blit(self.image, hover_rect)
