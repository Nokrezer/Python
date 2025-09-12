from CONSTANTS import *
import pygame

import random

from time import sleep

screen = pygame.display.set_mode((900, 500), vsync=False)

map = []

class Entity:
    def __init__(self):
        self.max_speed = 1

        self.rotation = 0

        self.past_speed_x = 0
        self.past_speed_y = 0

        self.can_bullet = True#Может ли сущность стрелять(необходимо для задержек между выпуском пуль)

        self.width = ENTITY_SIZE
        self.height = ENTITY_SIZE

        self.x = 0
        self.y = 0

        self.color = pygame.SRCALPHA

class Player(Entity):
    def __init__(self):
        super().__init__()

        self.speed = 0.4#Скорость
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)#Объект

        self.Live = False
        self.win = False

        self.point_counter = 0
        self.enemy_killed_counter = 0

    def draw(self):#Функция отрисовки сущности
        global rotated_player_texture
        pygame.draw.rect(screen, self.color, self.rect, 0)
        screen.blit(rotated_player_texture, self.rect)

    def controls_collision(self, collisions):#Управление игрока
        global player_texture, rotated_player_texture
        keys = pygame.key.get_pressed()#Получаем состояние всех нажатых клавиш
        
        if keys[pygame.K_a]:#Лево
            self.rotation = 90

            self.x += -self.speed
            self.past_speed_x = -1
            self.past_speed_y = 0

        elif keys[pygame.K_d]:#Право
            self.rotation = -90

            self.x += self.speed
            self.past_speed_x = 1
            self.past_speed_y = 0

        else:
            if keys[pygame.K_w]:#Верх
                self.rotation = 360

                self.y += -self.speed
                self.past_speed_y = -1
                self.past_speed_x = 0

            if keys[pygame.K_s]:#Вниз
                self.rotation = 180

                self.y += self.speed
                self.past_speed_y = 1
                self.past_speed_x = 0

        rotated_player_texture = pygame.transform.rotate(player_texture, self.rotation)

        if keys[pygame.K_SPACE] and self.can_bullet and (self.past_speed_x != 0 or self.past_speed_y != 0):#Если нажат пробел и можно стрелять
            self.can_bullet = False#Запрет на стреляние

            player_bullet = Bullet(self.rect.x+BULLET_SIZE/2, self.rect.y+BULLET_SIZE/2)#Создаем пулю
            player_bullet.Enemy_bullet = False#Не вражеская пуля

            player_bullet.speed_x = self.past_speed_x
            player_bullet.speed_y = self.past_speed_y
            
            bullets.append(player_bullet)#Добавляем в массив, для дальнейшей работы

        if self.x >= self.max_speed or self.x <= -self.max_speed:#Изменяем позицию игрока, если скорость достигла максимальной
            self.rect.x += self.x#Передвигаем игрока по x

        for wall in collisions:#перебираем массив с стенами

            if self.rect.colliderect(wall.rect):#Если игрок соприкоснулся со стеной
                if self.x > 0:
                    self.rect.right = wall.rect.left#Колллизия
                    break

                elif self.x < 0:
                    self.rect.left = wall.rect.right#Колллизия
                    break
        
        if self.x >= self.max_speed or self.x <= -self.max_speed:#Если x > максимальной скорости или меньше минусовой макс скорости, то
            self.x = 0#Сбрасываем скорость по x
            

        if self.y >= self.max_speed or self.y <= -self.max_speed:#Проверка, нужна чтобы число не округлялось до целого при изменении позиции игрока
            self.rect.y += self.y

        for wall in collisions:#перебираем массив с стенами
            if self.rect.colliderect(wall.rect):

                if self.y > 0:
                    self.rect.bottom = wall.rect.top#Колллизия
                    break

                elif self.y < 0:
                    self.rect.top = wall.rect.bottom#Колллизия
                    break
        
        if self.y >= self.max_speed or self.y <= -self.max_speed:
            self.y = 0#Сбрасываем скорость по y

    def get_points(self, points):
        global player

        for point in points:
            if self.rect.colliderect(point.rect):
                points.remove(point)
                player.point_counter += 1
                break

class Wall:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, WALL_SIZE, WALL_SIZE)

        self.color = WALL_COLOR

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, 0)
        screen.blit(BRICK_TEXTURE, self.rect)

