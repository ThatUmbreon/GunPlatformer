# external libraries
import pygame
from math import cos, sin, acos, asin, pi
import random



pygame.init()
pygame.mixer.init()

#objects
platforms = []
killboxes = []
respawn_point = (100,100)



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

def calc_rects(point1, point2):
    left = min(point1[0], point2[0])
    top = min(point1[1], point2[1])
    rect_width = abs(point1[0] - point2[0])
    rect_height = abs(point1[1] - point2[1])
    new_platform = pygame.Rect(left, top, rect_width, rect_height)
    return new_platform

def reset():
    global playerx, playery, player_xvel, player_yvel, change_level, bullets, magazine_size
    playerx = respawn_point[0]
    playery = respawn_point[1]
    player_xvel = 0
    player_yvel = 0
    change_level = False
    bullets = magazine_size

def die():
    global death_time, dying
    dying = True
    death_time = 100

def won():
    global level, change_level, won
    level += 1
    change_level = True

#I have tested this, this works
def fileWrite(File : str, boxes : list[pygame.Rect], killBoxes : list[pygame.Rect], spawnPoint : tuple[int,int], winZone : tuple[int,int,int,int]) -> None:
    with open(File, 'w') as file:
        for i in boxes:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("kill\n")
        for i in killBoxes:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("spawn\n")
        file.write(f"{spawnPoint}\n")
        file.write("win\n")
        

def fileRead(File : str) -> tuple[list[pygame.Rect],list[pygame.Rect],tuple[int,int]]:
    mode = 'boxes'
    boxes : list[pygame.Rect] = []
    killboxes : list[pygame.Rect] = []
    spawnpoint : tuple[int,int]
    winzone : tuple[int,int,int,int]
    with open(File, 'r') as file:
        for line in file:
            try:
                line = line[:-1]
                if line=="kill":
                    mode = 'kill'
                elif line =="spawn":
                    mode = 'spawn'
                elif line =="win":
                    mode = 'win'
                elif mode=='boxes':
                    boxes.append(eval(line))
                elif mode=='kill':
                    killboxes.append(eval(line))
                elif mode=='spawn':
                    spawnpoint=eval(line)
                elif mode=='win':
                    winzone=eval(line)
            except:
                pass
    return boxes,killboxes,spawnpoint,winzone
#this works, I tested it

# screen
WIDTH = 1200
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.SCALED|pygame.RESIZABLE|pygame.FULLSCREEN|pygame.SRCALPHA)
pygame.display.set_caption("GunPlatformer")

#world varbs
WLW=10000
WLH=1000
world_surf = pygame.Surface((WLW, WLH))

# player variables
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 20
PLAYER_SPEED = 5
playerx = respawn_point[0]
playery = respawn_point[1]
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
undo = False
redo = False
removed_platform = []
deleting = False

#levels and shit
change_level = True
win_zone = (WIDTH-100, 0, 100, HEIGHT)

level = int(1)
level0 = []
level1 = [pygame.Rect(96, 498, 577, 107),
pygame.Rect(770, 494, 356, 118),
pygame.Rect(1327, 492, 373, 125),
pygame.Rect(1199, -39, 54, 540),]

