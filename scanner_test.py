import cv2
from dbr import *
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
import os
os.environ['KIVY_IMAGE'] = 'pil'


class My_Button(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.2, 0.15)


Builder.load_string('''
<ScrolllabelLabel>:
    Label:
        text: root.text
        font_size: 13
        text_size: self.width, None
        size_hint_y: None
        height: self.texture_size[1]
''')
class ScrolllabelLabel(ScrollView):
    text = StringProperty('')


class My_Button(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.2,0.15)




class CamApp(App):

    def build(self):
        

        
        self.capture= None
        self.dbr_init()
        self.barcode_detected=0
        self.all_barcodes=[]
        self.totoalScan = 0
        self.cameraAmount = self.camera_amount()
        print(f"\n there are {self.cameraAmount} camera\n")


        ##dbr init
        self.img1 = Image(size_hint=(.4, .4),
                          pos_hint={'x': .1, 'y': .6})
        self.text = Label(text="No result:",
                          font_size=14,
                          size_hint=(.4, .4),
                          pos_hint={'x': .1, 'y': .25})
        self.camera_button = My_Button(text='Camera', font_size=14)
        self.camera_button.bind(on_press=self.camera_selection_callback)
        self.new_scroll = ScrolllabelLabel(
            text='Scan History:', pos_hint={'x': .6, 'y': .0})


        self.layout = FloatLayout()

        self.layout.add_widget(self.camera_button)
        self.layout.add_widget(self.img1)
        self.layout.add_widget(self.text)
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
                ret = self.reader.append_video_frame(frame)
            except Exception:
                print(Exception)
        else:
            return

    def text_results_callback_func(self,frame_id, t_results, user_data):
        for result in t_results:
            self.totoalScan+=1
            text_result = TextResult(result)
            self.text.text = f"\n\n Result:{text_result.barcode_text}\n\n Format:{text_result.barcode_format_string}\n\n Total Scan:{self.totoalScan}"

    def unique_barcode_callback_func(self, frame_id, t_results, user_data):
        for result in t_results:
            self.totoalScan += 1
            text_result = TextResult(result)
            self.text.text = f"\n\n Result: {text_result.barcode_text}\n\n Format: {text_result.barcode_format_string}\n\n Total Scan: {self.totoalScan}"
            self.new_scroll.text += f" \n{self.totoalScan}: {text_result.barcode_text}"
    def testDevice(self,source):
        cap = cv2.VideoCapture(source) 
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', source)
            return None
        else:
            print("video source:" + str(source))
            return cap


    def camera_selection_callback(self, th):
        self.video_width = 0
        self.video_height = 0

        # a. Decode video from camera
        self.camera = 0
        self.capture = cv2.VideoCapture(self.camera)

        # # b. Decode video file
        # video_file = "Put your video file path here."
        # vc = cv2.VideoCapture(video_file)

        video_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.capture.set(3, video_width)  # set width
        self.capture.set(4, video_height)  # set height
        stride = 0
        if self.capture.isOpened():
            rval, frame = self.capture.read()
            stride = frame.strides[0]
        else:
            return

        parameters = self.reader.init_frame_decoding_parameters()
        parameters.max_queue_length = 30
        parameters.max_result_queue_length = 30
        parameters.width = video_width
        parameters.height = video_height
        parameters.stride = stride
        parameters.image_pixel_format = EnumImagePixelFormat.IPF_RGB_888
        parameters.region_top = 0
        parameters.region_bottom = 100
        parameters.region_left = 0
        parameters.region_right = 100
        parameters.region_measured_by_percentage = 1
        parameters.threshold = 0.01
        parameters.fps = 0
        parameters.auto_filter = 1

        # start video decoding. The callback function will receive the recognized barcodes.
        self.reader.start_video_mode(
            parameters, text_result_callback_func=None, unique_barcode_callback_func=self.unique_barcode_callback_func)

        
        print(f"camera is:{self.camera}")
    
    
    def dbr_init(self):
        # dbr init
        error = BarcodeReader.init_license(
            "DLS2eyJoYW5kc2hha2VDb2RlIjoiMTAxMTcwOTE0LTEwMTUxMjc3MCIsIm1haW5TZXJ2ZXJVUkwiOiJodHRwczovL21sdHMuZHluYW1zb2Z0LmNvbS8iLCJvcmdhbml6YXRpb25JRCI6IjEwMTE3MDkxNCIsInN0YW5kYnlTZXJ2ZXJVUkwiOiJodHRwczovL3NsdHMuZHluYW1zb2Z0LmNvbS8iLCJjaGVja0NvZGUiOjIwNDYyNDk0NjR9")
        self.reader = BarcodeReader()
        settings = self.reader.get_runtime_settings()
        settings.barcode_format_ids = EnumBarcodeFormat.BF_QR_CODE
        settings.expected_barcodes_count = 1
        self.reader.update_runtime_settings(settings)

    def camera_amount(self):
    # Returns int value of available camera devices connected to the host device'''
        camera = 0
        while True:
            if (cv2.VideoCapture(camera).grab()) is True:
                camera = camera + 1
            else:
                cv2.destroyAllWindows()
                return (int(camera))



if __name__ == '__main__':
    CamApp().run()
    cv2.destroyAllWindows()