class Point:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, POINT_SIZE, POINT_SIZE)#Объект

        self.color = POINT_COLOR

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def destroy(self):
        points.remove(self)
        del self

class Map:
    def __init__(self):
        self.map = []
        self.enemys_max_count = 10
        self.map_size = 10
    
    def draw(self):#Занесение данных(игрок, стены, враги и тд) в массивы
        global walls, points, enemys, player
        start_x = (pygame.display.get_window_size()[0]/2)-((self.map_size*WALL_SIZE)/2)#Значение, которое не будет изменяться(только при масштабировании окна), для размещения игрового поля по середине экрана
        start_y = (pygame.display.get_window_size()[1]/2)-((self.map_size*WALL_SIZE)/2)#((self.map_size*WALL_SIZE+self.map_size)/2)
        
        x = start_x
        y = start_y
        generated = 0#счетчик, необходим для переноса на следующую строку отрисовки игровых элементов
        
        for i in self.map:

            if generated == self.map_size:#если сгенерированное количество равняется выбранному размеру карты, переносим отрисовку на следующую строку
                y += WALL_SIZE#перенос на следующую строку
                generated = 0#обнуляем
                x = start_x#обнуляем

            if i == 2:#Если 2, то добавляем стену
                walls.append(Wall(x, y))
            elif i == 1:#1 - очки
                points.append(Point(x+POINT_SIZE/2, y+POINT_SIZE/2))
            elif i == 3:#3 - враг
                enemys.append(Enemy(x, y))
            elif i == 4:#4 - игрок
                player.rect.x = 0
                player.rect.y = 0
                player.x = x
                player.y = y

            x += WALL_SIZE
            generated += 1
    
    #!!!!!
    #0 - пустота
    #1 - очки
    #2 - стена
    #3 - враг
    #4 - игрок
    
    def generator(self):
        generated_x = 0#счетчик, необходим для отслеживания сколько элементов отрисовалось и на какой строке. ЭТО НЕ КООРДИНАТЫ
        generated_y = 0

        player_placed = False#Определил ли генератор, местоположение игрока на карте
        enemys_count = 0#Счетчик, необходим для проверки сколько врагов на карте генератор уже создал
        
        for i in range(0, self.map_size**2):#возводим размер карты в степень, для добавления каждого блока
            
            if generated_x == 0 or generated_x == self.map_size-1 or generated_y == 0 or generated_y == self.map_size-1:#Создание рамки(границы) карты
                self.map.append(2)
                generated_x += 1

            else:#Заполнение внутри карты, стены, очки и тд
                generated_x += 1
                
                if self.map[len(self.map)-generated_y*2] == 0 or self.map[len(self.map)-1] == 0 or self.map[len(self.map)-generated_y*2] == 3 or self.map[len(self.map)-1] == 3:#Проверка, если есть пустота\враг сверху или слева, то генерируем что-либо
                    if generated_y == self.map_size-2 and generated_x >= self.map_size/3 and player_placed == False:#проверка, можно ли создать игрока на карте
                        self.map.append(4)#Добавление игрока на карту
                        player_placed = True
                        continue

                    elif generated_y < self.map_size/3 and enemys_count < self.enemys_max_count and self.map[len(self.map)-1] != 3:
                        self.map.append(random.randint(1, 3))
                        enemys_count += 1
                        continue

                    self.map.append(random.randint(0, 2))
                else:#Иначе добавляем пустоту
                    self.map.append(0)

            if generated_x >= self.map_size:#Если строка сформирована, то
                generated_x = 0             #сбрасываем счетчик
                generated_y += 1            #и переносим на следующую строку
        
class Bullet:
    def __init__(self, x, y):
        self.Enemy_bullet = None#Пуля игрока или врага
        self.color = BULLET_COLOR

        self.speed = 1
        self.speed_x = 0
        self.speed_y = 0

        self.width = BULLET_SIZE
        self.height = BULLET_SIZE

        self.rect = pygame.Rect(x, y, self.width, self.height)#Объект

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, 0)

    def move(self):
        self.rect.x += self.speed*self.speed_x
        self.rect.y += self.speed*self.speed_y

    def destroy(self):
        bullets.remove(self)
        del self.rect
        del self

    def collision(self, collisions):
        global player

        if type(collisions) == Player and collisions.rect:
            if self.rect.colliderect(collisions.rect) and self.Enemy_bullet == True:
                collisions.rect.x = -100
                collisions.rect.y = -100
                # collisions.destroy()
                self.destroy()  
                collisions.Live = False
                return True

        else:
            for i in collisions:
                if self.rect.colliderect(i.rect):
                    if type(i) == Wall:#Если любая пуля соприкоснулась со стеной
                        self.destroy()
                        
                        return True
                    
                    elif type(i) == Enemy and self.Enemy_bullet == False:#Если пуля игрока соприкоснулась с врагом
                        i.destroy()
                        self.destroy()

                        player.enemy_killed_counter += 1

                        if len(collisions) == 0:
                            player.win = True

                        return True

                    elif type(i) == Bullet and self != i:#Если пуля соприкоснулась с другой пулей, уничтожаем их двоих
                        i.destroy()
                        self.destroy()

                        return True

