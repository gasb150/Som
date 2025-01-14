import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from graphics import init_graphics, load_obj
from input import handle_input
from utils import cargar_objeto, convertir_coordenadas
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Game')
        init_graphics()
        self.running = True
        # Usar una ruta relativa para cargar el archivo room.obj
        obj_path = os.path.join(os.path.dirname(__file__), '../assets/room.obj')
        self.vertices, self.faces, self.materials = load_obj(obj_path)
        self.camera_distance = 0  # Distancia inicial de la cámara
        self.camera_x = 0  # Posición inicial de la cámara en X
        self.camera_y = 0  # Posición inicial de la cámara en Y
        self.camera_z = 160  # Posición inicial de la cámara en Z (fuera de la habitación)
        self.camera_speed = 1.0  # Velocidad de movimiento de la cámara
        self.rotation_speed = 2.0  # Velocidad de rotación de la cámara
        self.yaw = 0.0  # Rotación alrededor del eje Y
        self.pitch = 0.0  # Rotación alrededor del eje X
        self.mouse_sensitivity = 0.1  # Sensibilidad del mouse
        self.character_size = 0.5  # Tamaño del personaje
        self.door_open = False  # Estado inicial de la puerta (cerrada)
        self.door_animating = False  # Estado de la animación de la puerta
        self.door_animation_progress = 0.0  # Progreso de la animación de la puerta
        self.door_animation_speed = 0.02  # Velocidad de la animación de la puerta
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def check_collision(self, new_x, new_y, new_z):
        # Definir las áreas de colisión para las paredes
        wall_thickness = 1.0
        door_width = 20.0
        door_height = 40.0

        # Colisiones con las paredes laterales
        if new_x <= -40 + wall_thickness or new_x >= 40 - wall_thickness:
            return True
        # Colisiones con las paredes traseras y delanteras (excepto el hueco de la puerta)
        if (new_z <= -80 + wall_thickness or
            (new_z >= 160 - wall_thickness and
             (new_x < -10 or new_x > 10 or new_y < -40 or new_y > 0))):
            return True
        # Colisiones con el suelo y el techo
        if new_y <= -40 + wall_thickness or new_y >= 40 - wall_thickness:
            return True

        # Colisiones con la puerta cuando está cerrada
        if not self.door_open and not self.door_animating:
            if (new_z >= 160 - wall_thickness and
                -10 <= new_x <= 10 and -40 <= new_y <= 0):
                return True

        return False

    def run(self):
        while self.running:
            handle_input(self)

            # Actualizar la animación de la puerta
            if self.door_animating:
                self.update_door_animation()

            self.render_scene()
            pygame.time.wait(10)

        pygame.quit()

    def update_door_animation(self):
        if self.door_open:
            # Animar el cierre de la puerta
            self.door_animation_progress -= self.door_animation_speed
            if self.door_animation_progress <= 0.0:
                self.door_animation_progress = 0.0
                self.door_open = False
                self.door_animating = False
        else:
            # Animar la apertura de la puerta
            self.door_animation_progress += self.door_animation_speed
            if self.door_animation_progress >= 1.0:
                self.door_animation_progress = 1.0
                self.door_open = True
                self.door_animating = False

        # Interpolar la posición de la puerta
        door_offset = self.door_animation_progress * 20.0
        self.vertices[32] = (-10 - door_offset, -40, 160)
        self.vertices[33] = (10 - door_offset, -40, 160)
        self.vertices[34] = (-10 - door_offset, 0, 160)
        self.vertices[35] = (10 - door_offset, 0, 160)

    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Calcular la dirección de la cámara
        direction_x = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        direction_y = np.sin(np.radians(self.pitch))
        direction_z = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        camera_direction = np.array([direction_x, direction_y, direction_z])
        camera_target = np.array([self.camera_x, self.camera_y, self.camera_z]) + camera_direction

        gluLookAt(self.camera_x, self.camera_y, self.camera_z,
                  camera_target[0], camera_target[1], camera_target[2],
                  0, 1, 0)  # Actualizar la posición de la cámara

        # Deshabilitar el culling de caras traseras
        glDisable(GL_CULL_FACE)

        # Ajustar la configuración de profundidad
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)

        # Renderizar la habitación con materiales
        for face, material in self.faces:
            if material in self.materials:
                mat = self.materials[material]
                glMaterialfv(GL_FRONT, GL_AMBIENT, mat['Ka'])
                glMaterialfv(GL_FRONT, GL_DIFFUSE, mat['Kd'])
                glMaterialfv(GL_FRONT, GL_SPECULAR, mat['Ks'])
                # Asegurarse de que el valor de GL_SHININESS esté en el rango permitido
                shininess = max(0, min(128, mat['illum'] * 128))
                glMaterialf(GL_FRONT, GL_SHININESS, shininess)
                glColor4fv(mat['Kd'] + [mat['d']])
            glBegin(GL_QUADS)
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
