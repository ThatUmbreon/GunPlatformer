# external libraries
import pygame
from math import cos, sin, acos, asin, pi
import random
from enum import Enum
import os

from pygame.examples.midi import null_key

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
    global player_yvel, player_xvel, underwater
    '''what even is this shit.
    it calculates the point on the circumference of a circle with a given radius and center, that is in the direction of the point argument, with an optional angle added to it.
    like seriously what do you even call that'''
    #move this shit to for bullet in bullets list or whaterv, it bugs out when bullets leave the water or enter it.
    if underwater == True:
        playerx = radius*cos(addangle+acos((point[0]-center[0])/(distance(center,point)))) + player_xvel/2
        playery = radius*sin(addangle+asin((point[1]-center[1])/(distance(center,point)))) + player_yvel/2.5
    else:
        playerx = radius * cos(addangle + acos((point[0] - center[0]) / (distance(center, point))))
        playery = radius * sin(addangle + asin((point[1] - center[1]) / (distance(center, point))))
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
def fileWrite(File : str, boxes : list[pygame.Rect], killBoxes : list[pygame.Rect], jumpZones : list[pygame.Rect], water : list[pygame.Rect], spawnPoint : tuple[int,int], winZone : pygame.Rect) -> None:
    with open(File, 'w') as file:
        for i in boxes:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("kill\n")
        for i in killBoxes:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("jump\n")
        for i in jumpZones:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("water\n")
        for i in water:
            file.write(f"pygame.Rect{(i.x,i.y,i.w,i.h)}\n")
        file.write("spawn\n")
        file.write(f"{spawnPoint}\n")
        file.write("win\n")
        file.write(f"{(winZone.x,winZone.y,winZone.w,winZone.h)}\n")
        file.write("name\n")

def fileRead(File : str) -> tuple[list[pygame.Rect],list[pygame.Rect], list[pygame.Rect],tuple[int,int],pygame.Rect, list[str]]:
    global pomni_r34
    mode = 'boxes'
    boxes : list[pygame.Rect] = []
    killboxes : list[pygame.Rect] = []
    jump_zones : list[pygame.Rect] = []
    water : list[pygame.Rect] = []
    spawnpoint : tuple[int,int] = (0,0)
    winzone : tuple[int,int,int,int] = (0,0,0,0)
    name : str = "unnamed"
    try:
        with open(File, 'r') as file:
            for line in file:
                try:
                    line = line[:-1]
                    if line=="kill":
                        mode = 'kill'
                    elif line=="jump":
                        mode = 'jump'
                    elif line =="spawn":
                        mode = 'spawn'
                    elif line =="win":
                        mode = 'win'
                    elif line =="water":
                        mode = 'water'
                    elif line=="name":
                        mode = 'name'
                        print("name mode")
                    elif mode=='boxes':
                        boxes.append(eval(line))
                    elif mode=='kill':
                        killboxes.append(eval(line))
                    elif mode=='jump':
                        jump_zones.append(eval(line))
                    elif mode=='spawn':
                        spawnpoint=eval(line)
                    elif mode=='win':
                        winzone=eval(line)
                    elif mode=='water':
                        water.append(eval(line))
                    elif mode=='name':
                        name=line
                except:
                    print('error in reading file contents')
    except:
        print("errror in reading file")
    return boxes,killboxes,jump_zones,water,spawnpoint,pygame.Rect(winzone[0],winzone[1],winzone[2],winzone[3]), name
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
        case 7:
            File = "levels/level7"
        case 8:
            File = "levels/level8"
        case _:
            File = ""
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
crosshair = pygame.image.load("assets/crosshair.png").convert_alpha()
crosshair = pygame.transform.scale(crosshair,(32,32))
pygame.mouse.set_cursor((16,16),crosshair)
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
water = []
pink_orbs = []


