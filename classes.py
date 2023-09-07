import pygame
import numpy as np

# Global variables.
RADIUS = 2

class Physics_Body(pygame.sprite.Sprite):
    """
    Objects of this class represent physical bodies.
    Attributes;
        1. mass - type float. Positional argument on init.
        2. pos - type array. Vector representation of the body's position. Positional argument on init.
        3. radius - type float. The radius of the circular body.
        4. vel - type list. A list containing the current and previous velocity represented as vectors.
        5. acc - type list. A list containing the current and previous acceleration represented as vectors.
        6. ext_force - type array. The vector sum of forces applied on the body (during a timestep).
    """
    def __init__(self, mass, pos):
        super().__init__()
        self.mass = float(mass)
        self.pos = np.asarray(pos, dtype=float)
        self.radius = float(RADIUS)
                    # Prev. timestep.        # Current timestep.
        self.vel = [np.array([[0.], [0]]), np.array([[0.], [0]])]
        self.acc = [np.array([[0.], [0]]), np.array([[0.], [0]])]
        self.ext_force = np.array([[None], [None]]) # Must be reset to None on each timestep.
    def apply_force(self, force, max_force = 10**100):
        """
        Updates self.ext_force attribute.
        :param force: type array. The force that should be applied.
        :param max_force: type int. Maximum accepted component force magnitude.
        :return: Sets self.ext_force value appropiately.
        """
        if force.dtype != float:
            raise TypeError("Datatype of force-vector contents must be float!")
        if (np.absolute(force) > max_force).any():
            raise ValueError("Trying to apply infinite force!")
            # Could handle infinite gravity problem?

        if (self.ext_force == None).any():
            self.ext_force = force
        else:
            self.ext_force += force

    def react(self, dt):
        """
        The body's position is updated using 2-step Adams-Bashfort integration.
        :param dt: type float. Timestep size.
        :return: Updates attributes appropiately. Sets ext_force to None in preparation of the next timestep.
        """

        if (self.ext_force == None).any():
            raise Exception("This body has no external force to react to!")

        self.acc.append(self.ext_force * (1./self.mass))
        self.acc.pop(0)
        new_vel = self.vel[-1] + (dt/2.) * (3.*self.acc[-1] - self.acc[-2])
        self.vel.append(new_vel)
        self.vel.pop(0)
        new_pos = self.pos + (dt/2.) * (3.*self.vel[-1] - self.vel[-2])
        self.pos = new_pos
        self.ext_force = np.array([[None], [None]])

class Pgame_Body(Physics_Body):
    """
    Wrapper class for Physics_Body. Adds necessary attributes/methods to display a Physics_Body as a sprite in Pygame.
    """
    def __init__(self, mass, pos):
        super().__init__(mass, pos)
        self.image = pygame.Surface((RADIUS*2, RADIUS*2))
        self.image.fill("Grey") # Must be same color as the background.
        self.rect = self.image.get_rect(center=(self.pos[0, 0], self.pos[1, 0]))
        pygame.draw.circle(self.image, "Red", (RADIUS, RADIUS), RADIUS, 0) # Color of body.

    def animate(self):
        """
        Does nothing other than moving the sprite to its correct position.
        """
        self.rect.x, self.rect.y = self.pos[0,0], self.pos[1,0]




