import pygame
import sqlite3
import os
import sys
import random

WIDTH, HEIGHT = DISPLAY_SIZE = (1280, 968)
FPS = 60
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
#screen = pygame.display.set_mode((0, 0), pygame.RESIZABLE)
pygame.display.set_caption("Race Game")
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


def print_text(message="", x=0, y=0, font_color='black', font_size=30, frame_color=None, frame_indent=0, frame_width=1):
    font_type = pygame.font.Font(None, font_size)
    text = font_type.render(message, True, font_color)
    screen.blit(text, (x, y))
    if frame_color != None:
        pygame.draw.rect(screen, frame_color, (
            x - frame_indent, y - frame_indent, text.get_rect()[2] + frame_indent * 2,
            text.get_rect()[3] + frame_indent * 2), frame_width)


# def start_screen():
#     intro_text = ['гонки', 'Играть!', 'Магазин', "Гараж"]
#     fon = pygame.transform.scale(load_image('race_fon.jpg', None), (WIDTH, HEIGHT))
#     screen.blit(fon, (0, 0))
#     font = pygame.font.Font(None, 50)
#     text_coord = 50
#     string_rendered = font.render(intro_text[0], 1, pygame.Color('black'))
#     intro_rect = string_rendered.get_rect()
#     text_coord = 30
#     intro_rect.top = text_coord
#     intro_rect.x = 30
#     text_coord = intro_rect.height
#     screen.blit(string_rendered, intro_rect)
#
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#             elif event.type == pygame.MOUSEBUTTONDOWN:
#                 return
#
#         pygame.display.flip()
#         clock.tick(FPS)


class Hearts(pygame.sprite.Sprite):
    image = load_image('heart.png')
    image2 = load_image('broken_heart.png')

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
        self.rect.y = 130



    def line_move(self, pressed_keys):
        if pressed_keys[pygame.K_UP]:
            if self.rect.y > 300:
                self.rect.y -= 200
        if pressed_keys[pygame.K_DOWN]:
            if self.rect.y < 500:
                self.rect.y += 200


    def trrr(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)
        if pygame.sprite.spritecollideany(self, arrow_sprites):
            for h in hearts_sprites:
                h.heart_remove()

        if pygame.sprite.spritecollideany(self, zombie_sprites):
            for h in hearts_sprites:
                h.heart_remove()



# монстры
class Skelet(pygame.sprite.Sprite):
    image = load_image('skelet.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = Skelet.image
        self.image = pygame.transform.scale(self.image, (220, 200))
        self.rect = self.image.get_rect()

        self.rect.x = 800
        self.rect.y = 350

    def hit(self):
        pass


class Zombie(pygame.sprite.Sprite):
    image = load_image('zombie.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = Zombie.image
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect()

        self._step = 1

        self.rect.x = 800
        self.rect.y = 50

    def walk(self):
        if self.rect.x < 800 or self.rect.x > 900:
            self._step = -1 if self._step == 1 else 1
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect.x += self._step


# стрелы
class Arrow(pygame.sprite.Sprite):
    image = load_image('arrow.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = Arrow.image
        self.image = pygame.transform.flip(self.image, True, False)
        self.image = pygame.transform.scale(self.image, (150, 50))
        self.rect = self.image.get_rect()

        self.rect.x = 700
        self.rect.y = 415

    def shot(self):
        if self.rect.x >= -1000:
            self.rect.x -= 5
        else:
            self.rect.x = 700


# пауза игры
def pause():
    paused = True
    while paused:

        print_text('Пауза. Нажмите пробел для продолжения.', 50, HEIGHT // 2, 'white', 50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_PAUSE]:
                    paused = False
                    return


# создание объектов
hearts_sprites = pygame.sprite.Group()
for i in range(1000, 1180, 60):
    Hearts(i, hearts_sprites)

skelet_sprites = pygame.sprite.Group()
Skelet(skelet_sprites)

zombie_sprites = pygame.sprite.Group()
Zombie(zombie_sprites)

arrow_sprites = pygame.sprite.Group()
Arrow(arrow_sprites)

car_sprites = pygame.sprite.Group()
Car(car_sprites)


# запуск
# start_screen()
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
                pause()
                print('pause')
    screen.fill('black')

    screen.fill((58, 56, 53))

    fon = pygame.transform.scale(load_image('road.png', None), (WIDTH, 640))
    x1 = x1 - 10 if x1 > -WIDTH else WIDTH - 10
    x2 = x2 - 10 if x2 > -WIDTH else WIDTH - 10
    screen.blit(fon, (x1, 140))
    screen.blit(fon, (x2, 140))


    for car in car_sprites:
        car.trrr()
    for z in zombie_sprites:
        z.walk()
    for a in arrow_sprites:
        a.shot()

    clock.tick(FPS)

    car_sprites.draw(screen)
    zombie_sprites.draw(screen)
    arrow_sprites.draw(screen)
    skelet_sprites.draw(screen)
    hearts_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