class Enemy(Entity):
    def __init__(self, x, y):
        super().__init__()
        
        self.speed = 0.3

        self.animation_frame = 1#Необходимо, чтобы враг проходил како-то расстояние при каждом кадре
        self.max_animation_frame = 200#Сколько кадров будет идти враг в одном напралении

        self.rect = pygame.Rect(x, y, self.width, self.height)#Объект

        self.side = 2

    def draw(self):
        global enemy_texture, rotated_enemy_texture

        pygame.draw.rect(screen, self.color, self.rect, 0)
        screen.blit(rotated_enemy_texture, self.rect)

    def destroy(self):
        enemys.remove(self)
        del self.rect
        del self
    #Стороны передвижения/side
    #1 - вверх
    #2 - вправо
    #3 - вниз
    #4 - лево
    def moving_and_collision(self, collisions):
        global enemy_texture, rotated_enemy_texture
        
        if self.animation_frame == 1:
            self.side = random.randint(1, 4)
            self.animation_frame += 1
        
        elif self.animation_frame == self.max_animation_frame:
            self.animation_frame = 1
            
        else:
            self.animation_frame += 1

        if self.side == 1:
            rotated_enemy_texture = pygame.transform.rotate(enemy_texture, 0)
            self.y -= self.speed
            
        elif self.side == 3:
            rotated_enemy_texture = pygame.transform.rotate(enemy_texture, 180)
            self.y += self.speed
            
        elif self.side == 2:
            rotated_enemy_texture = pygame.transform.rotate(enemy_texture, -90)
            self.x += self.speed
            
        elif self.side == 4:
            rotated_enemy_texture = pygame.transform.rotate(enemy_texture, 90)
            self.x -= self.speed
            

        if self.x >= self.max_speed or self.x <= -self.max_speed:
            self.rect.x += self.x#Передвигаем игрока по x

        for wall in collisions:#перебираем массив с коллизией
            if self.rect.colliderect(wall.rect):#Если враг соприкоснулся со стеной
                self.animation_frame = 1
                if self.x > 0:
                    self.rect.right = wall.rect.left#Коллизия
                    break

                elif self.x < 0:
                    self.rect.left = wall.rect.right#Коллизия
                    break

        if self.x >= self.max_speed or self.x <= -self.max_speed:#Если x > максимальной скорости или меньше минусовой макс скорости, то
            self.x = 0#Сбрасываем скорость по x
        
        if self.y >= self.max_speed or self.y <= -self.max_speed:
            self.rect.y += self.y

        for wall in collisions:#перебираем массив с стенами
            if self.rect.colliderect(wall.rect):
                self.animation_frame = 1
                if self.y > 0:
                    self.rect.bottom = wall.rect.top#Коллизия
                    break

                elif self.y < 0:
                    self.rect.top = wall.rect.bottom#Коллизия
                    break

        if self.y >= self.max_speed or self.y <= -self.max_speed:
            self.y = 0#Сбрасываем скорость по y

    def pull_bullet(self):
        if random.randint(0, 100) >= 50 and self.can_bullet:
            bullet = Bullet(self.rect.x+BULLET_SIZE/2, self.rect.y+BULLET_SIZE/2)
            bullet.Enemy_bullet = True

            if self.side == 2:
                bullet.speed_x = 1
            elif self.side == 4:
                bullet.speed_x = -1
            elif self.side == 1:
                bullet.speed_y = -1
            elif self.side == 3:
                bullet.speed_y = 1

            bullets.append(bullet)
            self.can_bullet = False
walls = []
points = []
enemys = []
bullets = []

player = Player()#Создаем игрока и задаём настройки
