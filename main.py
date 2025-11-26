import sys
import re
import interface as face

_accumulator = "+000000"
_programCounter = 0
_programMemory = {}

# --- Class to facilitate the management of Memory ---
class MemoryManager:
    def __init__(self, parent):
        self.mem_dict = {}   # key: tab widget, value: memory dict
        self.parent = parent

    def add_mem_helper(self, tab_widget, program_memory):
        """Store memory keyed by the tab's widget ID."""
        self.mem_dict[tab_widget] = program_memory.copy()

    def remove_mem_helper(self, tab_widget):
        """Remove memory for a closed tab."""
        self.mem_dict.pop(tab_widget, None)

    def switch_mem(self, event):
        """Load memory for the newly selected tab."""
        try:
            tab_widget = self.parent.notebook.nametowidget(
                self.parent.notebook.select()
            )
            self.parent.initial_memory = self.mem_dict.get(tab_widget, {})
            self.parent.reset_memory()
        except Exception as e:
            print("Memory switch error:", e)

# --- Core instruction implementations ---
def _overflow_value(value: int) -> str:
    """Truncate to signed 6-digit word in 00XXXX format (keep last 4 digits)."""
    sign = '+' if value >= 0 else '-'
    digits = str(abs(value))[-4:]  # take last 4 digits only
    return f"{sign}00{digits.zfill(4)}"

def parse(word):
    """
    Parse instruction - supports both 4-digit and 6-digit formats:
    - 4-digit: [sign]XXYY where XX=opcode (2 digits), YY=operand (2 digits)
    - 6-digit: [sign]0XXYYY where 0XX=opcode (3 digits with leading 0), YYY=operand (3 digits)

    Takes a string instruction
    Returns a tuple (opcode, operand, full_word)
    """
    if not word:  # Check for empty string
        raise ValueError("Empty word instruction")

    word = word.strip()  # Remove whitespace

    if len(word) < 4:  # Check for too short
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
        operand = newWord[3:5]  # Last two digits (e.g., "25")
        return (opcode, operand, newWord)

    elif len(newWord) == 7:  # 6-digit format: +0XXYYY
        if not newWord[1:].isdigit():
            raise ValueError(f"Instruction contains non-digit characters: '{word}'")
        opcode = newWord[1:4]  # First three digits after sign (e.g., "010")
        operand = newWord[4:7]  # Last three digits (e.g., "025")
        # Strip leading zero from opcode for consistency with 4-digit format
        opcode = opcode.lstrip('0') or '0'  # Keep at least one digit
        if len(opcode) == 1:
            opcode = '0' + opcode  # Ensure 2-digit opcode (e.g., "10" not "1")
        return (opcode, operand, newWord)

    else:
        raise ValueError(f"Invalid instruction length: '{word}' (must be 4 or 6 digits plus sign)")


def convert_4_to_6_digit(instruction):
    """
    Convert a valid 4-digit instruction to 6-digit format.
    Raises ValueError if the input is not a valid 4-digit instruction.
    """

    if not instruction:
        raise ValueError("Empty instruction")

    instruction = instruction.strip()

    # Ensure sign
    if instruction[0] not in ('+', '-'):
        instruction = '+' + instruction

    # Already correct length?
    if len(instruction) == 7:
        return instruction

    # Must be exactly 5 characters (+XXXX)
    if len(instruction) != 5:
        raise ValueError(f"Invalid 4-digit instruction length: '{instruction}'")

    sign = instruction[0]
    digits = instruction[1:]

    # Ensure all 4 characters are digits
    if not digits.isdigit():
        raise ValueError(f"Invalid characters in 4-digit instruction: '{instruction}'")

    first_two = digits[:2]
    last_two = digits[2:]

    valid_opcodes = {
        '10','11','20','21','30','31','32','33','40','41','42','43'
    }

    # FUNCTION INSTRUCTION
    if first_two in valid_opcodes:
        opcode_3 = '0' + first_two
        operand_3 = '0' + last_two
        return f"{sign}{opcode_3}{operand_3}"

    # RAW NUMBER
    return f"{sign}00{digits}"



def read(tuple, input):
    """Read input and store in memory at given address."""
    if input is None:
        raise ValueError("No input provided for READ instruction")
    
    input = input.strip()  # Remove whitespace

    if not input:  # Check for empty string
        raise ValueError("Empty input for READ instruction")
    
    # Handle both 2-digit and 3-digit memory addresses
    address = tuple[1].zfill(3)  # Normalize to 3 digits for 250 memory locations
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in READ: {tuple[1]}")
    
    length = len(input)

    # Store as 6-digit format: +00XXXX
    if input[0] == "+" or input[0] == "-":
        if length > 7:  # Overflow: take last 4 digits
            input = input[0] + "00" + input[length - 4:]
            _programMemory[address] = input
        elif length == 7:  # Already 6-digit
            _programMemory[address] = input
        else:  # Less than 6 digits, pad to 6
            digits = input[1:]
            input = input[0] + "00" + ("0" * (4 - len(digits))) + digits
            _programMemory[address] = input
    else:             
        if length > 4:  # Overflow: take last 4 digits
            input = "+00" + input[length - 4:]
            _programMemory[address] = input
        elif length == 4:
            input = "+00" + input
            _programMemory[address] = input
        else:
            input = "+00" + ("0" * (4 - length)) + input
            _programMemory[address] = input


def write(tuple):
    """Write value from memory at given address."""
    _, address, _ = tuple

    # Normalize address to 3 digits
    address = address.zfill(3)
    
    if address not in _programMemory:
        raise ValueError(f"Invalid memory address in WRITE: {tuple[1]}")
    
    # Return the value from memory (already in 6-digit format)
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
    gui = face.Window()  # Create the GUI


if __name__ == "__main__":
    main()
