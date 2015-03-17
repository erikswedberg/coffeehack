/**
 * DeviceDetailViewController.m
 * MetaWearApiTest
 *
 * Created by Stephen Schiffli on 7/30/14.
 * Copyright 2014 MbientLab Inc. All rights reserved.
 *
 * IMPORTANT: Your use of this Software is limited to those specific rights
 * granted under the terms of a software license agreement between the user who
 * downloaded the software, his/her employer (which must be your employer) and
 * MbientLab Inc, (the "License").  You may not use this Software unless you
 * agree to abide by the terms of the License which can be found at
 * www.mbientlab.com/terms . The License limits your use, and you acknowledge,
 * that the  Software may not be modified, copied or distributed and can be used
 * solely and exclusively in conjunction with a MbientLab Inc, product.  Other
 * than for the foregoing purpose, you may not use, reproduce, copy, prepare
 * derivative works of, modify, distribute, perform, display or sell this
 * Software and/or its documentation for any purpose.
 *
 * YOU FURTHER ACKNOWLEDGE AND AGREE THAT THE SOFTWARE AND DOCUMENTATION ARE
 * PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED,
 * INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, TITLE,
 * NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT SHALL
 * MBIENTLAB OR ITS LICENSORS BE LIABLE OR OBLIGATED UNDER CONTRACT, NEGLIGENCE,
 * STRICT LIABILITY, CONTRIBUTION, BREACH OF WARRANTY, OR OTHER LEGAL EQUITABLE
 * THEORY ANY DIRECT OR INDIRECT DAMAGES OR EXPENSES INCLUDING BUT NOT LIMITED
 * TO ANY INCIDENTAL, SPECIAL, INDIRECT, PUNITIVE OR CONSEQUENTIAL DAMAGES, LOST
 * PROFITS OR LOST DATA, COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY,
 * SERVICES, OR ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT LIMITED TO ANY
 * DEFENSE THEREOF), OR OTHER SIMILAR COSTS.
 *
 * Should you have any questions regarding your right to use this Software,
 * contact MbientLab Inc, at www.mbientlab.com.
 */

#import "DeviceDetailViewController.h"
#import "MBProgressHUD.h"
#import "APLGraphView.h"
#import <math.h>

@interface DeviceDetailViewController () <MFMailComposeViewControllerDelegate>
@property (weak, nonatomic) IBOutlet UIScrollView *scrollView;
@property (weak, nonatomic) IBOutlet UISwitch *connectionSwitch;
@property (weak, nonatomic) IBOutlet UILabel *tempratureLabel;

@property (weak, nonatomic) IBOutlet UISegmentedControl *accelerometerScale;
@property (weak, nonatomic) IBOutlet UISegmentedControl *sampleFrequency;
@property (weak, nonatomic) IBOutlet UISwitch *highPassFilterSwitch;
@property (weak, nonatomic) IBOutlet UISegmentedControl *hpfCutoffFreq;
@property (weak, nonatomic) IBOutlet UISwitch *lowNoiseSwitch;
@property (weak, nonatomic) IBOutlet UISegmentedControl *activePowerScheme;
@property (weak, nonatomic) IBOutlet UISwitch *autoSleepSwitch;
@property (weak, nonatomic) IBOutlet UISegmentedControl *sleepSampleFrequency;
@property (weak, nonatomic) IBOutlet UISegmentedControl *sleepPowerScheme;
@property (weak, nonatomic) IBOutlet UISegmentedControl *tapDetectionAxis;
@property (weak, nonatomic) IBOutlet UISegmentedControl *tapDetectionType;

@property (weak, nonatomic) IBOutlet APLGraphView *accelerometerGraph;
@property (weak, nonatomic) IBOutlet UILabel *tapLabel;
@property (nonatomic) int tapCount;
@property (weak, nonatomic) IBOutlet UILabel *shakeLabel;
@property (nonatomic) int shakeCount;
@property (weak, nonatomic) IBOutlet UILabel *orientationLabel;

@property (weak, nonatomic) IBOutlet UILabel *mechanicalSwitchLabel;
@property (weak, nonatomic) IBOutlet UILabel *batteryLevelLabel;
@property (weak, nonatomic) IBOutlet UILabel *rssiLevelLabel;
@property (weak, nonatomic) IBOutlet UITextField *hapticPulseWidth;
@property (weak, nonatomic) IBOutlet UITextField *hapticDutyCycle;
@property (weak, nonatomic) IBOutlet UISegmentedControl *gpioPinSelector;
@property (weak, nonatomic) IBOutlet UILabel *gpioPinDigitalValue;
@property (weak, nonatomic) IBOutlet UILabel *gpioPinAnalogValue;

