from serial_data_reader import SerialDataReader
from winch_controller import WinchController
from video_output import VideoOutput
import threading
from time import sleep

serial_reader = SerialDataReader()
winch_controller = WinchController()
video_output = VideoOutput(serial_reader, winch_controller)

def handle_winch():
    while True:
        serial_data = serial_reader.read_serial_data()
        winch_controller.handle_state(serial_data)
        winch_controller.rotate_winch()

def update_video_overlay():
    sleep(1) # poista tämä kuvan ottamiseen
    while True:
        video_output.update_text_overlay()
        sleep(0.5)

def video_main_loop():
    video_output.main()

def main(): 
    thread_winch = threading.Thread(target=handle_winch)
    thread_winch.start()

    thread_video = threading.Thread(target=video_main_loop)
    thread_video.start()
    thread_video_overlay = threading.Thread(target=update_video_overlay)
    thread_video_overlay.start()
    
if __name__ == "__main__":
    main()