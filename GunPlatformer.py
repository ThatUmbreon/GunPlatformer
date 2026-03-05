# external libraries
import pygame
from math import cos, sin, acos, asin, pi
import random
from enum import Enum
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))



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
def fileWrite(File : str, boxes : list[pygame.Rect], killBoxes : list[pygame.Rect], spawnPoint : tuple[int,int], winZone : pygame.Rect) -> None:
    with open(File, 'w') as file:
        for i in boxes:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("kill\n")
        for i in killBoxes:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("spawn\n")
        file.write(f"{spawnPoint}\n")
        file.write("win\n")
        file.write(f"{(winZone.x,winZone.y,winZone.w,winZone.h)}\n")

def fileRead(File : str) -> tuple[list[pygame.Rect],list[pygame.Rect],tuple[int,int],pygame.Rect]:
    mode = 'boxes'
    boxes : list[pygame.Rect] = []
    killboxes : list[pygame.Rect] = []
    spawnpoint : tuple[int,int] = (0,0)
    winzone : tuple[int,int,int,int] = (0,0,0,0)
    try:
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
    except:
        pass
    return boxes,killboxes,spawnpoint,pygame.Rect(winzone[0],winzone[1],winzone[2],winzone[3])
#this works, I tested it

def getFile(level : int) -> str:
    File : str = ""
    match level:
        case 1:
            File = "levels/level1"
        case 2:
            File = "levels/level2"
        case 3:
            File = "levels/level3"
        case 4:
            File = "levels/level4"
        case 5:
            File = "levels/level5"
        case 6:
            File = "levels/level6"
        case _:
            File = ''
    return File

def print_at_end(title, list):
    evil_list = [str(whatever).replace("<rect(", "pygame.Rect(").replace(")>", "),") for whatever in list[:]]
    print(title)
    print(evil_list)

def reset_customs():
    global variable67, variable69, custom_rects
    variable67 = (0, 0)
    variable69 = (0, 0)
    custom_rects = []

