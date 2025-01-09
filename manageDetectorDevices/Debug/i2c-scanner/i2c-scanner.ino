#include <LiquidCrystal.h>

// Setup the LiquidCrystal library with the pin numbers we have
// physically connected the module to.
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

int lastUpdate = 0;
int currentIndex = 0;
char* lyrics[] = {
  "Drink all the...",
  "     BOOZE!     ",
  "Hack all the... ",
  "    THINGS!     "
};

void setup() {
  // Setup the number of columns and rows that are available on the LCD.
  lcd.begin(16, 2);
}

void loop() {
  // Get the time in milliseconds since the last reset.
  int time = millis();

  // If 800 milliseconds have passed since we last updated
  // the text on the screen, print the next line of the
  // lyrics on the screen.
  if ((time  - lastUpdate) >= 800)
  {
    // Move the cursor back to the first column of the first row.
    lcd.setCursor(0, 0);

    // If we are writing "Drink all the..." or "Hack all the..."
    // then clear the screen and print the appropriate line.
    if (currentIndex == 0 || currentIndex == 2)
    {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(lyrics[currentIndex]);
    }
    else
    {
      // If we are writing the second line, move the cursor there
      // and print the appropriate line.
      lcd.setCursor(0, 1);
      lcd.print(lyrics[currentIndex]);
    }

    // Increment or reset the current index.
    if (currentIndex == 3)
    {
      currentIndex = 0;
    }
    else
    {
      currentIndex += 1;
    }

    // Update the time that we last refreshed the screen to track
    // when to update it again.
    lastUpdate = time;
  }
}