import cv2

class CameraGenerator:
    def __init__(self,deviceIndex):
        self.capture = None
        self.deviceIndex = deviceIndex

        self.stride =0
        self.video_width=0
        self.video_height=0
        self.rval =None
        self.frame = None




    def set_configure(self):
        self.capture = cv2.VideoCapture(self.deviceIndex)
        self.video_width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.capture.set(3, self.video_width)  # set width
        self.capture.set(4, self.video_height)  # set height
        self.stride = 0
        if self.capture.isOpened():
            self.rval, self.frame = self.capture.read()
            self.stride = self.frame.strides[0]
        else:
            return
    def get_capture(self):
        return self.capture
    def get_stride(self):
        return self.stride
    def get_video_width(self):
        return self.video_width
    def get_video_height(self):
        return self.video_height

    
    