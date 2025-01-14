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
        self.camera_z = 160  # Posición inicial de la cámara en Z (fuera de la habitación)
        self.camera_speed = 1.0  # Velocidad de movimiento de la cámara
        self.rotation_speed = 2.0  # Velocidad de rotación de la cámara
        self.yaw = 0.0  # Rotación alrededor del eje Y
        self.pitch = 0.0  # Rotación alrededor del eje X
        self.mouse_sensitivity = 0.1  # Sensibilidad del mouse
        self.character_size = 0.5  # Tamaño del personaje
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def create_room_with_door_and_window(self):
        # Crear una habitación más grande y rectangular con un hueco para la puerta
        vertices = [
            (-40, -40, -80),  # 0
            (40, -40, -80),   # 1
            (40, 40, -80),    # 2
            (-40, 40, -80),   # 3
            (-40, -40, 160),  # 4
            (40, -40, 160),   # 5
            (40, 40, 160),    # 6
            (-40, 40, 160),   # 7
            (-48, -48, -96),  # 8 (pared trasera exterior)
            (48, -48, -96),   # 9 (pared trasera exterior)
            (48, 48, -96),    # 10 (pared trasera exterior)
            (-48, 48, -96),   # 11 (pared trasera exterior)
            (-48, -48, 192),  # 12 (pared delantera exterior)
            (48, -48, 192),   # 13 (pared delantera exterior)
            (48, 48, 192),    # 14 (pared delantera exterior)
            (-48, 48, 192),   # 15 (pared delantera exterior)
            (-40, -48, -80),  # 16 (suelo exterior)
            (40, -48, -80),   # 17 (suelo exterior)
            (40, -48, 160),   # 18 (suelo exterior)
            (-40, -48, 160),  # 19 (suelo exterior)
            (-40, 48, -80),   # 20 (techo exterior)
            (40, 48, -80),    # 21 (techo exterior)
            (40, 48, 160),    # 22 (techo exterior)
            (-40, 48, 160),   # 23 (techo exterior)
            (-10, -40, 160),  # 24 (borde izquierdo del hueco de la puerta)
            (10, -40, 160),   # 25 (borde derecho del hueco de la puerta)
            (-10, 0, 160),    # 26 (borde superior izquierdo del hueco de la puerta)
            (10, 0, 160),     # 27 (borde superior derecho del hueco de la puerta)
            (-10, -48, 192),  # 28 (borde izquierdo del hueco de la puerta exterior)
            (10, -48, 192),   # 29 (borde derecho del hueco de la puerta exterior)
            (-10, 0, 192),    # 30 (borde superior izquierdo del hueco de la puerta exterior)
            (10, 0, 192)      # 31 (borde superior derecho del hueco de la puerta exterior)
        ]
        faces = [
            (0, 1, 2, 3),  # Cara trasera interior
            (4, 24, 26, 7),  # Parte izquierda de la cara delantera interior
            (25, 5, 6, 27),  # Parte derecha de la cara delantera interior
            (26, 27, 6, 7),  # Parte superior de la cara delantera interior
            (0, 1, 5, 4),  # Cara inferior interior
            (2, 3, 7, 6),  # Cara superior interior
            (0, 3, 7, 4),  # Cara izquierda interior
            (1, 2, 6, 5),  # Cara derecha interior
            (8, 9, 10, 11),  # Cara trasera exterior
            (12, 28, 30, 15),  # Parte izquierda de la cara delantera exterior
            (29, 13, 14, 31),  # Parte derecha de la cara delantera exterior
            (30, 31, 14, 15),  # Parte superior de la cara delantera exterior
            (16, 17, 18, 19),  # Suelo exterior
            (20, 21, 22, 23),  # Techo exterior
            (0, 1, 9, 8),  # Conexión inferior trasera
            (1, 2, 10, 9),  # Conexión derecha trasera
            (2, 3, 11, 10),  # Conexión superior trasera
            (3, 0, 8, 11),  # Conexión izquierda trasera
            (4, 5, 13, 12),  # Conexión inferior delantera
            (5, 6, 14, 13),  # Conexión derecha delantera
            (6, 7, 15, 14),  # Conexión superior delantera
            (7, 4, 12, 15),  # Conexión izquierda delantera
            (24, 25, 29, 28),  # Marco inferior de la puerta
            (26, 27, 31, 30),  # Marco superior de la puerta
            (24, 26, 30, 28),  # Marco izquierdo de la puerta
            (25, 27, 31, 29)   # Marco derecho de la puerta
        ]

        return vertices, faces

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

        return False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False

            # Capturar el movimiento del mouse
            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            self.yaw += mouse_dx * self.mouse_sensitivity
            self.pitch -= mouse_dy * self.mouse_sensitivity

            # Limitar el ángulo de pitch para evitar rotaciones extrañas
            self.pitch = max(-89.0, min(89.0, self.pitch))

            keys = pygame.key.get_pressed()
            new_x, new_y, new_z = self.camera_x, self.camera_y, self.camera_z
            if keys[K_a]:
                new_x += self.camera_speed * np.sin(np.radians(self.yaw))  # Mover hacia izquierda
                new_z -= self.camera_speed * np.cos(np.radians(self.yaw))
            if keys[K_d]:
                new_x -= self.camera_speed * np.sin(np.radians(self.yaw))  # Mover hacia derecha
                new_z += self.camera_speed * np.cos(np.radians(self.yaw))
            if keys[K_s]:
                new_x -= self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia atrás
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

            # Comprobar colisiones antes de actualizar la posición de la cámara
            if not self.check_collision(new_x, new_y, new_z):
                self.camera_x, self.camera_y, self.camera_z = new_x, new_y, new_z

            self.render_scene()
            pygame.time.wait(10)

        pygame.quit()

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
            (0.5, 0.0, 0.5),  # Magenta oscuro para la conexión izquierda delantera
            (0.5, 0.0, 0.5),  # Magenta oscuro para la conexión inferior delantera
            (0.0, 0.5, 0.5),  # Cian oscuro para la conexión derecha delantera
            (0.5, 0.5, 0.5),  # Gris para la conexión superior delantera
            (0.5, 0.0, 0.0)   # Rojo oscuro para la conexión izquierda delantera
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
