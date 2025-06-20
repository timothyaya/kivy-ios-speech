# kivy-ios-speech

1. create speechbridge.m / speechbridge.h in xcode
   
2. update project-info.plist:
```
<key>NSMicrophoneUsageDescription</key>
<string>This app needs microphone access for recording and voice control.</string>
<key>NSSpeechRecognitionUsageDescription</key>
<string>This app needs speech recognition to interpret your commands.</string>
```
3. add python code : see files 
