import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from graphics import init_graphics, load_obj

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600), DOUBLEBUF | OPENGL)
        pygame.display.set_caption('3D Game')
        init_graphics()
        self.running = True
        self.vertices, self.faces = load_obj(r"C:\Users\hp\Documents\Tavo\Som\assets\rooms\wooden-watch-tower2.obj")
        self.camera_distance = 20  # Distancia inicial de la cámara
        self.camera_x = 0  # Posición inicial de la cámara en X
        self.camera_y = 0  # Posición inicial de la cámara en Y
        self.camera_z = 0  # Posición inicial de la cámara en Z
        self.camera_speed = 0.5  # Velocidad de movimiento de la cámara
        self.yaw = 0.0  # Rotación alrededor del eje Y
        self.pitch = 0.0  # Rotación alrededor del eje X
        self.mouse_sensitivity = 0.1  # Sensibilidad del mouse
        self.character_size = 1  # Tamaño del personaje
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.bounding_boxes = self.calculate_bounding_boxes()

    def calculate_bounding_boxes(self):
        # Calcular los bounding boxes para cada cara del objeto
        bounding_boxes = []
        for face in self.faces:
            vertices = [self.vertices[vertex_index] for vertex_index in face]
            min_x = min(vertex[0] for vertex in vertices)
            max_x = max(vertex[0] for vertex in vertices)
            min_y = min(vertex[1] for vertex in vertices)
            max_y = max(vertex[1] for vertex in vertices)
            min_z = min(vertex[2] for vertex in vertices)
            max_z = max(vertex[2] for vertex in vertices)
            bounding_boxes.append(((min_x, min_y, min_z), (max_x, max_y, max_z)))
 
        return bounding_boxes

    def check_collision(self, new_x, new_y, new_z):
        # Comprobar si la nueva posición de la cámara colisiona con algún bounding box
        for (min_corner, max_corner) in self.bounding_boxes:
            if (min_corner[0] - self.character_size <= new_x <= max_corner[0] + self.character_size and
                min_corner[1] - self.character_size <= new_y <= max_corner[1] + self.character_size and
                min_corner[2] - self.character_size <= new_z <= max_corner[2] + self.character_size):
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
            keys = pygame.key.get_pressed()
            new_x, new_y, new_z = self.camera_x, self.camera_y, self.camera_z
            if keys[K_w]:
                new_z -= self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia adelante
                new_x += self.camera_speed * np.sin(np.radians(self.yaw))
            if keys[K_s]:
                new_z += self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia atrás
                new_x -= self.camera_speed * np.sin(np.radians(self.yaw))
            if keys[K_a]:
                new_x -= self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia la izquierda
                new_z -= self.camera_speed * np.sin(np.radians(self.yaw))
            if keys[K_d]:
                new_x += self.camera_speed * np.cos(np.radians(self.yaw))  # Mover hacia la derecha
                new_z += self.camera_speed * np.sin(np.radians(self.yaw))
            if keys[K_SPACE]:
                new_y += self.camera_speed  # Subir
            if keys[K_LSHIFT]:
                new_y -= self.camera_speed  # Bajar

            # Capturar el movimiento del mouse
            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            self.yaw += mouse_dx * self.mouse_sensitivity
            self.pitch -= mouse_dy * self.mouse_sensitivity

            # Limitar el pitch para evitar que la cámara se voltee
            self.pitch = max(-89.0, min(89.0, self.pitch))

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

        gluLookAt(self.camera_x, self.camera_y, self.camera_distance + self.camera_z,
                  camera_target[0], camera_target[1], camera_target[2],
                  0, 1, 0)  # Actualizar la posición de la cámara
        
        glColor3f(0.0, 0.0, 1.0)  # Establecer el color del cubo a rojo

        # Renderizar la torre
        glBegin(GL_QUADS)
        for face in self.faces:
            for vertex_index in face:
                glVertex3fv(self.vertices[vertex_index])
        glEnd()

        # Renderizar el suelo
        glColor3f(0.5, 0.5, 0.5)  # Color gris para el suelo
        glBegin(GL_QUADS)
        glVertex3f(-500, -1, -500)
        glVertex3f(500, -1, -500)
        glVertex3f(500, -1, 500)
        glVertex3f(-500, -1, 500)
        glEnd()
       
        pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()