level2 = [pygame.Rect(81, 529, 492, 65),
pygame.Rect(1136, 531, 345, 109),
pygame.Rect(2053, 506, 161, 89),
pygame.Rect(2381, -77, 38, 949),
pygame.Rect(2590, 516, 284, 72),
pygame.Rect(2961, 121, 54, 903),
pygame.Rect(3314, 116, 42, 906),
pygame.Rect(3619, 118, 48, 949),
pygame.Rect(4023, -15, 47, 672),
pygame.Rect(3873, 635, 365, 52),
pygame.Rect(4427, 191, 70, 813),
pygame.Rect(4464, 940, 120, 51),
pygame.Rect(4639, -132, 64, 991),
pygame.Rect(4656, 748, 553, 108),
pygame.Rect(5332, 248, 60, 761),
pygame.Rect(4786, 509, 564, 85),
pygame.Rect(4680, 256, 581, 83),
pygame.Rect(4778, 85, 427, 78),
pygame.Rect(5182, 87, 216, 76),
pygame.Rect(5331, 136, 62, 116),
pygame.Rect(5629, -18, 34, 1111),]
level3 = [
pygame.Rect(67, 457, 331, 86),
pygame.Rect(463, -50, 214, 588),
pygame.Rect(468, 536, 33, 395),
pygame.Rect(427, 965, 83, 27),
pygame.Rect(601, 972, 81, 24),
pygame.Rect(505, 904, 94, 11),
pygame.Rect(547, 899, 18, 50),
pygame.Rect(647, 574, 33, 401),
pygame.Rect(591, 669, 58, 28),
pygame.Rect(498, 670, 59, 28),
pygame.Rect(978, 971, 29, 33),
pygame.Rect(671, 510, 581, 27),
pygame.Rect(734, 538, 151, 420),
pygame.Rect(779, 992, 72, 21),
pygame.Rect(877, 894, 395, 34),
pygame.Rect(913, 930, 10, 26),
pygame.Rect(956, 964, 9, 41),
pygame.Rect(1268, 896, 524, 15),
pygame.Rect(666, 585, 14, 388),
pygame.Rect(666, 607, 15, 366),
pygame.Rect(673, 579, 8, 391),
pygame.Rect(667, 575, 20, 399),
]
level4 = [pygame.Rect(476, 114, 40, 325),
pygame.Rect(714, 122, 33, 320),
pygame.Rect(290, 663, 91, 385),
pygame.Rect(1915, 834, 17, 45),
pygame.Rect(516, 725, 25, 48),]

level4_kill = [pygame.Rect(-15, 529, 1714, 39),
pygame.Rect(490, 108, 13, 11),
pygame.Rect(723, 119, 16, 9),
pygame.Rect(1925, -13, 64, 1105),
pygame.Rect(470, 564, 54, 342),]

#misc
camx = 0
camy = 0
death_time = 0
dying = False

#file loading
try:
    death_image = pygame.image.load('resources/blood-splatter.png').convert_alpha()
    death_sound = pygame.mixer.Sound('resources/hl2-stalker-scream.mp3')
except:
    print("failed to load file")
