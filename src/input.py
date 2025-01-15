import pygame
from pygame.locals import *
import numpy as np

def handle_input(game):
    for event in pygame.event.get():
        if event.type == QUIT:
            game.running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                game.running = False
            elif event.key == K_RETURN:
                if game.is_near_door():
                    game.door_animating = True

    # Capturar el movimiento del mouse
    mouse_dx, mouse_dy = pygame.mouse.get_rel()
    game.yaw += mouse_dx * game.mouse_sensitivity
    game.pitch -= mouse_dy * game.mouse_sensitivity

    # Limitar el ángulo de pitch para evitar rotaciones extrañas
    game.pitch = max(-89.0, min(89.0, game.pitch))

    keys = pygame.key.get_pressed()
    new_x, new_y, new_z = game.camera_x, game.camera_y, game.camera_z
    if keys[K_a]:
        new_x += game.camera_speed * np.sin(np.radians(game.yaw))  # Mover hacia izquierda
        new_z -= game.camera_speed * np.cos(np.radians(game.yaw))
    if keys[K_d]:
        new_x -= game.camera_speed * np.sin(np.radians(game.yaw))  # Mover hacia derecha
        new_z += game.camera_speed * np.cos(np.radians(game.yaw))
    if keys[K_s]:
        new_x -= game.camera_speed * np.cos(np.radians(game.yaw))  # Mover hacia atrás
        new_z -= game.camera_speed * np.sin(np.radians(game.yaw))
    if keys[K_w]:
        new_x += game.camera_speed * np.cos(np.radians(game.yaw))  # Mover hacia adelante
        new_z += game.camera_speed * np.sin(np.radians(game.yaw))
    if keys[K_q]:
        game.yaw -= game.rotation_speed  # Rotar a la izquierda
    if keys[K_e]:
        game.yaw += game.rotation_speed  # Rotar a la derecha
    if keys[K_SPACE]:
        new_y += game.camera_speed  # Subir
    if keys[K_LSHIFT]:
        new_y -= game.camera_speed  # Bajar

    # Comprobar colisiones antes de actualizar la posición de la cámara
    if not game.check_collision(new_x, new_y, new_z):
        game.camera_x, game.camera_y, game.camera_z = new_x, new_y, new_z
