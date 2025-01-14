import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def init_graphics():
    glEnable(GL_DEPTH_TEST)
    glScalef(2, 2, 2)  # Double the size of the model

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 0, 10, 1))  # Ajustar la posición de la luz
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Establecer el color de fondo a blanco
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (800/600), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 20, 0, 0, 0, 0, 1, 0)  # Alejar la cámara para visualizar correctamente
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)


def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#'):
                continue
            if line.startswith('v '):
                parts = line.strip().split()
                vertices.append(list(map(float, parts[1:4])))  # Solo tomar los primeros 3 valores
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(i.split('/')[0]) - 1 for i in parts[1:] if i.split('/')[0].isdigit()]
                faces.append(face)
    print("Vertices:", vertices)
    print("Faces:", faces)
    return vertices, faces