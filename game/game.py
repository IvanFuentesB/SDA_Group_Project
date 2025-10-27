import pygame
import random
import math
import os
from dataclasses import dataclass

from scripts.utils import load_image, load_images, Animation
from scripts.entities import PhysicsEntity, Player, Spikes, Enemy
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.particle import Particle
from scripts.spark import Spark
from scripts.shape import Shape, Circle
from scripts.camera import Camera

@dataclass
class GameConfig:
    SCREEN_LENGHT = 640
    SCREEN_HEIGHT = 480
    CAMERA_FOLLOW_SPEED = 5 # Lower is faster
    FRAMERATE = 60
    TOTAL_LEVELS = 4
    RENDER_SCALE = 2.0



    
class Level:
    def __init__(self,game, id, has_spikes, shape, player_pos):
        self.game = game
        self.id = id
        self.has_spikes = has_spikes
        self.shape = shape
        self.player_pos = list(player_pos)
        self.spawned_shape = False
        

        

class Game:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption('sigma sigma boy')
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_LENGHT, GameConfig.SCREEN_HEIGHT))

        self.display = pygame.Surface((GameConfig.SCREEN_LENGHT//2, GameConfig.SCREEN_HEIGHT//2))

        with open('config.txt', 'r') as f:
            config = dict(
                line.strip().split('=')
                for line in f
                if line.strip() and not line.startswith('#')
            )
        mqtt_ip = config.get('mqtt_ip')
        mqtt_port = int(config.get('mqtt_port', '1883'))
        self.camera = Camera(self, mqtt_ip, mqtt_port)
        
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
            'particle/particle': Animation(load_images('particles/particle'), img_duration = 6, loop = False),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_duration=6),
            'enemy/run': Animation(load_images('entities/enemy/run'),img_duration=4),        
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),
        }
        
        self.sfx = {
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
            'blast': pygame.mixer.Sound('data/sfx/blast.mp3')

        }
        
        self.sfx['ambience'].set_volume(0.2)
        self.sfx['shoot'].set_volume(0.4)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
        self.sfx['blast'].set_volume(0.8)
        
        self.clouds = Clouds(self.assets['clouds'], count = 16)
          
        self.tilemap = Tilemap(self, tile_size = 16)
        
        self.spikes = Spikes(self, 200, 500,(-60, 300), (0.5, 2.5))
        
        self.current_level = 3
        
        self.boss_shape = Circle(self, 'red', (0,0), (16,16)) #placeholder, will be automatically generated later
        self.current_shape = None
        
        self.level_attributes = {
            0: Level(self, 0,False,Shape(self, 'square', 'blue', (12, 4)),(103 ,129)),
            1: Level(self, 1, False, Circle(self, 'green', (135, 2), (16, 16)),(103, 129)),
            2: Level(self, 2, True, self.boss_shape, (103, 129)),
            3: Level(self, 3, False, None,(103, 129))
        }
        

        
        self.load_level(self.current_level)
 
        self.screenshake = 0

        self.switched_boss_music = False
        self.font = pygame.font.Font(None, 14)
        self.boss_timer_start_ms = None
        self.boss_big_blast_interval_ms = 20000
        self.boss_big_blast_max_cooldown_ms = 7000
        self.big_blast = False
       
    def generate_random_shape(self, pos : list):
    
        shape_list = {
            0: 'square',
            1: 'triangle',
            2: 'circle'
        }
        color_list = {
                0:'red',
                1:'blue',
                2:'green',
                3:'yellow'
        }            
        shape_type = random.randint(0, 1)
        shape_color = random.randint(0, 3)
    
        if shape_type != 2:
            return Shape(self,shape_list[shape_type], color_list[shape_color], pos)

        return Circle(self, color_list[shape_color],pos,(16, 16))
    
    def load_level(self, map_id):
        self.player = Player(self, self.level_attributes[map_id].player_pos, (self.assets['player'].get_width(), self.assets['player'].get_height()))
        self.spikes.delete()
        self.spikes.collided_player = False
        self.spikes.enable_spawn = self.level_attributes[self.current_level].has_spikes
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))

        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
            
        
        self.scroll: list[float] = [0, 0]
        self.particles = []
        self.projectiles = []
        self.sparks = []
           
        self.dead = 0
        self.transition = -30
        
        if map_id == 2:
            self.boss_timer_start_ms = pygame.time.get_ticks()
            self.boss_total_time = pygame.time.get_ticks()
      
                

    def run(self): #! Can use the really cool particles for the big blast
        if self.current_level != 2:
            pygame.mixer.music.load('data/music.wav')
            
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)
        
        while True:
            
           
            self.display.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
            
            self.current_shape = self.camera.get_latest_shape()
            if self.current_shape is not None:
                #print(f"Detected shape:{self.current_shape.type, self.current_shape.color}") #type:ignore
                if self.current_shape.type == self.level_attributes[self.current_level].shape.type and self.current_shape.color == self.level_attributes[self.current_level].shape.color: #type: ignore
                    self.level_attributes[self.current_level].spawned_shape = True
                    #print("Shape imported")  
            
            if not len(self.enemies) and any(tile.get('type') == 'door' for tile in self.tilemap.tiles_around(self.player.pos)):
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
                    self.big_blast = False
                    self.level_attributes[self.current_level].spawned_shape = False
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
            
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset = render_scroll)
                #print(f"Player pos:{self.player.pos}")
                #print(f"Player Tile pos:{self.player.pos[0]//self.tilemap.tile_size, self.player.pos[1]//self.tilemap.tile_size}")
            
             # [[x, y], direction, timer]
            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)
                    for i in range(4):
                        self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                elif projectile[2] > 360:
                    self.projectiles.remove(projectile)
                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)
                        self.dead += 1
                        self.sfx['hit'].play()
                        self.screenshake = max(16, self.screenshake)
                        for i in range(30):
                            angle = random.random() * math.pi * 2
                            speed = random.random() * 5
                            self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                            self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                        
            if self.level_attributes[self.current_level].spawned_shape:
                if isinstance(self.level_attributes[self.current_level].shape, Circle):
                    circle : Circle = self.level_attributes[self.current_level].shape # type:ignore
                    circle.spawned = True
                    if circle.spawned:
                    
                        if self.player.rect().colliderect(self.level_attributes[self.current_level].shape.rect()): #type:ignore
                            if self.player.rect().x < self.level_attributes[self.current_level].shape.rect().x:   #type:ignore
                                self.level_attributes[self.current_level].shape.movement[1] = True  #type:ignore
                            if self.player.rect().x > self.level_attributes[self.current_level].shape.rect().x:  #type:ignore
                                self.level_attributes[self.current_level].shape.movement[0] = True  #type:ignore
                        else:
                            self.level_attributes[self.current_level].shape.movement = [False, False] #type:ignore
                        
                        self.level_attributes[self.current_level].shape.update(self.tilemap,(self.level_attributes[self.current_level].shape.movement[1] - self.level_attributes[self.current_level].shape.movement[0], 0))  #type:ignore
                        self.level_attributes[self.current_level].shape.render(self.display, offset= render_scroll)    #type:ignore
                if isinstance(self.level_attributes[self.current_level].shape, Shape):
                    if not self.level_attributes[self.current_level].shape.spawned:
                        self.level_attributes[self.current_level].shape.spawn()
                        
            
            #for spike in self.spikes.spikes:
             #   print(spike.pos)
            if not (self.big_blast and pygame.time.get_ticks() - self.boss_timer_start_ms < self.boss_big_blast_max_cooldown_ms): #type: ignore
                self.spikes.update(self.player.rect(), self.tilemap,generate_random=not self.big_blast)
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
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            if self.current_level == 1: 
               if self.level_attributes[self.current_level].spawned_shape and self.level_attributes[1].shape.pos[1] > 190: #type:ignore
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
            if self.current_level == 2 and self.boss_timer_start_ms is not None:
                elapsed_s = int((pygame.time.get_ticks() - self.boss_timer_start_ms) / 1000)
                timer_surf = self.font.render(f"{elapsed_s}", True, (0, 0, 0))
                self.display.blit(timer_surf, (4, 4))
                
                # Generate shape when interval is reached
                if pygame.time.get_ticks() - self.boss_timer_start_ms >= self.boss_big_blast_interval_ms:
                    if not self.big_blast:  # Only generate once
                        self.boss_timer_start_ms = pygame.time.get_ticks()
                        self.big_blast = True
                        self.boss_timer_start_ms = pygame.time.get_ticks()
                        self.spikes.delete()
                        self.spikes.generate_vertical_spike_list(10, 50)
                        self.boss_shape = self.generate_random_shape([6, 9])
                        self.level_attributes[self.current_level].shape = self.boss_shape #type: ignore
                        self.sfx['blast'].play(0)
                
                if self.big_blast:
                    shape_img = self.assets[self.boss_shape.type][self.boss_shape.colors[self.boss_shape.color]].copy() #type:ignore
                    shape_img.set_alpha(100)
                    
                    screen_x = 96 - int(self.scroll[0])
                    screen_y = 145 - int(self.scroll[1])
                    
                    self.display.blit(shape_img, (screen_x, screen_y))
                    if self.level_attributes[self.current_level].spawned_shape == True:
                        self.boss_shape.spawn() #type: ignore
                    
                    if pygame.time.get_ticks() - self.boss_timer_start_ms >= self.boss_big_blast_max_cooldown_ms + 1000:
                        #print("Spaned shape")
                        self.big_blast = False
                        self.boss_timer_start_ms = pygame.time.get_ticks()
                        self.boss_shape.delete() #type: ignore
                        self.level_attributes[self.current_level].spawned_shape = False
                        
            if self.current_level == 2 and pygame.time.get_ticks() - self.boss_total_time > 60000: 
                self.transition += 1 
                if self.transition > 30:
                    self.current_level = min(GameConfig.TOTAL_LEVELS - 1, self.current_level + 1)

                    self.load_level(self.current_level)    
                    

                
            
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
