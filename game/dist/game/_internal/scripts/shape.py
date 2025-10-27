import pygame

class Shape: # This is just for triangles and squares, circles are a bit more complicated
    def __init__(self, game, shape_type: str, color: str, tile_pos):
        self.game = game
        self.type = shape_type
        self.color = color
        self.tile_pos = list(tile_pos)
        self.spawned = False
        self.colors = {
            'red': 0,
            'green': 1,
            'blue': 2,
            'yellow': 3
        }
        self.size = {
            'square': (2, 2),
            'triangle': (2, 3)
        }.get(shape_type,(1, 1))
        
    def spawn(self):
       #print(self.type, self.color, self.tile_pos)
       self.spawned = True
       location = f"{self.tile_pos[0]};{self.tile_pos[1]}"
       self.game.tilemap.tilemap[location] = {
           'type': self.type,
           'variant': self.colors[self.color],
           'pos': list(self.tile_pos)
       }
    def delete(self):
        location = f"{self.tile_pos[0]};{self.tile_pos[1]}"
        if self.game.tilemap.tilemap[location] is not None:
            del self.game.tilemap.tilemap[location]
class Circle():
    def __init__(self, game, color, pos, size):
        self.game = game
        self.size = size
        self.pos = list(pos)
        self.velocity : list[float] = [0, 0]
        self.color = color
        self.type = 'circle' 
        self.animation = self.game.assets[f"{self.type}/{self.color}"].copy()
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}
        self.spawned = False
        self.flip = False
        self.movement = [False, False]
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
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
                
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
        
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        if movement[0] != 0:
            self.animation.update()
        
    def render(self, surface, offset = (0, 0)):
        surface.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1]))
    