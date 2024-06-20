import pygame
import sqlite3
import os
import sys
import random
import time

WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 10
COIN_COLOR = (234, 156, 0)
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
pygame.display.set_caption("Race Game")
clock = pygame.time.Clock()
coll_sound = pygame.mixer.Sound('data\sound_collide.wav')

speed = 10
paused = False
con = sqlite3.connect("Race project")
cur = con.cursor()


# функция для загрузки изображений
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


# функция для удобного вывода текста на экран
def print_text(message="", x=0, y=0, font_color='black', font_size=30, frame_color=None, frame_indent=0, frame_width=1):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
    if frame_color:
        pygame.draw.rect(screen, frame_color, (
            x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2,
            text.get_rect()[3] + frame_indent * 2), frame_width)
    screen.blit(text, (x, y))
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


# начальный экран
def start_screen():
    global paused
    # музыка для начального экрана
    pygame.mixer.music.stop()
    pygame.mixer.music.load("data/music_start.mp3")
    pygame.mixer.music.play(-1)
    # изображение
    fon1 = load_image('start_fon8.jpeg')
    fon_img = pygame.transform.scale(fon1, (fon1.get_width() * 0.25, fon1.get_height() * 0.25))
    screen.blit(fon_img, (0, 0))
    work = True
    y1_snow, y2_snow = 0, -HEIGHT
    while work:
        clock.tick(10)
        screen.blit(fon_img, (0, 0))

        play_btn = print_text('Продолжить игру' if paused else 'Играть!', 100, 100, 'white', 190, 'grey', 20)
        shop_btn = print_text('Магазин', 75, 350, 'white', 190, 'grey', 20)
        best_result = cur.execute('SELECT best_result FROM progress').fetchone()[0]
        # подвижный снег
        y1_snow = y1_snow + speed if y1_snow < HEIGHT else -HEIGHT + speed
        y2_snow = y2_snow + speed if y2_snow < HEIGHT else -HEIGHT + speed
        screen.blit(pygame.transform.scale(load_image('snow.png'), (WIDTH, HEIGHT)), (0, y1_snow))
        screen.blit(pygame.transform.scale(load_image('snow.png'), (WIDTH, HEIGHT)), (0, y2_snow))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #  проверка на клик по кнопкам
                if play_btn[0] < event.pos[0] < play_btn[2] and play_btn[1] < event.pos[1] < play_btn[3]:
                    return game_screen()
                elif shop_btn[0] < event.pos[0] < shop_btn[2] and shop_btn[1] < event.pos[1] < shop_btn[3]:
                    return shop()

        pygame.display.flip()


def shop(finish=False, time_count=0, balance=0):
    pygame.mixer.stop()
    pygame.mixer.music.load("data/shop_music_.mp3")
    pygame.mixer.music.play(-1)

    def cars_draw(last_choice=0):
        # отрисовка машинок, цен, статусов
        x, y = 750, 0
        cars_bords = list()
        # конект с бд
        con = sqlite3.connect("Race project")
        cur = con.cursor()
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
        exit_bords = print_text('Назад', 10, 10, 'red', 50, 'red', 20, 5)
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
                        print_text(f'Машина уже выбрана', 50, 700, 'yellow', 100)

                # выход из магазина
                if exit_bords[0] < event.pos[0] < exit_bords[2] and exit_bords[1] < event.pos[1] < exit_bords[3]:
                    return finish_screen(time_count, balance) if finish else start_screen()
            screen_reset(last_choice)
            pygame.display.flip()