level = int(1)

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
        if level >= 1 and level <= 8:
            platforms,killboxes,jump_zones,water,respawn_point,win_zone, name = fileRead(getFile(level))
            if getFile(level)=="":
                level -=1

        elif level > 7:
            level -= 1
            print("no more levels")
        else:
            print("no more levels")
            level = 1
        reset()
        print(level)
        print(name)

    #spawning water

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
        if mouse_pos != (playerx-camx,playery-camy):
            player_xvel, player_yvel = thatcircleshit(RECOIL, (playerx-camx,playery-camy), mouse_pos, pi)
            bullet_list.append([[playerx,playery],thatcircleshit(BULLET_SPEED, (playerx-camx,playery-camy), mouse_pos)])
            bullets -= 1
        else:
            print("dumbass")
            kys = True

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
    for zone in water:
        pygame.draw.rect(world_surf, (0, 0, 170), zone)
    for zones in jump_zones:
        pygame.draw.rect(world_surf, (90, 250, 180), zones)
    for boxes in killboxes:
        pygame.draw.rect(world_surf, (100,20,20), boxes)
    for platform in platforms:
        pygame.draw.rect(world_surf, "brown", platform)

    for orbs in pink_orbs:
        pygame.draw.circle(world_surf, (160, 20, 50), orbs, 30)
    for objects in custom_rects:
        pygame.draw.rect(world_surf, "blue", objects)
    pygame.draw.rect(world_surf, "yellow", (respawn_point[0] - 20, respawn_point[1] - 20, 40, 40))

    #check if underwater
    for i in range(4):
        check1 = collisions(water, playerx, playery, walk + player_xvel, player_yvel, PLAYER_WIDTH, PLAYER_HEIGHT, GRAVITY)[0]
        check2 = collisions(water, playerx, playery, walk + player_xvel, player_yvel, PLAYER_WIDTH, PLAYER_HEIGHT, GRAVITY)[1]
        if check1 or check2:
            underwater = True
            GRAVITY = 0.5
            DRAG = 0.93
            RECOIL = 14
            PLAYER_SPEED = 3
            TERMINAL_VELOCITY = 30
            if player_yvel > min(TERMINAL_VELOCITY, 2.5):
                player_yvel -= 0.15
        else:
            underwater = False
            TERMINAL_VELOCITY = 15
            GRAVITY = 0.75
            DRAG = 0.9
            RECOIL = 20
            PLAYER_SPEED = 5

        #creator mode!
    if creator_mode:

        if keys[pygame.K_t]:
            new_orb = (mouse_pos[0]+camx, mouse_pos[1]+camy)
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
            for zone in water:
                if zone.collidepoint((mouse_pos[0] + camx, mouse_pos[1] + camy)):
                    water.remove(zone)
            for orbs in pink_orbs:
                if distance(orbs,(mouse_pos[0] + camx, mouse_pos[1] + camy)) < 30:
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
            elif keys[pygame.K_1]:
                water.append(new_platform)
                reset_customs()

        if keys[pygame.K_6] and keys[pygame.K_7]:
            fileWrite(getFile(level),platforms,killboxes,jump_zones, water,(int(respawn_point[0]), int(respawn_point[1])),win_zone)
            saved = True
            print("saved levels")
            
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
    if win:
        won()


    #puts images onto screen with offset for map
    screen.blit(world_surf, (-camx, -camy))
    #draws bullet count on screen
    write(f"Bullets: {bullets}/{magazine_size}",(0,0),20,(255,255,255))
    try:
        if saved:
            write("saved level", (WIDTH-220,0), 50, "green")
            saved = False
        if kys:
            #happens when someone shoots directly the middle of the screen.
            pass
    except:
        pass
    if dying:
        screen.blit(death_image, (0, 0, death_image.get_width(), death_image.get_height()))
        death_sound.play()
        death_time -= 1
        pygame.display.flip()
        pygame.time.wait(death_time)
        dying = False
        reset()

    rando = random.randint(0,100000)
    if rando == 1:
        death_sound.play()
    #you know what ts is ok
    pygame.display.flip()
    printin = False
if printin == True:
    print_at_end("Platforms", platforms)
    print_at_end("Killboxes", killboxes)
    print_at_end("Respawn Point", respawn_point)
    print_at_end("Win Zone", win_zone)
    print_at_end("jump Zone", jump_zones)
    print_at_end("water", water)
# close the game when we close it

pygame.quit()









