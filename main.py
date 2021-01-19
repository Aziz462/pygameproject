import pygame, os, sys 


FPS = 60

size = width, height = 800, 800
pygame.init()
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Player(pygame.sprite.Sprite):
    def __init__(self, idle_sheet, run_sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.is_left = False
        self.idle_frames = []
        self.cut_sheet(idle_sheet, columns, rows, self.idle_frames)
        self.cur_frame = 0
        self.run_frames = []
        self.cut_sheet(run_sheet, 6, rows, self.run_frames)
        self.image = self.idle_frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.cur_state = 'idle'

    def cut_sheet(self, sheet, columns, rows, frames):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        if self.cur_state == 'idle':
            self.image = self.idle_frames[self.cur_frame]
        else:
            self.image = self.run_frames[self.cur_frame]
        self.image = pygame.transform.scale(self.image, (50, 50))
        if self.is_left:
            self.image = pygame.transform.flip(self.image, True, False)

        
        
    
    def move(self, x, y):
        self.rect = self.rect.move(x, y)
        self.image = self.run_frames[self.cur_frame]
        self.cur_state = 'run'
        self.update()


player = Player(load_image('idle_hero.png'), load_image('run_hero.png'), 4, 1, 50, 50)

z = 0

while True:
    z += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT or \
               event.key == pygame.K_DOWN or \
               event.key == pygame.K_UP or \
               event.key == pygame.K_LEFT:
                player.cur_state = 'idle'
    
    if z % 6 == 0:
        player.cur_frame = (player.cur_frame + 1) % len(player.idle_frames)
    # if keys[pygame.K_LEFT]:
    keys = pygame.key.get_pressed()
    x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 5
    y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 5
    if x:
        print(x)
        if x < 0:
            player.is_left = True
        elif x > 0:
            player.is_left = False
        player.move(x, 0)
    if y:
        player.move(0, y)
    # player.rect.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 10
    # player.rect.y += (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 10

    screen.fill(pygame.Color("black"))
    all_sprites.draw(screen)
    all_sprites.update()
    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()