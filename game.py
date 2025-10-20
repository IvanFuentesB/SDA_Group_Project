import pygame
from dataclasses import dataclass

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

        self.img = pygame.image.load('data/images/entities/player/idle/idle0.png')
        self.img.set_colorkey((0, 0, 0))
        
        self.img_pos = [160,260]
        self.movement = [False, False]
        
    def run(self):
        while True:
            self.screen.fill((14, 219, 248))
            
            self.img_pos[1] += (self.movement[1] - self.movement[0]) * 5
            self.screen.blit(self.img,self.img_pos)
            
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.movement[0] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.movement[0] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[1] = False
                        
            pygame.display.update()
            self.clock.tick(GameConfig.FRAMERATE)
            
Game().run()