@property (weak, nonatomic) IBOutlet UIButton *startAccelerometer;
@property (weak, nonatomic) IBOutlet UIButton *stopAccelerometer;
@property (weak, nonatomic) IBOutlet UIButton *startLog;
@property (weak, nonatomic) IBOutlet UIButton *stopLog;
@property (weak, nonatomic) IBOutlet UIButton *startTap;
@property (weak, nonatomic) IBOutlet UIButton *stopTap;
@property (weak, nonatomic) IBOutlet UIButton *startShake;
@property (weak, nonatomic) IBOutlet UIButton *stopShake;
@property (weak, nonatomic) IBOutlet UIButton *startOrientation;
@property (weak, nonatomic) IBOutlet UIButton *stopOrientation;

@property (weak, nonatomic) IBOutlet UILabel *mfgNameLabel;
@property (weak, nonatomic) IBOutlet UILabel *serialNumLabel;
@property (weak, nonatomic) IBOutlet UILabel *hwRevLabel;
@property (weak, nonatomic) IBOutlet UILabel *fwRevLabel;

@property (weak, nonatomic) IBOutlet UILabel *firmwareUpdateLabel;

@property (strong, nonatomic) UIView *grayScreen;
@property (strong, nonatomic) NSArray *accelerometerDataArray;
@property (nonatomic) BOOL accelerometerRunning;
@property (nonatomic) BOOL switchRunning;
@property (strong, nonatomic) MBLNeopixelStrand* potLights;
@end

@implementation DeviceDetailViewController
@synthesize inputStream, outputStream;

int strandLength = 24;
float lightBright = 1.0;
float lightSaturation = 1.0;
float lightHue = 0.0;
float minTemp = 76.0f;
float maxTemp = 108.0f;
float curTemp = 0.0;

- (void)viewDidLoad
{
    [super viewDidLoad];
    
    self.grayScreen = [[UIView alloc] initWithFrame:CGRectMake(0, 120, self.view.frame.size.width, self.view.frame.size.height - 120)];
    self.grayScreen.backgroundColor = [UIColor grayColor];
    self.grayScreen.alpha = 0.4;
    [self.view addSubview:self.grayScreen];
    
    [self.stopAccelerometer setEnabled:NO];
    [self.stopLog setEnabled:NO];
    
    [self initNetworkCommunication];
    messages = [[NSMutableArray alloc] init];
}

- (void)viewWillAppear:(BOOL)animated
{
    [super viewWillAppear:animated];
    
    [self.device addObserver:self forKeyPath:@"state" options:NSKeyValueObservingOptionNew context:nil];
    [self connectDevice:YES];
}

- (void)viewWillDisappear:(BOOL)animated
{
    [_potLights turnStrandOff];     // turn off LEDs
    
    [super viewWillDisappear:animated];
    
    [self.device removeObserver:self forKeyPath:@"state"];

    if (self.accelerometerRunning) {
        [self stopAccelerationPressed:nil];
    }
    if (self.switchRunning) {
        [self StopSwitchNotifyPressed:nil];
    }
}

- (void)observeValueForKeyPath:(NSString *)keyPath ofObject:(id)object change:(NSDictionary *)change context:(void *)context
{
    if (self.device.state == CBPeripheralStateDisconnected) {
        [[NSOperationQueue mainQueue] addOperationWithBlock:^{
            [self setConnected:NO];
            [self.scrollView scrollRectToVisible:CGRectMake(0, 0, 10, 10) animated:YES];
        }];
    }
}

