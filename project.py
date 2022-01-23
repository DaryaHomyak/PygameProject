import pygame
import sqlite3
import os
import sys
import random
import time

WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 60
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)

pygame.display.set_caption("Race Game")
clock = pygame.time.Clock()
speed = 10


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


def print_text(message="", x=0, y=0, font_color='black', font_size=30, frame_color=None, frame_indent=0, frame_width=1):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
    if frame_color:
        pygame.draw.rect(screen, frame_color, (
            x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2,
            text.get_rect()[3] + frame_indent * 2), frame_width)
    return (x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2 + x,
            text.get_rect()[3] + frame_indent * 2 + y)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


def start_screen():
    fon1 = load_image('start_fon8.jpeg')
    fon_img = pygame.transform.scale(fon1, (fon1.get_width() * 0.25, fon1.get_height() * 0.25))
    screen.blit(fon_img, (0, 0))
    work = True
    pygame.FONCHANGE = pygame.USEREVENT + 1
    y1_snow, y2_snow = 0, -HEIGHT
    while work:
        clock.tick(10)
        screen.blit(fon_img, (0, 0))
        play_btn = print_text('Играть!', 30, 100, 'grey', 200, 'grey')
        shop_btn = print_text('Магазин', 30 // 2, 270, 'grey', 200, 'grey')
        settings_btn = print_text('Настройки', 30 // 2, 440, 'grey', 200, 'grey')
        y1_snow = y1_snow + speed if y1_snow < HEIGHT else -HEIGHT + speed
        y2_snow = y2_snow + speed if y2_snow < HEIGHT else -HEIGHT + speed
        screen.blit(pygame.transform.scale(load_image('snow.png'), (WIDTH, HEIGHT)), (0, y1_snow))
        screen.blit(pygame.transform.scale(load_image('snow.png'), (WIDTH, HEIGHT)), (0, y2_snow))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.FONCHANGE:
                pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn[0] < event.pos[0] < play_btn[2] and play_btn[1] < event.pos[1] < play_btn[3]:
                    return

                elif shop_btn[0] < event.pos[0] < shop_btn[2] and shop_btn[1] < event.pos[1] < shop_btn[3]:
                    return shop()
                elif settings_btn[0] < event.pos[0] < settings_btn[2] and settings_btn[1] < event.pos[1] < settings_btn[
                    3]:
                    print('settings')
        pygame.display.flip()


# конект с бд
con = sqlite3.connect("Race project")
cur = con.cursor()


def shop():
    COIN_COLOR = (234, 156, 0)

    def cars_draw(last_choice=0):
        # отрисовка машинок, цен, статусов
        x, y = 750, 0
        cars_bords = list()
        for car in cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall():
            car_img = pygame.transform.scale(load_image(car[3] + '.png', None), (180, 180))
            car_stat, car_price = car[1], int(car[2])
            screen.blit(car_img, (x, y))
            if car_stat == 'unlock' or car_stat == 'choosed':
                print_text('purchased', x + 60, y + 160, 'green', 25)
            else:
                print_text(str(car_price), x + 70, y + 160, 'yellow', 30)
            cars_bords.append((x, y, x + 180, y + 180))
            y = y + 180 if x == 1110 else y
            x = x + 180 if x < 1110 else 750

        name, stat, price, img = car_info = cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall()[
            last_choice]

        # отрисовка выбранной машинки
        screen.blit(pygame.transform.scale(load_image(img + '.png'), (700, 700)), (5, 50))

        # отрисовка квадрата подсветки
        clck = cars_bords[last_choice]
        pygame.draw.rect(screen, 'grey', (clck[0], clck[1], clck[2] - clck[0], clck[3] - clck[1]), 1)

        # отрисовка статуса машинок
        if stat == 'lock':
            buy_bords = print_text(f'Купить за {price}', 100, 800, COIN_COLOR, 100, (234, 156, 0),
                                   10)
        elif stat == 'choosed':
            buy_bords = print_text('Выбрано', 100, 800, (170, 226, 57), 100, 'green', 10)

        else:
            buy_bords = print_text('Взять', 100, 800, (32, 119, 42), 100, 'green', 10)
        return cars_bords, buy_bords, car_info

    def coins_draw():
        screen.blit(pygame.transform.scale(load_image('coin.png'), (40, 40)), (200, 0))
        print_text(str(cur.execute("""SELECT * FROM progress""").fetchall()[0][1]), 250, 0, COIN_COLOR, 68)

    def screen_reset(last_choice):
        screen.blit(pygame.transform.scale(load_image('shop_fon4.jpg'), (WIDTH, HEIGHT)), (0, 0))
        cars_draw(last_choice)
        coins_draw()
        # кнопка выхода в главное меню
        exit_bords = print_text('Выход', 0, 0, 'red', 50, 'red', 20, 5)
        return exit_bords

    last_choice = 0
    # фон
    screen.blit(pygame.transform.scale(load_image('road.png'), (WIDTH, HEIGHT)), (0, 0))
    # отрисовка баланса
    coins_draw()
    exit_bords = screen_reset(last_choice)

    # цикл отрисовки
    while True:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # нажатие на мышку ( выбор машинки/покупка машинки/выход из магазина )
            elif event.type == pygame.MOUSEBUTTONDOWN:

                cars_bords, buy_bords, car_info = cars_draw(last_choice)
                # проверка на клик по машинке
                for index, clck in enumerate(cars_bords):
                    if clck[0] < event.pos[0] < clck[2] and clck[1] < event.pos[1] < clck[3]:
                        last_choice = index
                        cars_bords, buy_bords, car_info = cars_draw(last_choice)
                        screen_reset(last_choice)
                        name, stat, price, img = car_info

                # проверка на клик по кнопке "купить"
                if buy_bords[0] < event.pos[0] < buy_bords[2] and buy_bords[1] < event.pos[1] < buy_bords[3]:
                    coins = cur.execute("""SELECT * FROM progress""").fetchall()[0][1]

                    # покупка
                    if coins >= price and stat == 'lock':
                        cur.execute(f'''UPDATE car_icons SET status = 'unlock' WHERE name = '{name}' ''')
                        cur.execute(f'''UPDATE progress SET coins == {coins - price}''')
                        con.commit()
                        print_text(f'Вы приобрели {name}', 50, WIDTH // 2, 'green', 100)

                    elif coins < price and stat == 'lock':
                        print_text(f'Недостаточно средств', 50, WIDTH // 2, 'red', 100)

                    elif stat == 'unlock':
                        cur.execute(f'''UPDATE car_icons SET status = 'unlock' WHERE status = 'choosed' ''')
                        cur.execute(f'''UPDATE car_icons SET status = 'choosed' WHERE name = '{name}' ''')
                        con.commit()

                    elif stat == 'choosed':
                        print_text(f'Машина уже выбрана', 50, WIDTH // 2, 'yellow', 100)

                    screen_reset(last_choice)

                # выход из магазина
                if exit_bords[0] < event.pos[0] < exit_bords[2] and exit_bords[1] < event.pos[1] < exit_bords[3]:
                    return start_screen()

            pygame.display.flip()


class Coins(pygame.sprite.Sprite):
    def __init__(self, line, *groups):
        super().__init__(*groups)
        con = sqlite3.connect("Race project")
        cur = con.cursor()
        #    img = load_image('truck.png')
        imgs = cur.execute("""SELECT link FROM car_icons ORDER BY price""").fetchall()
        print(imgs[random.randint(0, len(imgs) - 1)][0] + '.png')
        self.image = pygame.transform.rotate(load_image(imgs[random.randint(0, len(imgs) - 1)][0] + '.png'), 270)
        self.image = pygame.transform.scale(self.image, (256, 256))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = WIDTH
        self.rect.y = line * 150 + 60

    def truck_crash(self):
        self.image = pygame.transform.scale(load_image('broken_heart.png'), (60, 60))

    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)
        self.rect.x -= 30


class Truck(pygame.sprite.Sprite):

    def __init__(self, line, *groups):
        super().__init__(*groups)
        con = sqlite3.connect("Race project")
        cur = con.cursor()
        imgs = list(cur.execute("""SELECT link FROM car_icons WHERE status != "choosed" ORDER BY price """).fetchall())
        imgs.append(['truck'])
        print(imgs[random.randint(0, len(imgs) - 1)][0] + '.png')
        self.image_name = imgs[random.randint(0, len(imgs) - 1)][0] + '.png'
        self.image = pygame.transform.scale(load_image(self.image_name), (256, 256))
        self.image = pygame.transform.rotate(self.image, 270 if self.image_name != 'truck.png' else 180)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = WIDTH
        self.rect.y = line * 150 + 60

    def truck_crash(self):
        self.image = pygame.transform.scale(load_image('broken_heart.png'), (60, 60))

    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)
        self.rect.x -= 30
        for c in car_sprites:
            if pygame.sprite.collide_mask(self, c):
                self.truck_crash()



class Car(pygame.sprite.Sprite):
    con = sqlite3.connect("Race project")
    cur = con.cursor()
    image = load_image(cur.execute("""SELECT link FROM car_icons WHERE status == 'choosed' """).fetchone()[0] + '.png')
    image = pygame.transform.rotate(image, 90)

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = Car.image
        self.image = pygame.transform.scale(self.image, (256, 256))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.heart = 3

        self.rect.x = 0
        self.rect.y = 210

    def line_move(self, pressed_keys):
        if pressed_keys[pygame.K_UP]:
            if self.rect.y > 300:
                self.rect.y -= 150
        if pressed_keys[pygame.K_DOWN]:
            if self.rect.y < 500:
                self.rect.y += 150

    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)



# пауза игры
def pause():
    paused = True
    while paused:
        print_text('Пауза. Нажмите пробел для продолжения.', 50, 500, 'white', 70)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_PAUSE]:
                    return
def finish_screen():
    pass

# запуск начального экрана
start_screen()

# создание объектов
all_sprites = pygame.sprite.Group()

car_sprites = pygame.sprite.Group()
car1 = Car(car_sprites, all_sprites)
truck_sprites = pygame.sprite.Group()


x1_road, x2_road = 0, WIDTH
x1_snow, y1_snow, x2_snow, y2_snow, x3_snow, y3_snow, x4_snow, y4_snow, = 0, 0, -WIDTH, -HEIGHT, 0, -HEIGHT, WIDTH, 0
time_count = 0
metres = 0
MYEVENTTYPE = pygame.USEREVENT + 1
TIMEREVENT = pygame.USEREVENT + 2
pygame.time.set_timer(MYEVENTTYPE, 10000)
pygame.time.set_timer(TIMEREVENT, 1000)
running = True
while running:
    screen.fill('black')
    fon = pygame.transform.scale(load_image('town0.png', None), (WIDTH, 1000))

    # отрисовка подвижной дороги
    road = pygame.transform.scale(load_image('town0_1.png', None), (WIDTH, 1000))
    x1_road = x1_road - speed if x1_road > -WIDTH else WIDTH - speed
    x2_road = x2_road - speed if x2_road > -WIDTH else WIDTH - speed
    metres = metres + 1 if x1_road % 128 == 0 or x2_road % 128 == 0 else metres
    screen.blit(road, (x1_road, 0))
    screen.blit(road, (x2_road, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            for car in car_sprites:
                car.line_move(pygame.key.get_pressed())
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                pause()
                print('pause')
            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                start_screen()
        elif event.type == MYEVENTTYPE:
            truck = Truck(random.randint(1, 3), truck_sprites, all_sprites)
        elif event.type == TIMEREVENT:
            time_count += 1

    truck_sprites.update()
    car_sprites.update()

    # отрисовка гг
    car_sprites.draw(screen)

    # отрисовка остальных машин
    truck_sprites.draw(screen)

    # отрисовка снега
    snow = pygame.transform.scale(load_image('snow6.png'), (WIDTH, HEIGHT))
    x1_snow = x1_snow - speed if x1_snow > -WIDTH else WIDTH - speed
    x2_snow = x2_snow - speed if x2_snow > -WIDTH else WIDTH - speed
    x3_snow = x3_snow - speed if x3_snow > -WIDTH else WIDTH - speed
    x4_snow = x4_snow - speed if x4_snow > -WIDTH else WIDTH - speed

    y1_snow = y1_snow + speed if y1_snow < HEIGHT else -HEIGHT + speed
    y2_snow = y2_snow + speed if y2_snow < HEIGHT else -HEIGHT + speed
    y3_snow = y3_snow + speed if y3_snow < HEIGHT else -HEIGHT + speed
    y4_snow = y4_snow + speed if y4_snow < HEIGHT else -HEIGHT + speed

    screen.blit(snow, (x1_snow, y1_snow))
    screen.blit(snow, (x2_snow, y2_snow))
    screen.blit(snow, (x3_snow, y3_snow))
    screen.blit(snow, (x4_snow, y4_snow))
    # отрисовка  таймера
    print_text(time.strftime("%M:%S", time.gmtime(time_count)), 10, 10, 'white', 100)
    # отрисовка расстояния
    print_text(str(metres) + 'metres', 250, 10, 'white', 100)
    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()
con.close()
