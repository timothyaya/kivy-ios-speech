# kivy-ios-speech

1. create speechbridge.m / speechbridge.h in xcode

   add -fobjc-arc into compilerflags of speechbridge.m:
   
   build phases -> compile resources -> double click speechbridge.m -> add -fobjc-arc
   
   if this step is not done, an error "Cannot create __weak reference in file using manual reference counting" occures
   
3. update project-info.plist:
```
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for recording and voice control.</string>
<key>NSSpeechRecognitionUsageDescription</key>
<string>This app needs speech recognition to interpret your commands.</string>
```
3. add python code :

   import:
```
if platform == 'android':
    from speechrecorder_android import SpeechRecorder_android
if platform == 'ios':
    from speechrecorder_ios import SpeechRecorder_ios
if platform == 'win':
    from speechrecorder_win import SpeechRecorder_win
```
   code in build:
```
        self.recorder = None
        if platform == 'win':
            self.recorder = SpeechRecorder_win(callback=self._handle_text_command)
        if platform == 'win':
            self.recorder = SpeechRecorder_win(callback=self._handle_text_command)
        elif platform == 'android':
            self.recorder = SpeechRecorder_android(callback=self._handle_text_command)
            self.recorder.set_app(self)
        elif platform == 'ios':
            self.recorder = SpeechRecorder_ios(callback=self._handle_text_command)
            self.recorder.set_app(self)
```
   bind button:
```
        self.record_button.bind(on_touch_down=self.start_recording)
        self.record_button.bind(on_touch_up=self.stop_recording)
```
  handle to gpt: 
```
    def _handle_text_command(self, text):
        command = self.get_command_from_gpt(text)
        if command:
            self.status_label.text = f"指令：{command}"
            self.send_command_to_esp(command)
```
  gpt code: openai api can't be used in buildozer, use requests
```
    def get_command_from_gpt(self, text):
        prompt = """
             your prompt
"""
        try:
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2
            }

            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

            if response.status_code == 200:
                reply = response.json()["choices"][0]["message"]["content"]
                try:
                    return json.loads(reply)
                except json.JSONDecodeError:
                    return None
            else:
                return None
        except Exception as e:
            return None
```
  send to esp:
```
    def send_command_to_esp(self, command):
        if self.udp.udp_ip == "":
            return
        esp_ip = f"http://{self.udp.udp_ip}:8080" 
        device = command.get("device")
        action = command.get("action")
        if device and action:
            url = f"{esp_ip}/{device}/{action}"


            try:
                r = requests.get(url)
            except Exception as e:
                print("ESP error：", e)
```
