// LED driver program for the Groovik's Cube. 
// written by Mars, summer 2009.



// BOARD CONFIGURATION
// Each board must have a unique ID, so the central computer can map boards to faces. There is no way
// for the boards to do this on their own, so you must change this ID before flashing each dimmer board.
const byte kGuid = 'L' - 'A' + 1;

// For demo purposes, we will connect some common-cathode RGB LEDs to the arduino boards. To control these
// we must invert our signal: LOW to light the LED and HIGH to switch it off, the opposite of what the
// TTL power modules expect. Make sure to set this false on a release build.
#define LED_MODE false

// For further demo assistance, and general entertainment value, this board will run a simple sine-wave
// color fade in its main loop. This is not really what we want on the actual cube, so you should 
// disable this setting for release builds.
#define DEMO_MODE false
#if DEMO_MODE
boolean sDisableDemo = false;
#endif




// This program drives an array of LED power modules, rendering groups of three LEDs as 24-bit pixels.
// We will accept commands via serial, setting the brightness level for each channel. This program's
// job is to toggle each IO pin high and low at the correct intervals such that the ratio of time 
// spent in power and rest states yields the desired brightness.
const unsigned int kChannels = 15;
const unsigned int kPixels = 5;
const unsigned int kLevels = 256;

// Every message must begin with a synchronization byte and end with a checksum byte. The synchronization
// value is arbitrary. This value is also used to seed the checksum value.
const byte kSyncValue = 0x69;

struct color_t
{
  byte red;
  byte green;
  byte blue;
};

// We will periodically echo our current state back to the central computer. It will check our state
// against its expectations and reissue commands if we are in the wrong state. This struct defines the
// message format, not including the sync header or the checksum footer.
struct state_t
{
  byte guid;
  byte powermodule1;
  byte powermodule2;
  byte latency;
  color_t pixels[kPixels];
} globalstate;

// Additional state, used while lerping: what is the current level of each channel?
byte channels[kChannels];

// We'll use this timer to decide when next to send our status upstream.
long sNextState;
const int kUpdateInterval = 500; // milliseconds
const int kResponseInterval = 10;

// We expect update commands from the central computer, containing new state data.
// Preceded by a sync and followed by a checksum, this struct is the message format.
// Lerp_duration is in 4-millisecond units (thus roughly, 1/256 of a second).
struct command_t
{
  byte lerp_duration;
  color_t pixels[kPixels];
};

bool sFading;
long sFaderBegin;
long sFaderEnd;
const int kFaderInterval = 4; // milliseconds

// IO updates are driven by an interrupt timer, which will keep track of the current time and the
// brightness level that corresponds to that time. It will set IO state by blitting the contents of these
// state arrays to the IO ports that control the LED pins. The control system must therefore set brightness
// by making sure the bit corresponding to each channel is set for all states below the target brightness,
// and cleared for all states from the target through the end of the cycle.
// The size of this structure is extremely important: the AVR only has 2K of RAM, and at 6 bytes per entry
// this table already uses up 1.5K. If you add any more fields, look into the PROGMEM option - it may be
// possible to put this table in flash memory instead of SRAM.
struct brightness_t
{
  // Which IO ports should be active during this brightness level?
  byte stateD;
  byte stateB;
  byte stateC;
  // How long does the power phase of this level last?
  unsigned int duration;
  // How many ticks from now will the next interrupt occur?
  byte clockIncrement;
}; 

brightness_t levels[kLevels];
brightness_t *interruptLevel;

unsigned int cycleTime;
const byte kTimerMinimum = 96;
const byte kTimerMaximum = 255;
const unsigned int kCycleDuration = 65025;

// ----------------

