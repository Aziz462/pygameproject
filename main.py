import pygame, os, sys, random
from levelmap import LevelMap, Tile # класс карты и тайлов


FPS = 60 # кол-во кадров в секунду

size = width, height = 1000, 550 # размеры окна
pygame.init() # инициализация pygame
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group() # группы спрайтов
enemy_sprites = pygame.sprite.Group()
clock = pygame.time.Clock()


def end_screen(reason, score):
    """функция, которая создаёт заставку при конце игры"""
    if reason == 'dead': # текст, показывающийся при смерти игрока
        text = ["К сожалению во время ваших похождений",
                "вы были убиты.",
                f"Зато вы набрали {score} очков",]
    if reason == 'win': # текст показывающийся при победе игрока
        text = ["Вы открыли сундук...",
                "И он оказался пустым...",
                f"но зато вы заработали {score} очков"]
    

    # отображение текста на экране
    fon = pygame.transform.scale(load_image('gameover.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 150
    for line in text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.quit()
                sys.exit()
        pygame.display.flip()
        clock.tick(FPS)


def start_screen():
    """функция, которая создаёт заставку при запуске игры"""
    intro_text = ["Вы прибыли за сундуком с сокровищем,", 
                  "но он заперт ключом. Ваша задача - найти ключ,",
                  "но осторожнее, ведь не вы одни пришли за добычей...",
                  "a, d- ходьба, w - прыжок",
                  "зажать j и отпустить - выстрел из лука",
                  "k - удар мечом",
                  "подсказка - чтобы добраться до ключа, выпейте зелье в правом углу карты"]

    # отображение текста на экране
    fon = pygame.transform.scale(load_image('gameover.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 150
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)
        



def draw(screen, score, x, y):
    """функция, выводящая количество очков игрока"""
    font = pygame.font.Font(None, 30)
    text = font.render(score, True, (pygame.Color("yellow")))
    text_x = x
    text_y = y
    screen.blit(text, (text_x, text_y))


def load_image(name, colorkey=None):
    """загрузка изображений"""
    fullname = os.path.join('data', name)
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


# фон 
background = load_image("background.png")
background = pygame.transform.scale(background, (1100, 800))


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        
    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
    
    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)


class Item(pygame.sprite.Sprite):
    """класс для статичных объектов, к примеру ключ, сундук"""
    def __init__(self, idle_sheet, open_sheet, columns_rows, x, y):
        super().__init__(all_sprites)
        self.idle_frames = []
        self.cut_sheet(idle_sheet, columns_rows[0], self.idle_frames)
        self.open_frames = []
        self.cut_sheet(open_sheet, columns_rows[1], self.open_frames)
        self.cur_frame = 0
        self.image = self.idle_frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)
        self.opened = False

    def update(self):
        if not self.opened:
            self.image = self.idle_frames[self.cur_frame]
        else:
            self.image = self.open_frames[self.cur_frame]

    def open(self):
        if not self.opened:
            self.cur_frame = 0
            self.opened = True
        


    def cut_sheet(self, sheet, columns_rows, frames):
        columns, rows = columns_rows
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


class Player(pygame.sprite.Sprite):
    """класс игрока"""
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.invincibility = False # временная неуязвимость игрока после получения урона
        self.is_left = False 
        self.lives = 3 # количество жизней
        self.bowIsReady = False # заряжен ли лук
        self.potion = False # выпито ли зелье
        self.coins_count = 0 # количество собранных монет
        self.enemies_killed = 0 # количество убитых врагов
        self.key = False # был ли взят ключ
        self.cur_frame = 0 # текущий фрейм анимации
        self.idle_frames = [] # анимация бездействия
        self.cut_sheet(load_image('idle_hero.png'), 6, 1, self.idle_frames)
        self.fall_frames = [] # анимация падения 
        self.cut_sheet(load_image('fall_hero.png'), 6, 1, self.fall_frames)
        self.run_frames = [] # анимация бега
        self.cut_sheet(load_image('run_hero.png'), 6, 1, self.run_frames)
        self.jump_frames = [] # анимация прыжка
        self.cut_sheet(load_image('jump_hero.png'), 6, 1, self.jump_frames)
        self.hurt_frames = [] # анмация получения урона
        self.cut_sheet(load_image('hurt_hero.png'), 1, 1, self.hurt_frames)
        self.nock_frames = [] # анимация натягивания тетивы
        self.cut_sheet(load_image("nock.png"), 6, 1, self.nock_frames)
        self.loose_frames = [] # анимация выстрела из лука
        self.cut_sheet(load_image("loose.png"), 3, 1, self.loose_frames)
        self.attack_frames = [] # анимация атаки мечом
        self.cut_sheet(load_image("attack_hero.png"), 6, 1, self.attack_frames)
        self.image = self.idle_frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dx = 0 # передвижение по ординате x на каждое обновление персонажа
        self.dy = 0 # передвижение по ординате y на каждое обновление персонажа
        self.mask = pygame.mask.from_surface(self.image) # маска персонажа
        self.cur_state = 'idle' # текущее состояние 


    def cut_sheet(self, sheet, columns, rows, frames):
        """разрез листа спрайта на отдельные картинки"""
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))


    def update(self):
        if self.lives == 0: # конец игры, если у игрока закончились жизни
            end_screen('dead', self.coins_count + self.enemies_killed * 3)
        self.rect.x += self.dx 
        if self.dx < 0:
            self.is_left = True
        elif self.dx > 0:
            self.is_left = False

        collisionList = pygame.sprite.spritecollide(self, levelMap.layers[4].tiles, False)
        # определение пересечений игрока
        for tile in collisionList:
            if self.cur_state == 'hurt':
                self.dx = 0
                self.cur_state = 'idle'
            # передвижение игрока на правильную часть блока, чтобы предотворить погружение в тайлы
            elif self.dx > 0:
                self.rect.right = tile.rect.left
            else:
                self.rect.left = tile.rect.right

        self.rect.y += self.dy
        
        collisionList = pygame.sprite.spritecollide(self, levelMap.layers[4].tiles, False)
        if len(collisionList) > 0:
            if player.cur_state == 'hurt':
                self.dx = 0
                self.cur_state = 'idle'
            else:
                for tile in collisionList:
                    # передвижение игрока на правильную часть блока, чтобы предотворить погружение в тайлы
                    if self.dy > 0:
                        self.rect.bottom = tile.rect.top
                        self.dy = 1
                    else:
                        self.rect.top = tile.rect.bottom
                        self.dy = 0
                    if self.dx != 0:
                        if self.cur_state != 'hurt':
                            self.cur_state = 'run'
                    else:
                        if self.cur_state != 'nock' and self.cur_state != 'loose' and self.cur_state != 'attack':
                            self.cur_state = 'idle'
        else:
            # падение игрока, если под ним нет тайлов
            self.dy += 0.2
            if self.dy < 0 and self.cur_state != 'hurt':
                self.cur_state = 'jump'
            elif self.dy > 0 and self.cur_state != 'hurt':
                self.cur_state = 'fall'
        for coin in levelMap.layers[2].tiles:
            # сбор монет
            if pygame.sprite.collide_mask(player, coin):
                coin.kill()
                self.coins_count += 1
        if len(pygame.sprite.spritecollide(self, levelMap.layers[3].tiles, False)) > 0:
            # обработка падения в шипы
            end_screen('dead', self.coins_count + self.enemies_killed * 3)
        if pygame.sprite.collide_mask(self, key):
            # подбор ключа
            self.key = True
            key.open()
        if pygame.sprite.collide_mask(self, chest) and self.key:
            # открытие сундука
            chest.open()
        if self.cur_state != 'nock' and self.cur_state != 'loose' and self.bowIsReady:
            # снятие готовности лука при движении игрока во время натяжения тетивы
            self.bowIsReady = False
        for potion in levelMap.layers[1].tiles:
            # подбор зелья
            if pygame.sprite.collide_mask(self, potion):
                potion.kill()
                self.potion = True
        for enemy in enemy_sprites:
            # столкновение с противниками
            if pygame.sprite.collide_mask(self, enemy):
                if player.cur_state == 'attack':
                    enemy.hurt()
                elif player.cur_state != 'hurt' and enemy.cur_state != 'hurt':
                    player.hurt(enemy.direction)
                

        # смена фреймов анимации
        if self.cur_state == 'idle':
            self.image = self.idle_frames[self.cur_frame]
        elif self.cur_state == 'nock':
            self.image = self.nock_frames[self.cur_frame]
        elif self.cur_state == 'loose':
            self.image = self.loose_frames[self.cur_frame]
        elif self.cur_state == 'attack':
            self.image = self.attack_frames[self.cur_frame]
        elif self.cur_state == 'hurt':
            self.image = self.hurt_frames[self.cur_frame]
        elif self.cur_state == "run":
            self.image = self.run_frames[self.cur_frame]
        elif self.cur_state == 'jump':
            self.image = self.jump_frames[self.cur_frame]
        elif self.cur_state == 'fall':
            self.image = self.fall_frames[self.cur_frame]
        if self.is_left:
            self.image = pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    
    def move(self, x):
        """передвижение игрока"""
        self.dx += x
        if self.cur_state != 'jump' and self.cur_state != 'fall':
            self.image = self.run_frames[self.cur_frame]
            self.cur_state = 'run'
        
    def jump(self):
        """обработка прыжка"""
        self.rect.y += 2
        
        collision = pygame.sprite.spritecollide(self, levelMap.layers[4].tiles, False)
        self.rect.y -= 2

        if len(collision) > 0:
            self.cur_state = "jump"
            if not self.potion:
                self.dy = -6
            else:
                self.dy = -10
            self.update()
    
    def hurt(self, direction):
        """получение урона"""
        if not self.invincibility: 
            self.invincibility = True
            pygame.time.set_timer(pygame.USEREVENT, 1000)
            self.cur_frame = 0
            if direction == 'right':
                self.dx += 4
                self.dy += -3
            else:
                self.dx -= 4
                self.dy += -3
            self.lives -= 1
            self.cur_state = 'hurt'
    
    def nock(self):
        """натяжение тятивы"""
        self.bowIsReady = False
        self.cur_state = 'nock'
    
    def loose(self):
        """выстрел из лука"""
        self.cur_state = 'loose'
        dx = -10 if self.is_left else 10 
        self.arrow = Arrow(self.rect.x, self.rect.y, dx, self.is_left, self)
    
    def attack(self):
        """удар мечом"""
        self.cur_state = 'attack'

        

