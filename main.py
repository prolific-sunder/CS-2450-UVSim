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
    if not word: # Check for empty string
        raise ValueError("Empty word instruction")
    
    word = word.strip() # Remove whitespace
    
    if len(word) < 4: # Check for too short
        raise ValueError(f"Instruction too short: '{word}' (need at least 4 digits)")
    
    # Handle sign
    newWord = word
    if word[0] not in ('+', '-'):
        newWord = '+' + word
    
    # Check length after adding sign
    if len(newWord) != 5:
        if len(newWord) > 5:
            raise ValueError(f"Instruction too long: '{word}' (max 4 digits plus sign)")
        else:
            raise ValueError(f"Instruction invalid: '{word}")
        
    # Check if all characters are digits (except sign)
    if not newWord[1:].isdigit():
        raise ValueError(f"Instruction contains non-digit characters: '{word}'")
    
    # Parse into components
    opcode = (newWord[1:3])  # First two digits after sign
    operand = (newWord[3:])   # Last two digits
    return (opcode, operand, newWord)

def read(tuple, input):
    """Read input and store in memory at given address."""
    if input is None:
        raise ValueError("No input provided for READ instruction")
    
    input = input.strip() # Remove whitespace

    if not input: # Check for empty string
        raise ValueError("Empty input for READ instruction")
    
    if tuple[1] not in _programMemory:
        raise ValueError(f"Invalid memory address in READ: {tuple[1]}")
    
    length = len(input)

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
    """Write value from memory at given address."""
    # Takes parsed tuple
    _, address, _ = tuple

    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in WRITE: {address}")
    
    # Executes write instruction
    return _programMemory[address]

def load(tuple):
    # Takes parsed tuple
    # Executes load instruction
    global _accumulator # Accessing global accumulator
    global _programMemory # Accessing global program memory

    if tuple[1] not in _programMemory: # Checking if memory address exists
        raise ValueError(f"Invalid memory address in LOAD: '{tuple[1]}'")
    
    _accumulator = _programMemory[tuple[1]] # Loading value from memory to accumulator
    return

def store(tuple):
    # Takes parsed tuple
    # Executes store instruction
    global _accumulator # Accessing global accumulator
    global _programMemory # Accessing global program memory
    
    if tuple[1] not in _programMemory: # Checking if memory address exists
        raise ValueError(f"Invalid memory address in STORE: '{tuple[1]}'")
    
    _programMemory[tuple[1]] = _accumulator # Storing value from accumulator to memory
    return

def add(tuple):
    '''
    Add the value stored in memory at the given address to the accumulator
    Result is stored back in the accumulator.
    '''
    global _accumulator
    _, address, _ = tuple # Extract the memory address from the instruction

    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in ADD: '{address}'")
    
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

    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in SUBTRACT: '{address}'")

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

    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in MULTIPLY: '{address}'")

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

    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in DIVIDE: '{address}'")
    
    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    if mem_val == 0: #Prevents a division by 0 error
        raise ValueError("Division by zero error")

    result = acc_val // mem_val

    _accumulator = _overflow_value(result)
    return

def branch(tuple):
    """Unconditional branch: always set PC to operand."""
    global _programCounter
    address = tuple[1]
    if not address.isdigit() or not (0 <= int(address) <= 99):
        raise ValueError(f"Invalid branch address: '{address}'")

    _programCounter = int(tuple[1])

def branchneg(tuple):
    """Branch if accumulator is negative."""
    global _accumulator, _programCounter
    old_pc = _programCounter
    try:
        if int(_accumulator) < 0:
            _programCounter = int(tuple[1])
    except ValueError:
        raise ValueError(f"Invalid accumulator value: {_accumulator}")
    return _programCounter != old_pc

def branchzero(tuple):
    """Branch if accumulator is zero."""
    global _accumulator, _programCounter
    old_pc = _programCounter

    if int(_accumulator) == 0:
        address = tuple[1]
        if not address.isdigit() or not (0 <= int(address) <= 99):
            raise ValueError(f"Invalid branch address: '{address}'")
        _programCounter = int(tuple[1])
    return _programCounter != old_pc


def main():
    gui = face.Window()       # Create the GUI
    
if __name__ == "__main__":
    main()
