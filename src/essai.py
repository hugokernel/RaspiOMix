
import sys, tty
from time import sleep

def waitEnter():
    tty.setcbreak(sys.stdin)
    while True:
        if ord(sys.stdin.read(1)) == 10:
            break

def gpio():
    from random import randint
    return randint(0, 1)

def testInput():
    for index in range(0, 4):

        print("> Insert IO%i connector and switch input mode and press [Enter]" % index)
        waitEnter()

        status = list('[.....]')
        count = 1
        value, last = gpio(), gpio()
        while True:
            sys.stdout.write("\r Switch between high and low level on input : %s   \r" % ("".join(status)) )
            sys.stdout.flush()
            sleep(0.5)
            value = gpio()

            if value == last:
                continue;

            last = value

            if value == 1:
                status[count] = '1'
            else:
                status[count] = '0'
            count += 1

            if count >= 7:
                break

        print("\n[Input %i: Ok !]" % index)
    print("Input test done !")

def testOutput():
    print("[Output test]")
    print("> Switch to output mode and press [Enter]")
    waitEnter()

    print("Press 1 to power on led, 0 to power off, enter [Y] if done !")

    string = ''
    while True:
        char = sys.stdin.read(1)
        if char == '1':
            pass
        elif char == '0':
            pass
        elif char == 'Y':
            break

        string += char
        sys.stdout.write("\r - %s   \r" % string)
        sys.stdout.flush()

    print("[Output test: Ok !]")
    print("\n--")

print("""
   __                 _   ___ _      _      
  /__\ __ _ ___ _ __ (_) /___( )\/\ (_)_  __
 / \/// _` / __| '_ \| |//  ///    \| \ \/ /
/ _  \ (_| \__ \ |_) | / \_/// /\/\ \ |>  < 
\/ \_/\__,_|___/ .__/|_\___/ \/    \/_/_/\_\\
               |_|""")

def printMenu():
    menu = [
        [ '1. Input' ],
        [ '2. Output' ],
        [ '3. Serial' ],
        [ '4. Analog' ],
        [ '5. Exit' ]
    ]

    print("Menu :")
    for m in menu:
        print(" " + m[0])

printMenu()

tty.setcbreak(sys.stdin)
while True:
    choice = sys.stdin.read(1)
    if choice == '1':
        testInput()
        printMenu()
    elif choice == '2':
        Raspiomix_Test.output()
    elif choice == '3':
        Raspiomix_Test.serial()
    elif choice == '4':
        Raspiomix_Test.analog()
    elif choice == '5':
        exit(0)

print("\n")
print("\n")

