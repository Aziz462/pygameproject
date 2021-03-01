import pygame
import pytmx


class Layer:
    """класс слоя, хранящий тайлы"""
    def __init__(self, index, levelmap, group):
        self.index = index # номер слоя

        self.tiles = pygame.sprite.Group()
        self.levelmap = levelmap
        # в цикле тайлы добавляются в слой
        for y in range(self.levelmap.height):
            for x in range(self.levelmap.width):
                image = self.levelmap.map.get_tile_image(x, y, self.index)
                if image:
                    self.tiles.add(Tile(x * self.levelmap.tile_size, y * self.levelmap.tile_size, image, group))

    def draw(self, screen):
        """Функция рисует тайлы на экране"""
        self.tiles.draw(screen)


class Tile(pygame.sprite.Sprite):
    # класс тайла
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
    # класс всей карты
    def __init__(self, filename, screen, group):
        self.map = pytmx.load_pygame(filename) # загрузка карты
        # определение констант карты
        self.height = self.map.height 
        self.width = self.map.width
        self.tile_size = 15

        self.screen = screen       
        
        # создание и заполнение слоёв
        self.layers = []
        for layer in range(len(self.map.layers)):
            self.layers.append(Layer(layer, self, group))

    def render(self, screen):
        # вывод тайлов слоёв на экран
        for layer in self.layers:
            layer.draw(screen)