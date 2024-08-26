import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class VideoOutput:
    def __init__(self, serial_reader, winch_controller):
        Gst.init(None)
        
        self.serial_data_reader = serial_reader
        self.winch_controller = winch_controller
        
        self.transmitter_overlays = []
        self.winch_overlay = None

    def create_pipeline(self):
        # Create the pipeline
        pipeline = Gst.Pipeline.new("pipeline")

        # Create elements
        source = Gst.ElementFactory.make("libcamerasrc", "source")

        transmitter_overlay_0 = self.create_text_overlay("serial_overlay_0", "top", "left")
        self.transmitter_overlays.append(transmitter_overlay_0)
        transmitter_overlay_1 = self.create_text_overlay("serial_overlay_1", "top", "right")
        self.transmitter_overlays.append(transmitter_overlay_1)
        self.winch_overlay = self.create_text_overlay("winch_state_overlay", "bottom", "left")

        queue = Gst.ElementFactory.make("queue", "queue")
        sink = Gst.ElementFactory.make("fpsdisplaysink", "fps_sink")
        sink.set_property("video-sink", Gst.ElementFactory.make("glimagesink", "gl_sink"))
        #sink = Gst.ElementFactory.make("glimagesink", "gl_sink")
        sink.set_property("sync", False)

        # Add elements to the pipeline
        pipeline.add(source)
        pipeline.add(transmitter_overlay_0)
        pipeline.add(transmitter_overlay_1)
        pipeline.add(self.winch_overlay)
        pipeline.add(queue)
        pipeline.add(sink)

        # Create caps
        caps = Gst.Caps.new_empty()
        structure = Gst.Structure.new_empty("video/x-raw")
        structure.set_value("width", 1280)
        structure.set_value("height", 720)
        #framerate = Gst.Fraction()
        #framerate.numerator = 30
        #framerate.denominator = 1
        structure.set_value("framerate", Gst.Fraction(30, 1))
        structure.set_value("format", "NV12")
        caps.append_structure(structure)

        # Create a capsfilter and set the caps
        filter = Gst.ElementFactory.make("capsfilter", "filter")
        filter.set_property("caps", caps)
        pipeline.add(filter)

        # Link the elements
        source.link(transmitter_overlay_0)
        transmitter_overlay_0.link(transmitter_overlay_1)
        transmitter_overlay_1.link(self.winch_overlay)
        
        self.winch_overlay.link(queue)
        queue.link(filter)
        filter.link(sink)

        return pipeline

    def create_screenshot_pipeline(self):
        screenshot_pipeline = Gst.Pipeline.new("screenshot_pipeline")

        # Create elements
        source = Gst.ElementFactory.make("libcamerasrc", "source")
        if not source:
            print("Error: Unable to create source element.")
            return None

        transmitter_overlay_0 = self.create_text_overlay("serial_overlay_0", "top", "left")
        self.transmitter_overlays.append(transmitter_overlay_0)
        transmitter_overlay_1 = self.create_text_overlay("serial_overlay_1", "top", "right")
        self.transmitter_overlays.append(transmitter_overlay_1)
        self.winch_overlay = self.create_text_overlay("winch_state_overlay", "bottom", "left")

        jpegenc = Gst.ElementFactory.make("jpegenc", "jpegenc")
        jpegenc.set_property("snapshot", True)
        if not jpegenc:
            print("Error: Unable to create jpegenc element.")
            return None

        filesink = Gst.ElementFactory.make("filesink", "filesink")
        filesink.set_property("location", "screenshot.jpg")
        if not filesink:
            print("Error: Unable to create filesink element.")
            return None

        # Create caps
        caps = Gst.Caps.new_empty()
        structure = Gst.Structure("video/x-raw")
        structure.set_value("width", 1280)
        structure.set_value("height", 720)
        structure.set_value("framerate", Gst.Fraction(30, 1))
        structure.set_value("format", "NV12")
        caps.append_structure(structure)

        # Create a capsfilter and set the caps
        filter = Gst.ElementFactory.make("capsfilter", "filter")
        filter.set_property("caps", caps)
        if not filter:
            print("Error: Unable to create capsfilter element.")
            return None

        # Add elements to the pipeline
        screenshot_pipeline.add(source)
        screenshot_pipeline.add(transmitter_overlay_0)
        screenshot_pipeline.add(transmitter_overlay_1)
        screenshot_pipeline.add(self.winch_overlay)
        screenshot_pipeline.add(filter)
        screenshot_pipeline.add(jpegenc)
        screenshot_pipeline.add(filesink)

        # Link the elements
        if not (source.link(transmitter_overlay_0) and
                transmitter_overlay_0.link(transmitter_overlay_1) and
                transmitter_overlay_1.link(self.winch_overlay) and
                self.winch_overlay.link(filter) and
                filter.link(jpegenc) and
                jpegenc.link(filesink)):
            print("Error: Unable to link elements in the pipeline.")
            return None

        return screenshot_pipeline
    
    def create_text_overlay(self, name: str, valignment: str, halignment: str):
        overlay = Gst.ElementFactory.make("textoverlay", name)
        overlay.set_property("text", "")
        overlay.set_property("shaded-background", True)
        overlay.set_property("valignment", valignment)
        overlay.set_property("halignment", halignment)
        overlay.set_property("font-desc", "Roman, 10")

        return overlay
    
    def construct_overlay_string(self):  
        text = f"Winch: {self.winch_controller.winch_state}\n"
        for serial_no, data in self.serial_data_reader.serial_data.items():
            transmitter_is_paired = data["learn_status"]
            if not transmitter_is_paired:
                continue

            rssi = data["rssi"]
            battery_voltage = data["battery_voltage"]
            battery_low = data["battery_low_voltage"]
            transmitter_state = data["current_state"]

            text += "------\n"
            if transmitter_state == "TimedOut":
                text += (
                    f"S/N: {serial_no}\n"
                    f"State: {transmitter_state}\n"  
                )
            else:
                text += ( 
                    f"S/N: {serial_no}\n"
                    f"Battery voltage: {battery_voltage:.02f}V\n"
                    f"Battery low: {battery_low}\n"
                    f"RSSI: {rssi}\n"
                    f"State: {transmitter_state}\n"
                )
        return text

    def update_text_overlay(self):
        """try:
            text = self.construct_overlay_string()
            self.transmitter_overlays[0].set_property("text", text)
        except Exception as e:
            print(f"update_text_overlay: {e}")"""

        try:
            # Winch overlay
            self.winch_overlay.set_property("text", self.winch_controller.winch_state)

            # Transmitter overlays
            for i, (serial_no, data) in enumerate(self.serial_data_reader.serial_data.items()):
                transmitter_is_paired = data["learn_status"]
                if not transmitter_is_paired:
                    return
                
                rssi = data["rssi"]
                battery_voltage = data["battery_voltage"]
                battery_low = data["battery_low_voltage"]
                transmitter_state = data["current_state"]

                textoverlay = self.transmitter_overlays[i]

                if transmitter_state == "TimedOut":
                    textoverlay.set_property(
                        "text", 
                        f"S/N: {serial_no}\n"
                        f"State: {transmitter_state}")    
                else:
                    textoverlay.set_property(
                        "text", 
                        f"S/N: {serial_no}\n"
                        f"Battery voltage: {battery_voltage:.02f}V\n"
                        f"Battery low: {battery_low}\n"
                        f"RSSI: {rssi}\n"
                        f"State: {transmitter_state}")
        except Exception as e:
            print(f"update_text_overlay: {e}")
    
    def on_message(self, bus, message):
        message_type = message.type

        if message_type == Gst.MessageType.ERROR:
            err, debug_info = message.parse_error()
            print(f"Error received from element {message.src.get_name()}: {err.message}")
            print(f"Debugging information: {debug_info if debug_info else 'none'}")
            self.main_loop.quit()  # Stop the main loop on error

        elif message_type == Gst.MessageType.EOS:
            print("End-Of-Stream reached.")
            self.main_loop.quit()  # Stop the main loop on EOS

    def main(self):
        pipeline = self.create_pipeline()
        #pipeline = self.create_screenshot_pipeline()
        pipeline.set_state(Gst.State.PLAYING)

        # Set up the bus to listen for messages
        bus = pipeline.get_bus()
        bus.add_signal_watch()
        #bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)

        # Create and run the main loop
        main_loop = GLib.MainLoop()
        main_loop.run()