// The interrupt routine fires every time the timer's count register overflows.
// Just entering this routine appears to consume at least 32 ticks.
ISR(TIMER2_OVF_vect) 
{
  if (cycleTime >= interruptLevel->duration) {
    // Move to the next brightness level
    if (cycleTime < kCycleDuration) {
      interruptLevel++;
    } else {
      interruptLevel = levels;
    }
  }
  // Blit the current brightness level state to our IO ports.
  PORTD = (PORTD & 0x03) | interruptLevel->stateD;
  PORTB = (PORTB & 0xC0) | interruptLevel->stateB;
  PORTC = (PORTC & 0xF8) | interruptLevel->stateC;
  // Predict the time that the next interrupt will occur.
  byte increment = interruptLevel->clockIncrement;
  cycleTime += increment;
  // Reset the timer, including whatever time has elapsed in this interrupt, so our timing stays
  // fixed even if we do some variable amount of work here.
  TCNT2 += (kTimerMaximum - increment);
}

void SetupLevels()
{
  // Populate the brightness level table, which drives our interrupt behavior.
  // Calculate as much as possible ahead of time, so we reduce overhead (and thus latency).
  unsigned int previousDuration;
  for (int i = 0; i < kLevels; i++) {
    unsigned int duration = i * i;
    levels[i].duration = duration;
    unsigned int increment = max( duration - previousDuration, kTimerMinimum );
    while (increment > kTimerMaximum) increment >>= 1;
    levels[i].clockIncrement = increment;
  } 
}

void SetupInterrupt()
{
  // Populate the brightness level state table we will use to drive interrupt behavior.
  SetupLevels();
  
  // Disable interrupts while we go configure the registers.
  cli();
  // Set Timer2 to use /1 prescaling, which gives us 16 MHz resolution.
  // This interrupt will fire whenever its 8-bit counter overflows, which would normally happen 
  // every 16 microseconds. We can adjust this by preloading the counter with some value, such
  // that the overflow happens in fewer ticks, but that will be driven by the cycle duration.
  TCCR2B = (TCCR2B & ~0x07) | (0x01);
  TCNT2 = 0;

  // Use normal mode
  TCCR2A &= ~((1<<WGM21) | (1<<WGM20));
  // Use internal clock - external clock not used in Arduino
  ASSR &= ~(1<<AS2);
  //Timer2 Overflow Interrupt Enable, clear the two output compare interrupt enables
  TIMSK2 |= (1<<TOIE2);
  TIMSK2 &= ~((1<<OCIE2A) | (1<<OCIE2B));  
  
  // Our cycle is all reset to zero.
  cycleTime = 0;
  interruptLevel = &levels[0];
  
  // Re-enable interrupts now that the registers have been set up.
  sei();
}

// ------------

void SetChannel( unsigned int channel, unsigned int level )
{
  // Make sure our inputs are reasonable. We'll simply ignore anything that doesn't make sense,
  // then count on the status response protocol to clue the host in.
  if (channel >= kChannels) return;
  if (level >= kLevels) return;
  channels[channel] = level;
  // All of our output pins are controlled by three registers: PORTD, PORTB, PORTC.
  // PORTD controls pins 0 through 7; we leave 0 and 1 for serial communication, and use only
  // the six pins 2 through 7. PORTB controls pins 8 through 13; the high two bits control the
  // timing crystals, so again we'll leave them alone. PORTC controls the "analog inputs" 0-5,
  // which we can also use as digital pins 14 through 19.
  // Each channel corresponds to one bit in one of these registers. We will set the brightness
  // level by enabling the channel's bit during some fraction of the cycle and clearing it during
  // the rest. Since our input is an 8-bit value, we use a 256-element array, where the time
  // between each element increases at an exponential rate.
  byte setD = (channel >= 0x0 && channel < 0x6) ? 1 << (channel + 0x2) : 0;
  byte setB = (channel >= 0x6 && channel < 0xC) ? 1 << (channel - 0x6) : 0;
  byte setC = (channel >= 0xC && channel < 0xF) ? 1 << (channel - 0xC) : 0;
  byte clearD = ~setD;
  byte clearB = ~setB;
  byte clearC = ~setC;
  // The demo LEDs are common cathode, so they need to be driven HIGH to turn off and LOW to turn
  // on. If this code was built for the demo board and not a production board, we'll invert the
  // senses of our IO bits.
  brightness_t *dest = levels;
  for (int i = 0; i < level; i++) {
    #if LED_MODE
    dest->stateD &= clearD;
    dest->stateB &= clearB;
    dest->stateC &= clearC;
    #else
    dest->stateD |= setD;
    dest->stateB |= setB;
    dest->stateC |= setC;
    #endif
    dest++;
  }
  for (int i = level; i < kLevels; i++) {
    #if LED_MODE
    dest->stateD |= setD;
    dest->stateB |= setB;
    dest->stateC |= setC;
    #else
    dest->stateD &= clearD;
    dest->stateB &= clearB;
    dest->stateC &= clearC;
    #endif
    dest++;
  }
}

