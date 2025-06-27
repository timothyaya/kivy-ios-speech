#import <Foundation/Foundation.h>
#import <Speech/Speech.h>

@interface SpeechBridge : NSObject <SFSpeechRecognizerDelegate>

+ (instancetype)shared;
- (void)startRecognition;
- (void)reset;
- (BOOL)isRecognitionDone;

@end