- (void)initNetworkCommunication {
    CFReadStreamRef readStream;
    CFWriteStreamRef writeStream;
    CFStreamCreatePairWithSocketToHost(NULL, (CFStringRef)@"10.90.2.142", 8008, &readStream, &writeStream);
    inputStream = (NSInputStream *)CFBridgingRelease(readStream);
    outputStream = (NSOutputStream *)CFBridgingRelease(writeStream);
    [inputStream setDelegate:self];
    [outputStream setDelegate:self];
    [inputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [outputStream scheduleInRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
    [inputStream open];
    [outputStream open];
    NSLog(@"opening stream");
    
}

- (void)stream:(NSStream *)theStream handleEvent:(NSStreamEvent)streamEvent {
    NSLog(@"stream event %i", streamEvent);
    switch (streamEvent) {
            
        case NSStreamEventOpenCompleted:
            NSLog(@"Stream opened");
            break;
            
        case NSStreamEventErrorOccurred:
            NSLog(@"Can not connect to the host!");
            break;
            
        case NSStreamEventEndEncountered:
            [theStream close];
            [theStream removeFromRunLoop:[NSRunLoop currentRunLoop] forMode:NSDefaultRunLoopMode];
            break;
            
        case NSStreamEventHasBytesAvailable:
            
            if (theStream == inputStream) {
                
                uint8_t buffer[1024];
                int len;
                
                while ([inputStream hasBytesAvailable]) {
                    len = [inputStream read:buffer maxLength:sizeof(buffer)];
                    if (len > 0) {
                        
                        NSString *output = [[NSString alloc] initWithBytes:buffer length:len encoding:NSASCIIStringEncoding];
                        
                        if (nil != output) {
                            NSLog(@"server said: %@", output);
                            NSArray *array = [output componentsSeparatedByString:@":"];
                            NSLog(@"%@", array);
                            if([array[0]  isEqual: @"bright"]) {
                                lightBright = [array[1] floatValue];
                                NSLog(@"new brightness value: %f", lightBright);
                                [self updateStrand];
                            }
                            else if([array[0]  isEqual: @"saturation"]) {
                                lightSaturation = [array[1] floatValue];
                                NSLog(@"new saturation value: %f", lightSaturation);
                                [self updateStrand];
                            }
                            else if([array[0]  isEqual: @"hue"]) {
                                lightHue = [array[1] floatValue];
                                NSLog(@"new hue value: %f", lightHue);
                                [self updateStrand];
                            }
                            else if([array[0]  isEqual: @"lowTemp"]) {
                                minTemp = [array[1] floatValue];
                                NSLog(@"new min temp: %f", minTemp);
                                [self updateStrand];
                            }
                            else if([array[0]  isEqual: @"highTemp"]) {
                                maxTemp = [array[1] floatValue];
                                NSLog(@"new max temp: %f", maxTemp);
                                [self updateStrand];
                            }
                            else if([array[0]  isEqual: @"pollTemp"]) {
                                NSLog(@"polling temp sensor");
                                [self readTempraturePressed:nil];
                            }
                            else if([array[0]  isEqual: @"setTemp"]) {
                                float fakeTemp = [array[1] floatValue];
                                NSLog(@"faking temp data %f", fakeTemp);
                                
                            }
                            else if([array[0]  isEqual: @"updateStrand"]) {
                                [self updateStrand];
                            }
                            else if([array[0]  isEqual: @"resetStrand"]) {
                                [_potLights rotateStrandWithDirection:MBLRotationDirectionAwayFromBoard repetitions:0 period:100];
                                [_potLights turnStrandOff];
                            }
                            else if([array[0]  isEqual: @"getTemp"]) {
                                [self pollCoffeeSensor];
                            }
                        }
                    }
                }
            }
            break;
            
        default:
            NSLog(@"Unknown event");
    }
}

- (void)pollCoffeeSensor {
    MBLGPIOPin *pinTemp = self.device.gpio.pins[1];
    [pinTemp.analogAbsolute readWithHandler:^(MBLNumericData *obj, NSError *error) {
        NSLog(@"Pin Voltage: %f mV", obj.value.floatValue);
        float temperatureC = (obj.value.floatValue - 0.5) * 100 ;
        float temperatureF = (temperatureC * 9.0 / 5.0) + 32.0;
        [self sendSocketMessage:@"temp" : [NSString stringWithFormat:@"%f", temperatureF] ];
        lightHue = [self normTemp:temperatureF];
        NSLog(@"new hue: %f", lightHue);
        curTemp = temperatureF;
    }];
}

- (void)updateServer {
    [self pollCoffeeSensor];
    [self sendTempToServer:curTemp];
    [self updateStrand];
}

// Initialize LED strand
- (MBLNeopixelStrand *)newStrand
{
    //const int length = 60;                              // How many LEDs in your NeoPixel stand
    const MBLColorOrdering color = MBLColorOrderingGBR;
    // RBG (low is blue, high green), RGB (low is red), GBR (low is blue, high is green), GRB (low is red, high blue)
    const MBLStrandSpeed speed = MBLStrandSpeedSlow;    // Fast or Slow
    MBLNeopixelStrand *strand = [self.device.neopixel strandWithColor:color speed:speed pin:0 length:strandLength];
    [strand rotateStrandWithDirection:MBLRotationDirectionAwayFromBoard repetitions:0 period:100];
    float twiddleStrength = 0.4;
    for (int i = 0; i < strandLength; i++) {
        float twiddle = 1-(twiddleStrength/2.0) + twiddleStrength * (float)rand() / RAND_MAX;
        UIColor *curColor = [UIColor colorWithHue:0.9*twiddle saturation:lightSaturation brightness:lightBright alpha:1.0];
        [strand setPixel:i color:curColor];
    }
    //[strand holdStrandWithEnable:true];
    [strand rotateStrandWithDirection:MBLRotationDirectionAwayFromBoard repetitions:0xff period:100];
    return strand;
}

// Called once view is available.
- (void)setConnected:(BOOL)on
{
    [self.connectionSwitch setOn:on animated:YES];
    [self.grayScreen setHidden:on];
    
    
    _potLights = [self newStrand];
    
    NSString *response  = [NSString stringWithFormat:@"iam:%@", @"pot"];
    NSData *data = [[NSData alloc] initWithData:[response dataUsingEncoding:NSASCIIStringEncoding]];
    [outputStream write:[data bytes] maxLength:[data length]];
    
    // poll temp sensor very N seconds
    [NSTimer scheduledTimerWithTimeInterval:15.0
                                     target:self
                                   selector:@selector(updateServer)
                                   userInfo:nil
                                    repeats:YES];
    
    // start notifying on internal temp change, unreliable
    NSLog(@"turning on temp change detection");
    self.device.temperature.units = MBLTemperatureUnitFahrenheit;
    self.device.temperature.samplePeriod = 500;
    self.device.temperature.delta = 0.2;
    [self.device.temperature.changeEvent startNotificationsWithHandler:^(MBLNumericData *obj, NSError *error) {
        // what to do when change detected
        float newVal = [self normTemp:obj.value.floatValue];
        NSLog(@"temp change: %f, mapped: %f", obj.value.floatValue, newVal);
        
        // change LED color one at a time
        [self.device.led setLEDColor:[UIColor redColor] withIntensity:newVal];
        int i = arc4random_uniform(strandLength);
        float twiddle = 1.0;//0.3 * (float)rand() / RAND_MAX;
        UIColor *curColor = [UIColor colorWithHue:newVal*twiddle saturation:lightSaturation brightness:lightBright alpha:1.0];
        //[_potLights setPixel:i color:curColor];
    }];
    
    // notify on shake, not working
    [self.device.accelerometer.shakeEvent startNotificationsWithHandler:^(id obj, NSError *error) {
        NSLog(@"shaken: %@", obj);
        [self sendSocketMessage:@"move" :[NSString stringWithFormat:@"%@", @"me"]];
    }];
}

- (void)connectDevice:(BOOL)on
{
    MBProgressHUD *hud = [MBProgressHUD showHUDAddedTo:self.view animated:YES];
    if (on) {
        hud.labelText = @"Connecting...";
        [self.device connectWithHandler:^(NSError *error) {
            [self setConnected:(error == nil)];
            hud.mode = MBProgressHUDModeText;
            if (error) {
                hud.labelText = error.localizedDescription;
                [hud hide:YES afterDelay:2];
            } else {
                hud.labelText = @"Connected!";
                [hud hide:YES afterDelay:0.5];
            }
        }];
    } else {
        hud.labelText = @"Disconnecting...";
        [self.device disconnectWithHandler:^(NSError *error) {
            [self setConnected:NO];
            hud.mode = MBProgressHUDModeText;
            if (error) {
                hud.labelText = error.localizedDescription;
                [hud hide:YES afterDelay:2];
            } else {
                hud.labelText = @"Disconnected!";
                [hud hide:YES afterDelay:0.5];
            }
        }];
    }
}

- (IBAction)connectionSwitchPressed:(id)sender
{
    [self connectDevice:self.connectionSwitch.on];
}


- (float)normTemp:(float)temp
{
    float maxOutput = 0.65;
    float newVal = maxOutput*(temp-minTemp)/(maxTemp-minTemp);
    if (newVal>1.0) {
        newVal = 1.0;
    }
    else if(newVal<0.0) {
        newVal = 0.0;
    }
    return newVal;
}

- (void)sendTempToServer:(float)temp {
    NSString *urlString = [NSString stringWithFormat:FIREBROW_BASE_URL];
    urlString = [urlString stringByAppendingString:[NSString stringWithFormat:@"?temp=%f", temp]];
    NSLog(@"%@", urlString);
    NSURL *url = [NSURL URLWithString:urlString];
    NSLog(@"%@", url);
    
    NSMutableURLRequest *request = [NSMutableURLRequest requestWithURL:url];
    [request setURL:url];
    [request setHTTPMethod:@"GET"];
    //[request setValue:@"application/json" forHTTPHeaderField:@"Content-Type"];
    NSError *getError;
    NSURLResponse *getResponse;
    NSData *getData = [NSURLConnection sendSynchronousRequest:request returningResponse:&getResponse error:&getError];
    NSLog(@"%@", getData);
}

- (IBAction)readTempraturePressed:(id)sender
{
    self.device.temperature.units = MBLTemperatureUnitFahrenheit;
    [self.device.temperature readTemperatureWithHandler:^(NSDecimalNumber *temp, NSError *error) {
        NSString *suffix = self.device.temperature.units == MBLTemperatureUnitCelsius ? @"°C" : @"°F";
        self.tempratureLabel.text = [[temp stringValue] stringByAppendingString:suffix];
        float newVal = [self normTemp:[temp floatValue]];
        NSLog(@"temp: %@, map: %f", temp, newVal);
        
        //[self sendTempToServer:temp];
        // adjust strand
        //[self updateStrand];
        
        
        [self sendSocketMessage:@"internal temp" :[NSString stringWithFormat:@"%@", temp]];
    }];
}

// send socket message
-(void)sendSocketMessage:(NSString*)label : (NSString*)data {
    NSString *socketResponse  = [NSString stringWithFormat:@"%@:%@", label, data];
    NSData *socketData = [[NSData alloc] initWithData:[socketResponse dataUsingEncoding:NSASCIIStringEncoding]];
    [outputStream write:[socketData bytes] maxLength:[socketData length]];
}

- (void)updateStrand {
    //[_potLights rotateStrandWithDirection:MBLRotationDirectionAwayFromBoard repetitions:0 period:0];
    for (int i = 0; i < strandLength; i++) {
        float twiddle = 0.3 * (float)rand() / RAND_MAX;     // little random spice
        UIColor *curColor = [UIColor colorWithHue:lightHue saturation:lightSaturation brightness:lightBright*twiddle alpha:1.0];
        [_potLights setPixel:i color:curColor];
    }
    //[_potLights rotateStrandWithDirection:MBLRotationDirectionAwayFromBoard repetitions:0xff period:100];
    //[strand turnStrandOff];
}

- (IBAction)turnOnGreenLEDPressed:(id)sender
{
    [self.device.led setLEDColor:[UIColor greenColor] withIntensity:0.25];
}
- (IBAction)flashGreenLEDPressed:(id)sender
{
    [self.device.led flashLEDColor:[UIColor greenColor] withIntensity:0.25];
}

- (IBAction)turnOnRedLEDPressed:(id)sender
{
    [self.device.led setLEDColor:[UIColor redColor] withIntensity:0.25];
}
- (IBAction)flashRedLEDPressed:(id)sender
{
    [self.device.led flashLEDColor:[UIColor redColor] withIntensity:0.25];
}

- (IBAction)turnOnBlueLEDPressed:(id)sender
{
    [self.device.led setLEDColor:[UIColor blueColor] withIntensity:0.25];
}
- (IBAction)flashBlueLEDPressed:(id)sender
{
    [self.device.led flashLEDColor:[UIColor blueColor] withIntensity:0.25];
}

- (IBAction)turnOffLEDPressed:(id)sender
{
    [self.device.led setLEDOn:NO withOptions:1];
}

- (IBAction)readSwitchPressed:(id)sender
{
    [self.device.mechanicalSwitch.switchValue readWithHandler:^(MBLNumericData *obj, NSError *error) {
        self.mechanicalSwitchLabel.text = obj.value.boolValue ? @"Down" : @"Up";
    }];
}

- (IBAction)startSwitchNotifyPressed:(id)sender
{
    self.switchRunning = YES;
    [self.device.mechanicalSwitch.switchUpdateEvent startNotificationsWithHandler:^(MBLNumericData *isPressed, NSError *error) {
        self.mechanicalSwitchLabel.text = isPressed.value.boolValue ? @"Down" : @"Up";
    }];
}

- (IBAction)StopSwitchNotifyPressed:(id)sender
{
    self.switchRunning = NO;
    [self.device.mechanicalSwitch.switchUpdateEvent stopNotifications];
}

- (IBAction)readBatteryPressed:(id)sender
{
    [self.device readBatteryLifeWithHandler:^(NSNumber *number, NSError *error) {
        self.batteryLevelLabel.text = [number stringValue];
    }];
}

- (IBAction)readRSSIPressed:(id)sender
{
    [self.device readRSSIWithHandler:^(NSNumber *number, NSError *error) {
        self.rssiLevelLabel.text = [number stringValue];
    }];
}

- (IBAction)readDeviceInfoPressed:(id)sender
{
    self.mfgNameLabel.text = self.device.deviceInfo.manufacturerName;
    self.serialNumLabel.text = self.device.deviceInfo.serialNumber;
    self.hwRevLabel.text = self.device.deviceInfo.hardwareRevision;
    self.fwRevLabel.text = self.device.deviceInfo.firmwareRevision;
}

- (IBAction)resetDevicePressed:(id)sender
{
    // Resetting causes a disconnection
    [self setConnected:NO];
    [self.device resetDevice];
}

- (IBAction)checkForFirmwareUpdatesPressed:(id)sender
{
    [self.device checkForFirmwareUpdateWithHandler:^(BOOL isTrue, NSError *error) {
        self.firmwareUpdateLabel.text = isTrue ? @"Avaliable!" : @"Up To Date";
    }];
}

- (IBAction)updateFirmware:(id)sender
{
    // Pause the screen while update is going on
    MBProgressHUD *hud = [MBProgressHUD showHUDAddedTo:self.view animated:YES];
    hud.mode = MBProgressHUDModeDeterminateHorizontalBar;
    hud.labelText = @"Updating...";
    
    [self.device updateFirmwareWithHandler:^(NSError *error) {
        hud.mode = MBProgressHUDModeText;
        if (error) {
            NSLog(@"Firmware update error: %@", error.localizedDescription);
            [[[UIAlertView alloc] initWithTitle:@"Update Error"
                                        message:[@"Please re-connect and try again, if you can't connect, try MetaBoot Mode to recover.\nError: " stringByAppendingString:error.localizedDescription]
                                       delegate:nil
                              cancelButtonTitle:@"Okay"
                              otherButtonTitles:nil] show];
            [hud hide:YES];
        } else {
            hud.labelText = @"Success!";
            [hud hide:YES afterDelay:2.0];
        }
    } progressHandler:^(float number, NSError *error) {
        if (number != hud.progress) {
            hud.progress = number;
            if (number == 1.0) {
                hud.mode = MBProgressHUDModeIndeterminate;
                hud.labelText = @"Resetting...";
            }
        }
    }];
}

- (IBAction)startHapticDriverPressed:(id)sender
{
    uint8_t dcycle = [self.hapticDutyCycle.text intValue];
    uint16_t pwidth = [self.hapticPulseWidth.text intValue];
    [self.device.hapticBuzzer startHapticWithDutyCycle:dcycle pulseWidth:pwidth completion:nil];
}

- (IBAction)startiBeaconPressed:(id)sender
{
    [self.device.iBeacon setBeaconOn:YES];
}

- (IBAction)stopiBeaconPressed:(id)sender
{
    [self.device.iBeacon setBeaconOn:NO];
}

- (IBAction)setPullUpPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    pin.configuration = MBLPinConfigurationPullup;
}
- (IBAction)setPullDownPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    pin.configuration = MBLPinConfigurationPulldown;
}
- (IBAction)setNoPullPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    pin.configuration = MBLPinConfigurationNopull;
}
- (IBAction)setPinPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    [pin setToDigitalValue:YES];
}
- (IBAction)clearPinPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    [pin setToDigitalValue:NO];
}
- (IBAction)readDigitalPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    [pin.digitalValue readWithHandler:^(MBLNumericData *obj, NSError *error) {
        self.gpioPinDigitalValue.text = obj.value.boolValue ? @"1" : @"0";
    }];
}
- (IBAction)readAnalogPressed:(id)sender
{
    MBLGPIOPin *pin = self.device.gpio.pins[self.gpioPinSelector.selectedSegmentIndex];
    [pin.analogAbsolute readWithHandler:^(MBLNumericData *obj, NSError *error) {
        self.gpioPinAnalogValue.text = [NSString stringWithFormat:@"%.3fV", obj.value.doubleValue];
    }];
}

