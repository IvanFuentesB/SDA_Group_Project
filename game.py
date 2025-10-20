import pygame
from dataclasses import dataclass

from scripts.utils import load_image
from scripts.entities import PhysicsEntity

@dataclass
class GameConfig:
    SCREEN_LENGHT = 640
    SCREEN_HEIGHT = 480
    FRAMERATE = 60
    

class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption('sigma sigma boy')
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_LENGHT, GameConfig.SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]
        
        self.assets = {
            'player' : load_image('entities/player/idle/idle0.png')
        }
        
        self.player = PhysicsEntity(self, 'player', (50,50), (8,15))
        
    def run(self):
        while True:
            self.screen.fill((14, 219, 248))
            
            self.player.update((self.movement[1] - self.movement[0], 0))
            self.player.render(self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        
            pygame.display.update()
            self.clock.tick(GameConfig.FRAMERATE)
            
Game().run()
