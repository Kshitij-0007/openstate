import pygame
import time
from .player import Player
from .guard import Guard
from .level import Level
from .ui import UI

class GameState:
    MENU = 0
    PLAYING = 1
    LEVEL_COMPLETE = 2
    GAME_OVER = 3
    TRANSITION = 4

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.state = GameState.PLAYING
        self.current_level = 1
        self.max_levels = 10
        self.stars = 0
        self.total_stars = 0
        self.sound_enabled = True
        
        # Initialize components
        self.level = Level(self.current_level, self.screen_width, self.screen_height)
        self.player = Player(self.level.player_start_pos)
        self.ui = UI(self.screen_width, self.screen_height)
        
        # Game timing
        self.level_start_time = time.time()
        self.level_time = 0
        self.transition_time = 0
        
        # Game over reason
        self.game_over_reason = ""
        
        # Load sounds
        self.load_sounds()
        
    def load_sounds(self):
        # Create empty sounds as placeholders
        self.sounds = {
            'pickup': pygame.mixer.Sound(buffer=bytearray(44)),
            'alert': pygame.mixer.Sound(buffer=bytearray(44)),
            'level_complete': pygame.mixer.Sound(buffer=bytearray(44)),
            'footstep': pygame.mixer.Sound(buffer=bytearray(44)),
            'game_over': pygame.mixer.Sound(buffer=bytearray(44))
        }
        
        # Set default volume
        for sound in self.sounds.values():
            sound.set_volume(0.5)
    
    def handle_event(self, event):
        # Handle menu events
        if self.state == GameState.MENU:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check for button clicks
                mouse_pos = pygame.mouse.get_pos()
                play_button, sound_button = self.ui.render_menu(self.screen, self.sound_enabled)
                
                if play_button.collidepoint(mouse_pos):
                    self.state = GameState.PLAYING
                    self.restart_level()
                elif sound_button.collidepoint(mouse_pos):
                    self.toggle_sound()
        
        # Handle game over events
        elif self.state == GameState.GAME_OVER:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                restart_button, menu_button = self.ui.render_game_over(self.screen, self.game_over_reason)
                
                if restart_button.collidepoint(mouse_pos):
                    self.restart_level()
                    self.state = GameState.PLAYING
                elif menu_button.collidepoint(mouse_pos):
                    self.state = GameState.MENU
    
    def update(self):
        if self.state == GameState.PLAYING:
            # Update level time
            self.level_time = time.time() - self.level_start_time
            
            # Handle continuous key presses for smoother control
            keys = pygame.key.get_pressed()
            
            # Reset velocities - ninja should be stationary unless keys are pressed
            self.player.vel_x = 0
            self.player.vel_y = 0
            
            # Handle directional movement with WASD - top-down view
            if keys[pygame.K_a]:  # Left
                self.player.vel_x = -self.player.speed
                self.player.facing_right = False
            if keys[pygame.K_d]:  # Right
                self.player.vel_x = self.player.speed
                self.player.facing_right = True
            if keys[pygame.K_w]:  # Up
                self.player.vel_y = -self.player.speed
            if keys[pygame.K_s]:  # Down
                self.player.vel_y = self.player.speed
                
            # Crouching/hiding with Ctrl
            self.player.is_crouching = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
            
            # Update player
            self.player.update(self.level)
            
            # Update moving maze elements
            self.level.update_moving_elements()
            
            # Update guards
            for guard in self.level.guards:
                guard.update(self.level, self.player)
                
                # Check if player is detected by guard
                if guard.detect_player(self.player, self.level):
                    if self.sound_enabled:
                        self.sounds['alert'].play()
                        self.sounds['game_over'].play()
                    
                    # Set game over state
                    self.state = GameState.GAME_OVER
                    self.game_over_reason = "Ninja Captured!"
                    return
            
            # Check if player collected a scroll - only if directly on it
            for scroll in self.level.scrolls[:]:
                # Check for exact position overlap (center points within a small threshold)
                player_center = self.player.rect.center
                scroll_center = scroll.rect.center
                distance_x = abs(player_center[0] - scroll_center[0])
                distance_y = abs(player_center[1] - scroll_center[1])
                
                if distance_x < 12 and distance_y < 12:  # Smaller threshold for more precise collection
                    self.level.scrolls.remove(scroll)
                    if self.sound_enabled:
                        self.sounds['pickup'].play()
            
            # Check if player reached the exit
            if self.player.rect.colliderect(self.level.exit_rect):
                if len(self.level.scrolls) == 0:
                    # All scrolls collected
                    self.stars = 3
                else:
                    # Exit reached but not all scrolls collected
                    self.stars = 1
                
                self.total_stars += self.stars
                if self.sound_enabled:
                    self.sounds['level_complete'].play()
                self.state = GameState.LEVEL_COMPLETE
                self.transition_time = time.time()
        
        elif self.state == GameState.LEVEL_COMPLETE:
            # Wait for 2 seconds before transitioning to next level
            if time.time() - self.transition_time > 2.0:
                self.next_level()
    
    def render(self):
        # Clear the screen
        self.screen.fill((0, 0, 0))
        
        if self.state == GameState.PLAYING or self.state == GameState.LEVEL_COMPLETE or self.state == GameState.GAME_OVER:
            # Render level
            self.level.render(self.screen)
            
            # Render player
            self.player.render(self.screen)
            
            # Render UI
            if self.state == GameState.PLAYING or self.state == GameState.LEVEL_COMPLETE:
                self.ui.render(self.screen, self.current_level, len(self.level.scrolls), 
                              self.level_time, self.state == GameState.LEVEL_COMPLETE, self.stars, self.sound_enabled)
            
            # Render game over screen
            if self.state == GameState.GAME_OVER:
                self.ui.render_game_over(self.screen, self.game_over_reason)
        
        elif self.state == GameState.MENU:
            self.ui.render_menu(self.screen, self.sound_enabled)
    
    def toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        
        # Mute or unmute all sounds
        volume = 0.5 if self.sound_enabled else 0.0
        for sound in self.sounds.values():
            sound.set_volume(volume)
    
    def restart_level(self):
        self.level = Level(self.current_level, self.screen_width, self.screen_height)
        self.player = Player(self.level.player_start_pos)
        self.level_start_time = time.time()
        self.level_time = 0
    
    def next_level(self):
        self.current_level += 1
        if self.current_level > self.max_levels:
            self.current_level = 1  # Loop back to first level
        
        self.restart_level()
        self.state = GameState.PLAYING
