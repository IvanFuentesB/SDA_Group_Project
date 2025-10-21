import pygame
from dataclasses import dataclass

from scripts.utils import load_image, load_images
from scripts.entities import PhysicsEntity
from scripts.tilemap import Tilemap

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

        self.display = pygame.Surface((GameConfig.SCREEN_LENGHT//2, GameConfig.SCREEN_HEIGHT//2))

        self.clock = pygame.time.Clock()

        self.movement = [False, False]
        
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor':load_images('tiles/large_decor'),
            'stone':load_images('tiles/stone'),
            'player' : load_image('entities/player.png')
        }
        
        self.player = PhysicsEntity(self, 'player', 
                                    (50,50), 
                                    (self.assets['player'].get_width(),
                                     self.assets['player'].get_height())
        )
        
        self.tilemap = Tilemap(self, tile_size = 16)
        
    def run(self):
        while True:
            self.display.fill((14, 219, 248))
            
            self.tilemap.render(self.display)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display)
            
            print(self.tilemap.physics_rects_around(self.player.pos))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                    if event.key == pygame.K_DOWN:
                        self.player.velocity[1] = 10
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                        
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))            
            pygame.display.update()
            self.clock.tick(GameConfig.FRAMERATE)
            
Game().run()