class Node:
    """
    Objects of this class represent nodes in the quadtree. Attributes;
    1. coords - type array. The coordinates of its bounding box, a (2x2) array of tuples where each tuple corresponds
                to the coordinates of each corner of the bounding box. Positional arg on init.
    2. contents - type list.  A list containing all body objects contained within the bounding box. Positional arg
                  on init.
    3. parent - type None/Node. The parent Node of the node. Keyword arg. Default = None
    4. children - type list. A list containing all children Nodes of the node. Keyword arg. Default = [].
    5. total_mass - type float. The total mass of all bodies contained within the bounding box.
    6. com - type array. Vector representation of the nodes center of mass.

    Important! -> On object creation, contents must be set and accurate.
    Note that the total_mass and com attributes are automatically set on object creation.
    """
    def __init__(self, coords, contents, parent=None, children= None): # wtf
        self.coords = coords
        self.contents = contents
        self.parent = parent
        self.children = children

        if len(self.contents) == 0: # Empty node.
            self.total_mass = 0.
            self.com = np.array([[None], [None]]) # This is kinda weird....
        elif len(self.contents) == 1: # Leaf node.
            self.total_mass = self.contents[0].mass
            self.com = self.contents[0].pos
        else: # Internal node or root.
            total_mass = 0.
            for mass in self.contents:
                total_mass += mass.mass
            self.total_mass = total_mass
            weighted_pos = np.array([[0.], [0]])
            for i in range(len(self.contents)):
                weighted_pos += self.contents[i].mass * self.contents[i].pos
            self.com = weighted_pos * (1./self.total_mass)

    def display(self, BACKGROUND, color="Blue"):
        """
        Displays the nodes bounding box on the background.
        """
        leftupper = self.coords[0,0]
        rightupper = self.coords[0,1]
        leftlower = self.coords[1,0]
        rightlower = self.coords[1,1]
        pygame.draw.line(BACKGROUND, color, leftupper, rightupper)
        pygame.draw.line(BACKGROUND, color, leftupper, leftlower)
        pygame.draw.line(BACKGROUND, color, rightupper, rightlower)
        pygame.draw.line(BACKGROUND, color, leftlower, rightlower)
    def get_quadrants(self):
        """
        Divides the bounding box into four equally sized boxes. Method is only used in .subdivide.
        :return: type tuple. A tuple of the coordinates of each box.
        """
        arr = np.array([
            [(-1.,-1), (-1,-1), (-1,-1)],
            [(-1,-1), (-1,-1), (-1,-1)],
            [(-1,-1), (-1,-1), (-1,-1)]
        ])
        arr[0,0] = self.coords[0,0]
        arr[0,2] = self.coords[0,1]
        arr[2,0] = self.coords[1,0]
        arr[2,2] = self.coords[1,1]


        arr[1,1] = (self.coords[0,0][0] + (self.coords[0,1][0] - self.coords[0,0][0])/2., self.coords[0,0][1] +
                    (self.coords[1,0][1] - self.coords[0,0][1])/2.)
        arr[0,1] = (self.coords[0,0][0] + (self.coords[0,1][0] - self.coords[0,0][0])/2. , self.coords[0,0][1])
        arr[2,1] = ((self.coords[0,0][0] + self.coords[0,1][0])/2., self.coords[1,0][1])
        arr[1,0] = (self.coords[0,0][0], self.coords[0,0][1] + (self.coords[1,0][1] - self.coords[0,0][1])/2.)
        arr[1,2] = (self.coords[0,1][0], self.coords[0,1][1] + (self.coords[1,1][1] - self.coords[0,1][1])/2.)

        first = np.array([
            [arr[0, 0], arr[0, 1]],
            [arr[1, 0], arr[1, 1]]
        ])
        second = np.array([
            [arr[0, 1], arr[0, 2]],
            [arr[1, 1], arr[1, 2]]
        ])
        third = np.array([
            [arr[1, 0], arr[1, 1]],
            [arr[2, 0], arr[2, 1]]
        ])
        fourth = np.array([
            [arr[1, 1], arr[1, 2]],
            [arr[2, 1], arr[2, 2]]
        ])
        return (first, second, third, fourth)

    def subdivide(self):
        """
        Creates 4 child node objects. Initializes each child correctly.
        :return: Updates the self.children attribute.
        """
        coords1, coords2, coords3, coords4 = self.get_quadrants()
        middle = np.array([[coords1[1,1][0]], [coords1[1,1][1]]])

        contents1 = []
        contents2 = []
        contents3 = []
        contents4 = []
        for body in self.contents:
            if body.pos[0,0] >= middle[0,0]:
                if body.pos[1,0] >= middle[1,0]:
                    contents4.append(body)
                else:
                    contents2.append(body)
            else:
                if body.pos[1,0] >= middle[1,0]:
                    contents3.append(body)
                else:
                    contents1.append(body)
        child1 = Node(coords1, contents1, parent=self, children=[]) # Why does this have to be specified????
        child2 = Node(coords2, contents2, parent=self, children=[])
        child3 = Node(coords3, contents3, parent=self, children=[])
        child4 = Node(coords4, contents4, parent=self, children=[])
        self.children = [] #wtf
        self.children.append(child1)
        self.children.append(child2)
        self.children.append(child3)
        self.children.append(child4)




