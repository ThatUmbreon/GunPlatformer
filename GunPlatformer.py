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
    playerx = radius*cos(addangle+acos((point[0]-center[0])/(distance(center,point))))
    playery = radius*sin(addangle+asin((point[1]-center[1])/(distance(center,point))))
    return playerx, playery

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
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.SCALED|pygame.RESIZABLE|pygame.FULLSCREEN)
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

#creator mode variables
creator_mode = True
custom_rects = []
variable67 = (0,0)
variable69 = (0,0)

 # for starters we should just store platforms as rects, and then later we can add types and stuff to them by making them a list of [type, rect] or something
platforms = [pygame.Rect(0,HEIGHT-100,WIDTH,100),pygame.Rect(WIDTH-200,HEIGHT-200,200,100),pygame.Rect(WIDTH//2-100,HEIGHT-300,200,30)]

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
    
    # KILL or fullscreen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running=False
            if event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
    
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

    # moves bullets according to their velocity, and removes them if they go offscreen
    for bullet in bullet_list:
        bullet[0][0] += bullet[1][0] * dt
        bullet[0][1] += bullet[1][1] * dt
        if bullet[0][0] < 0 or bullet[0][0] > WIDTH or bullet[0][1] < 0 or bullet[0][1] > HEIGHT or any(pygame.Rect(bullet[0][0]-5, bullet[0][1]-5, 10, 10).colliderect(platform) for platform in platforms):
            bullet_list.remove(bullet)

    # applies drag/friction
    player_xvel *= DRAG**dt

    # applies gravity
    player_yvel += GRAVITY*dt

    # caps fall speed to terminal velocity
    player_yvel = min(player_yvel, TERMINAL_VELOCITY)

    # walking figured we would be able to walk, but only jump with recoil
    walk = ((keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])) * PLAYER_SPEED

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
            #could you please provide docs on how to make ts work with new platforms, like how do i add a platform that has collision.
            if pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform):
                horizontal_blocked = True
            if pygame.Rect(playerx-PLAYER_WIDTH//2,playery+(player_yvel*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform):
                vertical_blocked = True
            if pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery+((player_yvel+GRAVITY)*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform) and not (pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform) or pygame.Rect(playerx-PLAYER_WIDTH//2,playery+(player_yvel*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform)):
                horizontal_blocked = True
                vertical_blocked = True
        if horizontal_blocked:
            player_xvel = 0
        else:
            playerx += (player_xvel+walk)*dt/4
        if vertical_blocked:
            if player_yvel > 0:
                bullets = magazine_size
            player_yvel = 0
        else:
            playery += player_yvel*dt/4
        
    #background
    screen.fill((67,41,69))

    #draws FLOOR!! (we dont have platforms or anything so its just a floor)
    for platform in platforms:
        pygame.draw.rect(screen, "brown", platform)

        # levil maker! doesnt work btw, idk y
    if creator_mode:
        if variable67 != (0,0):
            pygame.draw.circle(screen, "red", variable67, 10)
        if variable69 != (0,0):
            pygame.draw.circle(screen, "purple", variable69, 10)
        if keys[pygame.K_q]:
                variable67 = mouse_pos
        elif keys[pygame.K_e]:
            variable69 = (mouse_pos[0], mouse_pos[1])
        elif keys[pygame.K_r] and variable67 != (0,0) and variable69 != (0,0):
            custom_rects.append(pygame.Rect(variable67, variable69))
        elif keys[pygame.K_p]:
            variable67 = (0,0)
            variable69 = (0,0)
        for objects in custom_rects:
            pygame.draw.rect(screen, "blue", (variable67[0],variable67[1],variable69[0]-variable67[0],variable69[1]-variable67[1]))
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