void SetPixel( int pixel, const struct color_t & color )
{
  // Update our global state so we respond with accurate status messages.
  globalstate.pixels[pixel] = color;
}

void SetFader( int duration )
{
  sFading = true;
  sFaderBegin = millis();
  sFaderEnd = sFaderBegin + duration * kFaderInterval;
}

// ----------------

class Checksum
{
  public:
    Checksum() : mVal(0) {}
    void Next( byte value );
    byte Value() { return mVal; }
  private:
    byte mVal;
};

void Checksum::Next( byte value )
{
  // Rotate the existing value, to distribute bits evenly
  mVal = ((mVal & 0x7F) << 1) | ((mVal & 0x80) >> 7);
  // Add in the new value
  mVal += value;
}

void PushState()
{
  // Guid never changes, but by putting it here we don't need to initialize it elsewhere.
  globalstate.guid = kGuid;
  // Find out what the power modules are up to. I'm not completely sure what these values represent,
  // but there will be some kind of sensor connected to analog inputs 3 and 4, and the central computer
  // wants to know what its results are. Input values are 0..1023, so we have to lose the low bits.
  globalstate.powermodule1 = analogRead( 3 ) >> 2;
  globalstate.powermodule2 = analogRead( 4 ) >> 2;
  
  // Our message begins with a sync byte and ends with a checksum (which includes the sync).
  Checksum check;
  Serial.print( kSyncValue, BYTE );
  check.Next( kSyncValue );
  
  // Copy all of the bytes in our global state struct to the serial port.
  byte *src = (byte*)&globalstate;
  for (unsigned int i = 0; i < sizeof(globalstate); i++) {
    check.Next( *src );
    Serial.print( *src++, BYTE );
  }
  
  // Finish the message by sending the checksum.
  Serial.print( check.Value(), BYTE );
  
  // Now that we have sent a status update, it is not necessary to push another one until the
  // requisite number of milliseconds have passed, unless we receive input in the interim.
  sNextState = millis() + kUpdateInterval;
}

class CommandBuffer
{
  public:
    boolean Next( command_t *it );
  protected:
    void Add( byte val );
    byte Data( int offset );
    boolean Validate( command_t *it );
  private:
    // Command packet is the sizeof a command plus a sync byte and a checksum
    static const int kPacketBytes = 1 + sizeof(command_t) + 1;
    byte buffer[kPacketBytes];
    byte pos;
};

boolean CommandBuffer::Next( command_t *it )
{
  Add( Serial.read() );
  // See if this might be a complete message.
  boolean valid = false;
  if (Data(0) == kSyncValue) {
    valid = Validate( it );
  }
  // If we received a full, valid message, we will respond, but there is no need to do so immediately
  // because we know we are in the correct state. We will wait a few ticks in case there are other
  // commands coming down the pipeline. If the message was invalid, we should respond as quickly as
  // possible, because we will be in the wrong state until the host resends the command.
  sNextState = min( sNextState, millis() + (valid ? 0 : kResponseInterval) );
  // The caller does not care about these distinctions, and simply wants to know whether it should try
  // to process the command we just received.
  return valid;
}

void CommandBuffer::Add( byte val )
{
  buffer[pos] = val;
  pos = (pos + 1) % kPacketBytes;
}

byte CommandBuffer::Data( int offset )
{
  return buffer[(pos + offset) % kPacketBytes];
}

boolean CommandBuffer::Validate( command_t *it )
{
  // Copy our bytes out to the command parameter, totting up the checksum as we go.
  // We will return true if the message is valid, false if incomplete or bogus.
  Checksum check;
  check.Next( Data(0) );
  byte *dest = (byte*)it;
  for (int i = 0; i < sizeof(command_t); i++) {
    *dest = Data( i + 1 );
    check.Next( *dest++ );
  }
  return check.Value() == Data( kPacketBytes - 1 );
}