- (void)updateAccelerometerSettings
{
    if (self.accelerometerScale.selectedSegmentIndex == 0) {
        self.accelerometerGraph.fullScale = 2;
    } else if (self.accelerometerScale.selectedSegmentIndex == 1) {
        self.accelerometerGraph.fullScale = 4;
    } else {
        self.accelerometerGraph.fullScale = 8;
    }
    
    self.device.accelerometer.fullScaleRange = (int)self.accelerometerScale.selectedSegmentIndex;
    self.device.accelerometer.sampleFrequency = (int)self.sampleFrequency.selectedSegmentIndex;
    self.device.accelerometer.highPassFilter = self.highPassFilterSwitch.on;
    self.device.accelerometer.filterCutoffFreq = self.hpfCutoffFreq.selectedSegmentIndex;
    self.device.accelerometer.lowNoise = self.lowNoiseSwitch.on;
    self.device.accelerometer.activePowerScheme = (int)self.activePowerScheme.selectedSegmentIndex;
    self.device.accelerometer.autoSleep = self.autoSleepSwitch.on;
    self.device.accelerometer.sleepSampleFrequency = (int)self.sleepSampleFrequency.selectedSegmentIndex;
    self.device.accelerometer.sleepPowerScheme = (int)self.sleepPowerScheme.selectedSegmentIndex;
    self.device.accelerometer.tapDetectionAxis = (int)self.tapDetectionAxis.selectedSegmentIndex;
    self.device.accelerometer.tapType = (int)self.tapDetectionType.selectedSegmentIndex;
}

