import pygame
import numpy as np
import time
import random
from classes import Pgame_Body

# Implement naive n-body simulation to make sure that Adams-Bashforth is
# correctly implemented.

# Is correctly implemented. Shut off gravity issue persists.
# I think that can be solved with the min_side in the tree???

# Global variables.
pygame.init()
WIN_SIZE = (800,800)
CANVAS = pygame.display.set_mode(WIN_SIZE)
BACKGROUND = pygame.Surface(WIN_SIZE)
BACKGROUND_CLR = "Grey"
BACKGROUND.fill(BACKGROUND_CLR)
CLOCK = pygame.time.Clock()
FPS = 60
RADIUS = 4
SPRITE_GROUP = pygame.sprite.Group()
G = 100
THETA = 0.5


def gravitate(m, otherm):
    if m == otherm:
        raise Exception("Cant apply force to self!")
    r = otherm.pos - m.pos
    r_mag = np.sqrt(np.dot(r.T[0], r.T[0]))
    if r_mag < 2*RADIUS:
        return
    r_hat = r * (1./r_mag)
    F = G*m.mass*otherm.mass * (1./r_mag**2) * r_hat
    m.apply_force(F)

def make_bodies(mass, num, give_random_initial_vel = False):
    for i in range(num):
        x = random.randint(300, 500)
        y = random.randint(300, 500)
        body = Pgame_Body(mass, np.array([[x], [y]]))
        SPRITE_GROUP.add(body)

make_bodies(200, 3)
print(type(SPRITE_GROUP))

t0 = time.time()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    t1 = time.time()
    dt = t1 - t0
    t0 = t1
    CANVAS.blit(BACKGROUND, (0,0))

    for mainbod in SPRITE_GROUP:
        for otherbod in SPRITE_GROUP:
            if mainbod == otherbod:
                pass
            else:
                gravitate(mainbod, otherbod)
                try:
                    mainbod.react(dt)
                except Exception:
                    pass
                mainbod.animate()
    print(dt)
    SPRITE_GROUP.draw(CANVAS)
    pygame.display.update()
    CLOCK.tick(FPS)