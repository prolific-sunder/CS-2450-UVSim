import sys
import re
import interface as face

_accumulator = "+0000"
_programCounter = 0
_programMemory = {}

# --- Class to facilitate the management of Memory ---
class MemoryManager:
    def __init__(self, parent):
        self.mem_dict = {}
        self.parent = parent

    def add_mem_helper(self, program_memory: dict):
        curr_tab = self.parent.notebook.index(self.parent.notebook.select())
        self.mem_dict[curr_tab] = program_memory

    def remove_mem_helper(self):
        try:
            curr_tab = self.parent.notebook.index(self.parent.notebook.select())
            self.mem_dict.pop(curr_tab)
        except:
            pass

    def switch_mem(self, event):
        # Find which tab has been selected, and load the appropriate memory into the core
        try:
            # if there is a tab, then find it
            curr_tab = self.parent.notebook.index(self.parent.notebook.select())
            # load the memory core with the memory from the file
            self.parent.initial_memory = self.mem_dict[curr_tab]

            self.parent.reset_memory()
        except:
            # If there is no tab, it's because the last tab was closed
            print("Error?")

# --- Core instruction implementations ---
def _overflow_value(value: int) -> str:
    """Truncate to signed four-digit word (keep last 4 digits)."""
    sign = '+' if value >= 0 else '-'
    digits = str(abs(value))[-4:]  # take last 4 digits only
    return f"{sign}{digits.zfill(4)}"

def parse(word):
    """
    Parse instruction - supports both 4-digit and 6-digit formats:
    - 4-digit: [sign]XXYY where XX=opcode (2 digits), YY=operand (2 digits)
    - 6-digit: [sign]0XXYYY where 0XX=opcode (3 digits with leading 0), YYY=operand (3 digits)
    
    Takes a string instruction
    Returns a tuple (opcode, operand, full_word)
    """
    if not word: # Check for empty string
        raise ValueError("Empty word instruction")
    
    word = word.strip() # Remove whitespace
    
    if len(word) < 4: # Check for too short
        raise ValueError(f"Instruction too short: '{word}' (need at least 4 digits)")
    
    # Check for proper format before adding sign
    if not re.fullmatch(r'^[+-]?\d+$', word):
        raise Exception("Word instruction contains invalid characters")
    
    # Handle sign
    newWord = word
    if word[0] not in ('+', '-'):
        newWord = '+' + word
    
    # Determine format based on length
    if len(newWord) == 5:  # 4-digit format: +XXYY
        if not newWord[1:].isdigit():
            raise ValueError(f"Instruction contains non-digit characters: '{word}'")
        opcode = newWord[1:3]  # First two digits after sign (e.g., "10")
        operand = newWord[3:5] # Last two digits (e.g., "25")
        return (opcode, operand, newWord)
    
    elif len(newWord) == 7: # 6-digit format: +0XXYYY
        if not newWord[1:].isdigit():
            raise ValueError(f"Instruction contains non-digit characters: '{word}'")
        opcode = newWord[1:4]  # First three digits after sign (e.g., "010")
        operand = newWord[4:7] # Last three digits (e.g., "025")
        # Strip leading zero from opcode for consistency with 4-digit format
        opcode = opcode.lstrip('0') or '0' # Keep at least one digit
        if len(opcode) == 1:
            opcode = '0' + opcode # Ensure 2-digit opcode (e.g., "10" not "1")
        return (opcode, operand, newWord)
    
    else:
        raise ValueError(f"Invalid instruction length: '{word}' (must be 4 or 6 digits plus sign)")

def convert_4_to_6_digit(instruction):
    """
    Convert 4-digit instruction to 6-digit format.
    4-digit: +XXYY becomes +0XX0YY
    Opcode gets leading zero: 10 becomes 010
    Operand gets leading zero: 25 becomes 025
    """
    if not instruction:
        return instruction
    
    instruction = instruction.strip()
    
    # Handle sign
    if instruction[0] not in ('+', '-'):
        instruction = '+' + instruction
    
    # Check if already 6-digit format
    if len(instruction) == 7:
        return instruction
    
    # Check if valid 4-digit format
    if len(instruction) != 5:
        return instruction  # Return as-is if invalid
    
    sign = instruction[0]
    first_two_digits = instruction[1:3]
    last_two_digits = instruction[3:5]
    
    valid_opcodes = {'10', '11', '20', '21', '30', '31', '32', '33', '40', '41', '42', '43'}
    
    if first_two_digits in valid_opcodes:
        # This is a function code - add leading zero to both opcode and operand
        opcode_3digit = '0' + first_two_digits  # 10 -> 010
        operand_3digit = '0' + last_two_digits  # 25 -> 025
        return f"{sign}{opcode_3digit}{operand_3digit}"
    else:
        # This is a raw number - prefix with 00 and keep all 4 digits
        all_four_digits = instruction[1:]  # Get all 4 digits
        return f"{sign}00{all_four_digits}"

