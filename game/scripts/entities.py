import pygame
import math
import random
import time
from scripts.particle import Particle
from scripts.spark import Spark

class PhysicsEntity:
    
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity : list[float] = [0, 0] 
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
        
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tilemap, movement = (0, 0)):
        
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
         
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_rects_around(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y        

        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement 
                    
        self.velocity[1] = min(5, self.velocity[1] + 0.1) 
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
    def render(self, surface, offset = (0, 0)):
        surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
       

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game,'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.slamming = False
        self.dashing = 0
        
        
    def update(self, tilemap, movement=(0, 0)):
        
        super().update(tilemap, movement=movement)
    
        
        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            self.slamming = False
     
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
            
        if not self.wall_slide:
            if not self.slamming:    
                if self.air_time > 4:
                    self.set_action('jump')
                elif movement[0] != 0:
                    self.set_action('run')
                else:
                    self.set_action('idle')
            else:
                self.set_action('slam')

        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center,velocity=pvelocity, frame=random.randint(0, 7) ))


        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center,velocity=pvelocity, frame=random.randint(0, 7) ))

       
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
    
    def render(self, surface, offset = (0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surface, offset=offset)
        
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        elif self.jumps:
            self.slamming = False
            self.jumps -= 1
            self.velocity[1] = -3.3
            self.air_time = 5
            return True
    def ground_slam(self):
        if not self.wall_slide and not self.collisions['down']:
            self.velocity[1] = 10 
            self.slamming = True
    def dash(self):
        if not self.dashing:
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60

class Spike:
    def __init__(self, game, pos, x_velocity):
        self.game = game
        self.pos = list(pos)
        
        self.x_velocity = x_velocity
        self.animation = self.game.assets['spike'].copy()
        self.size = (15, 9)
        self.spawn_time = pygame.time.get_ticks()
        self.anim_offset = (-1, -1)   
        self.collided_player = False
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])

    def update(self, player_rect):
        
        if not self.collided_player and player_rect.colliderect(self.rect()):
            self.collided_player = True
            for i in range(30):
                angle = random.random() * math.pi * 2
                speed = random.random() * 5
                self.game.sparks.append(Spark(self.rect().center, angle, 2 + random.random()))
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center,velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
            self.game.sparks.append(Spark(self.rect().center, math.pi, 5 + random.random()))
            self.game.sparks.append(Spark(self.rect().center, 0 , 5 + random.random()))
        
        
        self.pos[0] -= self.x_velocity
        #print(f"Spike: {self.pos}")
        self.animation.update()
        
    def render(self, surface, offset = (0, 0)):
        surface.blit(self.animation.img(), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        
        
class Spikes:
    def __init__(self,game, spawn_interval_seconds, start_x, y_limits, speed_limits):
        self.game = game
        self.spawn_interval = spawn_interval_seconds
        self.start_x = start_x
        self.min_y = y_limits[0]
        self.max_y = y_limits[1]
        self.min_speed = speed_limits[0]
        self.max_speed = speed_limits[1]    
        
        self.collided_player = False
        self.spike_collided_player_index = None
        
        self.enable_spawn = False
        
        self.last_spawn_ms = 0
        self.spikes = []
        
        self.max_spike_spawn_time_ms = int(15 * 1000)
    
    def delete(self):
        self.spikes.clear()
        
    def update(self, player_rect):
        if not self.enable_spawn:
            return
        
        if pygame.time.get_ticks() - self.last_spawn_ms >= self.spawn_interval:
            self.last_spawn_ms = pygame.time.get_ticks()
            start_y = random.randint(self.min_y, self.max_y)
            spike_velocity = random.uniform(self.min_speed, self.max_speed)
            
            self.spikes.append(Spike(self.game,(self.start_x, start_y),spike_velocity))
        
        for spike_index, spike in enumerate(self.spikes):
            spike.update(player_rect)
            
            if spike.collided_player:
                self.collided_player = True
                
                self.spike_collided_player_index = spike_index
            
            if pygame.time.get_ticks() - spike.spawn_time >= self.max_spike_spawn_time_ms:
                self.spikes.remove(spike)
                
    def render(self, surface, offset = (0, 0)):
        if not self.enable_spawn:
            return
        for spike in self.spikes:
            spike.render(surface, offset = offset)
    