- (IBAction)startAccelerationPressed:(id)sender
{
    [self updateAccelerometerSettings];
    
    [self.startAccelerometer setEnabled:NO];
    [self.stopAccelerometer setEnabled:YES];
    [self.startLog setEnabled:NO];
    [self.stopLog setEnabled:NO];
    self.accelerometerRunning = YES;
    // These variables are used for data recording
    NSMutableArray *array = [[NSMutableArray alloc] initWithCapacity:1000];
    self.accelerometerDataArray = array;
    
    [self.device.accelerometer.dataReadyEvent startNotificationsWithHandler:^(MBLAccelerometerData *acceleration, NSError *error) {
        [self.accelerometerGraph addX:(float)acceleration.x / 1000.0 y:(float)acceleration.y / 1000.0 z:(float)acceleration.z / 1000.0];
        // Add data to data array for saving
        [array addObject:acceleration];
    }];
}

- (IBAction)stopAccelerationPressed:(id)sender
{
    [self.device.accelerometer.dataReadyEvent stopNotifications];
    self.accelerometerRunning = NO;

    [self.startAccelerometer setEnabled:YES];
    [self.stopAccelerometer setEnabled:NO];
    [self.startLog setEnabled:YES];
}

- (IBAction)startAccelerometerLog:(id)sender
{
    [self updateAccelerometerSettings];
    
    [self.startLog setEnabled:NO];
    [self.stopLog setEnabled:YES];
    [self.startAccelerometer setEnabled:NO];
    [self.stopAccelerometer setEnabled:NO];
    
    [self.device.accelerometer.dataReadyEvent startLogging];
}

