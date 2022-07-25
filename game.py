import pygame
import cv2 as cv
import sys
import random
import time
from PoseTracker import PoseTracker
import numpy as np

def update_ball_position():
    global ball_speed_x, ball_speed_y, hits
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1

    if ball.left <= 0:
        ball_speed_x *= -1 

    if ball.colliderect(player):
        hits += 1
        ball_speed_x *= -1
        
    if ball.colliderect(opponent):
        ball_speed_x *= -1


def update_player_position(net_distance):

    MAX_PUSHUP_HEIGHT = 0.7
    MIN_PUSHUP_HEIGHT = 0.05
    PUSHUP_RANGE = MAX_PUSHUP_HEIGHT - MIN_PUSHUP_HEIGHT

    player.y = screen_height * ((PUSHUP_RANGE-net_distance)/PUSHUP_RANGE)

    if player.top <= 0:
        player.top = 0
    if player.bottom >= screen_height:
        player.bottom = screen_height

def update_opponent_position():

    if ball_speed_y > 0:
        opponent.y += opponent_speed

    if ball_speed_y < 0:
        opponent.y -= opponent_speed

def game_restart():
    global ball_speed_x, ball_speed_y
    ball.center = (screen_width/2, screen_height/2)
    ball_speed_x *= random.choice((1,-1))
    ball_speed_y *= random.choice((1,-1))

    player.x = screen_width-10
    player.y = screen_height/2 - 70

    opponent.x = 0
    opponent.y = screen_height/2 - 70
    time.sleep(1)

def has_lost():
    global points
    if ball.left <= 0 and not (ball.bottom >= opponent.top and ball.top <= opponent.bottom):
        print('You won!')
        points[1] += 1
        game_restart()

    if ball.right >= screen_width and not (ball.bottom >= player.top and ball.top <= player.bottom):
        print('Opponent won!')
        points[0] += 1
        game_restart()


pygame.init()
clock = pygame.time.Clock()

screen_width = 1080
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Pong')

background_color = pygame.Color('grey12')
light_grey = (200,200,200)

font = pygame.font.Font('freesansbold.ttf', 32)
hits_text = font.render('Hits: 0', True, light_grey, background_color)
points_text = font.render('Points: 0|0', True, light_grey, background_color)
hits_rect = hits_text.get_rect()
points_rect = points_text.get_rect()
hits_rect.center = (screen_width/2 - 140, 30)
points_rect.center = (screen_width/2 + 140, 30)


ball = pygame.Rect(screen_width/2 - 15, screen_height/2-15, 30, 30)
player = pygame.Rect(screen_width-10, screen_height/2 - 70, 10, 140)
opponent = pygame.Rect(0, screen_height/2 - 70, 10, 140)

ball_speed_x = 15 * random.choice((1,-1))
ball_speed_y = 15 * random.choice((1,-1))

points = [0,0]
hits = 0
opponent_speed = 13

detector = PoseTracker()

while True:

    ## CV LOOP
    previous_time = time.time()
    detector.detect()
    detector.display()
    left_distance = detector.y_distance(0,16)
    right_distance = detector.y_distance(0,15)

    net_distance =(left_distance + right_distance) / 2
    
    current_time = time.time()
    fps = 1/(current_time-previous_time)
    print(f'FPS: {fps}')
    cv.waitKey(1)




    ## GAME LOOP
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


    has_lost()
    update_player_position(net_distance)
    update_opponent_position()
    update_ball_position()

    hits_text = font.render(f'Hits: {hits}', True, light_grey, background_color)
    points_text = font.render(f'Points: {points[0]}|{points[1]}', True, light_grey, background_color)
    hits_rect = hits_text.get_rect()
    points_rect = points_text.get_rect()
    hits_rect.center = (screen_width/2 - 140, 30)
    points_rect.center = (screen_width/2 + 140, 30)
 
    screen.fill(background_color)
    screen.blit(hits_text, hits_rect)
    screen.blit(points_text, points_rect)
    pygame.draw.rect(screen, light_grey, player)
    pygame.draw.rect(screen, light_grey, opponent)
    pygame.draw.ellipse(screen, light_grey, ball)
    pygame.draw.aaline(screen, light_grey, (screen_width/2, 0), (screen_width/2, screen_height))


    pygame.display.flip()