import sys
import gc
import pygame
from sys import exit
import time
import numpy as np
import random
from classes import Physics_Body, Pgame_Body, Node
from matplotlib import pyplot as plt

SPRITE_GROUP = pygame.sprite.Group()
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


RESOL = 10**-6
RADIUS = 2
G = 100

numbodies = list(range(4, 100, 1))
BH = []
EU = []
for num in numbodies:
    BODIES = distribute_bodies(5, num)
    t0 = time.time()
    THETA = 0.5
    for i in range(15): # frames
        NODE0 = Node(np.array([[(0., 0), (800, 0)], [(0, 800), (800, 800)]]), BODIES)
        quadtree(NODE0)
        for body in BODIES:
            get_force(body, NODE0)
            try:
                body.react(0.2)
            except Exception:
                pass
        clear_tree(NODE0)
    t1 = time.time()
    BH.append(t1 - t0)
    t0 = time.time()
    # print("BH")
    THETA = 0.
    for i in range(15): # frames
        NODE0 = Node(np.array([[(0., 0), (800, 0)], [(0, 800), (800, 800)]]), BODIES)
        quadtree(NODE0)
        for body in BODIES:
            get_force(body, NODE0)
            try:
                body.react(0.2)
            except Exception:
                pass
        clear_tree(NODE0)
    t1 = time.time()
    EU.append(t1 - t0)
    # print("EU")

complex = [0.003*n*np.log(n) for n in numbodies]

plt.plot(numbodies, BH, label="THETA = 0.5")
plt.plot(numbodies, EU, label="THETA = 0.")
plt.plot(numbodies, complex, label="O(nlog(n))")
plt.legend()
plt.show()