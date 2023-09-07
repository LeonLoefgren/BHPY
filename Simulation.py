import sys
from matplotlib import pyplot as plt
import pygame
from sys import exit
import time
import numpy as np
import random
from classes import Physics_Body, Pgame_Body, Node
import gc

############ Finished ####################
# Transfer project to C++, change integration to Störmer-Verlet and make in 3-space. 



# Global variables.
pygame.init()
WIN_SIZE = (800,800)
CANVAS = pygame.display.set_mode(WIN_SIZE)
BACKGROUND = pygame.Surface(WIN_SIZE)
BACKGROUND_CLR = "Grey"
BACKGROUND.fill(BACKGROUND_CLR)
CLOCK = pygame.time.Clock()
FPS = 30
RADIUS = 2
SPRITE_GROUP = pygame.sprite.Group()
G = 100
THETA = 0.7
RESOL = 4

def distribute_bodies(mass, num):
    L = []
    for i in range(num):
        x = random.randint(0, 800)
        y = random.randint(0, 800)
        body = Pgame_Body(mass, np.array([[x], [y]]))
        SPRITE_GROUP.add(body)
        L.append(body)
    return L
def quadtree(node):
    """
    Constructs the quadtree from the root node.
    :param node: type Node. On first call is root.
    :param side_lim: type int. No nodes with side-lengts < side_lim are constructed in order to limit recursion depth.
    :return: Creates all node objects which populate the quadtree.
    """
    if abs(node.coords[0,0][0] - node.coords[0,1][0]) < RESOL or len(node.contents) <= 1:
        # If recursion depth reached or empty node reached or leaf node reached.
        return
    else:
        # node is either root or internal.
        node.subdivide()
        for child in node.children:
             quadtree(child)

def get_force(body, node): # Look you can acess theta but not change it!
    # This func looks like shit.
    try:
        r = node.com - body.pos
    except TypeError: # Empty node I believe. Because node.com is None-array!
        return

    r_mag = np.sqrt(np.dot(r.T[0], r.T[0]))
    if r_mag <= RESOL:
        return
    else:
        if len(node.children) == 0: # Is either empty, leaf, or recursive stop.
            if len(node.contents) == 0: # is empty.
                return
            elif len(node.contents) == 1: # is leaf
                if node.contents[0] != body:
                    r_hat = r * (1./r_mag)
                    F = G*body.mass*node.total_mass * (1./r_mag**2) * r_hat
                    try:
                        body.apply_force(F)
                    except ValueError:
                        return
                else:
                    return
            else: # is recursive stop.
                # Make sure that body is not in this node...
                if not body in node.contents:
                    r_hat = r * (1./r_mag)
                    F = G * body.mass * node.total_mass * (1./r_mag**2) * r_hat
                    try:
                        body.apply_force(F)
                    except ValueError:
                        return
                else:
                    return

        else: # Is root or internal node.
            s = abs(node.coords[0, 0][0] - node.coords[0, 1][0])
            theta = s/r_mag
            if theta < THETA: # Treat as single body.
                r_hat = r * (1./r_mag)
                F = G * body.mass * node.total_mass * (1. / r_mag ** 2) * r_hat
                try:
                    body.apply_force(F)
                except ValueError:
                    return
            else:
                for child in node.children:
                    get_force(body, child)


def remove_nodes(node):
    if len(node.children) == 0:
        node.parent = None
        return
    else:
        for child in node.children:
            remove_nodes(child)
        node.children = []

def clear_tree(node):
    remove_nodes(node)
    # gc.collect() # Not needed anymore?

def show_tree(node, BACKGROUND):
    node.display(BACKGROUND)
    if len(node.children) == 0:
        return
    else:
        for child in node.children:
            show_tree(child, BACKGROUND)

BODIES = distribute_bodies(10, 100)


i = 0
t0 = time.time()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
    t1 = time.time()
    dt = t1 - t0
    # print(f"Frame = {i}")
    # print(f"delta time= {dt}")
    t0 = t1
    CANVAS.blit(BACKGROUND, (0,0))
    BACKGROUND.fill(BACKGROUND_CLR)
    NODE0 = Node(np.array([[(0., 0), (800, 0)], [(0, 800), (800, 800)]]), BODIES)

    quadtree(NODE0)
    # show_tree(NODE0, BACKGROUND)
    for body in BODIES:
        get_force(body, NODE0)
        try:
            body.react(dt)
            body.animate()
        except Exception:
            pass



    # print(f"Ref count = {sys.getrefcount(Node)}")
    clear_tree(NODE0)
    # print(f"Ref count after cleaning = {sys.getrefcount(Node)}")
    SPRITE_GROUP.draw(CANVAS)
    pygame.display.update()
    i += 1
    CLOCK.tick(FPS)
