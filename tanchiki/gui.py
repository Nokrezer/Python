import pygame
from CONSTANTS import *
from game import screen

pygame.font.init()


class Button:
    def __init__(self, x, y, height, width, text="", color=BLACK, text_size=20, text_pos=[0, 0]):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.color = color
        self.rect = pygame.Rect(self.x, self.y, self.height, self.width)
        self.text = text
        self.text_pos = text_pos

        self.past_pressed = False

        self.font = pygame.font.Font('font.ttf', text_size)

    def draw(self, screen, event):
        pygame.draw.rect(screen, self.color, self.rect, 0)

        draw_text = self.font.render(self.text, False, WHITE)
        screen.blit(draw_text, (self.x+self.text_pos[0], self.y+self.text_pos[1]))

        mouse_x, mouse_y = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed(3)
        
        if mouse_x > self.rect.x and mouse_x < self.rect.right and mouse_y > self.rect.y and mouse_y < self.rect.bottom and pressed[0] == False and self.past_pressed == True:
            event()

        self.past_pressed = pressed[0]