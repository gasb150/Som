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
        self.vertices, self.faces, self.door_vertices, self.door_faces, self.wall_with_door_faces, self.wall_without_door_faces = self.create_room_with_door_and_window()
        self.camera_distance = 0  # Distancia inicial de la cámara
        self.camera_x = 10  # Posición inicial de la cámara en X (frente a la puerta)
        self.camera_y = 0  # Posición inicial de la cámara en Y
        self.camera_z = 40  # Posición inicial de la cámara en Z (fuera de la habitación)
        self.camera_speed = 0.5  # Velocidad de movimiento de la cámara
        self.rotation_speed = 2.0  # Velocidad de rotación de la cámara
        self.yaw = 180.0  # Rotación alrededor del eje Y (mirando hacia la puerta)
        self.pitch = 0.0  # Rotación alrededor del eje X
        self.mouse_sensitivity = 0.1  # Sensibilidad del mouse
        self.character_size = 0.5  # Tamaño del personaje
        self.door_open = False  # Estado inicial de la puerta (cerrada)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def create_room_with_door_and_window(self):
        # Crear una habitación más grande y rectangular con una puerta y una ventana
        # Hacemos las paredes más gruesas ajustando las coordenadas de los vértices
        vertices = [
            (-20, -20, -20),  # 0
            (20, -20, -20),   # 1
            (20, 20, -20),    # 2
            (-20, 20, -20),   # 3
            (-20, -20, 20),   # 4
            (20, -20, 20),    # 5
            (20, 20, 20),     # 6
            (-20, 20, 20),    # 7
            (-24, -24, -24),  # 8 (pared trasera exterior)
            (24, -24, -24),   # 9 (pared trasera exterior)
            (24, 24, -24),    # 10 (pared trasera exterior)
            (-24, 24, -24),   # 11 (pared trasera exterior)
            (-24, -24, 24),   # 12 (pared delantera exterior)
            (24, -24, 24),    # 13 (pared delantera exterior)
            (24, 24, 24),     # 14 (pared delantera exterior)
            (-24, 24, 24),    # 15 (pared delantera exterior)
            (-20, -24, -20),  # 16 (suelo exterior)
            (20, -24, -20),   # 17 (suelo exterior)
            (20, -24, 20),    # 18 (suelo exterior)
            (-20, -24, 20),   # 19 (suelo exterior)
            (-20, 24, -20),   # 20 (techo exterior)
            (20, 24, -20),    # 21 (techo exterior)
            (20, 24, 20),     # 22 (techo exterior)
            (-20, 24, 20)     # 23 (techo exterior)
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

        # Definir vértices y caras para la puerta
        door_vertices = [
            (5, -20, 20),  # 0
            (15, -20, 20),  # 1
            (15, 10, 20),  # 2
            (5, 10, 20)  # 3
        ]
        door_faces = [
            (0, 1, 2, 3)  # Cara de la puerta
        ]

        # Definir caras de la pared con y sin la puerta
        wall_with_door_faces = [
            (4, 0, 3, 7),  # Parte izquierda de la pared delantera con hueco para la puerta
            (1, 5, 6, 2),  # Parte derecha de la pared delantera con hueco para la puerta
            (0, 1, 2, 3)   # Parte superior de la pared delantera con hueco para la puerta
        ]
        wall_without_door_faces = [
            (4, 0, 3, 7),  # Parte izquierda de la pared delantera sin hueco
            (1, 5, 6, 2),  # Parte derecha de la pared delantera sin hueco
            (0, 1, 2, 3)   # Parte superior de la pared delantera sin hueco
        ]

        return vertices, faces, door_vertices, door_faces, wall_with_door_faces, wall_without_door_faces

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.running = False
                    elif event.key == K_RETURN:
                        self.door_open = not self.door_open  # Cambiar el estado de la puerta

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

            # Actualizar la posición de la cámara
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
            (0.5, 0.0, 0.5)   # Magenta oscuro para la conexión izquierda delantera
        ]
        for i, face in enumerate(self.faces[10:]):  # Las siguientes caras son las conexiones
            glColor3f(*connection_colors[i])
            glBegin(GL_QUADS)
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
            glEnd()

        # Renderizar la pared delantera con o sin la puerta
        if self.door_open:
            for face in self.wall_with_door_faces:
                glColor3f(0.0, 1.0, 0.0)  # Verde para la pared delantera con hueco para la puerta
                glBegin(GL_QUADS)
                for vertex_index in face:
                    glVertex3fv(self.vertices[vertex_index])
                glEnd()
        else:
            for face in self.wall_without_door_faces:
                glColor3f(0.0, 1.0, 0.0)  # Verde para la pared delantera sin hueco
                glBegin(GL_QUADS)
                for vertex_index in face:
                    glVertex3fv(self.vertices[vertex_index])
                glEnd()

        # Renderizar la puerta
        glColor3f(0.6, 0.3, 0.0)  # Color marrón para la puerta
        glBegin(GL_QUADS)
        for vertex_index in self.door_faces[0]:
            vertex = self.door_vertices[vertex_index]
            if self.door_open:
                # Si la puerta está abierta, rotarla alrededor del eje Y
                angle = np.radians(90)
                x, y, z = vertex
                x_new = x * np.cos(angle) - z * np.sin(angle)
                z_new = x * np.sin(angle) + z * np.cos(angle)
                vertex = (x_new, y, z_new)
            glVertex3fv(vertex)
        glEnd()

        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
