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

# запуск
x1, x2 = 0, HEIGHT
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            pass
    screen.fill('black')
    screen.fill((58, 56, 53))

    fon = pygame.transform.scale(load_image('road2.png', None), (HEIGHT, HEIGHT))
    x1 = x1 - speed if x1 > -HEIGHT else HEIGHT - speed
    x2 = x2 - speed if x2 > -HEIGHT else HEIGHT - speed
    screen.blit(fon, (x1, 0))
    screen.blit(fon, (x2, 0))

    pygame.display.flip()

pygame.quit()