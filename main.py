# -*- coding: utf-8 -*-
"""
Created on Sun Mar 23 09:20:00 2025

@author: Marth
"""

## import modules
import asyncio
import os
import pygame
import numpy as np

## pygame setup
pygame.init()
pygame.display.set_caption('CHEESE BLASTER')
xwidth = 1000
ywidth = 600
screen = pygame.display.set_mode((xwidth, ywidth))
clock = pygame.time.Clock()
pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT])
#pygame.key.set_repeat(5, 5)
bdir = os.path.dirname(os.path.abspath(__file__))

## load images
def load_img(filename):
    pathfile = os.path.join(bdir, 'img', filename)
    return pygame.image.load(pathfile)
# game texts
logo = load_img('cb_logo_resize.png')
l1_header = load_img('level1_graphic.png')
l2_header = load_img('level2_graphic.png')
l3_header = load_img('level3_graphic.png')
win_graphic = load_img('win_graphic.png')
lose_graphic_1 = load_img('ohnoos_cheese.png')
lose_graphic_2 = load_img('ohnooos_tomato_soup.png')
lose_graphic_3 = load_img('ohnooos_ice_cream.png')
# lose_graphic_4 = load_img('ohnooos_level4.png')
# game objects
gun = load_img('nerfgun.png')
bread = load_img('bread_nobg_resize.PNG')
cheese = load_img('cheese_nobg_resize.PNG')
bowl = load_img('bowl_no_bg_tilt2_resize.PNG')
tomato = load_img('tomato_nobg_resize.PNG')
scoop = load_img('scoop_resize.png')
cone = load_img('cone_resize.png')
# score icons
toastie = load_img('toastie.png')
soup = load_img('soup.png')
iccone = load_img('iccone.png')
rainbow = load_img('rainbow_nobg.PNG')

## define function to initialize falling objects
def initialize_falling_var(f_img):
    return ({'img': f_img,
             'speed': np.random.randint(3, 12),
             'x': np.random.randint(100, xwidth - 20),
             'y': np.random.randint(-20000, -20)})

## define function to blit level change graphic
def show_level_graphic(screen, level_graphic):
    h_rect = level_graphic.get_rect()
    h_rect.center = (xwidth/2, ywidth/2)
    screen.blit(level_graphic, h_rect)

## define functions to celebrate victory
# initialize confetti
def initialize_confetti():
    palette = [(255, 0, 0), (255, 102, 0), (0, 204, 0),
               (204, 0, 153), (0, 0, 255), (255, 0, 102), (255, 255, 0)]
    confetti = {'x': np.random.randint(10, 990, 100),
                'y': np.random.randint(-1000, -50, 100),
                'c': [palette[i] for i in np.random.randint(0, len(palette), 100)]}
    return confetti

# display confetti and win graphics
def win_screen(screen, confetti, win_even_row):
    ## draw tasty foods
    y_disp = list(range(10, ywidth - 10, 50))
    f_disp = y_disp[0:len(y_disp):2] if win_even_row else y_disp[1:len(y_disp):2]
    r_disp = y_disp[1:len(y_disp):2] if win_even_row else y_disp[0:len(y_disp):2]
    for x in range(10, xwidth - 10, 150):
        for y in f_disp:
            screen.blit(toastie, (x, y))
            screen.blit(soup, (x + 50, y))
            screen.blit(iccone, (x + 100, y - 15))
        for y in r_disp:
            screen.blit(rainbow, (x, y))

    ## draw and iterate confetti
    for n in range(0, len(confetti['x'])):
        x = confetti['x'][n]
        y = confetti['y'][n]
        poly = [(x, y), (x, y + 8), (x + 3, y + 6), (x + 3, y - 2), (x, y)]
        pygame.draw.polygon(screen, confetti['c'][n], poly)
        pygame.draw.polygon(screen, 'black', poly, width=1)
        if confetti['y'][n] < ywidth:
            confetti['y'][n] = confetti['y'][n] + 4
        else:
            confetti['y'][n] = np.random.randint(-1000, -50)

