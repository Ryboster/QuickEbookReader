from RPLCD.i2c import CharLCD
from time import sleep
from PyPDF2 import PdfReader
import re
from sys import argv

try:
    script, pdf_filepath = argv
except ValueError:
    print("No filepath specified. Please provide path to a PDF file.\n")
    print("Syntax:\n\t python3 script.py path/to/file.pdf\n")
    exit(0) 
    
###
### This script connects to an LCD connected to your board's I2C bus.
### It then reads an ebook in PDF format and displays it word-by-word
### on the screen.
##
### The purpose of this software is to train your reading speed without
### having to waste 500W on running a PC when all you're doing is reading
### a book.
###

class QuickEbookReader():
    ### To use this class, configure CharLCD initialization first.
    
    def __init__(self, words_per_minute, clear_duration):
        self.LCD = CharLCD(
            i2c_expander='PCF8574', ### Set i2c expander (found imprinted on chip)
            address=0x27,           ### Set SCL address (found with `i2cdetect <port:int>`)
            cols=16, rows=2         ### Set display size
        )
        self.TWINING_SYMBOLS = ["/", "-", "–", "+", "~", "|", "=", "*", "&"]
        self.WORDS_PER_MINUTE = words_per_minute    ### The number of words displayed every 60 seconds.
        self.LCD_CLEAR_DURATION = clear_duration    ### Speed at which the LCD will be cleared.
        
    def read_ebook(self, path):
        print("parsing ebook ... this may take a while. ")
        self.reader = PdfReader(path)
        self.text_content = ""
        for page in self.reader.pages:
            self.text_content += page.extract_text()
        self.extract_words()
            
    def extract_words(self):
        print("extracting words ...")
        self.all_words = self.text_content.split(" ")
        self.all_words = [x.strip() for x in self.all_words] # trim newline characters and trailing spaces.
        self.separate_words()
        
    def separate_words(self):
        print("untwining words ...")
        new_words = []
        for word in self.all_words:
            split_done = False
            for symbol in self.TWINING_SYMBOLS:
                if re.search(rf'\w{re.escape(symbol)}\w', word):
                    parts = re.split(rf'({re.escape(symbol)})', word)
                    new_words.extend([p for p in parts if p])
                    split_done = True
                    break 
            if not split_done:
                new_words.append(word)
        self.all_words = new_words
        
    def display_ebook(self):
        print("DISPLAYING")
        for word in self.all_words:
            self.LCD.write_string(word)
            sleep(60 / self.WORDS_PER_MINUTE)
            self.LCD.clear()
            sleep(self.LCD_CLEAR_DURATION)

    def __del__(self):
        self.LCD.close(clear=True)
        
if __name__ == "__main__":
    reader = QuickEbookReader(230, 0.075)
    reader.read_ebook(pdf_filepath)
    reader.display_ebook()