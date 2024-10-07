## Install packages (Raspberry Pi)
```
sudo apt update && sudo apt upgrade
sudo apt install gobject-introspection libgirepository1.0-dev libcairo2-dev pkg-config libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio python3-gst-1.0
```
```
pip install -r requirements.txt
```
## Enable serial port (Raspberry Pi)
```
sudo raspi-config
```
Interface Options > Serial Port > " Would you like the serial port hardware to be enabled?": Yes
## Create systemd services (Raspberry Pi)
1. Edit `winch.service` to set the correct paths for `ExecStart` and `WorkingDirectory`.

2. Move both `winch.service` and `pigpio.service` to the systemd directory:
    ```
    sudo mv winch.service /etc/systemd/system/
    sudo mv pigpio.service /etc/systemd/system/
    ```
3. Enable and start both services
    ```
    sudo systemctl enable --now pigpio.service
    sudo systemctl enable --now winch.service
    ```
## Upload code (ESP32)
1. Upload `winch_transmitter_esp.ino` to ESP32

## Tested devices:  
-Raspberry Pi Zero 2 W (Raspberry Pi OS 12 Bookworm)  
-Raspberry Pi 4 Model B (Raspberry Pi OS 12 Bookworm)  
-SparkFun ESP32 Thing
