import cv2
from camera import CameraGenerator
from dbr import *
from barcodereader import DBRGenerator
import datetime

from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
import os
os.environ['KIVY_IMAGE'] = 'pil'




class ScrolllabelLabel(ScrollView):
    text = StringProperty('')


class CameraButton(Button):
    pass

class ScanResultLabel(Label):
    pass
class VideoFrame(Image):
    pass

class CamApp(App):

    def build(self):
        

        
        self.capture= None
        license = "DLS2eyJoYW5kc2hha2VDb2RlIjoiMTAxMTcwOTE0LTEwMTUxMjc3MCIsIm1haW5TZXJ2ZXJVUkwiOiJodHRwczovL21sdHMuZHluYW1zb2Z0LmNvbS8iLCJvcmdhbml6YXRpb25JRCI6IjEwMTE3MDkxNCIsInN0YW5kYnlTZXJ2ZXJVUkwiOiJodHRwczovL3NsdHMuZHluYW1zb2Z0LmNvbS8iLCJjaGVja0NvZGUiOjIwNDYyNDk0NjR9"
        self.DBRGnt =DBRGenerator(license=license)
        self.reader =self.DBRGnt.get_reader()
        self.camera_device_index = 0
        self.start_time=None
        self.end_time=None

        self.img1 = VideoFrame()
        self.scan_result = ScanResultLabel()
        self.new_scroll = ScrolllabelLabel()
        self.camera_button = CameraButton()
        self.camera_button.bind(on_press=self.camera_selection_for_decoding_callback)


        self.layout = FloatLayout()

        self.layout.add_widget(self.camera_button)
        self.layout.add_widget(self.img1)
        self.layout.add_widget(self.scan_result)
        self.layout.add_widget(self.new_scroll)
        
        Clock.schedule_interval(self.update, 1.0/33.0)


        return self.layout

    def update(self,dt):
        if self.capture:

            # display image from cam in opencv window
            ret, frame = self.capture.read()
            # convert it to texture
            buf1 = cv2.flip(frame, 0)
            if buf1 is None:
                return
            buf = buf1.tobytes()
            texture1 = Texture.create(
                size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            # if working on RASPBERRY PI, use colorfmt='rgba' here instead, but stick with "bgr" in blit_buffer.
            texture1.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
            # display image from the texture
            self.img1.texture = texture1
            try:
                # append frame to video buffer cyclically
                self.start_time = datetime.datetime.now()
                ret = self.reader.append_video_frame(frame)
            except Exception:
                print(Exception)
        else:
            return

    def unique_barcode_callback_func(self, frame_id, t_results, user_data):
        for result in t_results:
            self.end_time = datetime.datetime.now()
            time_interval = self.end_time-self.start_time
            self.DBRGnt.append_scan_history(TextResult(result))
            self.DBRGnt.get_total_scans()
            print("scanned")
            print(type(self.DBRGnt.get_last_scan()))
            self.scan_result.text = f"\n\n Result: {self.DBRGnt.get_last_scan().barcode_text} \n\n Format: {self.DBRGnt.get_last_scan().barcode_format_string}\n\n Total Scan: {self.DBRGnt.get_total_scans()}\n\n Time cost: {time_interval.microseconds/1000}ms"
            self.new_scroll.text += f"\n{self.DBRGnt.get_total_scans()}: {self.DBRGnt.get_last_scan().barcode_text}"


    def camera_selection_for_decoding_callback(self,dt):

        # a. Decode video from camera
        Camera = CameraGenerator(deviceIndex=self.camera_device_index)
        self.camera_device_index+=1
        Camera.set_configure()
        self.capture = Camera.get_capture()

        # # b. Decode video file
        # video_file = "Put your video file path here."
        # vc = cv2.VideoCapture(video_file)

        video_width = Camera.get_video_width()
        video_height = Camera.get_video_height()
        stride=Camera.get_stride()
        self.DBRGnt.set_parameters(video_height=video_height,video_width=video_width,stride=stride)
        parameters = self.DBRGnt.get_parameters()
        # start video decoding. The callback function will receive the recognized barcodes.

        self.reader.stop_video_mode()
        self.reader.start_video_mode(
            parameters, text_result_callback_func=None, unique_barcode_callback_func=self.unique_barcode_callback_func)


    
    






if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
