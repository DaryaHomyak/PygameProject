import pygame

import os
import sys
import random

WIDTH, HEIGHT = DISPLAY_SIZE = (1200, 900)
FPS = 60
pygame.init()
screen = pygame.display.set_mode(DISPLAY_SIZE)
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


def start_screen():
    intro_text = ['гонки', 'Играть!', 'Магазин', "Гараж"]
    fon = pygame.transform.scale(load_image('race_fon.jpg', None), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 30
        intro_rect.top = text_coord
        intro_rect.x += 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return

        pygame.display.flip()
        clock.tick(FPS)


class Hearts(pygame.sprite.Sprite):
    image = load_image('heart.png')
    image2 = load_image('broken_heart.png')

    def __init__(self, place, *groups):
        super().__init__(*groups)
        self.image = Hearts.image
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = Hearts.image.get_rect()

        self.rect.x = place
        self.rect.y = 10

    def heart_remove(self):
        self.image = Hearts.image2
        self.image = pygame.transform.scale(self.image, (60, 60))


class Car(pygame.sprite.Sprite):
    image = load_image('car.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = Car.image
        self.image = pygame.transform.scale(self.image, (512, 256))
        self.rect = Car.image.get_rect()
        self.heart = 3

        self.rect.x = 0
        self.rect.y = 0
        #                                                 !!!!!!!!!!!!!!!!
        #
        #                                                вот здесь проблема с пересечением спрайтов
        #
        #   по идее, сердечки должны меняться только при пересечении машинки со стрелой, но при запуске они изменены в самом начале...

        if pygame.sprite.spritecollideany(self, arrow_sprites):
            for h in hearts_sprites:
                h.heart_remove()

        if pygame.sprite.spritecollideany(self, zombie_sprites):
            for h in hearts_sprites:
                h.heart_remove()

    #                                                !!!!!!!!!!!!!!!!!!!!!!!!!!

    def line_move(self, pressed_key):
        if pressed_key[pygame.K_UP]:
            self.rect.y -= 300
        if pressed_key[pygame.K_DOWN]:
            self.rect.y += 300
        if pressed_key[pygame.K_RIGHT]:
            self.rect.x += 300
        if pressed_key[pygame.K_LEFT]:
            self.rect.x -= 300

    def trrr(self):
        self.rect.move_ip(random.randrange(-1, 2), 0)


# монстры
class Skelet(pygame.sprite.Sprite):
    image = load_image('skelet.png')

    def __init__(self, *groups):
        super().__init__(*groups)
        self.image = Skelet.image
        self.image = pygame.transform.scale(self.image, (220, 200))
        self.rect = Skelet.image.get_rect()

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
        self.rect = Zombie.image.get_rect()

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
        self.rect = Arrow.image.get_rect()

        self.rect.x = 700
        self.rect.y = 415

    def shot(self):
        if self.rect.x >= -1000:
            self.rect.x -= 5
        else:
            self.rect.x = 700


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
start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            for car in car_sprites:
                car.line_move(pygame.key.get_pressed())
    screen.fill('black')
    for i in range(1, 3):
        pygame.draw.line(screen, 'white', (0, i * 300), (1200, i * 300), 10)
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
