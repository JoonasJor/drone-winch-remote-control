## Install packages
```
sudo apt update
sudo apt install gobject-introspection libgirepository1.0-dev libcairo2-dev pkg-config libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgstreamer-plugins-bad1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-x gstreamer1.0-alsa gstreamer1.0-gl gstreamer1.0-gtk3 gstreamer1.0-qt5 gstreamer1.0-pulseaudio python3-gst-1.0
```
```
pip install -r requirements.txt
```
## Enable serial Port
```
sudo raspi-config
```
Interface Options > Serial Port > " Would you like the serial port hardware to be enabled?": Yes
## Create systemd service
```
sudo nano /etc/systemd/system/name.service
```
```
[Unit]
Description=Start pigpio daemon and run main.py

[Service]
ExecStart=/path/to/script/start.sh
WorkingDirectory=/path/to/script/
StandardOutput=inherit
StandardError=inherit
Restart=always

[Install]
WantedBy=multi-user.target
```
```
sudo systemctl enable name.service
sudo systemctl start name.service
```

### Tested devices:  
-Raspberry Pi Zero 2 W (Raspberry Pi OS 12 Bookworm)  
-Raspberry Pi 4 Model B (Raspberry Pi OS 12 Bookworm)