- (IBAction)stopAccelerometerLog:(id)sender
{
    MBProgressHUD *hud = [MBProgressHUD showHUDAddedTo:self.view animated:YES];
    hud.mode = MBProgressHUDModeDeterminateHorizontalBar;
    hud.labelText = @"Downloading...";
    
    [self.device.accelerometer.dataReadyEvent downloadLogAndStopLogging:YES handler:^(NSArray *array, NSError *error) {
        [hud hide:YES];
        if (!error) {
            self.accelerometerDataArray = array;
            for (MBLAccelerometerData *acceleration in array) {
                [self.accelerometerGraph addX:(float)acceleration.x / 1000.0 y:(float)acceleration.y / 1000.0 z:(float)acceleration.z / 1000.0];
            }
        }
    } progressHandler:^(float number, NSError *error) {
        hud.progress = number;
    }];
    [self.stopLog setEnabled:NO];
    [self.startLog setEnabled:YES];
    [self.startAccelerometer setEnabled:YES];
}


- (IBAction)sendDataPressed:(id)sender
{
    NSMutableData *accelerometerData = [NSMutableData data];
    for (MBLAccelerometerData *dataElement in self.accelerometerDataArray) {
        @autoreleasepool {
            [accelerometerData appendData:[[NSString stringWithFormat:@"%f,%d,%d,%d\n",
                                            dataElement.timestamp.timeIntervalSince1970,
                                            dataElement.x,
                                            dataElement.y,
                                            dataElement.z] dataUsingEncoding:NSUTF8StringEncoding]];
        }
    }
    [self sendMail:accelerometerData];
}

