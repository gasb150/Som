import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from graphics import init_graphics, load_obj

from OpenGL.GL import glGetString, GL_VERSION
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Game')
        init_graphics()
        self.running = True
        self.vertices, self.faces = load_obj("/home/gsanmartin/Documents/Study/3DPython2/3d-game-project/assets/rooms/room1.obj")
        self.camera_distance = 20  # Distancia inicial de la cámara

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 4:  # Scroll up
                        self.camera_distance -= 1
                    elif event.button == 5:  # Scroll down
                        self.camera_distance += 1
                        print(self.camera_distance)
            self.render_scene()

            pygame.time.wait(10)

        pygame.quit()

    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(0, 0, self.camera_distance, 0, 0, 0, 0, 1, 0)  # Actualizar la posición de la cámara
        
       # glClearColor(1.0, 1.0, 1.0, 1.0)  # Establecer el color de fondo a blanco
        glColor3f(0.0, 0.0, 1.0)  # Establecer el color del cubo a rojo
        

        glBegin(GL_QUADS)
        for face in self.faces:
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()
       
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()