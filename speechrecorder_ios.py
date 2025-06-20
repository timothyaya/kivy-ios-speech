class SpeechRecorder_ios:
    def __init__(self, callback=None):
        from pyobjus import autoclass
        from pyobjus.dylib_manager import load_framework, INCLUDE
        load_framework(INCLUDE.Foundation)
        load_framework(INCLUDE.AVFoundation)
        self.bridge = autoclass('SpeechBridge').shared()
        self.callback = callback
        self.app = None

    def set_app(self, app):
        self.app = app

    def start_recording(self):
        print("🎙️ iOS 開始錄音")
        if self.app:
            self.app.status_label.text = "錄音中..."
        self.bridge.startRecognition()

    def stop_recording(self):
        print("🛑 iOS 停止錄音")
        if self.app:
            self.app.status_label.text = "辨識中..."
        self.bridge.stopRecognition()
        from kivy.clock import Clock
        Clock.schedule_interval(self.check_result, 0.5)

    def check_result(self, dt):
        if self.bridge.isRecognitionDone():
            from kivy.clock import Clock
            Clock.unschedule(self.check_result)
            self.read_result()

    def read_result(self):
        import os
        path = os.path.join(os.path.expanduser("~"), "Documents", "result.txt")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read().strip()
                if self.app:
                    self.app.status_label.text = f"語音辨識：{text}"
                print("✅ 語音結果：", text)
                if self.callback:
                    self.callback(text)
        else:
            if self.app:
                self.app.status_label.text = "❌ 未找到結果檔案"
            print("❌ 無結果檔案")