class Arrow(pygame.sprite.Sprite):
    """класс стрел, выпускаемых игроком"""
    def __init__(self, x, y, dx, is_left, player):
        super().__init__(all_sprites)
        self.image = load_image("arrow.png")
        self.rect = self.image.get_rect()
        self.rect.x = x 
        self.rect.y = y
        self.player = player
        if is_left:
            self.image = pygame.transform.flip(self.image, True, False)
        self.dx = dx
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        """обработка попадания"""
        self.rect.x += self.dx
        collision = []
        for tile in levelMap.layers[4].tiles:
            if pygame.sprite.collide_mask(tile, self):
                collision.append(tile)
        for enemy in enemy_sprites:
            if pygame.sprite.collide_mask(self, enemy):
                self.kill()
                enemy.hurt()
        if len(collision) > 0:
            self.kill()
            


        


class Enemy(pygame.sprite.Sprite):
    def __init__(self, columns, rows, x, y):
        super().__init__(all_sprites, enemy_sprites)
        self.is_right = False
        self.direction = None # направление, в котором находится герой
        self.standing_frames = [] # анимация бездействия противников
        self.cut_sheet(load_image("Standing.png"), 1, 1, self.standing_frames)
        self.walking_frames = [] # анимация ходьбы противников
        self.cut_sheet(load_image("Walking.png"), 2, 1, self.walking_frames)
        self.hurt_frames = [] # анимация получения урона противников
        self.cut_sheet(load_image("enemy_hurt.png"), 1, 1, self.hurt_frames)
        self.cur_frame = 0 # текущий фрейм анимации
        self.image = self.standing_frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.dx = 0 # передвижение по ординате x на каждое обновление 
        self.dy = 0 # передвижение по ординате y на каждое обновление
        self.cur_state = 'standing' # текущее состояние

    def cut_sheet(self, sheet, columns, rows, frames):
        """разрез листа спрайта на отдельные картинки"""
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))
    
    def update(self):
        if self.direction == 'right':
            self.dx += 1
            self.is_right = True
        elif self.direction == 'left':
            self.dx -= 1
            self.is_right = False
        self.rect.x += self.dx
        # проверка на пересечения
        collisionList = pygame.sprite.spritecollide(self, levelMap.layers[4].tiles, False)
        for tile in collisionList:
            if self.dx > 0:
                self.rect.right = tile.rect.left
            else:
                self.rect.left = tile.rect.right
        self.rect.y += self.dy
        # проверка на пересечения
        collisionList = pygame.sprite.spritecollide(self, levelMap.layers[4].tiles, False)
        if len(collisionList) > 0:
            for tile in collisionList:
                if self.cur_state == 'hurt':
                    self.dx = 0
                    self.kill()
                if self.dy > 0:
                    self.rect.bottom = tile.rect.top
                    self.dy = 1
                else:
                    self.rect.top = tile.rect.bottom
                    self.dy = 0
                # определение анимации при нападения на героя
                if abs(player.rect.x - self.rect.x) > 3 and abs(player.rect.x - self.rect.x) < 250 and self.cur_state != 'hurt':
                    if abs(player.rect.y - self.rect.y) > 5 and abs(player.rect.y - self.rect.y) < 100:
                        self.cur_state = 'walking'
                else:
                    self.cur_state = 'standing'
        else:
            self.dy += 0.2
            self.cur_state == 'standing'

        # смена фрейма анимации
        if self.cur_state == 'standing':
            self.image = self.standing_frames[0]
        elif self.cur_state == 'walking':
            self.image = self.walking_frames[self.cur_frame]
        elif self.cur_state == 'hurt':
            self.image = self.hurt_frames[self.cur_frame]
        if self.is_right:
            self.image = pygame.transform.flip(self.image, True, False)
        
        # определение направления, в котором находится герой
        if abs((player.rect.x + player.rect.w // 2) - self.rect.x) < 250 and abs(player.rect.y - self.rect.y) > 5 and abs(player.rect.y - self.rect.y) < 100:
            self.direction = "right" if ((player.rect.x + player.rect.w // 2) - self.rect.x) > 0 else "left"
        else:
            self.direction = None
        self.dx = 0
    
    def hurt(self):
        """обработка получения урона"""
        if self.cur_state != 'hurt':
            self.cur_frame = 0
            self.dx -= 4
            self.dy += -3
            self.cur_state = 'hurt'
            player.enemies_killed += 1


# картинка для отображения здоровья игрока
heart = load_image("heart.png")
heart = pygame.transform.scale(heart, (20, 20))
      

player = Player(600, 1201) # объявление героя
key = Item(load_image("idle_key.png"), load_image("key_taken.png"), ((8, 1), (5, 1)), 2058, 903) # объявление ключа
chest = Item(load_image("chest_idle.png"), load_image("chest_unlocked.png"), ((1, 1), (8, 1)), 530, 1183) # объявление сундука

#объявление врагов
enemy1 = Enemy(2, 1, 2000, 700)
enemy2 = Enemy(2, 1, 2000, 1100)
enemy3 = Enemy(2, 1, 2400, 200)
ememy4 = Enemy(2, 1, 2600, 213)

levelMap = LevelMap("map.tmx", screen, all_sprites) # объявление карты
camera = Camera() # объявление камеры
start_screen() # запуск заставки


def health():
    """Функция, отображающая здоровье игрока на экране"""
    x = 8
    for i in range(player.lives):
        screen.blit(heart, (x, 40))
        x += 30


z = 0
while True:
    z += 1
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # обработка закрытия игры
            pygame.quit()
            sys.exit()
        if event.type == pygame.USEREVENT: # обработка конца неуязвимости игрока
            if player.invincibility:
                player.invincibility = False
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_w: # обработка прыжка
                player.jump()
            if event.key == pygame.K_j: # обработка натяжения тетивы
                player.cur_frame = 0
                player.nock()
            if event.key == pygame.K_k: # обработка удара мечом
                player.cur_frame = 0
                player.attack()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a: 
                player.cur_state = 'idle'
                player.dx = 0
            if event.key == pygame.K_d:
                player.cur_state = 'idle'
                player.dx = 0
            if event.key == pygame.K_j: # обработка выстрела
                if player.bowIsReady:
                    player.loose()
                player.cur_frame = 0
    
    keys = pygame.key.get_pressed()
    if z % 6 == 0:
        if player.cur_state == 'nock' and player.cur_frame == 5:
            player.bowIsReady = True
        elif player.cur_state == 'nock' and not keys[pygame.K_j]:
            player.bowIsReady = False
            player.cur_state = 'idle'
        elif player.cur_state == 'hurt':
            pass
        elif player.cur_state == 'loose' and player.cur_frame > 1:
            player.cur_state = 'idle'
        elif player.cur_state == 'jump' and player.cur_frame == 5:
            pass
        else:
            player.cur_frame = (player.cur_frame + 1) % len(player.idle_frames)

        if key: # смена фрейма анимации ключа
            key.cur_frame = (key.cur_frame + 1) % len(player.idle_frames)
        if key.opened and key.cur_frame == 4:
            key.kill()
        if chest.cur_frame == 7: 
            chest.kill()
        if chest.opened: # смена фрейма анимации сундука
            chest.cur_frame = (chest.cur_frame + 1) % len(chest.open_frames)
        if chest.opened and chest.cur_frame == 7: # конец игры, если закончена анимация открытия сундука
            end_screen('win', player.coins_count + player.enemies_killed * 3)
        for enemy in enemy_sprites: # смена фрейма анимации врагов
            if enemy.cur_state == 'walking': 
                enemy.cur_frame = (enemy.cur_frame + 1) % len(enemy.walking_frames)


    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.dx = -5
    if keys[pygame.K_d]:
        player.dx = 5
    if player.cur_state == 'nock' and not keys[pygame.K_j]:
        player.cur_state == 'idle'
    
    
        


    camera.update(player) # следование камеры за игроком
    for sprite in all_sprites:
        camera.apply(sprite)
    screen.fill(pygame.Color("black"))
    screen.blit(background, (0, 0)) # фон
    levelMap.render(screen) # рендер карты 
    all_sprites.draw(screen) # отрисовка спрайтов 
    all_sprites.update() 
    draw(screen, str(player.coins_count + player.enemies_killed * 3), 10, 10) # вывод на экран счёта игрока
    health() 
    pygame.display.flip() # обновление экрана 
    clock.tick(FPS) 
