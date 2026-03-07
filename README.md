# GunPlatformer
Terminal 1:
``` bash 
sudo apt-get update
./start-gui.sh
```

Terminal 2:
``` bash
mkdir -p /tmp/xdg-runtime-$UID
chmod 0700 /tmp/xdg-runtime-$UID
export XDG_RUNTIME_DIR=/tmp/xdg-runtime-$UID
export DISPLAY=:1
python GunPlatformer.py
```

controls:
    BASE GAME:
    a or LEFT_KEY = move left
    d or RIGHT_KEY = move right
    LEFT_CLICK or SPACEBAR = shoot
    MOVE_CURSOR = move aiming
    r = restart level
    F_11 = toggle fullscreen
    F_1 = previous level
    F_2 = next level
    ESCAPE = kill program
    CREATOR MODE:
    F_9 = toggle creator mode
    q = select point A at cursor pos
    e = select point B at cursor pos
    z = creates platform between point A, and points B
    l = moves win zone between point A, and points B
    j = creates bullet refill zones Between points A, and point B
    g = creates killboxes between points A, and point B
    m = moves spawn point to cursor
    BACKSPACE = deletes platform or win zone at cursor 
    CTRL+Z = undo platform creation
    CTRL+SHIFT+Z = redo platform creation
    w = moves player up
    a = moves player left
    s = moves player down
    d = moves player right
    6+7 = saves current level

How to play:
    shoot and you will be pushed in the opposite direction of where you shoot
    try to reach the end point, usually to the right

How to add level:
    add 1 to variable, max_level
    add another segment to def getfile()
    press 6+7 simultaneously to save level after adding stuff
    make sure to name your level and add the ULID (unique level ID)