## define main game function
async def main():
    ## initialize status variables
    playing = True
    fired = False
    init = False
    show_graphic = True
    win_status = False

    ## set goals, initialize score
    level = 1
    level_goal = 10
    score = 0

    ## define the ammo and falling objects for each level
    level_imgs = {'level1': [l1_header, cheese, bread, toastie, lose_graphic_1],
                  'level2': [l2_header, tomato, bowl, soup, lose_graphic_2],
                  'level3': [l3_header, scoop, cone, iccone, lose_graphic_3],
                  'level4': [l3_header, scoop, cone, iccone, lose_graphic_3]}
    level_graphic = level_imgs['level' + str(level)][0]
    
    ## initialize player
    gun_pos = [25, 575]
    ammo_pos = gun_pos
    ammo_num = 15
    fired_timer = 0
    collision_vars = []

    ## initialize vars for win screen
    win_flash = 20
    win_even_row = True
    confetti = initialize_confetti()

    while playing:

        ## fill screen background color
        screen.fill('lightskyblue')

        ## display win screen
        if win_status:
            win_screen(screen, confetti, win_even_row)
            if win_flash > 0:
                win_flash -= 1
            else:
                win_flash = 20
                win_even_row = not win_even_row

        ## draw logo
        screen.blit(logo, (200, 20))

        ## if level has not been initialized, define objects and their stats
        if not init:
            # set the identity of the falling object by level
            h_img = level_imgs['level' + str(level)][0]
            a_img = level_imgs['level' + str(level)][1]
            f_img = level_imgs['level' + str(level)][2]
            c_img = level_imgs['level' + str(level)][3]
            l_img = level_imgs['level' + str(level)][4]

            # reset ammo number and score
            score = 0
            ammo_num = 15

            # initialize falling object stats
            falling_vars = []
            for n in range(0, 100):
                falling_vars.append(initialize_falling_var(f_img))

            # report initialization
            init = True

        # at level start, display directions
        if show_graphic:
            show_level_graphic(screen, level_graphic)

        # show active game elements
        else:
            ## draw score
            header_font = pygame.font.SysFont('arial', 16, bold=True, italic=False)
            screen.blit(header_font.render('LEVEL:', True, 'black'), (820, 10))
            screen.blit(header_font.render(str(level), True, 'black'), (960, 10))
            screen.blit(header_font.render('LEVEL GOAL:', True, 'black'), (820, 30))
            screen.blit(header_font.render(str(10), True, 'black'), (960, 30))
            screen.blit(header_font.render('LEVEL SCORE:', True, 'black'), (820, 50))
            screen.blit(header_font.render(str(score), True, 'black'), (960, 50))
            screen.blit(header_font.render('AMMO:', True, 'black'), (820, 70))
            screen.blit(header_font.render(str(ammo_num), True, 'black'), (960, 70))
            
            ## draw falling objects and update position 
            fobjs = []
            for num, fv in enumerate(falling_vars):
                fobjs.append(screen.blit(fv['img'], (fv['x'], fv['y'])))
                fv['y'] = fv['y'] + fv['speed']

            ## draw ammunition if fired
            if fired:
                aobj = screen.blit(a_img, ammo_pos)
                ammo_pos[0] = ammo_pos[0] + 20
                if ammo_pos[0] > xwidth:
                    fired = False

            ## draw gun 
            screen.blit(gun, gun_pos)

            ## check for cheese and bread collisions
            if fired:
                for num, obj in enumerate(fobjs):
                    if aobj.colliderect(obj):
                        # if collision, reinitialize fobj and update score
                        falling_vars[num] = initialize_falling_var(f_img)
                        score += 1
                        collision_vars.append({'img': c_img,
                                               'timer': 20,
                                               'pos': [ammo_pos[0], ammo_pos[1]]})
                
            # if ammo is depleted,
            if ammo_num == 0 and ammo_pos[0] > xwidth:
                # reset play variables
                fired = False
                init = False
                show_graphic = True
                collision_vars = []
                # if level goal has been met, go to next level
                if score >= level_goal:
                    level += 1
                    level_graphic = level_imgs['level' + str(level)][0]
                    if level == 4:
                        level_graphic = win_graphic
                        init = True
                        win_status = True
                # if level goal has not been met, reinitialize level
                elif score < level_goal:
                    level_graphic = l_img

            ## show collision/score increase 
            col_font = pygame.font.SysFont('arial', 30, bold=True, italic=False)
            for cv in collision_vars:
                if cv['timer'] > 0:
                    cv['pos'][1] = cv['pos'][1] - 5
                    screen.blit(col_font.render('+', True, 'black'),
                                (cv['pos'][0] - 12, cv['pos'][1] + 8))
                    screen.blit(cv['img'], cv['pos'])
                    cv['timer'] = cv['timer'] - 1

            ## update fired timer
            if fired_timer > 0:
                fired_timer -= 1

        ## update display
        pygame.display.update()
        
        ## get key presses
        keys = pygame.key.get_pressed()

        ## if W, move gun up
        if keys[pygame.K_w]:
            gun_pos[1] = gun_pos[1] - 5

        ## if S, move gun down
        if keys[pygame.K_s]:
            gun_pos[1] = gun_pos[1] + 5

        ## if enter, fire cheese
        if keys[pygame.K_RETURN]:
            if fired_timer == 0 and ammo_num > 0:
                fired = True
                # set timer to avoid game registering multiple key presses
                fired_timer = 15
                # start ammo at gun_pos
                ammo_pos = [gun_pos[0] + 30, gun_pos[1]]
                # reduce ammo supply number by 1
                ammo_num -= 1

        ## if space, start level or restart after lose
        if keys[pygame.K_SPACE]:
            show_graphic = False

        ## limit FPS to 30
        clock.tick(30)
        await asyncio.sleep(0)

## play game
asyncio.run(main())