class Coins(pygame.sprite.Sprite):
    def __init__(self, line, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale(load_image('coin.png'), (80, 80))
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect.x = WIDTH
        self.rect.y = line * 150 + 140

    def update(self):
        self.rect.x -= speed
        for c in car_sprites:
            if pygame.sprite.collide_mask(self, c):
                con = sqlite3.connect("Race project")
                cur = con.cursor()
                coins_now = cur.execute(f'''SELECT coins FROM progress''').fetchone()[0]
                cur.execute(f'''UPDATE progress SET coins == {coins_now + random.randint(1, 10)}''')
                con.commit()
                con.close()
                self.rect.y -= 10
                self.kill()


class Truck(pygame.sprite.Sprite):
    def __init__(self, line, *groups):
        super().__init__(*groups)
        con = sqlite3.connect("Race project")
        cur = con.cursor()
        imgs = list(cur.execute("""SELECT link FROM car_icons WHERE status != "choosed" ORDER BY price """).fetchall())
        con.close()
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
        self.kill()
        coll_sound.play(1)

    def update(self):
        global speed
        self.rect.move_ip(random.randrange(-1, 2), 0)
        if self.rect.x > - 300:
            self.rect.x -= speed * 2 + 10
        else:
            self.kill()
        for c in car_sprites:
            if pygame.sprite.collide_mask(self, c):
                self.truck_crash()
                while pygame.sprite.collide_mask(self, c) and speed > 0:
                    speed -= 1


class Car(pygame.sprite.Sprite):
    con = sqlite3.connect("Race project")
    cur = con.cursor()
    image = load_image(cur.execute("""SELECT link FROM car_icons WHERE status == 'choosed' """).fetchone()[0] + '.png')
    con.close()
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
        # line_sound.play(1)

    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)


