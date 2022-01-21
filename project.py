import pygame
import sqlite3
import os
import sys
import random

WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 10
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
# screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
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
    if frame_color != None:
        pygame.draw.rect(screen, frame_color, (
            x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2,
            text.get_rect()[3] + frame_indent * 2), frame_width)

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
    fon1 = load_image('start_fon5_1.jpg')
    fon1 = pygame.transform.scale(fon1, (fon1.get_width() * 3, fon1.get_height() * 3))
    fon2 = load_image('start_fon5_2.jpg')
    fon2 = pygame.transform.scale(fon2, (fon2.get_width() * 3, fon2.get_height() * 3))
    screen.blit(fon1, (0, 0))
    print_text('Играть!', HEIGHT // 2, 100, 'white', 200, 'grey')
    while True:
        screen.blit(fon1, (0, 0))
        pygame.display.flip()
        # clock.tick(30)
        # screen.blit(fon2, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()


class Truck(pygame.sprite.Sprite):
    image = pygame.transform.flip(load_image('truck.png'), True, False)

    def __init__(self, line, *groups):
        super().__init__(*groups)
        self.image = pygame.transform.scale(Truck.image, (256, 256))
        self.rect = self.image.get_rect()

        self.rect.x = WIDTH
        self.rect.y = line * 200

    def truck_crash(self):
        self.image = pygame.transform.scale(load_image('broken_heart.png'), (60, 60))


    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)
        self.rect.x -= 30


class Hearts(pygame.sprite.Sprite):
    image = load_image('heart.png')
    image2 = pygame.transform.scale(load_image('broken_heart.png'), (60, 60))

    def __init__(self, place, *groups):
        super().__init__(*groups)
        self.image = Hearts.image
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()

        self.rect.x = place
        self.rect.y = 10

    def heart_remove(self):
        self.image = self.image2
        self.image = pygame.transform.scale(self.image, (60, 60))


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
        self.heart = 3

        self.rect.x = 0
        self.rect.y = 200

    def line_move(self, pressed_keys):
        if pressed_keys[pygame.K_UP]:
            if self.rect.y > 300:
                self.rect.y -= 200
        if pressed_keys[pygame.K_DOWN]:
            if self.rect.y < 500:
                self.rect.y += 200

    def update(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)
        if pygame.sprite.spritecollideany(self, truck_sprites):
            for t in truck_sprites:
                t.truck_crash()
            for h in hearts_sprites:
                h.remove()



# # пауза игры
# def pause():
#     paused = True
#     while paused:
#
#         print_text('Пауза. Нажмите пробел для продолжения.', 50, HEIGHT // 2, 'white')
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#             elif event.type == pygame.KEYDOWN:
#                 if pygame.key.get_pressed()[pygame.K_PAUSE]:
#                     # paused = False
#                     return


# создание объектов
all_sprites = pygame.sprite.Group()

hearts_sprites = pygame.sprite.Group()
for i in range(1000, 1180, 60):
    Hearts(i, hearts_sprites, all_sprites)



car_sprites = pygame.sprite.Group()
Car(car_sprites, all_sprites)

truck_sprites = pygame.sprite.Group()
Truck(1, truck_sprites, all_sprites)

# запуск
start_screen()
x1, x2 = 0, WIDTH
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            for car in car_sprites:
                car.line_move(pygame.key.get_pressed())
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                #                pause()
                print('pause')
    screen.fill('black')

    fon = pygame.transform.scale(load_image('town0.png', None), (WIDTH, 1000))
    x1 = x1 - speed if x1 > -WIDTH else WIDTH - speed
    x2 = x2 - speed if x2 > -WIDTH else WIDTH - speed
    screen.blit(fon, (x1, 0))
    screen.blit(fon, (x2, 0))

    truck_sprites.update()
    car_sprites.update()
    # clock.tick(10)
    # print(clock.get_time())
    # timer = pygame.time.set_timer()
    # print(timer)
    car_sprites.draw(screen)

    hearts_sprites.draw(screen)
    truck_sprites.draw(screen)
    print_text(str(clock.tick() // 10), 200, 500, 'white', 200)
    pygame.display.flip()

pygame.quit()

