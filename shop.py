import sqlite3
import pygame
import sys
import os

WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 10
COIN_COLOR = (234, 156, 0)
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
pygame.display.set_caption("Race Game")
clock = pygame.time.Clock()

# конект с бд для получения машинок
con = sqlite3.connect("Race project")
cur = con.cursor()
all_cars_info = cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall()


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


def cars_draw(last_choice=0):
    global all_cars_info
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
    screen.blit(pygame.transform.scale(load_image('cute.jpg'), (WIDTH, HEIGHT)), (0, 0))
    cars_draw(last_choice)
    coins_draw()
    # кнопка выхода в главное меню
    exit_bords = print_text('Выход', 0, 0, 'red', 50, 'red', 20, 5)
    return exit_bords

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



def shop():
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
#                for place, r in enumerate(cur.execute('SELECT * FROM car_icons ORDER BY price').fetchall()):
#                    print_text(str(r), 0, place * 20, 'white')

                # выход из магазина
                if exit_bords[0] < event.pos[0] < exit_bords[2] and exit_bords[1] < event.pos[1] < exit_bords[3]:
                    return

            pygame.display.flip()


shop()
con.close()
