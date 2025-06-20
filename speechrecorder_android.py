class SpeechRecorder_android:
    def __init__(self, callback=None):
        from android import activity
        self.callback = callback
        self.app = None  # optional fallback
        activity.bind(on_activity_result=self.on_activity_result)

    def set_app(self, app):
        self.app = app

    def start_recording(self):
        if self.app:
            self.app.status_label.text = "啟動 Android 語音輸入..."
        self._launch_android_speech()

    def stop_recording(self):
        pass

    def _launch_android_speech(self):
        from jnius import autoclass, cast
        from android.runnable import run_on_ui_thread

        @run_on_ui_thread
        def launch():
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')

            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "zh-TW")
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "請說話...")

            currentActivity = cast('android.app.Activity', PythonActivity.mActivity)
            currentActivity.startActivityForResult(intent, 1001)

        launch()

    def on_activity_result(self, request_code, result_code, intent):
        if request_code == 1001 and result_code == -1 and intent:
            from jnius import autoclass
            results = intent.getStringArrayListExtra("android.speech.extra.RESULTS")
            if results and len(results) > 0:
                text = results.get(0)
                if self.app:
                    self.app.status_label.text = f"語音辨識：{text}"
                if self.callback:
                    self.callback(text)
