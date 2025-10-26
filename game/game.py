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
from scripts.shape import Shape, Circle
@dataclass
class GameConfig:
    SCREEN_LENGHT = 640
    SCREEN_HEIGHT = 480
    CAMERA_FOLLOW_SPEED = 5 # Lower is faster
    FRAMERATE = 60
    TOTAL_LEVELS = 3
    RENDER_SCALE = 2.0


#def get_shape():
#    return shape_type, shape_color
                
    
class Level:
    def __init__(self, id, has_spikes, shape, player_pos):
        self.id = id
        self.has_spikes = has_spikes
        self.shape = shape
        self.player_pos = list(player_pos)

        

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
            'door': load_images('tiles/door'),
            'square':load_images('tiles/square'),
            'triangle':load_images('tiles/triangle'),
            'circle/red': Animation(load_images('tiles/circle/red'), img_duration = 4, loop = True),
            'circle/green': Animation(load_images('tiles/circle/green'), img_duration = 4,loop = True),
            'circle/blue': Animation(load_images('tiles/circle/blue'), img_duration = 4,loop = True),
            'circle/yellow': Animation(load_images('tiles/circle/yellow'), img_duration = 4,loop = True),
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
        
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),

        }
        
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)

        
        self.clouds = Clouds(self.assets['clouds'], count = 16)
        
                
        self.tilemap = Tilemap(self, tile_size = 16)
        
        self.spikes = Spikes(self, 200, 500,(-60, 170), (0.5, 2.5))
        
        self.square = Shape(self, 'square', 'red', (1, 1))
        self.triangle = Shape(self, 'triangle', 'red', (10, 1))
        self.current_level = 0
        
        self.level_attributes = {
            0: Level(0,False,Shape(self, 'square', 'red', (12, 4)),(103 ,129)),
            1: Level(1, False, Circle(self, 'blue', (135, 2), (16, 16)),(103, 129)),
            2: Level(2, True, None, (103, 129))
        }
        
        self.load_level(self.current_level)
 
        self.screenshake = 0

        self.switched_boss_music = False
    
    def load_level(self, map_id):
        self.player = Player(self, self.level_attributes[map_id].player_pos, (self.assets['player'].get_width(), self.assets['player'].get_height()))
        self.spikes.delete()
        self.spikes.collided_player = False
        self.spikes.enable_spawn = self.level_attributes[self.current_level].has_spikes
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.scroll: list[float] = [0, 0]
        self.particles = []
        self.sparks = []
           
        self.dead = 0
        self.transition = -30
        
            
                

    def run(self): #! Can use the really cool particles for the big blast
        if self.current_level != 2:
            pygame.mixer.music.load('data/music.wav')
            
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)
        
        while True:
            
            
            self.display.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
               

            
            if any(tile.get('type') == 'door' for tile in self.tilemap.tiles_around(self.player.pos)):
                self.transition += 1 
                if self.transition > 30:
                    self.current_level = min(GameConfig.TOTAL_LEVELS - 1, self.current_level + 1)

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
            print(f"Player pos:{self.player.pos}")
            #print(f"Player Tile pos:{self.player.pos[0]//self.tilemap.tile_size, self.player.pos[1]//self.tilemap.tile_size}")
            
            if isinstance(self.level_attributes[self.current_level].shape, Circle):
                circle : Circle = self.level_attributes[self.current_level].shape # type:ignore
                if circle.spawned:
                    
                    if self.player.rect().colliderect(self.level_attributes[self.current_level].shape.rect()): #type:ignore
                        if self.player.rect().x < self.level_attributes[self.current_level].shape.rect().x:   #type:ignore
                            self.level_attributes[self.current_level].shape.movement[1] = True  #type:ignore
                        if self.player.rect().x > self.level_attributes[self.current_level].shape.rect().x:  #type:ignore
                            self.level_attributes[self.current_level].shape.movement[0] = True  #type:ignore
                    self.level_attributes[self.current_level].shape.update(self.tilemap,(self.level_attributes[self.current_level].shape.movement[1] - self.level_attributes[self.current_level].shape.movement[0], 0))  #type:ignore
                    self.level_attributes[self.current_level].shape.render(self.display, offset= render_scroll)    #type:ignore
                else:
                    self.level_attributes[self.current_level].shape.movement = [False, False] #type:ignore
            
            
            self.spikes.update(self.player.rect())
            self.spikes.render(self.display, offset= render_scroll)
            
            if self.spikes.collided_player and self.dead == 0:
                self.screenshake = max(16, self.screenshake)
                self.sfx['hit'].play()
                self.dead += 1
            
            for spark in self.sparks.copy():
                kill = spark.update()
                spark.render(self.display, offset = render_scroll)
                if kill:
                    self.sparks.remove(spark)
            
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
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_DOWN:
                        self.player.ground_slam()
                    if event.key == pygame.K_x:
                        self.player.dash()
                    if event.key == pygame.K_e:
                        self.level_attributes[self.current_level].shape.spawn()
                    if event.key == pygame.K_r:
                        self.level_attributes[self.current_level].shape.spawned = True #type:ignore
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            if self.current_level == 1: 
               if self.level_attributes[1].shape.pos[1] > 190: #type:ignore
                    for y in range(1, 9):
                        loc = f"16;{y}"
                        self.tilemap.tilemap.pop(loc, None)
                    self.tilemap.autotile()
            if not self.switched_boss_music and self.current_level == 2:
                self.switched_boss_music = True
                pygame.mixer.music.unload()
                pygame.mixer.music.load('data/boss_music.mp3')
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                    
            
            
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
