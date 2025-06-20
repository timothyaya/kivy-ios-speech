import speech_recognition as sr

class SpeechRecorder_win():
    def __init__(self, callback=None):
        self.recognizer = sr.Recognizer()
        self.audio = None
        self.recording = False
        self.mic = None
        self.callback = callback  # callback: 辨識完傳回的函式

    def start_recording(self):
        try:
            self.mic = sr.Microphone()
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("🎙️ 開始錄音")
                self.audio = self.recognizer.listen(source, phrase_time_limit=5)
            self.recording = True
        except Exception as e:
            print(f"錄音錯誤: {e}")
            self.recording = False

    def stop_recording(self):
        print("🛑 結束錄音並辨識")
        if not self.recording or self.audio is None:
            print("⚠️ 無錄音資料")
            return

        try:
            text = self.recognizer.recognize_google(self.audio, language="zh-TW")
            print("辨識結果：", text)
            if self.callback:
                self.callback(text)
        except sr.UnknownValueError:
            print("無法辨識語音")
        except sr.RequestError as e:
            print(f"語音服務錯誤: {e}")
        finally:
            self.recording = False
            self.audio = None