import pygame
import random
import math
from dataclasses import dataclass

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Spikes
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
@dataclass
class GameConfig:
    SCREEN_LENGHT = 640
    SCREEN_HEIGHT = 480
    CAMERA_FOLLOW_SPEED = 5 # Lower is faster
    FRAMERATE = 60
    TOTAL_LEVELS = 3
    

class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption('sigma sigma boy')
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_LENGHT, GameConfig.SCREEN_HEIGHT))

        self.display = pygame.Surface((GameConfig.SCREEN_LENGHT//2, GameConfig.SCREEN_HEIGHT//2), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((GameConfig.SCREEN_LENGHT//2, GameConfig.SCREEN_HEIGHT//2))
        
        
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
            'player/wall_slide': Animation(load_images('entities/player/wall_slide'), img_duration=3 , loop= True),
            'player/slam': Animation(load_images('entities/player/slam')),
            'spike': Animation(load_images('/projectile/spike')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_duration = 20, loop = False),
            'particle/particle': Animation(load_images('particles/particle'), img_duration = 6, loop = False)
        }
        
        self.clouds = Clouds(self.assets['clouds'], count = 16)
        
                
        self.tilemap = Tilemap(self, tile_size = 16)
        
        self.spikes = Spikes(self, 500, 170,(70, 150), (0.5, 2.5))
        
        self.current_level = 0
        
        self.load_level(self.current_level)
 
        self.screenshake = 0

    
    def load_level(self, map_id):
        self.player = Player(self, (50,50), (self.assets['player'].get_width(), self.assets['player'].get_height()))
        self.spikes.delete()
        self.spikes.collided_player = False
        self.spikes.enable_spawn = False
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
        if map_id is 0:
            self.spikes.enable_spawn = True
        self.scroll: list[float] = [0, 0]
        self.particles = []
        self.sparks = []
           
        self.dead = 0
        self.transition = -30    

    def run(self): #! Can use the really cool particles for the big blast
        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
            
            
            if any(tile.get('type') == 'door' for tile in self.tilemap.tiles_around(self.player.pos)):
                self.transition += 1 
                if self.transition > 30:
                    self.current_level = max(GameConfig.TOTAL_LEVELS - 1, self.current_level + 1)
                    self.load_level(self.current_level)
            if self.transition < 0:
                self.transition += 1
                
                
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(self.transition + 1, 30)
                if self.dead > 40:
                    self.load_level(self.current_level)
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / GameConfig.CAMERA_FOLLOW_SPEED
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / GameConfig.CAMERA_FOLLOW_SPEED
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            for rect in self.leaf_spawners:
                if random.random() * 49999 < rect.width * rect.height:
                    pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                    self.particles.append(Particle(self, 'leaf', pos, velocity = [-0.1, 0.3], frame = random.randint(0, 20)))
            
            self.clouds.update()
            self.clouds.render(self.display, offset = render_scroll)
            
            self.tilemap.render(self.display, offset = render_scroll)
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset = render_scroll)

            self.spikes.update(self.player.rect())
            self.spikes.render(self.display, offset= render_scroll)
            
            if self.spikes.collided_player:
                self.screenshake = max(16, self.screenshake)
                self.dead += 1
            
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)
            
            display_mask = pygame.mask.from_surface(self.display)    
            display_sillhouete = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            self.display_2.blit(display_sillhouete, (0, 0))
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset = render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.jump()
                    if event.key == pygame.K_DOWN:
                        self.player.ground_slam()
                    if event.key == pygame.K_x:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
                
            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), screenshake_offset)            
            pygame.display.update()
            self.clock.tick(GameConfig.FRAMERATE)
            
Game().run()