def read(tuple, input):
    """Read input and store in memory at given address."""
    if input is None:
        raise ValueError("No input provided for READ instruction")
    
    input = input.strip() # Remove whitespace

    if not input: # Check for empty string
        raise ValueError("Empty input for READ instruction")
    
    address = tuple[1].zfill(3) # Normalize to 3 digits for 250 memory locations
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in READ: {tuple[1]}")
    
    length = len(input)

    if input[0] == "+" or input[0] == "-":
        if length > 5:
            input = input[0] + input[length - 4:]
            _programMemory[address] = input
        elif length == 5:
            _programMemory[address] = input
        else:
            input = input[0] + ("0" * (5 - length)) + input[1:]
            _programMemory[address] = input
    else:             
        if length > 4:
            input = "+" + input[length - 4:]
            _programMemory[address] = input
        elif length == 4:
            input = "+" + input
            _programMemory[address] = input
        else:
            input = "+" + ("0" * (4 - length)) + input
            _programMemory[address] = input

def write(tuple):
    """Write value from memory at given address."""
    _, address, _ = tuple

    # Normalize address to 3 digits
    address = address.zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in WRITE: {tuple[1]}")
    
    # Executes write instruction
    return _programMemory[address]

def load(tuple):
    """Load value from memory into accumulator."""
    global _accumulator
    global _programMemory

    # Normalize address to 3 digits
    address = tuple[1].zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in LOAD: '{tuple[1]}'")
    
    _accumulator = _programMemory[address]
    return

def store(tuple):
    """Store accumulator value into memory."""
    global _accumulator
    global _programMemory
    
    # Normalize address to 3 digits
    address = tuple[1].zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in STORE: '{tuple[1]}'")
    
    _programMemory[address] = _accumulator
    return

def add(tuple):
    """
    Add the value stored in memory at the given address to the accumulator.
    Result is stored back in the accumulator.
    """
    global _accumulator
    _, address, _ = tuple

    # Normalize address to 3 digits
    address = address.zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in ADD: '{tuple[1]}'")
    
    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    result = acc_val + mem_val

    _accumulator = _overflow_value(result)
    return

def subtract(tuple):
    """
    Subtract the value stored in memory from the accumulator.
    Result is stored back in the accumulator.
    """
    global _accumulator
    _, address, _ = tuple

    # Normalize address to 3 digits
    address = address.zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in SUBTRACT: '{tuple[1]}'")

    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    result = acc_val - mem_val

    _accumulator = _overflow_value(result)
    return

def multiply(tuple):
    """
    Multiply the value in the accumulator by the value stored in memory.
    Result is stored back in the accumulator.
    """
    global _accumulator
    _, address, _ = tuple

    # Normalize address to 3 digits
    address = address.zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in MULTIPLY: '{tuple[1]}'")

    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    result = acc_val * mem_val

    _accumulator = _overflow_value(result)
    return

def divide(tuple):
    """
    Divide the value in the accumulator by the value stored in memory.
    Result is stored back in the accumulator.
    This currently uses floor division.
    """
    global _accumulator
    _, address, _ = tuple

    # Normalize address to 3 digits
    address = address.zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in DIVIDE: '{tuple[1]}'")
    
    acc_val = int(_accumulator)
    mem_val = int(_programMemory[address])

    if mem_val == 0:  # Prevents a division by 0 error
        raise ValueError("Division by zero error")

    result = acc_val // mem_val

    _accumulator = _overflow_value(result)
    return

def branch(tuple):
    """Unconditional branch: always set PC to operand."""
    global _programCounter
    address = tuple[1]
    
    # Validate address range (0-249 for 250 memory locations)
    if not address.isdigit() or not (0 <= int(address) <= 249):
        raise ValueError(f"Invalid branch address: '{address}'")

    _programCounter = int(address)

def branchneg(tuple):
    """Branch if accumulator is negative."""
    global _accumulator, _programCounter
    old_pc = _programCounter
    try:
        if int(_accumulator) < 0:
            address = tuple[1]
            if not address.isdigit() or not (0 <= int(address) <= 249):
                raise ValueError(f"Invalid branch address: '{address}'")
            _programCounter = int(address)
    except ValueError:
        raise ValueError(f"Invalid accumulator value: {_accumulator}")
    return _programCounter != old_pc

def branchzero(tuple):
    """Branch if accumulator is zero."""
    global _accumulator, _programCounter
    old_pc = _programCounter

    if int(_accumulator) == 0:
        address = tuple[1]
        if not address.isdigit() or not (0 <= int(address) <= 249):
            raise ValueError(f"Invalid branch address: '{address}'")
        _programCounter = int(address)
    return _programCounter != old_pc



def main():
    gui = face.Window()       # Create the GUI
    
if __name__ == "__main__":
    main()
