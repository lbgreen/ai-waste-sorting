#import <AVFoundation/AVFoundation.h>
#import <Foundation/Foundation.h>
int main(void) { @autoreleasepool { NSArray *devices = [[AVCaptureDevice devicesWithMediaType:AVMediaTypeVideo] arrayByAddingObjectsFromArray:[AVCaptureDevice devicesWithMediaType:AVMediaTypeMuxed]]; devices=[devices sortedArrayUsingComparator:^NSComparisonResult(AVCaptureDevice *a,AVCaptureDevice *b){return [a.uniqueID compare:b.uniqueID];}]; for (NSUInteger i=0;i<devices.count;i++) { AVCaptureDevice *d=devices[i]; printf("%lu: %s\n",(unsigned long)i,d.localizedName.UTF8String); } } return 0; }
