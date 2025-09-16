# MAIN FILE
import sys

def parse(word):
    # Takes a string instruction
    # Returns a tuple
    # Check if word is signed
    newWord = '+'
    if (word[0] != '+') and (word[0] != '-'):
        newWord += word
    else:
        newWord = word

    # Check if word is right size
    if (len(word) != 5):
        raise Exception("Word instruction not correct length")
    
    # Create the tuple
    newTuple = (newWord[1:3], newWord[3:], newWord)
    return newTuple

def read(tuple):
    # Takes the parsed tuple
    # Executes Read instruction
    return

def write(tuple):
    # Takes parsed tuple
    # Executes write instruction
    return

def load(tuple):
    # Takes parsed tuple
    # Executes load instruction
    return

def store(tuple):
    # Takes parsed tuple
    # Executes store instruction
    return

def add(tuple):
    # Takes parsed tuple
    # Executes add instruction
    return

def subtract(tuple):
    # Takes parsed tuple
    # Executes subtract instruction
    return

def divide(tuple):
    # Takes parsed tuple
    # Executes divide instruction
    return

def multiply(tuple):
    # Takes parsed tuple
    # Executes multiply instruction
    return

def branch(tuple):
    # Takes parsed tuple
    # Executes branch instruction
    return

def branchneg(tuple):
    # Takes parsed tuple
    # Executes branchneg instruction
    return

def branchzero(tuple):
    # Takes parsed tuple
    # Executes branchzero instruction
    return

def main():
    # Accessing command line args
    txtfile = sys.argv[1]

    # Test for if file exists
    try:
        f = open(txtfile)
        f.close
    except:
        #raise Exception("File not found!")
        print("Program halted with error code 1: File not found")
        return
    
    # Adding all instructions to the array
    global _programMemory
    _programMemory = {}
    with open(txtfile, 'r') as file:
        memoryCounter = 0
        for line in file:
            _programMemory.update({"{:02d}".format(memoryCounter) : line.strip()})
            memoryCounter += 1
    
    for x in _programMemory:
        print(x, _programMemory[x])

    # Parsing through the instructions, and calling the Parse function
    programcounter = 0
    global _accumulator
    while (programcounter < 100):
        # Call the parser
        tuple = parse(_programMemory["{:02d}".format(programcounter)])

        # Call each instruct function
        if tuple[0] == '10':
            read(tuple)
        elif tuple[0] == '11':
            write(tuple)
        elif tuple[0] == '20':
            load(tuple)
        elif tuple[0] == '21':
            store(tuple)
        elif tuple[0] == '30':
            add(tuple)
        elif tuple[0] == '31':
            subtract(tuple)
        elif tuple[0] == '32':
            divide(tuple)
        elif tuple[0] == '33':
            multiply(tuple)
        elif tuple[0] == '40':
            branch(tuple)
        elif tuple[0] == '41':
            branchneg(tuple)
        elif tuple[0] == '42':
            branchzero(tuple)
        elif tuple[0] == '43':
            programcounter += 100

        # Increment Program counter
        programcounter += 1
    
    print("Program halted with code 0")

if __name__ == '__main__':
    main()