void PullCommands()
{
  // We will pull each byte into a rotating buffer. Whenever we recognize a valid message,
  // we will process its command. The only command we know about instructs us to set the red, green,
  // and blue channels of a certain pixel to a certain level.
  static CommandBuffer readbuf;
  while (Serial.available()) {
    command_t input;
    if (readbuf.Next( &input )) {
      SetFader( input.lerp_duration );
      for (int i = 0; i < kPixels; i++) {
        SetPixel( i, input.pixels[i] );
      }
      #if DEMO_MODE
      // Once we get a message from the central computer, we must stop running the demo mode, or
      // the demo will compete with the actual device state. That would be bad.
      sDisableDemo = true;
      #endif
      return;
    }
  }
}

void SerialUpdate()
{
  PullCommands();
  // We will post an update every time we receive any bytes. If 500 milliseconds have elapsed since
  // the last time we posted an update, we'll send another, just in case. This way the host can simply
  // respond to status messages by validating and sending corrections if necessary; it doesn't have to
  // actively ping, since it knows every board will check in at regular intervals.
  if (millis() >= sNextState) {
    PushState();
  }
}

// ----------------

void InterpolateChannel( int channel, long clock, byte target )
{
  boolean mapping = clock < sFaderEnd;
  byte current = channels[channel];
  byte newval = mapping ? map( clock, sFaderBegin, sFaderEnd, current, target ) : target;
  SetChannel( channel, newval );
}

void InterpolatePixel( int pixel, long clock )
{
  int channel = pixel * kChannels / kPixels;
  color_t &color = globalstate.pixels[pixel];
  InterpolateChannel( channel + 0, clock, color.red );
  InterpolateChannel( channel + 1, clock, color.green );
  InterpolateChannel( channel + 2, clock, color.blue );
}

void FaderUpdate()
{
  if (sFading) {
    long clock = millis();
    for (int i = 0; i < kPixels; i++) {
      InterpolatePixel( i, constrain( clock, sFaderBegin, sFaderEnd ) );
    }
    if (clock < sFaderEnd) {
      sFaderBegin = clock;
    } else {
      sFading = false;
    }
  }
}

// ----------------

#if DEMO_MODE
void RunDemo()
{
  long time = millis();  
  if (sFading) return;
  if (time % 2000 > 40) return;
  const color_t palette[6] = {
    {255, 255, 255}, // white
    {255, 0, 0}, // red
    {0, 0, 255}, // blue
    {255, 165, 0}, // orange
    {0, 255, 0}, // green
    {255, 255, 0}}; // yellow
  SetFader( 200 );
  for (int i = 0; i < kPixels; i++) {
    color_t color = palette[(time + i * 13) % 5];
    SetPixel( i, color );
  }
}
#endif //DEMO_MODE

// ----------------

void setup()
{ 
  // Get our IO pins ready for output. We accomplish this by setting each pin's corresponding
  // data direction register bit high.
  DDRD |= 0xFC;
  DDRB |= 0x3F;
  DDRC |= 0x07;
  // Connect the serial port so we can receive commands & respond with status information.
  Serial.begin( 38400 );
  //Serial.begin( 9600 );
  // Now that we're ready to rock, fire up the interrupt timer that drives our PWM cycle.
  SetupInterrupt();
}

void loop()
{  
  if (!sFading) {
    // LED control is all driven by the Timer2 interrupt, so the main loop just needs to wait for 
    // commands and periodically post status updates. Our PWM cycle runs at 128 Hz, which takes
    // 8 milliseconds, so there is absolutely no point in checking more often than that; even 64 Hz
    // updates would give us very smooth animation, though, so we won't bother to check more often
    // than every 16 milliseconds.
    delay( 16 );
    SerialUpdate();
    #if DEMO_MODE
    if (!sDisableDemo) {
      RunDemo();
    }
    #endif
  } else {
    delay( kFaderInterval );
  }
  FaderUpdate();
}