death_image = pygame.transform.scale(death_image, (WIDTH, HEIGHT))

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
    #background
    world_surf.fill((67, 41, 69))
    screen.fill((41,41,41))
    # KILL or fullscreen
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                running=False
            elif event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif event.key == pygame.K_z and keys[pygame.K_LCTRL] and platforms != [] and not keys[pygame.K_LSHIFT]:
                undo = True
            elif event.key == pygame.K_z and keys[pygame.K_LCTRL] and keys[pygame.K_LSHIFT] and platforms != []:
                redo = True
            elif event.key == pygame.K_r:
                reset()
            elif event.key == pygame.K_F9:
                creator_mode = not creator_mode
            elif event.key == pygame.K_F1:
                level -= 1
                change_level = True
            elif event.key == pygame.K_F2:
                level += 1
                change_level = True
    #levels shit
    if change_level:
        if level == 0:
            platforms = level0
            killboxes = []
        elif level == 1:
            platforms = level1
            respawn_point = (370.0, 419.0)
            win_zone = (1747, -11, 164, 1026)
            killboxes = []
        elif level == 2:
            platforms = level2
            respawn_point = (370.0, 419.0)
            win_zone = (5387, 843, 246, 157)
            killboxes = []
        elif level == 3:
            platforms = level3
            respawn_point = (236.0, 294.0)
            win_zone = (670, -89, 226, 606)
            killboxes = []
        elif level == 4:
            platforms = level4
            respawn_point = (206.0, 279.0)
            win_zone = (-7, 566, 309, 491)
            killboxes = level4_kill
        elif level > 0:
            level -=1
            print("no more levels")
        reset()
        print(level)

    # get inputs
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    camx = playerx - WIDTH / 2
    camy = playery - HEIGHT / 2

    # stops player from shooting constantly unless creaTIVE MODE
    shoot = (mouse_click[0] and (creator_mode or not hold)) or (keys[pygame.K_SPACE] and not space_hold)
    hold = mouse_click[0]
    if keys[pygame.K_SPACE] and not creator_mode:
        space_hold = True
    else:
        space_hold = False

    # shooting, applies recoil and reduces bullets by 1
    if shoot and bullets > 0:
        player_xvel, player_yvel = thatcircleshit(RECOIL, (playerx-camx,playery-camy), mouse_pos, pi)
        bullet_list.append([[playerx,playery],thatcircleshit(BULLET_SPEED, (playerx-camx,playery-camy), mouse_pos)])
        bullets -= 1

    # moves bullets according to their velocity, and removes them if they go offscreen
    for bullet in bullet_list:
        bullet[0][0] += bullet[1][0] * dt
        bullet[0][1] += bullet[1][1] * dt
        if bullet[0][0] < 0 or bullet[0][0] > WLW or bullet[0][1] < 0 or bullet[0][1] > WLH or any(pygame.Rect(bullet[0][0] - 5, bullet[0][1] - 5, 10, 10).colliderect(platform) for platform in platforms):
            bullet_list.remove(bullet)

    # applies drag/friction
    player_xvel *= DRAG**dt

    # applies gravity
    player_yvel += GRAVITY*dt

    # caps fall speed to terminal velocity
    player_yvel = min(player_yvel, TERMINAL_VELOCITY)

    # walking
    walk = ((keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])) * PLAYER_SPEED

    # untranslated collision detection and response
    # i use quartersteps (check for collisions 4 times per frame) to make it more accurate and also because thats what super mario 64 does
    # also im checking for horizontal and vertical collisions separately, so that you can slide along walls and not get stuck on corners
    # that corner bug had me stumped for a while for platformergame, so im taking no chances
    for i in range(4):
        horizontal_blocked = False
        vertical_blocked = False
        for platform in platforms:
            if pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform):
                horizontal_blocked = True
            if pygame.Rect(playerx-PLAYER_WIDTH//2,playery+(player_yvel*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform):
                vertical_blocked = True
            if pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery+((player_yvel+GRAVITY)*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform) and not (pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform) or pygame.Rect(playerx-PLAYER_WIDTH//2,playery+(player_yvel*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(platform)):
                horizontal_blocked = True
                vertical_blocked = True


        #actually moving
        if horizontal_blocked:
            player_xvel = 0
        elif not creator_mode:
            playerx += (player_xvel+walk)*dt/4
        if vertical_blocked:
            if player_yvel > 0:
                bullets = magazine_size
            player_yvel = 0
        elif not creator_mode:
            playery += player_yvel*dt/4

    #death collision
    if not creator_mode:
        for i in range(4):
            for boxes in killboxes:
                if pygame.Rect((playerx+((player_xvel+walk)*dt/4)-PLAYER_WIDTH//2),playery-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(boxes):
                    die()
                if pygame.Rect(playerx-PLAYER_WIDTH//2,playery+(player_yvel*dt/4)-PLAYER_HEIGHT//2,PLAYER_WIDTH,PLAYER_HEIGHT).colliderect(boxes):
                    die()
        if playerx<0:
            playerx = PLAYER_WIDTH//2+1
            player_xvel = 0
            die()
        elif playerx>WLW:
            playerx = WLW - PLAYER_WIDTH //2-1
            player_xvel = 0
            die()
        if playery<0:
            playery = PLAYER_HEIGHT//2+1
            player_yvel = 0
            die()
        elif playery>WLH:
            playery = WLH - PLAYER_HEIGHT //2-1
            player_yvel = 0
            reset()
            die()


    #draws platfroms and shit

    pygame.draw.rect(world_surf, "green", win_zone)
    for boxes in killboxes:
        pygame.draw.rect(world_surf, (100,20,20), boxes)
    for platform in platforms:
        pygame.draw.rect(world_surf, "brown", platform)
    pygame.draw.rect(world_surf, "yellow", (respawn_point[0] - 20, respawn_point[1] - 20, 40, 40))

        #creator mode!
    if creator_mode:
        if variable67 != (0,0):
            pygame.draw.circle(world_surf, "red", (variable67), 10)
        if variable69 != (0,0):
            pygame.draw.circle(world_surf, "purple", (variable69), 10)
        if keys[pygame.K_q]:
                variable67 = mouse_pos[0]+camx, mouse_pos[1]+camy
        elif keys[pygame.K_e]:
            variable69 = mouse_pos[0]+camx, mouse_pos[1]+camy
        elif keys[pygame.K_m]:
            respawn_point = mouse_pos[0]+camx, mouse_pos[1]+camy
        elif keys[pygame.K_BACKSPACE]:
            deleting = True
        if deleting:
            for platform in platforms:
                if platform.collidepoint((mouse_pos[0]+camx, mouse_pos[1]+camy)):
                    removed_platform.append(platforms.pop(platforms.index(platform)))
            for boxes in killboxes:
                if boxes.collidepoint((mouse_pos[0]+camx, mouse_pos[1]+camy)):
                    killboxes.remove(boxes)
            win_rect = pygame.Rect(win_zone[0], win_zone[1], win_zone[2], win_zone[3])
            if win_rect.collidepoint((mouse_pos[0]+camx, mouse_pos[1]+camy)):
                win_zone = (0,0,0,0)
            deleting = False
        if undo:
            removed_platform.append(platforms.pop())
            undo = False
        try:
            if redo and removed_platform:
                platforms.append(removed_platform[-1])
                removed_platform.remove(removed_platform[-1])
                redo = False
        except:
            pass
        if variable67 != (0,0) and variable69 != (0,0):
            new_platform = calc_rects(variable67, variable69)
            custom_rects.append(new_platform)
            if keys[pygame.K_z]:
                variable67 = (0,0)
                variable69 = (0,0)
                platforms.append(new_platform)
                custom_rects = []
            elif keys[pygame.K_l]:
                variable67 = (0,0)
                variable69 = (0,0)
                custom_rects = []
                win_zone = new_platform
            elif keys[pygame.K_g]:
                variable67 = (0,0)
                variable69 = (0,0)
                custom_rects = []
                killboxes.append(new_platform)

        bullets = 6000
        if keys[pygame.K_w]:
            playery -= 20
        if keys[pygame.K_s]:
            playery += 20
        if keys[pygame.K_a]:
            playerx -= 20
        if keys[pygame.K_d]:
            playerx += 20


        for objects in custom_rects:
            pygame.draw.rect(world_surf, "blue", new_platform)
    #draws bullets
    for bullet in bullet_list:
        pygame.draw.circle(world_surf, "yellow", bullet[0], 5)

    #moves cam
    camx=playerx - WIDTH//2
    camy=playery - HEIGHT//2

    #draws player
    player_rect = pygame.Rect(playerx - PLAYER_WIDTH // 2, playery - PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT)
    pygame.draw.rect(world_surf, (67, 255, 255), (playerx - PLAYER_WIDTH // 2, playery - PLAYER_HEIGHT // 2, PLAYER_WIDTH, PLAYER_HEIGHT))

    #checks for win
    win = pygame.Rect(player_rect).colliderect(win_zone)
    if win:
        won()


    #puts images onto screen with offset for map
    screen.blit(world_surf, (-camx, -camy))
    #draws bullet count on screen
    write(f"Bullets: {bullets}/{magazine_size}",(0,0),20,(255,255,255))

    if dying:
        screen.blit(death_image, (0, 0, death_image.get_width(), death_image.get_height()))
        death_sound.play()
        death_time -= 1
        pygame.display.flip()
        pygame.time.wait(death_time)
        dying = False
        reset()

    rando = random.randint(0,10000)
    if rando == 1:
        death_sound.play()
    #you know what ts is ok
    pygame.display.flip()
platformlist = [str(platform).replace("<rect(","pygame.Rect(").replace(")>","),") for platform in platforms[:]]
print("Platforms:")
for platform in platformlist:
    print(platform)
killboxlist = [str(boxes).replace("<rect(","pygame.Rect(").replace(")>","),") for boxes in killboxes[:]]
print("Killboxes:")
for boxes in killboxlist:
    print(boxes)

print("respawn point:")
print((respawn_point[0]//1, respawn_point[1]//1))
print("win_zone:")
win_zone = str(win_zone).replace("<rect(","(").replace(")>",")")
print(win_zone)
# close the game when we close it

pygame.quit()

