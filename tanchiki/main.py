import pygame
import sys

# from CONSTANTS import *#константы, цвета и тд
from game import *#логика игры
from gui import *

import threading

pygame.init()
pygame.font.init()

my_font = pygame.font.Font('font.ttf', 20)
game_started = False

map_genrator = Map()
c = pygame.time.Clock()

set_enemy_pos_event = pygame.USEREVENT + 1#Ивент, для изменения позиций врагов
pygame.time.set_timer(set_enemy_pos_event, 50)#Раз в 50 мили сек все враги будут передвигаться

bullet_timer = pygame.USEREVENT + 2#Ивент, для таймера между выстрелами для игрока и для врагов
pygame.time.set_timer(bullet_timer, 700)

start_game_btn = Button(screen.get_size()[0]/2-115, screen.get_size()[1]/2-120, 230, 75, "PLAY", RED, 100, [-2, -7])#screen.get_size()[0]/2, screen.get_size()[1]/2
# game_settings_btn = Button(screen.get_size()[0]/2-130, screen.get_size()[1]/2-30, 260, 40, "SETTINGS", RED, 60)
map_size_plus_btn = Button(screen.get_size()[0]/2+10, screen.get_size()[1]/2-33, 26, 24, "+", RED, 35, [-1, -4])
map_size_minus_btn = Button(screen.get_size()[0]/2+50, screen.get_size()[1]/2-33, 25, 25, "-", RED, 70, [2, -25])
new_game_btn = Button(screen.get_size()[0]/2-100, screen.get_size()[1]/2-50, 220, 45, "NEW GAME", RED, 50)

font_2 = pygame.font.Font('font.ttf', 50)
game_over_text = font_2.render("GAME OVER", False, RED)
win_text = font_2.render("GAME WIN", False, GREEN)

def to_menu():
    global game_started, player
    game_started = False
    player.win = False
    player.point_counter = 0
    player.enemy_killed_counter = 0

def start_game():
    global game_started, player, map_genrator
    map_genrator.map.clear()
    enemys.clear()
    walls.clear()
    points.clear()
     
    map_genrator.generator()
    map_genrator.draw()

    game_started = True
    player.Live = True
    
def map_size_plus():
    global map_genrator
    if map_genrator.map_size < 20:
        map_genrator.map_size += 1

def map_size_minus():
    global map_genrator
    if map_genrator.map_size > 10:
        map_genrator.map_size -= 1
    
while True:
    c.tick(80)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if player.Live:
            if event.type == set_enemy_pos_event:
                pass
                # for i in enemys:
                    # i.moving_and_collision(walls)

            if event.type == bullet_timer:
                player.can_bullet = True  

                for i in enemys:
                    i.can_bullet = True
                    
    if game_started == True:
        if player.Live == True and player.win == False:
            
            player.draw()#Отрисовка игрока
            player.controls_collision(walls)#Управление игроком и коллизия со стенами 
            player.get_points(points)#Проверка, прикасается ли игрок к очкам
            
            for i in bullets:
                i.draw()
                i.move()
                try:
                    if i.collision(player): continue
                    if i.collision(walls): continue
                    if i.collision(enemys): continue
                    if i.collision(bullets): continue
                except Exception as e:
                    break

            for i in walls:
                i.draw()
            
            for i in points:
                i.draw()

            for i in enemys:
                
                # threading.Thread(target=i.moving_and_collision, args=(walls,)).start()
                
                i.moving_and_collision(walls)
                i.pull_bullet()
                i.draw()
                

        elif player.Live == False:
            screen.blit(game_over_text, (screen.get_size()[0]/2-115, screen.get_size()[1]/2-100))
            new_game_btn.draw(screen, to_menu)
        
        elif player.win == True:
            screen.blit(win_text, (screen.get_size()[0]/2-95, screen.get_size()[1]/2-100))
            new_game_btn.draw(screen, to_menu)
        
    else:
        map_size_plus_btn.draw(screen, map_size_plus)
        map_size_minus_btn.draw(screen, map_size_minus)
        start_game_btn.draw(screen, start_game)
        
        map_size_txt = my_font.render(f"MAP SIZE: {map_genrator.map_size}", False, WHITE)
        screen.blit(map_size_txt, (screen.get_size()[0]/2-115, screen.get_size()[1]/2-30))

    # pygame.draw.rect(screen, GREEN, pygame.Rect(pygame.display.get_window_size()[0]/2, 0, 3, 1000), 0)
    # pygame.draw.rect(screen, GREEN, pygame.Rect(0, pygame.display.get_window_size()[1]/2, 1000, 3), 0)
    
    fps_text = my_font.render(f'FPS {int(c.get_fps())}', False, WHITE)
    screen.blit(fps_text, (0,0))

    points_text = my_font.render(f'Points: {player.point_counter}', False, WHITE)
    screen.blit(points_text, (0,15))

    enemy_killed_text = my_font.render(f'Enemy killed: {player.enemy_killed_counter}', False, WHITE)
    screen.blit(enemy_killed_text, (0,32))

    pygame.display.flip()
    screen.fill(BLACK)