def collisions(rect_list,x,y,x_vel,y_vel,width,height,gravity):
    hblock = False
    vblock = False
    for anything in rect_list:
        if pygame.Rect((x + (x_vel * dt / 4) - width // 2), y - height // 2,
                       width, height).colliderect(anything):
            hblock = True
        if pygame.Rect(x - width // 2, y + (y_vel * dt / 4) - height // 2, width,
                       height).colliderect(anything):
            vblock = True
        if pygame.Rect((x + (x_vel * dt / 4) - width // 2),
                       y + ((y_vel + gravity) * dt / 4) - height // 2, width,
                       height).colliderect(anything) and not (
                pygame.Rect((x + (x_vel * dt / 4) - width // 2),
                            y - height // 2, width, height).colliderect(
                        anything) or pygame.Rect(x - width // 2,
                                                 y + (y_vel * dt / 4) - height // 2, width,height).colliderect(anything)):
            hblock = True
            vblock = True

    return hblock, vblock


class EnemyVariant(Enum):
    DEFAULT=0 # stupid dumbass just walks in a straight line and turns around when they hit a wall, they can't even avoid falling off platforms
    SMART=1 # default but they turn around at the edge of platforms
    JUMP=2 # jumps when it hits a wall, but doesn't turn around
    LARGE=3 # default but slower, larger, and bulkier
    FLY=4 # goes back and forth between two points in the sky
    TRACK=5 # walks towards the player
    SHOOT=6 # immobile, shoots towards the player
    FLY_TRACK=7 # flies towards the player
    FLY_SHOOT=8 # flies between two points in the sky and shoots at the player
    FIGHTER_JET=9 # flies and shoots at the player
    BOMB=10 # explodes on death
    BOMBER=11 # immobile, throws bombs at the player
    BOMBER_JET=12 # flies above the player and drops bombs

class Enemy:
    def __init__(self,pos:list[float,float],variant:EnemyVariant):
        self.pos = pos
        self.y_vel = 0
        self.variant = variant
        self.hp = 10
        self.facing_right = False
        self.size = 1
        self.speed = 1
        self.gravity = True
        self.detect_ledge = False
        self.jump = False
        self.track = False
        self.shoot = False
        self.bomb = False
    def main(self):
        self.move()
        self.draw()
    def draw(self):
        pygame.draw.rect(world_surf, (255, 167, 67),
                         (self.pos[0] - self.size*ENEMY_WIDTH // 2, self.pos[1] - self.size*ENEMY_HEIGHT // 2, self.size*ENEMY_WIDTH, self.size*ENEMY_HEIGHT))
    def move(self):
        self.y_vel += self.gravity*GRAVITY*dt
        for i in range(4):
            block = collisions(platforms,self.pos[0],self.pos[1],self.speed*ENEMY_SPEED,self.y_vel,self.size*ENEMY_WIDTH,self.size*ENEMY_HEIGHT,GRAVITY)
            if block[1]:
                if self.y_vel<=0 and (block[0] or (self.detect_ledge and False)):
                    if self.jump:
                        self.y_vel = ENEMY_JUMP_HEIGHT
                    else:
                        self.facing_right = not self.facing_right
                else:
                    self.pos[0] += self.speed*ENEMY_SPEED*dt/4*(2*self.facing_right-1)
                self.y_vel = 0
            else:
                self.pos[1] += self.y_vel*dt/4

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

# enemy variables
enemy_list = []
ENEMY_SPEED = 5
ENEMY_WIDTH = 20
ENEMY_HEIGHT = 20
ENEMY_JUMP_HEIGHT = 15

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
jump_zones = []
pink_orbs = []

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

level5 = [pygame.Rect(2, 968, 87, 32),
pygame.Rect(-5, 906, 13, 103),
pygame.Rect(5, 901, 205, 12),
pygame.Rect(155, 942, 43, 66),
pygame.Rect(33, 775, 179, 73),
pygame.Rect(2, 649, 27, 22),
pygame.Rect(-5, 650, 18, 20),
pygame.Rect(139, 272, 90, 31),
pygame.Rect(372, 414, 168, 46),
pygame.Rect(373, 456, 74, 490),
pygame.Rect(450, 993, 60, 10),
pygame.Rect(2287, 978, 59, 23),
pygame.Rect(2379, 506, 133, 498),
pygame.Rect(2121, 575, 256, 38),
pygame.Rect(2121, 437, 181, 66),
pygame.Rect(2208, 679, 87, 15),
pygame.Rect(2381, -6, 130, 512),
pygame.Rect(1995, -2, 61, 335),
pygame.Rect(1854, 665, 149, 23),
pygame.Rect(1888, 287, 61, 25),
pygame.Rect(1671, 85, 49, 605),
pygame.Rect(1485, 640, 187, 44),
pygame.Rect(1210, 248, 131, 49),
pygame.Rect(908, -6, 60, 489)]

level5_kill = [pygame.Rect(115, 946, 39, 55),
pygame.Rect(88, 971, 43, 32),
pygame.Rect(294, 835, 45, 173),
pygame.Rect(294, 775, 44, 61),
pygame.Rect(211, 775, 90, 17),
pygame.Rect(34, 650, 17, 70),
pygame.Rect(296, 213, 42, 562),
pygame.Rect(37, 211, 44, 439),
pygame.Rect(155, 550, 140, 40),
pygame.Rect(76, 311, 121, 28),
pygame.Rect(296, 105, 43, 106),
pygame.Rect(26, 629, 10, 36),
pygame.Rect(-22, 214, 59, 434),
pygame.Rect(296, 207, 43, 16),
pygame.Rect(323, 106, 107, 110),
pygame.Rect(538, 0, 49, 463),
pygame.Rect(448, 649, 1035, 61),
pygame.Rect(1483, 683, 857, 82),
pygame.Rect(1998, 429, 43, 265),
pygame.Rect(2001, 417, 137, 33),
pygame.Rect(1859, 303, 76, 305),
pygame.Rect(1931, 305, 67, 21),
pygame.Rect(1776, 398, 88, 78),
pygame.Rect(1711, 85, 56, 52),
pygame.Rect(1061, 176, 152, 472),
pygame.Rect(1431, -9, 55, 403),
pygame.Rect(1605, 237, 63, 30),
pygame.Rect(1486, 375, 94, 27),
pygame.Rect(1665, 236, 12, 169),
pygame.Rect(1434, 391, 35, 113),
pygame.Rect(1357, 459, 80, 39),
pygame.Rect(1581, 375, 11, 27),
pygame.Rect(672, 301, 132, 364),
pygame.Rect(675, 212, 128, 90)]
# win zone isnt working and i cant fix it so just gonna do this
lv5win_zone = (445, 459, 69, 194)
lv6win_zone = (1397, 84, 17, 63)

level6 = [pygame.Rect(1, 989, 33, 8),
pygame.Rect(39, 651, 104, 33),
pygame.Rect(286, 626, 5, 100),
pygame.Rect(292, 737, 17, 10),
pygame.Rect(285, 726, 4, 23),
pygame.Rect(286, 813, 6, 60),
pygame.Rect(286, 872, 6, 125),
pygame.Rect(291, 988, 10, 5),
pygame.Rect(285, 795, 5, 20),
pygame.Rect(288, 798, 4, 16),
pygame.Rect(286, 790, 6, 10),
pygame.Rect(419, 988, 55, 7),
pygame.Rect(1508, 996, 108, 7),
pygame.Rect(1487, 700, 15, 6),
pygame.Rect(1441, 917, 19, 3),
pygame.Rect(439, 736, 34, 14),
pygame.Rect(493, 134, 58, 12)
]

level6_kill = [pygame.Rect(55, 754, 36, 239),
pygame.Rect(90, 827, 53, 165),
pygame.Rect(140, 945, 57, 47),
pygame.Rect(192, 983, 62, 7),
pygame.Rect(142, 659, 71, 10),
pygame.Rect(214, 442, 13, 280),
pygame.Rect(278, 312, 7, 676),
pygame.Rect(250, 982, 32, 10),
pygame.Rect(165, 312, 13, 236),
pygame.Rect(174, 311, 106, 15),
pygame.Rect(39, 467, 126, 80),
pygame.Rect(-1, 203, 113, 145),
pygame.Rect(416, 200, 14, 611),
pygame.Rect(283, 611, 74, 12),
pygame.Rect(417, 16, 12, 187),
pygame.Rect(-6, -16, 118, 224),
pygame.Rect(166, 239, 119, 75),
pygame.Rect(284, 237, 42, 10),
pygame.Rect(111, -3, 318, 140),
pygame.Rect(-5, 674, 44, 5),
pygame.Rect(353, 427, 64, 10),
pygame.Rect(348, 707, 69, 5),
pygame.Rect(367, 711, 52, 101),
pygame.Rect(367, 812, 63, 121),
pygame.Rect(368, 930, 11, 23),
pygame.Rect(320, 853, 48, 20),
pygame.Rect(280, 753, 36, 22),
pygame.Rect(410, 804, 20, 18),
pygame.Rect(369, 977, 8, 24),
pygame.Rect(374, 942, 1151, 6),
pygame.Rect(376, 930, 1147, 14),
pygame.Rect(1516, 604, 13, 342),
pygame.Rect(1516, 539, 11, 68),
pygame.Rect(1469, 374, 8, 320),
pygame.Rect(1469, 263, 7, 111),
pygame.Rect(1470, 228, 4, 35),
pygame.Rect(1420, 203, 7, 620),
pygame.Rect(1420, -21, 7, 227),
pygame.Rect(1425, -11, 145, 165),
pygame.Rect(1516, 150, 10, 316),
pygame.Rect(1570, -10, 7, 1008),
pygame.Rect(486, 431, 13, 503),
pygame.Rect(489, 158, 10, 174),
pygame.Rect(489, 151, 935, 9),
pygame.Rect(398, -40, 282, 80),
pygame.Rect(422, 764, 68, 170),
pygame.Rect(420, 31, 1008, 48),
pygame.Rect(653, -64, 818, 117)
]
#misc
camx = 0
camy = 0
death_time = 0
dying = False
variable671 = (0,0)
variable691 = (0,0)

#file loading
try:
    death_image = pygame.image.load('assets/blood-splatter.png').convert_alpha()
    death_sound = pygame.mixer.Sound('assets/hl2-stalker-scream.mp3')
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

    #level switching
    if change_level:
        if level >= 1 and level <= 6:
            platforms,killboxes,respawn_point,win_zone = fileRead(getFile(level))
            if getFile(level)=="":
                level -=1
        elif level > 6:
            level = 6
            print("no more levels")
        else:
            print("no more levels")
            level = 1
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

    for enemy in enemy_list:
        enemy.main()

    # applies drag/friction
    player_xvel *= DRAG**dt

    # applies gravity
    player_yvel += GRAVITY*dt

    # caps fall speed to terminal velocity
    player_yvel = min(player_yvel, TERMINAL_VELOCITY)

    # walking
    walk = ((keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])) * PLAYER_SPEED

    # collisions
    for i in range(4):
        horizontal_blocked = collisions(platforms,playerx,playery,walk+player_xvel,player_yvel,PLAYER_WIDTH,PLAYER_HEIGHT,GRAVITY)[0]
        vertical_blocked = collisions(platforms,playerx,playery,walk+player_xvel,player_yvel,PLAYER_WIDTH,PLAYER_HEIGHT,GRAVITY)[1]

        refill1 = collisions(jump_zones,playerx,playery,walk+player_xvel,player_yvel,PLAYER_WIDTH,PLAYER_HEIGHT,GRAVITY)[0]
        refill2 = collisions(jump_zones,playerx,playery,walk+player_xvel,player_yvel,PLAYER_WIDTH,PLAYER_HEIGHT,GRAVITY)[1]
        if refill1 or refill2:
            bullets = magazine_size



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
    # cant figure out why winzone doesent spawn so just gonna do this
    if level == 5:
        pygame.draw.rect(world_surf, "green", lv5win_zone)
    if level == 6:
        pygame.draw.rect(world_surf, "green", lv6win_zone)
    for boxes in killboxes:
        pygame.draw.rect(world_surf, (100,20,20), boxes)
    for platform in platforms:
        pygame.draw.rect(world_surf, "brown", platform)
    for zones in jump_zones:
        pygame.draw.rect(world_surf, (90, 250, 180), zones)
    for orbs in pink_orbs:
        pygame.draw.circle(world_surf, (255, 150, 200), orbs, 30)
    for objects in custom_rects:
        pygame.draw.rect(world_surf, "blue", objects)
    pygame.draw.rect(world_surf, "yellow", (respawn_point[0] - 20, respawn_point[1] - 20, 40, 40))


        #creator mode!
    if creator_mode:

        if keys[pygame.K_t]:
            new_orb = mouse_pos[0]+camx, mouse_pos[1]+camy
            pink_orbs.append(new_orb)

        if keys[pygame.K_KP_PLUS]:
            enemy_list.append(Enemy([mouse_pos[0]+camx, mouse_pos[1]+camy],EnemyVariant.DEFAULT))

        if variable67 != (0,0):
            pygame.draw.circle(world_surf, "red", (variable67), 10)

        if variable69 != (0,0):
            pygame.draw.circle(world_surf, "purple", (variable69), 10)

        if keys[pygame.K_q]:
            variable67 = mouse_pos[0]+camx, mouse_pos[1]+camy
            changing_var = True

        elif keys[pygame.K_e]:
            variable69 = mouse_pos[0]+camx, mouse_pos[1]+camy
            changing_var = True

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
            for zones in jump_zones:
                if zones.collidepoint((mouse_pos[0] + camx, mouse_pos[1] + camy)):
                    jump_zones.remove(zones)
            for orbs in pink_orbs:
                if orbs.collidepoint((mouse_pos[0] + camx, mouse_pos[1] + camy)):
                    pink_orbs.remove(orbs)
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
            if changing_var:
                new_platform = calc_rects(variable67, variable69)
                changing_var = False
            custom_rects.clear()
            custom_rects.append(new_platform)
            if keys[pygame.K_z]:
                platforms.append(new_platform)
                reset_customs()
            elif keys[pygame.K_l]:
                win_zone = new_platform
                reset_customs()
            elif keys[pygame.K_g]:
                killboxes.append(new_platform)
                reset_customs()
            elif keys[pygame.K_j]:
                jump_zones.append(new_platform)
                reset_customs()

        if keys[pygame.K_6] and keys[pygame.K_7]:
            fileWrite(getFile(level),platforms,killboxes,(int(respawn_point[0]), int(respawn_point[1]),win_rect))
            
        bullets = 6000
        if keys[pygame.K_w]:
            playery -= 20
        if keys[pygame.K_s]:
            playery += 20
        if keys[pygame.K_a]:
            playerx -= 20
        if keys[pygame.K_d]:
            playerx += 20



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
    if level == 5:
        win = pygame.Rect(player_rect).colliderect(lv5win_zone)
    if level == 6:
        win = pygame.Rect(player_rect).colliderect(lv6win_zone)
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
print_at_end("Platforms", platforms)
print_at_end("Killboxes", killboxes)
print_at_end("Respawn Point", respawn_point)
print_at_end("Win Zone", win_zone)
print_at_end("jump Zone", jump_zones)
# close the game when we close it

pygame.quit()








