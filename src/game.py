import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *  # Importar GLUT
import numpy as np
from graphics import init_graphics, load_obj
from input import handle_input
from utils import cargar_objeto, convertir_coordenadas
import os

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1000, 600), DOUBLEBUF | OPENGL)  # Aumentar el ancho de la ventana
        pygame.display.set_caption('3D Game')
        init_graphics()
        self.running = True
        # Usar una ruta relativa para cargar el archivo room.obj
        obj_path = os.path.join(os.path.dirname(__file__), '../assets/room.obj')
        self.vertices, self.faces, self.materials = load_obj(obj_path)
        self.camera_distance = 0  # Distancia inicial de la cámara
        self.camera_x = 0  # Posición inicial de la cámara en X
        self.camera_y = 0  # Posición inicial de la cámara en Y
        self.camera_z = 0  # Posición inicial de la cámara en Z
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
        self.light_on = True  # Estado inicial del foco (encendido)
        self.switch_position = (30, -10, 160)  # Posición del interruptor en la pared
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        self.font = pygame.font.SysFont('Arial', 18)  # Fuente para el texto de los controles
        self.show_mouse_icon = False  # Estado inicial de la visibilidad del icono del mouse
        self.mouse_icon1 = pygame.image.load(os.path.join(os.path.dirname(__file__), '../assets/mouse_icon_1.png'))  # Cargar la imagen del mouse
        self.mouse_icon2 = pygame.image.load(os.path.join(os.path.dirname(__file__), '../assets/mouse_icon_2.png'))  # Cargar la imagen del mouse
        self.current_mouse_icon = self.mouse_icon1 # Imagen actual del mouse
        self.mouse_icon_timer = 0  # Temporizador para alternar entre las imágenes del mouse

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

    def is_near_door(self):
        # Verificar si el jugador está cerca de la puerta
        door_x = 0
        door_y = -20
        door_z = 160
        distance = np.sqrt((self.camera_x - door_x) ** 2 + (self.camera_y - door_y) ** 2 + (self.camera_z - door_z) ** 2)
        return distance < 50  # Aumentar el umbral de distancia a 50 unidades

    def is_near_switch(self):
        # Verificar si el jugador está cerca del interruptor
        switch_x, switch_y, switch_z = self.switch_position
        distance = np.sqrt((self.camera_x - switch_x) ** 2 + (self.camera_y - switch_y) ** 2 + (self.camera_z - switch_z) ** 2)
        
        # Calcular la dirección en la que la cámara está mirando
        direction_x = np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        direction_y = np.sin(np.radians(self.pitch))
        direction_z = np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        camera_direction = np.array([direction_x, direction_y, direction_z])
        
        # Calcular el vector desde la cámara hasta el interruptor
        to_switch = np.array([switch_x - self.camera_x, switch_y - self.camera_y, switch_z - self.camera_z])
        to_switch_normalized = to_switch / np.linalg.norm(to_switch)
        
        # Calcular el ángulo entre la dirección de la cámara y el vector hacia el interruptor
        dot_product = np.dot(camera_direction, to_switch_normalized)
        angle = np.degrees(np.arccos(dot_product))
        
        # Verificar si la cámara está mirando hacia el interruptor (umbral de 30 grados)
        is_facing_switch = angle < 30
        
        return distance < 30 and is_facing_switch  # Umbral de distancia para activar el interruptor
        # Verificar si el jugador está cerca del interruptor
        switch_x, switch_y, switch_z = self.switch_position
        distance = np.sqrt((self.camera_x - switch_x) ** 2 + (self.camera_y - switch_y) ** 2 + (self.camera_z - switch_z) ** 2)
        return distance < 50  # Umbral de distancia para activar el interruptor

    def run(self):
        while self.running:
            handle_input(self)

            # Actualizar la animación de la puerta
            if self.door_animating:
                self.update_door_animation()

             # Actualizar el temporizador del icono del mouse
            self.mouse_icon_timer += 1
            if self.mouse_icon_timer >= 30:  # Alternar cada 30 fotogramas (ajusta según sea necesario)
              self.mouse_icon_timer = 0
              if self.current_mouse_icon == self.mouse_icon1:
                self.current_mouse_icon = self.mouse_icon2
              else:
                self.current_mouse_icon = self.mouse_icon1

            self.render_scene()
            pygame.display.flip()  # Mover la actualización de la pantalla aquí
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

        # Imprimir el progreso de la animación para depuración
        print(f"Door animation progress: {self.door_animation_progress}")

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
    
    
        # Encender o apagar la luz según el estado de light_on
        if self.light_on:
            glEnable(GL_LIGHT0)
            # Posicionar la luz en el bombillo
            glLightfv(GL_LIGHT0, GL_POSITION, (0, 30, -100, 1))  # (x, y, z, w) w=1 para luz puntual
            glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 1, 1))
            glLightfv(GL_LIGHT0, GL_SPECULAR, (1, 1, 1, 1))
            glLightfv(GL_LIGHT0, GL_AMBIENT, (0, 0, 0, 1))  # Luz ambiental más fuerte
        else:
            glDisable(GL_LIGHT0)
    
        # Renderizar el interruptor en la pared
        self.render_switch()
    
        # Renderizar los controles en la pantalla
        self.render_controls()
    
        # Renderizar la barra de progreso de la puerta
        self.render_door_progress()
    
        # Renderizar el bombillo colgando de un bastón
        self.render_light_bulb()

        # Renderizar el icono del mouse si es necesario
        self.render_mouse_icon()

    def render_light_bulb(self):
        # Renderizar el bastón
        glPushMatrix()
        glTranslatef(0, 40, 40)  # Posicionar el bastón en el centro del techo
        if 'LampMaterial' in self.materials:
            mat = self.materials['LampMaterial']
            glMaterialfv(GL_FRONT, GL_AMBIENT, mat['Ka'])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, mat['Kd'])
            glMaterialfv(GL_FRONT, GL_SPECULAR, mat['Ks'])
            shininess = max(0, min(128, mat['illum'] * 128))
            glMaterialf(GL_FRONT, GL_SHININESS, shininess)
        glBegin(GL_QUADS)
        glVertex3f(-0.5, 0, 0)
        glVertex3f(0.5, 0, 0)
        glVertex3f(0.5, -10, 0)
        glVertex3f(-0.5, -10, 0)
        glEnd()
        glPopMatrix()
    
        # Renderizar el bombillo
        glPushMatrix()
        glTranslatef(0, 30, 40)  # Posicionar el bombillo al final del bastón
        glColor3f(1, 1, 0)  # Color amarillo para el bombillo
        glutSolidSphere(2, 20, 20)  # Dibujar una esfera como bombillo
        glPopMatrix()
    
        glColor3f(1, 1, 1)  # Restaurar el color blanco para los objetos restantes
    
    def render_switch(self):
        # Verificar si el jugador está cerca del interruptor
        if self.is_near_switch():
            self.show_mouse_icon = True
        else:
            self.show_mouse_icon = False

        # Renderizar el interruptor en la pared
        glPushMatrix()
        glTranslatef(*self.switch_position)
        if 'SwitchMaterial' in self.materials:
            mat = self.materials['SwitchMaterial']
            glMaterialfv(GL_FRONT, GL_AMBIENT, mat['Ka'])
            glMaterialfv(GL_FRONT, GL_DIFFUSE, mat['Kd'])
            glMaterialfv(GL_FRONT, GL_SPECULAR, mat['Ks'])
            shininess = max(0, min(128, mat['illum'] * 128))
            glMaterialf(GL_FRONT, GL_SHININESS, shininess)
        glBegin(GL_QUADS)
        glVertex3f(-1, -1, 0)
        glVertex3f(1, -1, 0)
        glVertex3f(1, 1, 0)
        glVertex3f(-1, 1, 0)
        glEnd()
        glPopMatrix()


    def render_controls(self):
        controls_text = [
            "WASD: Move",
            "Mouse: Look around",
            "Space: Move up",
            "Shift: Move down",
            "Q/E: Rotate",
            "Enter: Open/Close door",
            "Esc: Quit"
        ]
        y_offset = 10
        text_color = (0, 0, 0) if self.light_on else (255, 255, 255)
        for i, line in enumerate(controls_text):
            self.render_text(line, 10, y_offset + i * 20, color=text_color)

    def render_text(self, text, x, y, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        glWindowPos2d(x, y)
    
        # Guardar el estado actual de OpenGL
        glPushAttrib(GL_ALL_ATTRIB_BITS)
    
        # Configurar el modo de mezcla para renderizar el texto correctamente
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
        # Restaurar el estado anterior de OpenGL
        glPopAttrib()

    def render_door_progress(self):
        if self.door_animating:
            progress_text = "Opening" if not self.door_open else "Closing"
            screen_width, screen_height = self.screen.get_size()
            bar_width, bar_height = 200, 20
            x = (screen_width - bar_width) // 2
            y = (screen_height - bar_height) // 2
            self.render_progress_bar(x, y, bar_width, bar_height, self.door_animation_progress, progress_text)

    def render_progress_bar(self, x, y, width, height, progress, text):
        # Guardar el estado actual de OpenGL
        glPushAttrib(GL_ALL_ATTRIB_BITS)

        # Configurar el modo de proyección para 2D
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, self.screen.get_width(), self.screen.get_height(), 0)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Deshabilitar la prueba de profundidad para dibujar en 2D
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)  # Deshabilitar la iluminación para dibujar en 2D

        # Dibujar el fondo de la barra de progreso
        glColor4f(0.5, 0.5, 0.5, 1)  # Color gris para el fondo
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # Dibujar la barra de progreso
        glColor4f(0, 1, 0, 1)  # Color verde para la barra de progreso
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width * progress, y)
        glVertex2f(x + width * progress, y + height)
        glVertex2f(x, y + height)
        glEnd()

        # Renderizar el texto encima de la barra de progreso
        self.render_text(text, x + width // 2 - 30, y - 30)  # Ajustar la posición y

        # Restaurar el estado anterior de OpenGL
        glEnable(GL_DEPTH_TEST)  # Habilitar la prueba de profundidad nuevamente
        glEnable(GL_LIGHTING)  # Habilitar la iluminación nuevamente
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        glPopAttrib()
    
    def render_mouse_icon(self):
        if self.show_mouse_icon:
            icon_width, icon_height = self.current_mouse_icon.get_size()
            icon_data = pygame.image.tostring(self.current_mouse_icon, "RGBA", True)
            glWindowPos2d(self.screen.get_width() // 2 - icon_width // 2, self.screen.get_height() // 2 - icon_height // 2)
    
            # Guardar el estado actual de OpenGL
            glPushAttrib(GL_ALL_ATTRIB_BITS)
    
            # Configurar el modo de mezcla para renderizar la imagen correctamente
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
            glDrawPixels(icon_width, icon_height, GL_RGBA, GL_UNSIGNED_BYTE, icon_data)
    
            # Restaurar el estado anterior de OpenGL
            glPopAttrib()

if __name__ == "__main__":
    glutInit()  # Inicializar GLUT
    game = Game()
    game.run()