#import "SpeechBridge.h"
#import <AVFoundation/AVFoundation.h>
#import <Speech/Speech.h>

@interface SpeechBridge ()
@property (nonatomic, strong) AVAudioEngine *audioEngine;
@property (nonatomic, strong) SFSpeechRecognizer *speechRecognizer;
@property (nonatomic, strong) SFSpeechAudioBufferRecognitionRequest *recognitionRequest;
@property (nonatomic, strong) SFSpeechRecognitionTask *recognitionTask;
@property (nonatomic, assign) BOOL recognitionDone;
@end

@implementation SpeechBridge

+ (instancetype)shared {
    static SpeechBridge *sharedInstance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        sharedInstance = [[SpeechBridge alloc] init];
    });
    return sharedInstance;
}

- (void)startRecognition {
    NSLog(@"🚀 開始辨識流程");
    self.recognitionDone = NO;

    self.audioEngine = [[AVAudioEngine alloc] init];
    self.speechRecognizer = [[SFSpeechRecognizer alloc] initWithLocale:[NSLocale localeWithLocaleIdentifier:@"zh-TW"]];
    self.recognitionRequest = [[SFSpeechAudioBufferRecognitionRequest alloc] init];

    NSError *error = nil;

    [[AVAudioSession sharedInstance] setCategory:AVAudioSessionCategoryPlayAndRecord error:&error];
    [[AVAudioSession sharedInstance] setMode:AVAudioSessionModeMeasurement error:&error];
    [[AVAudioSession sharedInstance] setActive:YES withOptions:AVAudioSessionSetActiveOptionNotifyOthersOnDeactivation error:&error];

    AVAudioInputNode *inputNode = self.audioEngine.inputNode;
    if (!inputNode) {
        NSLog(@"❌ 無法取得輸入裝置");
        return;
    }

    self.recognitionRequest.shouldReportPartialResults = NO;

    __weak typeof(self) weakSelf = self;
    self.recognitionTask = [self.speechRecognizer recognitionTaskWithRequest:self.recognitionRequest
                                                                   resultHandler:^(SFSpeechRecognitionResult * _Nullable result, NSError * _Nullable error) {
        if (result) {
            NSString *transcription = result.bestTranscription.formattedString;
            NSLog(@"✅ 辨識成功：%@", transcription);
            [weakSelf writeResultToFile:transcription];
        }

        if (error || result.isFinal) {
            [weakSelf.audioEngine stop];
            [inputNode removeTapOnBus:0];
            weakSelf.recognitionRequest = nil;
            weakSelf.recognitionTask = nil;
            weakSelf.recognitionDone = YES;

            if (error) {
                NSLog(@"❌ 語音辨識錯誤：%@", error.localizedDescription);
            }
        }
    }];

    AVAudioFormat *recordingFormat = [inputNode outputFormatForBus:0];
    [inputNode installTapOnBus:0 bufferSize:1024 format:recordingFormat
                         block:^(AVAudioPCMBuffer * _Nonnull buffer, AVAudioTime * _Nonnull when) {
        [weakSelf.recognitionRequest appendAudioPCMBuffer:buffer];
    }];

    [self.audioEngine prepare];
    [self.audioEngine startAndReturnError:&error];
    if (error) {
        NSLog(@"❌ 錄音啟動失敗：%@", error.localizedDescription);
    } else {
        NSLog(@"✅ audioEngine 啟動成功，開始錄音...");
    }
}

- (void)stopRecognition {
    NSLog(@"🛑 使用者停止說話");
    if (self.audioEngine.running) {
        [self.audioEngine stop];
        [self.recognitionRequest endAudio];
    }
}

- (BOOL)isRecognitionDone {
    return self.recognitionDone;
}

- (void)writeResultToFile:(NSString *)result {
    NSString *docsDir = [NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES) firstObject];
    NSString *filePath = [docsDir stringByAppendingPathComponent:@"result.txt"];
    NSError *error = nil;
    [result writeToFile:filePath atomically:YES encoding:NSUTF8StringEncoding error:&error];
    if (error) {
        NSLog(@"❌ 寫入結果檔案錯誤：%@", error.localizedDescription);
    } else {
        NSLog(@"📄 結果已儲存至：%@", filePath);
    }
}

@end
