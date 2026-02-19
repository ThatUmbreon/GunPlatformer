# external libraries
import pygame
from math import cos, sin, acos, asin, pi

def distance(p1, p2):
    '''pythagoras'''
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5

def thatcircleshit(radius, center, point, addangle=0):
    '''what even is this shit.
    it calculates the point on the circumference of a circle with a given radius and center, that is in the direction of the point argument, with an optional angle added to it.
    like seriously what do you even call that'''
    x = radius*cos(addangle+acos((point[0]-center[0])/(distance(center,point))))
    y = radius*sin(addangle+asin((point[1]-center[1])/(distance(center,point))))
    return x, y

def write(msg, pos, size, color):
    '''draw text on the screen, aligned topleft'''
    sFont = pygame.font.SysFont("Arial", size)
    sSurf = sFont.render(msg, True, color)
    sRect = sSurf.get_rect()
    sRect.topleft = pos
    screen.blit(sSurf, sRect)

# initialize pygame (thats important)
pygame.init()

# screen
WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.SCALED|pygame.RESIZABLE)
pygame.display.set_caption("GunPlatformer")

# player variables
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 20
PLAYER_SPEED = 5
playerx = WIDTH//2
playery = HEIGHT//2
player_xvel = 0
player_yvel = 0

# physics variables
DRAG = 0.9
GRAVITY = 0.75
TERMINAL_VELOCITY = 15

# gun variables
BULLET_SPEED = 10
RECOIL = 20
bullet_list = []
shoot = False
hold = False
bullets = 6
magazine_size= 6

platforms = [pygame.Rect(0,HEIGHT-100,WIDTH,100)] # for starters we should just store platforms as rects, and then later we can add types and stuff to them by making them a list of [type, rect] or something

# clock for delta time
clock = pygame.time.Clock()
# run the game
running = True
# max fps
fpsCap = 60
# game loop
while running:
    # delta time :)
    dt = clock.tick(fpsCap)/1000*(fpsCap if fpsCap > 0 else 1)
    
    # KILL
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running=False
    
    # get inputs
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()
    
    # stops player from shooting constantly
    shoot = mouse_click[0] and not hold
    hold = mouse_click[0]
    
    # shooting, applies recoil and reduces bullets by 1
    if shoot and bullets > 0:
        player_xvel, player_yvel = thatcircleshit(RECOIL, (playerx,playery), mouse_pos, pi)
        bullet_list.append([[playerx,playery],thatcircleshit(BULLET_SPEED, (playerx,playery), mouse_pos)])
        bullets -= 1
        
    # moves player according to velocity
    playerx += player_xvel * dt
    playery += player_yvel * dt

    # moves bullets according to their velocity, and removes them if they go offscreen
    for bullet in bullet_list:
        bullet[0][0] += bullet[1][0] * dt
        bullet[0][1] += bullet[1][1] * dt
        if bullet[0][0] < 0 or bullet[0][0] > WIDTH or bullet[0][1] < 0 or bullet[0][1] > HEIGHT:
            bullet_list.remove(bullet)

    # applies drag/friction
    player_xvel *= DRAG**dt

    # applies gravity
    player_yvel += GRAVITY*dt

    # caps fall speed to terminal velocity
    player_yvel = min(player_yvel, TERMINAL_VELOCITY)

    # walking figured we would be able to walk, but only jump with recoil
    playerx += ((keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])) * PLAYER_SPEED * dt

    # player may not go offscreen
    if PLAYER_WIDTH//2 > playerx or playerx > WIDTH-PLAYER_WIDTH//2:
        playerx = max(PLAYER_WIDTH//2, min(WIDTH-PLAYER_WIDTH//2, playerx))
        player_xvel = 0
    if PLAYER_HEIGHT//2 > playery or playery > HEIGHT-PLAYER_HEIGHT//2:
        playery = max(PLAYER_HEIGHT//2, min(HEIGHT-PLAYER_HEIGHT//2, playery))
        player_yvel = 0

    # untranslated collision detection and response
    # i use quartersteps (check for collisions 4 times per frame) to make it more accurate and also because thats what super mario 64 does
    # also im checking for horizontal and vertical collisions separately, so that you can slide along walls and not get stuck on corners
    # that corner bug had me stumped for a while for platformergame, so im taking no chances
    for i in range(4):
        horizontal_blocked = False
        vertical_blocked = False
        for platform in platforms:
            if pygame.Rect((x+(hVel/4)+10)%820-20,y-10,20,20).colliderect(platform[1]):
                horizontal_blocked = True
                wTyp = platform[0]
            if pygame.Rect(x-10,y+(vVel/4)-10,20,20).colliderect(platform[1]):
                vertical_blocked = True
                fTyp = platform[0]
                if fTyp == 8:
                    wSfc = wArr[cLvl].index(platform)
            if pygame.Rect((x+(hVel/4)+10)%820-20,y+((vVel-gAcc)/4)-10,20,20).colliderect(platform[1]) and not (pygame.Rect((x+(hVel/4)+10)%820-20,y-10,20,20).colliderect(platform[1]) or pygame.Rect(x-10,y+(vVel/4)-10,20,20).colliderect(platform[1])):
                horizontal_blocked = True
                vertical_blocked = True
        if horizontal_blocked:
            if wTyp == 6:
                hVel *= -1.25
                vVel -= 5
                fDir *= -1
            else:
                hVel = 0
        if vertical_blocked:
            if vVel > 0:
                jmps = 0
                cTme = 0
                wJmp = False
            if fTyp == 6 and (vVel > 1 or vVel < 0):
                vVel *= -0.95
            else:
                vVel = 0
            if wTyp == 6:
                hVel *= -1.25
                vVel -= 5
                fDir *= -1
            else:
                hVel = 0
        else:
            if hVel != 0:
                wTyp = -1
            x = (x+(hVel/4)+10)%820-10
            sCdn += 1
            if sCdn >= 20:
                if fTyp == 5 and hVel != 0:
                    aSFX.play()
                elif hAcc != 0:
                    sSFX.play()
                sCdn = 0
        if vBlk:
            if vVel > 0:
                jmps = 0
                cTme = 0
                wJmp = False
            if fTyp == 6 and (vVel > 1 or vVel < 0):
                vVel *= -0.95
            else:
                vVel = 0
            hVel *= pSfc[fTyp]
        else:
            if vVel != 0 and cTme >= jPrd:
                fTyp = -1
            y = y+(vVel/4)
            if wTyp == 5 and hVel == 0 and sCdn >= 19:
                aSFX.play()
            if cJmp == 1:
                cTme += 1
        
    #background
    screen.fill((67,41,69))

    #draws FLOOR!! (we dont have platforms or anything so its just a floor)
    pygame.draw.rect(screen, "brown", (0,HEIGHT-100+PLAYER_HEIGHT/2, WIDTH, HEIGHT))

    #draws bullets
    for bullet in bullet_list:
        pygame.draw.circle(screen, "yellow", bullet[0], 5)

    #draws player
    pygame.draw.rect(screen,(67,255,255),(playerx-PLAYER_WIDTH//2,playery-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT))
    
    #draws bullet count on screen
    write(f"Bullets: {bullets}/{magazine_size}",(0,0),20,(255,255,255))

    #you know what ts is ok
    pygame.display.flip()

# close the game when we close it
pygame.quit()