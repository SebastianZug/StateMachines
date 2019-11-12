typedef struct {
    int state;
    int next;
    int A_red;
    int A_yellow;
    int A_green;
    int timer;
} ampel_state_t;

ampel_state_t state_table[4] = {
 
// state     A_red             timer 
//  |   next  |  A_yellow       |    
//  |    |    |   |    A_green  |       
//----------------------------------------------
{   0,   1,   1,  0,    0,      10},
{   1,   2,   1,  1,    0,      2  },
{   2,   3,   0,  0,    1,      10},
{   3,   0,   0,  1,    0,      2, }
};

const int greenPin = A0;
const int yellowPin = 11;
const int redPin = 13;
int state = 0;

void setup() {
  pinMode(greenPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  pinMode(redPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("\nJunction lights - Project\n");
}

void loop() {
  if (state_table[state].A_red == 1) digitalWrite(redPin, HIGH);
  else digitalWrite(redPin, LOW);
  if (state_table[state].A_yellow == 1) digitalWrite(yellowPin, HIGH);
  else digitalWrite(yellowPin, LOW);
  if (state_table[state].A_green == 1) digitalWrite(greenPin, HIGH);
  else digitalWrite(greenPin, LOW);
  Serial.print(state);
  Serial.print("--> Waiting for Timer");
  Serial.print(state_table[state].timer);
  delay(state_table[state].timer*1000);
  Serial.print(" = expired -- > ");
  state =  state_table[state].next;
  Serial.println(state);
}
