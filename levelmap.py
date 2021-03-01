import pygame
import pytmx


class Layer:
    def __init__(self, index, levelmap, group):
        self.index = index
        print(self.index)

        self.tiles = pygame.sprite.Group()
        self.levelmap = levelmap
        for y in range(self.levelmap.height):
            for x in range(self.levelmap.width):
                image = self.levelmap.map.get_tile_image(x, y, self.index)
                if image:
                    self.tiles.add(Tile(x * self.levelmap.tile_size, y * self.levelmap.tile_size, image, group))

    def draw(self, screen):
        self.tiles.draw(screen)


class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile, group):
        pygame.sprite.Sprite.__init__(self, group)
        if tile:
            self.image = tile
            self.mask = pygame.mask.from_surface(self.image)
            self.isEmpty = False
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y
        else:
            self.image = None
            self.isEmpty = True



class LevelMap:
    def __init__(self, filename, screen, group):
        self.map = pytmx.load_pygame(filename)
        self.height = self.map.height
        self.width = self.map.width
        self.screen = screen
        self.tile_size = 15
        
        self.layers = []
        print(self.map.layers)
        for layer in range(len(self.map.layers)):
            self.layers.append(Layer(layer, self, group))
        print(self.layers)

    def render(self, screen):
        for layer in self.layers:
            layer.draw(screen)

    
    def get_tile_id(self, pos):
        return self.map.tiledgidmap[self.map.get_tile_gid(*pos, 0)]
    
