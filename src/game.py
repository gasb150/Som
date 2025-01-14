import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from graphics import init_graphics

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Game')
        init_graphics()
        self.running = True
        self.vertices, self.faces = self.create_room_with_door_and_window()
        self.camera_distance = 0  # Distancia inicial de la cámara
        self.camera_x = 0  # Posición inicial de la cámara en X
        self.camera_y = 0  # Posición inicial de la cámara en Y
        self.camera_z = 30  # Posición inicial de la cámara en Z (fuera de la habitación)
        self.camera_speed = 0.5  # Velocidad de movimiento de la cámara
        self.rotation_speed = 2.0  # Velocidad de rotación de la cámara
        self.yaw = 0.0  # Rotación alrededor del eje Y
        self.pitch = 0.0  # Rotación alrededor del eje X
        self.mouse_sensitivity = 0.1  # Sensibilidad del mouse
        self.character_size = 0.5  # Tamaño del personaje
        pygame.mouse.set_visible(True)
        pygame.event.set_grab(False)

    def create_room_with_door_and_window(self):
        # Crear una habitación más grande con una puerta y una ventana
        # Hacemos las paredes más gruesas ajustando las coordenadas de los vértices
        vertices = [
            (-10, -10, -10),  # 0
            (10, -10, -10),   # 1
            (10, 10, -10),    # 2
            (-10, 10, -10),   # 3
            (-10, -10, 10),   # 4
            (10, -10, 10),    # 5
            (10, 10, 10),     # 6
            (-10, 10, 10),    # 7
            (-12, -12, -12),  # 8 (pared trasera exterior)
            (12, -12, -12),   # 9 (pared trasera exterior)
            (12, 12, -12),    # 10 (pared trasera exterior)
            (-12, 12, -12),   # 11 (pared trasera exterior)
            (-12, -12, 12),   # 12 (pared delantera exterior)
            (12, -12, 12),    # 13 (pared delantera exterior)
            (12, 12, 12),     # 14 (pared delantera exterior)
            (-12, 12, 12),    # 15 (pared delantera exterior)
            (-10, -12, -10),  # 16 (suelo exterior)
            (10, -12, -10),   # 17 (suelo exterior)
            (10, -12, 10),    # 18 (suelo exterior)
            (-10, -12, 10),   # 19 (suelo exterior)
            (-10, 12, -10),   # 20 (techo exterior)
            (10, 12, -10),    # 21 (techo exterior)
            (10, 12, 10),     # 22 (techo exterior)
            (-10, 12, 10)     # 23 (techo exterior)
        ]
        faces = [
            (0, 1, 2, 3),  # Cara trasera interior
            (4, 5, 6, 7),  # Cara delantera interior
            (0, 1, 5, 4),  # Cara inferior interior
            (2, 3, 7, 6),  # Cara superior interior
            (0, 3, 7, 4),  # Cara izquierda interior
            (1, 2, 6, 5),  # Cara derecha interior
            (8, 9, 10, 11),  # Cara trasera exterior
            (12, 13, 14, 15),  # Cara delantera exterior
            (16, 17, 18, 19),  # Suelo exterior
            (20, 21, 22, 23),  # Techo exterior
            (0, 1, 9, 8),  # Conexión inferior trasera
            (1, 2, 10, 9),  # Conexión derecha trasera
            (2, 3, 11, 10),  # Conexión superior trasera
            (3, 0, 8, 11),  # Conexión izquierda trasera
            (4, 5, 13, 12),  # Conexión inferior delantera
            (5, 6, 14, 13),  # Conexión derecha delantera
            (6, 7, 15, 14),  # Conexión superior delantera
            (7, 4, 12, 15)   # Conexión izquierda delantera
        ]
        return vertices, faces

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
            keys = pygame.key.get_pressed()
            new_x, new_y, new_z = self.camera_x, self.camera_y, self.camera_z
            if keys[K_a]:
                new_x += self.camera_speed * np.sin(np.radians(self.yaw))  # Mover hacia izquierda
                new_z -= self.camera_speed * np.cos(np.radians(self.yaw))
            if keys[K_d]:
                new_x -= self.camera_speed * np.sin(np.radians(self.yaw))  # Mover hacia derecha
                new_z += self.camera_speed * np.cos(np.radians(self.yaw))
            if keys[K_s]:
                new_x -= self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia atás
                new_z -= self.camera_speed * np.sin(np.radians(self.yaw))
            if keys[K_w]:
                new_x += self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia adelante
                new_z += self.camera_speed * np.sin(np.radians(self.yaw))
            if keys[K_q]:
                self.yaw -= self.rotation_speed  # Rotar a la izquierda
            if keys[K_e]:
                self.yaw += self.rotation_speed  # Rotar a la derecha
            if keys[K_SPACE]:
                new_y += self.camera_speed  # Subir
            if keys[K_LSHIFT]:
                new_y -= self.camera_speed  # Bajar

            # Actualizar la posición de la cámara
            self.camera_x, self.camera_y, self.camera_z = new_x, new_y, new_z

            self.render_scene()
            pygame.time.wait(10)

        pygame.quit()

    def render_scene(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Calcular la dirección de la cámara
        direction_x = np.cos(np.radians(self.yaw))
        direction_y = 0
        direction_z = np.sin(np.radians(self.yaw))
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

        # Renderizar la habitación interior con colores diferentes para cada pared
        colors = [
            (1.0, 0.0, 0.0),  # Rojo para la cara trasera interior
            (0.0, 1.0, 0.0),  # Verde para la cara delantera interior
            (0.0, 0.0, 1.0),  # Azul para la cara inferior interior
            (1.0, 1.0, 0.0),  # Amarillo para la cara superior interior
            (1.0, 0.0, 1.0),  # Magenta para la cara izquierda interior
            (0.0, 1.0, 1.0)   # Cian para la cara derecha interior
        ]
        for i, face in enumerate(self.faces[:6]):  # Las primeras 6 caras son las de la habitación interior
            glColor3f(*colors[i])
            glBegin(GL_QUADS)
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        # Renderizar la habitación exterior con colores diferentes para cada pared
        exterior_colors = [
            (0.5, 0.0, 0.0),  # Rojo oscuro para la cara trasera exterior
            (0.0, 0.5, 0.0),  # Verde oscuro para la cara delantera exterior
            (0.0, 0.0, 0.5),  # Azul oscuro para el suelo exterior
            (0.5, 0.5, 0.0)   # Amarillo oscuro para el techo exterior
        ]
        for i, face in enumerate(self.faces[6:10]):  # Las siguientes caras son las de la habitación exterior
            glColor3f(*exterior_colors[i])
            glBegin(GL_QUADS)
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        # Renderizar las conexiones entre las paredes interiores y exteriores
        connection_colors = [
            (0.5, 0.0, 0.5),  # Magenta oscuro para la conexión inferior trasera
            (0.0, 0.5, 0.5),  # Cian oscuro para la conexión derecha trasera
            (0.5, 0.5, 0.5),  # Gris para la conexión superior trasera
            (0.5, 0.0, 0.0),  # Rojo oscuro para la conexión izquierda trasera
            (0.0, 0.5, 0.0),  # Verde oscuro para la conexión inferior delantera
            (0.0, 0.0, 0.5),  # Azul oscuro para la conexión derecha delantera
            (0.5, 0.5, 0.0),  # Amarillo oscuro para la conexión superior delantera
            (0.5, 0.0, 0.5)   # Magenta oscuro para la conexión izquierda delantera
        ]
        for i, face in enumerate(self.faces[10:]):  # Las siguientes caras son las conexiones
            glColor3f(*connection_colors[i])
            glBegin(GL_QUADS)
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
