import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import os

def init_graphics():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)  # Usar una función de profundidad menos o igual para mejorar la precisión
    glClearDepth(1.0)  # Establecer la profundidad máxima
    glDepthRange(0.0, 1.0)  # Establecer el rango de profundidad
    glScalef(2, 2, 2)  # Duplicar el tamaño del modelo

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    # Ajustar la posición de la luz para que esté en el centro del techo de la habitación
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 40, 0, 1))  # (x, y, z, w) w=1 para luz puntual
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1))  # Luz ambiental débil
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Establecer el color de fondo a negro
    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (800/600), 0.1, 300.0)  # Ajustar el rango de visión de la cámara
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 0, 0, 0, -1, 0, 1, 0)  # Ajustar la dirección de la cámara
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

def load_obj(filename):
    vertices = []
    faces = []
    materials = {}
    current_material = None

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#'):
                continue
            if line.startswith('mtllib '):
                mtl_filename = line.strip().split()[1]
                mtl_path = os.path.join(os.path.dirname(filename), mtl_filename)
                materials = load_mtl(mtl_path)
            elif line.startswith('usemtl '):
                current_material = line.strip().split()[1]
            elif line.startswith('v '):
                parts = line.strip().split()
                vertices.append(list(map(float, parts[1:4])))  # Solo tomar los primeros 3 valores
            elif line.startswith('f '):
                parts = line.strip().split()
                face = [int(i.split('/')[0]) - 1 for i in parts[1:] if i.split('/')[0].isdigit()]
                faces.append((face, current_material))

    return vertices, faces, materials

def load_mtl(filename):
    materials = {}
    current_material = None

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('#'):
                continue
            if line.startswith('newmtl '):
                current_material = line.strip().split()[1]
                materials[current_material] = {}
            elif line.startswith('Ka '):
                materials[current_material]['Ka'] = list(map(float, line.strip().split()[1:4]))
            elif line.startswith('Kd '):
                materials[current_material]['Kd'] = list(map(float, line.strip().split()[1:4]))
            elif line.startswith('Ks '):
                materials[current_material]['Ks'] = list(map(float, line.strip().split()[1:4]))
            elif line.startswith('d '):
                materials[current_material]['d'] = float(line.strip().split()[1])
            elif line.startswith('illum '):
                materials[current_material]['illum'] = int(line.strip().split()[1])

    return materials
