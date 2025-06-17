#!/usr/bin/env python3
import pygame
import sys
import os
from src.game import Game, GameState

def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()
    
    # Set up the display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Openstate - Ninja Stealth")
    
    # Create game instance
    game = Game(screen)
    game.state = GameState.MENU  # Start with the menu
    
    # Create UI for menu
    ui = game.ui
    
    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            # Allow escape key to exit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game.state == GameState.PLAYING:
                    game.state = GameState.MENU
                else:
                    running = False
            
            # Pass events to game
            game.handle_event(event)
        
        # Update game state
        if game.state == GameState.PLAYING or game.state == GameState.LEVEL_COMPLETE:
            game.update()
        
        # Render the game
        game.render()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
    
    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
