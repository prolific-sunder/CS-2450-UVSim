# MAIN FILE
import sys

# Global Vars
_accumulator = "+0000"
_programCounter = 0
_programMemory = {}

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
    # Unpack tuple
    _, address, _ = tuple
    # Executes Read instruction
    word = input("Enter input: ")
    try:
        # Try converting to int
        value = int(word)
        # Stores input to memory
        _programMemory[address] = value
    except ValueError:
        raise ValueError("Program only accepts signed/unsigned integer values")

def write(tuple):
    # Takes parsed tuple
    _, address, _ = tuple
    # Executes write instruction
    print(_programMemory[address])

def load(tuple):
    # Takes parsed tuple
    # Executes load instruction
    global _accumulator # Accessing global accumulator
    global _programMemory # Accessing global program memory
    try:
        _programMemory[tuple[1]] # Checking if memory address exists
    except KeyError:
        print("Program halted with error code 1: Invalid memory address")
        sys.exit(1)
    _accumulator = _programMemory[tuple[1]] # Loading value from memory to accumulator
    return

def store(tuple):
    # Takes parsed tuple
    # Executes store instruction
    global _accumulator # Accessing global accumulator
    global _programMemory # Accessing global program memory
    try:
        _programMemory[tuple[1]] # Checking if memory address exists
    except KeyError:
        print("Program halted with error code 1: Invalid memory address")
        sys.exit(1) 
    _programMemory[tuple[1]] = _accumulator # Storing value from accumulator to memory
    return

def add(tuple):
    '''
    Add the value stored in memory at the given address to the accumulator
    Result is stored back in the accumulator.
    '''
    global _accumulator
    _, address, _ = tuple # Extract the memory address from the instruction

    acc_val = int(_accumulator) # Covert accumulator string to integer
    mem_val = int(_programMemory[address]) # Convert memory word to integer

    result = acc_val + mem_val # Perform Addition

    _accumulator = f"{result:+05d}"
    return


def subtract(tuple):
    '''
    Subtract the value stored in memory from the accumulator.
    Result is stored back in the accumulator.
    '''
    global _accumulator
    _, address, _ = tuple

    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    result = acc_val - mem_val

    _accumulator = f"{result:+05d}"
    return


def multiply(tuple):
    '''
    Multiple the value in the accumulator by the value stored in memory.
    Result is stored back in the accumulator.
    '''
    global _accumulator
    _, address, _ = tuple

    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    result = acc_val * mem_val

    _accumulator = f"{result:+05d}"
    return


def divide(tuple):
    '''
    Divide the value in thea ccumulator by the value stored in memory.
    Result is stored back in the accumulator.

    This currently uses floor division.
    '''
    global _accumulator
    _, address, _ = tuple

    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    if mem_val == 0: #Prevents a division by 0 error
        raise Exception("Division by zero error")

    result = acc_val // mem_val

    _accumulator = f"{result:+05d}"
    return

def branch(tuple):
    # Takes parsed tuple
    # Executes branch instruction
    global _programCounter
    _programCounter = int(tuple[1]) - 1

    return

def branchneg(tuple):
    # Takes parsed tuple
    # Executes branchneg instruction
    if (_accumulator[0] == '-'):
        global _programCounter
        _programCounter = int(tuple[1]) - 1

    return

def branchzero(tuple):
    # Takes parsed tuple
    # Executes branchzero instruction
    if (_accumulator == "0000"):
        global _programCounter
        _programCounter = int(tuple[1]) - 1

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
    with open(txtfile, 'r') as file:
        memoryCounter = 0
        for line in file:
            _programMemory.update({"{:02d}".format(memoryCounter) : line.strip()})
            memoryCounter += 1
    
    # Populating all the remaining memory locations
    while (memoryCounter < 100):
        _programMemory.update({"{:02d}".format(memoryCounter) : "+0000"})
        memoryCounter += 1

    # Parsing through the instructions, and calling the Parse function
    global _accumulator
    global _programCounter
    while (_programCounter < 100):
        # Call the parser
        tuple = parse(_programMemory["{:02d}".format(_programCounter)])

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
            _programCounter += 100

        # Increment Program counter
        _programCounter += 1
    
    print("Program halted with code 0")

if __name__ == '__main__':
    main()