def settings():
    screen.blit(load_image('start_fon6_1.jpg'), (0, 0))
    exit_bords = print_text('Назад', 10, 10, 'red', 50, 'red', 20, 5)
    vol_bords = list()
    run = True
    for i in range(1, 11):
        vol_bords.append(print_text('i', i * 20, 500, 'white', 100, 'white', 10, 10))
    # цикл отрисовки
    while run:
        screen.blit(load_image('start_fon6_1.jpg'), (0, 0))
        exit_bords = print_text('Назад', 10, 10, 'red', 50, 'red', 20, 5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()
            # нажатие на мышку ( выбор машинки/покупка машинки/выход из магазина )
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # выход из настроек
                if exit_bords[0] < event.pos[0] < exit_bords[2] and exit_bords[1] < event.pos[1] < exit_bords[3]:
                    return start_screen()
                # проверка на клик по кнопке
                for i, bord in enumerate(vol_bords):
                    if bord[0] < event.pos[0] < bord[2] and bord[1] < event.pos[1] < bord[3]:
                        print(i + 1)


def finish_screen(time_count, start_balance, balance=0):
    global speed, paused
    pygame.mixer.stop()
    pygame.mixer.music.load("data/win_music.mp3")
    pygame.mixer.music.play(-1)
    fon_img = load_image('start_fon7.jpg')
    fon_img = pygame.transform.scale(fon_img, (fon_img.get_width() * 0.5, fon_img.get_height() * 0.5))
    y1_snow, y2_snow = 0, -HEIGHT
    con = sqlite3.connect("Race project")
    cur = con.cursor()
    coins_in_db = cur.execute(f'''SELECT coins FROM progress''').fetchone()[0]
    collected_coins = coins_in_db - start_balance
    con.close()
    bonus = 10000 // time_count
    bonus_counter = 0
    work = True
    while work:
        screen.fill('black')
        clock.tick(5)
        screen.blit(fon_img, (0, 0), (500, 0, 2000, 2000))
        y1_snow = y1_snow + speed if y1_snow < HEIGHT else -HEIGHT + speed
        y2_snow = y2_snow + speed if y2_snow < HEIGHT else -HEIGHT + speed
        screen.blit(pygame.transform.scale(load_image('snow6.png'), (WIDTH, HEIGHT)), (0, y1_snow))
        screen.blit(pygame.transform.scale(load_image('snow6.png'), (WIDTH, HEIGHT)), (0, y2_snow))

        play_btn = print_text('Играть снова', 300, 600, 'white', 150, (155, 71, 25), frame_width=0)
        shop_btn = print_text('Магазин', 50, 750, 'white', 150, (201, 103, 14), frame_width=0)
        start_screen_btn = print_text('Главное меню', 500, 750, 'white', 150, (229, 97, 76), frame_width=0)
        print_text(time.strftime("%M:%S", time.gmtime(time_count)), 450, 100, 'white', 150)
        screen.blit(pygame.transform.scale(load_image('coin.png'), (80, 80)), (450, 250))
        print_text(f'{balance}', 550, 250, COIN_COLOR, 150)
        if balance != collected_coins:
            balance += 1
        else:
            print_text(f'--бонус за время:{bonus_counter}--', 200, 400, 'green', 100)
        if bonus_counter != bonus:
            bonus_counter += 1
        else:
            con = sqlite3.connect("Race project")
            cur = con.cursor()
            cur.execute(f'''UPDATE progress SET coins == {bonus + coins_in_db}''')
            con.commit()
            con.close()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_btn[0] < event.pos[0] < play_btn[2] and play_btn[1] < event.pos[1] < play_btn[3]:
                    return game_screen()
                elif shop_btn[0] < event.pos[0] < shop_btn[2] and shop_btn[1] < event.pos[1] < shop_btn[3]:
                    return shop(True, time_count, balance)
                elif start_screen_btn[0] < event.pos[0] < start_screen_btn[2] and start_screen_btn[1] < event.pos[1] < \
                        start_screen_btn[3]:
                    return start_screen()
        pygame.display.flip()


# создание объектов
all_sprites = pygame.sprite.Group()

car_sprites = pygame.sprite.Group()
car1 = Car(car_sprites, all_sprites)

truck_sprites = pygame.sprite.Group()
coins_sprites = pygame.sprite.Group()


def game_screen():
    global speed, paused
    pygame.mixer.stop()
    pygame.mixer.music.load("data/music1.mp3")
    pygame.mixer.music.play(-1)
    x1_road, x2_road = 0, WIDTH
    x1_snow, y1_snow, x2_snow, y2_snow, x3_snow, y3_snow, x4_snow, y4_snow, = 0, 0, -WIDTH, -HEIGHT, 0, -HEIGHT, WIDTH, 0
    time_count = 0
    metres = 0
    speed = 10

    TRUCK_SPAWN = pygame.USEREVENT + 1
    TIMEREVENT = pygame.USEREVENT + 2
    COIN_SPAWN = pygame.USEREVENT + 3

    pygame.time.set_timer(TRUCK_SPAWN, 30000 // speed)
    pygame.time.set_timer(TIMEREVENT, 1000)
    pygame.time.set_timer(COIN_SPAWN, 50000 // speed)
    start_balance = cur.execute(f'''SELECT coins FROM progress''').fetchone()[0]
    running = True
    while running:
        screen.fill('black')
        # отрисовка подвижной дороги
        road = pygame.transform.scale(load_image('town0_1.png', None), (WIDTH, 1000))
        x1_road = x1_road - speed if x1_road > -WIDTH + speed else WIDTH - speed
        x2_road = x2_road - speed if x2_road > -WIDTH + speed else WIDTH - speed
        screen.blit(road, (0, 0))
        screen.blit(road, (x1_road, 0))
        screen.blit(road, (x2_road, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                for car in car_sprites:
                    car.line_move(pygame.key.get_pressed())
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    paused = True
                    start_screen()
                if pygame.key.get_pressed()[pygame.K_RIGHT]:
                    if speed < 201:
                        speed += 1
            elif event.type == TRUCK_SPAWN and speed != 0:
                truck = Truck(random.randint(1, 3), truck_sprites, all_sprites)
            elif event.type == TIMEREVENT:
                time_count += 1
                metres += speed / 3.6
            elif event.type == COIN_SPAWN and speed != 0:
                coin = Coins(random.randint(1, 3), coins_sprites, all_sprites)

        truck_sprites.update()
        car_sprites.update()
        coins_sprites.update()
        # отрисовка гг
        car_sprites.draw(screen)
        coins_sprites.draw(screen)
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
        if metres < 1000:
            print_text(f'{int(metres)}m', 250, 10, 'white', 100)
            paused = False
        else:
            print_text(f'{int(metres // 1000)}.{int(metres % 1000 // 100)} km', 250, 10, 'white', 100)
        pygame.draw.rect(screen, 'red', (850, 20, 200, 20), 0)
        pygame.draw.rect(screen, 'darkgreen', (850, 20, metres // 10, 20), 0)

        # отрисовка скорости
        print_text(f'{str(speed)}km/h', 500, 10, 'white', 100)
        if metres // 1000 >= 2:
            finish_screen(time_count, start_balance)
        clock.tick(FPS)
        pygame.display.flip()


# запуск начального экрана
start_screen()
pygame.quit()
con.close()
