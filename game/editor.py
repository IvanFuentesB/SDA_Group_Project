import pygame
from dataclasses import dataclass

from scripts.utils import load_images, load_image
from scripts.tilemap import Tilemap



@dataclass
class GameConfig:
    SCREEN_LENGHT = 640
    SCREEN_HEIGHT = 480
    CAMERA_FOLLOW_SPEED = 5 # Lower is faster
    FRAMERATE = 60
    RENDER_SCALE = 2.0

class Editor:
    def __init__(self) -> None:
        pygame.init()

        pygame.display.set_caption('editor')
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_LENGHT, GameConfig.SCREEN_HEIGHT))

        self.display = pygame.Surface((GameConfig.SCREEN_LENGHT//2, GameConfig.SCREEN_HEIGHT//2))

        self.clock = pygame.time.Clock()

        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor':load_images('tiles/large_decor'),
            'stone':load_images('tiles/stone'),
            'door':load_images('tiles/door')
        }
        
        self.movement = [False, False, False, False]
        
        self.tilemap = Tilemap(self, tile_size = 16)
        
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass
        
        self.scroll: list[float] = [0, 0]
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        
        self.left_clicking = False
        self.right_clicking = False
        self.shift = False
        self.on_grid = True
        
    def run(self):
        while True:
            self.display.fill((0, 0, 0))
            
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.tilemap.render(self.display, offset = render_scroll)
            
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(100)
            
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / GameConfig.RENDER_SCALE, mpos[1] / GameConfig.RENDER_SCALE)
            tile_position = (int((mpos[0] + self.scroll[0]) // self.tilemap.tile_size), int((mpos[1] + self.scroll[1]) // self.tilemap.tile_size))
            
            if self.on_grid:
                self.display.blit(current_tile_img, (tile_position[0] * self.tilemap.tile_size - self.scroll[0], tile_position[1] * self.tilemap.tile_size - self.scroll[1]))
            else:
                self.display.blit(current_tile_img, mpos)
                
            if self.left_clicking and self.on_grid:
                self.tilemap.tilemap[str(tile_position[0]) + ';' + str(tile_position[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_position}
            if self.right_clicking:
                tile_location = str(tile_position[0]) + ';' + str(tile_position[1])
                if tile_location in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_location]
                for tile in self.tilemap.offgrid_tiles.copy():
                    tile_img = self.assets[tile['type']][tile['variant']]
                    tile_r = pygame.Rect(tile['pos'][0] - self.scroll[0], tile['pos'][1] - self.scroll[1], tile_img.get_width(), tile_img.get_height())
                    if tile_r.collidepoint(mpos):
                        self.tilemap.offgrid_tiles.remove(tile)
                    
                
            self.display.blit(current_tile_img, (5, 5))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_clicking = True
                        if not self.on_grid:
                            self.tilemap.offgrid_tiles.append({'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': (mpos[0] + self.scroll[0], mpos[1] + self.scroll[1])}) 
                    if event.button == 3:
                        self.right_clicking = True
                    if self.shift:
                        if event.button == 4:
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        if event.button == 4:
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_clicking = False
                    if event.button == 3:
                        self.right_clicking = False
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        self.movement[3] = True
                    if event.key == pygame.K_g:
                        self.on_grid = not self.on_grid
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:
                        self.shift = False
                        
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))            
            pygame.display.update()
            self.clock.tick(GameConfig.FRAMERATE)
            
Editor().run()
