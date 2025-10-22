import pygame
from dataclasses import dataclass

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds

@dataclass
class GameConfig:
    SCREEN_LENGHT = 640
    SCREEN_HEIGHT = 480
    CAMERA_FOLLOW_SPEED = 5 # Lower is faster
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
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle': Animation(load_images('entities/player/idle'), img_duration = 6),
            'player/run': Animation(load_images('entities/player/run'), img_duration=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'))

        }
        
        self.clouds = Clouds(self.assets['clouds'], count = 16)
        
        self.player = Player(self, (50,50), (self.assets['player'].get_width(), self.assets['player'].get_height()))
        
        self.tilemap = Tilemap(self, tile_size = 16)
        
        self.tilemap.load('map.json')
        
        self.scroll: list[float] = [0, 0]
        
    def run(self):
        while True:
            self.display.blit(self.assets['background'], (0, 0))
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / GameConfig.CAMERA_FOLLOW_SPEED
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / GameConfig.CAMERA_FOLLOW_SPEED
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.clouds.update()
            self.clouds.render(self.display, offset = render_scroll)
            
            self.tilemap.render(self.display, offset = render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset = render_scroll)
            
           
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
