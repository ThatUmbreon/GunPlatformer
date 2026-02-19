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