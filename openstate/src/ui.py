import pygame

class UI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Font setup
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.large_font = pygame.font.SysFont('Arial', 36)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0, 128)  # Semi-transparent black
        self.star_color = (255, 215, 0)  # Gold
        self.empty_star_color = (100, 100, 100)  # Gray
        
        # Button properties
        self.button_width = 120
        self.button_height = 40
        self.button_color = (50, 50, 150)
        self.button_hover_color = (70, 70, 170)
        self.sound_button_rect = pygame.Rect(
            screen_width - 150, 
            screen_height - 50, 
            self.button_width, 
            self.button_height
        )
    
    def render(self, screen, level_number, scrolls_remaining, level_time, level_complete, stars, sound_enabled):
        # Create a semi-transparent overlay for the UI
        ui_overlay = pygame.Surface((self.screen_width, 40), pygame.SRCALPHA)
        ui_overlay.fill(self.bg_color)
        screen.blit(ui_overlay, (0, 0))
        
        # Render level number
        level_text = f"Level: {level_number}"
        level_surface = self.font.render(level_text, True, self.text_color)
        screen.blit(level_surface, (10, 10))
        
        # Render scrolls remaining
        scroll_text = f"Scrolls: {scrolls_remaining}"
        scroll_surface = self.font.render(scroll_text, True, self.text_color)
        screen.blit(scroll_surface, (150, 10))
        
        # Render timer
        minutes = int(level_time) // 60
        seconds = int(level_time) % 60
        timer_text = f"Time: {minutes:02d}:{seconds:02d}"
        timer_surface = self.font.render(timer_text, True, self.text_color)
        screen.blit(timer_surface, (300, 10))
        
        # Render stars
        star_x = self.screen_width - 120
        for i in range(3):
            color = self.star_color if i < stars else self.empty_star_color
            pygame.draw.polygon(screen, color, [
                (star_x + i*30 + 15, 10),  # Top point
                (star_x + i*30 + 20, 20),  # Right point
                (star_x + i*30 + 30, 22),  # Bottom right
                (star_x + i*30 + 22, 30),  # Bottom
                (star_x + i*30 + 15, 25),  # Bottom left
                (star_x + i*30 + 8, 30),   # Bottom
                (star_x + i*30 + 0, 22),   # Bottom left
                (star_x + i*30 + 10, 20),  # Left point
            ])
        
        # Render sound status
        sound_text = "Sound: ON" if sound_enabled else "Sound: OFF"
        sound_surface = self.small_font.render(sound_text, True, self.text_color)
        screen.blit(sound_surface, (self.screen_width - 100, 10))
        
        # Render level complete message
        if level_complete:
            complete_overlay = pygame.Surface((300, 100), pygame.SRCALPHA)
            complete_overlay.fill((0, 0, 0, 200))  # More opaque black
            screen.blit(complete_overlay, (self.screen_width // 2 - 150, self.screen_height // 2 - 50))
            
            complete_text = "Level Complete!"
            complete_surface = self.font.render(complete_text, True, self.text_color)
            screen.blit(complete_surface, (self.screen_width // 2 - complete_surface.get_width() // 2, 
                                          self.screen_height // 2 - 30))
            
            stars_text = f"Stars: {stars}/3"
            stars_surface = self.font.render(stars_text, True, self.star_color)
            screen.blit(stars_surface, (self.screen_width // 2 - stars_surface.get_width() // 2, 
                                       self.screen_height // 2 + 10))
        
        # Render controls help at the bottom
        controls_text = "Controls: W/A/S/D to move, Ctrl to hide"
        controls_surface = self.small_font.render(controls_text, True, self.text_color)
        screen.blit(controls_surface, (10, self.screen_height - 25))
    
    def render_menu(self, screen, sound_enabled):
        # Fill screen with dark background
        screen.fill((20, 20, 40))
        
        # Title
        title = self.large_font.render("OPENSTATE - NINJA STEALTH", True, (255, 255, 255))
        screen.blit(title, (self.screen_width // 2 - title.get_width() // 2, 100))
        
        # Play button
        play_button_rect = pygame.Rect(
            self.screen_width // 2 - self.button_width // 2,
            self.screen_height // 2 - self.button_height // 2,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(screen, self.button_color, play_button_rect, border_radius=5)
        play_text = self.font.render("PLAY", True, self.text_color)
        screen.blit(play_text, (play_button_rect.centerx - play_text.get_width() // 2, 
                               play_button_rect.centery - play_text.get_height() // 2))
        
        # Sound toggle button
        sound_button_rect = pygame.Rect(
            self.screen_width // 2 - self.button_width // 2,
            self.screen_height // 2 + 60,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(screen, self.button_color, sound_button_rect, border_radius=5)
        sound_text = self.font.render("SOUND: " + ("ON" if sound_enabled else "OFF"), True, self.text_color)
        screen.blit(sound_text, (sound_button_rect.centerx - sound_text.get_width() // 2, 
                                sound_button_rect.centery - sound_text.get_height() // 2))
        
        # Controls info
        controls_text = "Controls: W/A/S/D to move, Ctrl to hide"
        controls_surface = self.small_font.render(controls_text, True, self.text_color)
        screen.blit(controls_surface, (self.screen_width // 2 - controls_surface.get_width() // 2, 
                                      self.screen_height - 50))
        
        return play_button_rect, sound_button_rect
    
    def render_game_over(self, screen, reason):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = "GAME OVER"
        game_over_surface = self.large_font.render(game_over_text, True, (255, 0, 0))
        screen.blit(game_over_surface, (self.screen_width // 2 - game_over_surface.get_width() // 2, 
                                       self.screen_height // 2 - 100))
        
        # Reason text
        reason_surface = self.font.render(reason, True, self.text_color)
        screen.blit(reason_surface, (self.screen_width // 2 - reason_surface.get_width() // 2, 
                                    self.screen_height // 2 - 40))
        
        # Restart button
        restart_button_rect = pygame.Rect(
            self.screen_width // 2 - self.button_width - 10,
            self.screen_height // 2 + 20,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(screen, self.button_color, restart_button_rect, border_radius=5)
        restart_text = self.font.render("RESTART", True, self.text_color)
        screen.blit(restart_text, (restart_button_rect.centerx - restart_text.get_width() // 2, 
                                  restart_button_rect.centery - restart_text.get_height() // 2))
        
        # Menu button
        menu_button_rect = pygame.Rect(
            self.screen_width // 2 + 10,
            self.screen_height // 2 + 20,
            self.button_width,
            self.button_height
        )
        pygame.draw.rect(screen, self.button_color, menu_button_rect, border_radius=5)
        menu_text = self.font.render("MENU", True, self.text_color)
        screen.blit(menu_text, (menu_button_rect.centerx - menu_text.get_width() // 2, 
                               menu_button_rect.centery - menu_text.get_height() // 2))
        
        return restart_button_rect, menu_button_rect
