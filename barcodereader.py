from dbr import *
class DBRGenerator:
    def __init__(self,license):

        self.license = license
        self.reader = None
        self.parameters = None
        self.scanhistory=[]

        self.dbr_init()

    def dbr_init(self):
            # dbr init
        error = BarcodeReader.init_license(self.license)
        self.reader = BarcodeReader()
        settings = self.reader.get_runtime_settings()
        settings.barcode_format_ids = EnumBarcodeFormat.BF_QR_CODE
        settings.expected_barcodes_count = 1
        self.reader.update_runtime_settings(settings)
    def get_reader(self):
        return self.reader
    def set_parameters(self,video_width,video_height,stride):
        self.parameters = self.reader.init_frame_decoding_parameters()
        self.parameters.max_queue_length = 30
        self.parameters.max_result_queue_length = 30
        self.parameters.width = video_width
        self.parameters.height = video_height
        self.parameters.stride = stride
        self.parameters.image_pixel_format = EnumImagePixelFormat.IPF_RGB_888
        self.parameters.region_top = 0
        self.parameters.region_bottom = 100
        self.parameters.region_left = 0
        self.parameters.region_right = 100
        self.parameters.region_measured_by_percentage = 1
        self.parameters.threshold = 0.01
        self.parameters.fps = 0
        self.parameters.auto_filter = 1
    def get_parameters(self):
        return self.parameters
    def append_scan_history(self,result):
        self.scanhistory.append(result)
    def get_scan_history(self):
        return self.scanhistory
    def get_total_scans(self):
        return len(self.scanhistory)
    def get_last_scan(self):
        return self.scanhistory[-1]