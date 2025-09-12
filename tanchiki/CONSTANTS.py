import pygame

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (52, 103, 235)
ORANGE = (224, 130, 29)

PLAYER_COLOR = BLACK
WALL_COLOR = ORANGE
ENEMY_COLOR = BLACK
POINT_COLOR = BLUE
BULLET_COLOR = WHITE

BULLET_SIZE = 10
WALL_SIZE = 23
ENTITY_SIZE = 20
POINT_SIZE = 10

BRICK_TEXTURE = pygame.transform.scale(pygame.image.load('brick.png'), (WALL_SIZE,WALL_SIZE))
rotated_player_texture = player_texture = pygame.transform.scale(pygame.image.load('player.png'), (ENTITY_SIZE, ENTITY_SIZE))
rotated_enemy_texture = enemy_texture = pygame.transform.scale(pygame.image.load('enemy.png'), (ENTITY_SIZE, ENTITY_SIZE))

MAP = [1, 1, 1, 1, 1, 
        1, 0, 0, 0, 1,
        1, 0, 0, 0, 1,
        1, 0, 0, 0, 1,
        1, 1, 1, 1, 1
        ]