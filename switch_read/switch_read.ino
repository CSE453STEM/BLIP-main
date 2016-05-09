/* File: switch_read.ino
 * Auth: Kevin Duggan
 * Desc: This program reads a row of 7 switches and a pushbutton
 *       and transmits over serial whenever a change is detected
 * Pins: 2-8:   Toggle Switch input (requires pulldown resistor)
 *       9:     Pushbutton input (requires pulldown resistor)
 */

byte bits;
byte oldbits;
byte i;
byte val;

void setup() {
    Serial.begin(19200);
    for (i = 2; i < 10; i++) { /* Initialize pins and value */
        pinMode(i, INPUT);
        bits |= digitalRead(i);
        bits << 1;
    }
    oldbits = !bits; /* Ensures state is printed at power-on */
}

void loop() {
    /* Build byte out of 8 bits read from pins */
    bits = 0;
    for (i = 0; i < 8; i++) {
        val = (byte) digitalRead(i + 2);
        bits |= (val << i);
    }
    if (bits != oldbits) {
        oldbits = bits;
        /* String of binary representation is best format to pass to Python */
        Serial.write(bits); 
        Serial.println();
    }
}