- (void)sendMail:(NSData *)attachment
{
    if (![MFMailComposeViewController canSendMail]) {
        [[[UIAlertView alloc] initWithTitle:@"Mail Error" message:@"This device does not have an email account setup" delegate:nil cancelButtonTitle:@"Okay" otherButtonTitles:nil] show];
        return;
    }

    // Get current Time/Date
    NSDateFormatter *dateFormatter = [[NSDateFormatter alloc] init];
    [dateFormatter setTimeStyle:NSDateFormatterLongStyle];
    [dateFormatter setDateStyle:NSDateFormatterShortStyle];
    
    // Some filesystems hate colons
    NSString *dateString = [[dateFormatter stringFromDate:[NSDate date]] stringByReplacingOccurrencesOfString:@":" withString:@"_"];
    // I hate spaces in dates
    dateString = [dateString stringByReplacingOccurrencesOfString:@" " withString:@"_"];
    // OS hates forward slashes
    dateString = [dateString stringByReplacingOccurrencesOfString:@"/" withString:@"_"];
    
    MFMailComposeViewController *emailController = [[MFMailComposeViewController alloc] init];
    emailController.mailComposeDelegate = self;
    
    // attachment
    NSString *name = [NSString stringWithFormat:@"AccData_%@.txt", dateString, nil];
    [emailController addAttachmentData:attachment mimeType:@"text/plain" fileName:name];
    
    // subject
    NSString *subject = [NSString stringWithFormat:@"Accelerometer Data %@.txt", dateString, nil];
    [emailController setSubject:subject];
    
    NSMutableString *body = [[NSMutableString alloc] initWithFormat:@"The data was recorded on %@.\n", dateString];
    [body appendString:[NSString stringWithFormat:@"Scale = %d\n", (int)self.accelerometerScale.selectedSegmentIndex]];
    [body appendString:[NSString stringWithFormat:@"Freq = %d\n", (int)self.sampleFrequency.selectedSegmentIndex]];
    [body appendString:[NSString stringWithFormat:@"HPF On = %d\n", (int)self.highPassFilterSwitch.on]];
    [body appendString:[NSString stringWithFormat:@"HPF Cutoff = %d\n", (int)self.hpfCutoffFreq.selectedSegmentIndex]];
    [body appendString:[NSString stringWithFormat:@"LowNoise On = %d\n", self.lowNoiseSwitch.on]];
    [body appendString:[NSString stringWithFormat:@"Active Power Scheme = %d\n", (int)self.activePowerScheme.selectedSegmentIndex]];
    [body appendString:[NSString stringWithFormat:@"Auto Sleep On = %d\n", self.autoSleepSwitch.on]];
    [body appendString:[NSString stringWithFormat:@"SleepFreq = %d\n", (int)self.sleepSampleFrequency.selectedSegmentIndex]];
    [body appendString:[NSString stringWithFormat:@"Sleep Power Scheme = %d\n", (int)self.sleepPowerScheme.selectedSegmentIndex]];
    [emailController setMessageBody:body isHTML:NO];
    
    [self presentViewController:emailController animated:YES completion:NULL];
}

