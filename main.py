import sys
import interface as face

_accumulator = "+0000"
_programCounter = 0
_programMemory = {}

# --- Core instruction implementations ---
def _overflow_value(value: int) -> str:
    """Truncate to signed four-digit word (keep last 4 digits)."""
    sign = '+' if value >= 0 else '-'
    digits = str(abs(value))[-4:]  # take last 4 digits only
    return f"{sign}{digits.zfill(4)}"

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

def read(tuple, input):
    length = len(input)
    sinage = "+"

    if input[0] == "+" or input[0] == "-":
        if length > 5:
            input = input[0] + input[length - 4:]
            _programMemory[tuple[1]] = input
        elif length == 5:
            _programMemory[tuple[1]] = input
        else:
            input = input[0] + ("0" * (5 - length)) + input[1:]
            _programMemory[tuple[1]] = input
    else:             
        if length > 4:
            input = "+" + input[length - 4:]
            _programMemory[tuple[1]] = input
        elif length == 4:
            input = "+" + input
            _programMemory[tuple[1]] = input
        else:
            input = "+" + ("0" * (4 - length)) + input
            _programMemory[tuple[1]] = input

def write(tuple):
    # Takes parsed tuple
    _, address, _ = tuple
    # Executes write instruction
    return _programMemory[address]

def load(tuple):
    # Takes parsed tuple
    # Executes load instruction
    global _accumulator # Accessing global accumulator
    global _programMemory # Accessing global program memory
    try:
        _programMemory[tuple[1]] # Checking if memory address exists
    except KeyError:
        raise Exception("Invalid memory address in LOAD")
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
        raise Exception("Invalid memory address in STORE")
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

    _accumulator = _overflow_value(result)
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

    _accumulator = _overflow_value(result)
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

    _accumulator = _overflow_value(result)
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

    _accumulator = _overflow_value(result)
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
    gui = face.Window()       # Create the GUI
    
if __name__ == "__main__":
    main()
