import sqlite3
import pygame
import sys
import os


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


WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 10
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
pygame.display.set_caption("Race Game")
clock = pygame.time.Clock()


def print_text(message, x, y, font_color='black', font_size=30, frame_color=None):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
    if frame_color != None:
        pygame.draw.rect(screen, frame_color, (x, y, text.get_rect()[2], text.get_rect()[3]), 1)


def shop():
    con = sqlite3.connect("Race project")
    cur = con.cursor()
    result = cur.execute("""SELECT * FROM car_icons ORDER BY price""").fetchall()
    for elem in result:
        print(elem)
    con.close()
    x, y = 750, 0
    cars_bords = list()
    for car in result:
        car_img = pygame.transform.scale(load_image(car[3] + '.jpg', None), (180, 180))
        car_price = int(car[2])
        car_rect = car_img.get_rect()
        car_stat = True if car[1] == 'unlock' else False
        screen.blit(car_img, (x, y))
        if car_stat:
            print_text('purchased', x + 60, y + 160, 'green', 25)
        else:
            print_text(str(car_price), x + 70, y + 160, 'yellow', 30)
        cars_bords.append((x, y, x + 180, y + 180))
        y = y + 180 if x == 1110 else y
        x = x + 180 if x < 1110 else 750

    print()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for index, clck in enumerate(cars_bords):
                    if clck[0] < event.pos[0] < clck[2] and clck[1] < event.pos[1] < clck[3]:
                        # pygame.draw.rect(screen, 'grey', (clck[0], clck[1], clck[2] - clck[0], clck[3] - clck[1]), 1)
                        screen.blit(pygame.transform.scale(load_image(result[index][3] + '.jpg'), (700, 700)), (5, 50))
                        print_text(f'Купить за {result[index][2]}', 50, 800, 'purple', 50, 'purple')
        pygame.display.flip()

shop()