-(void)mailComposeController:(MFMailComposeViewController*)controller didFinishWithResult:(MFMailComposeResult)result error:(NSError*)error
{
    [self dismissViewControllerAnimated:YES completion:nil];
}

- (IBAction)startTapPressed:(id)sender
{
    [self.startTap setEnabled:NO];
    [self.stopTap setEnabled:YES];
    
    [self updateAccelerometerSettings];
    [self.device.accelerometer.tapEvent startNotificationsWithHandler:^(id obj, NSError *error) {
        self.tapLabel.text = [NSString stringWithFormat:@"Tap Count: %d", ++self.tapCount];
    }];
}

- (IBAction)stopTapPressed:(id)sender
{
    [self.startTap setEnabled:YES];
    [self.stopTap setEnabled:NO];
    
    [self.device.accelerometer.tapEvent stopNotifications];
    self.tapCount = 0;
    self.tapLabel.text = @"Tap Count: 0";
}

- (IBAction)startShakePressed:(id)sender
{
    [self.startShake setEnabled:NO];
    [self.stopShake setEnabled:YES];
    
    [self updateAccelerometerSettings];
    [self.device.accelerometer.shakeEvent startNotificationsWithHandler:^(id obj, NSError *error) {
        self.shakeLabel.text = [NSString stringWithFormat:@"Shakes: %d", ++self.shakeCount];
    }];
}

- (IBAction)stopShakePressed:(id)sender
{
    [self.startShake setEnabled:YES];
    [self.stopShake setEnabled:NO];
    
    [self.device.accelerometer.shakeEvent stopNotifications];
    self.shakeCount = 0;
    self.shakeLabel.text = @"Shakes: 0";
}

- (IBAction)startOrientationPressed:(id)sender
{
    [self.startOrientation setEnabled:NO];
    [self.stopOrientation setEnabled:YES];
    
    [self updateAccelerometerSettings];
    [self.device.accelerometer.orientationEvent startNotificationsWithHandler:^(id obj, NSError *error) {
        MBLOrientationData *data = obj;
        switch (data.orientation) {
            case MBLAccelerometerOrientationPortrait:
                self.orientationLabel.text = @"Portrait";
                break;
            case MBLAccelerometerOrientationPortraitUpsideDown:
                self.orientationLabel.text = @"PortraitUpsideDown";
                break;
            case MBLAccelerometerOrientationLandscapeLeft:
                self.orientationLabel.text = @"LandscapeLeft";
                break;
            case MBLAccelerometerOrientationLandscapeRight:
                self.orientationLabel.text = @"LandscapeRight";
                break;
        }
    }];
}

- (IBAction)stopOrientationPressed:(id)sender
{
    [self.startOrientation setEnabled:YES];
    [self.stopOrientation setEnabled:NO];
    
    [self.device.accelerometer.orientationEvent stopNotifications];
    self.orientationLabel.text = @"XXXXXXXXXXXXXX";
}

@end
