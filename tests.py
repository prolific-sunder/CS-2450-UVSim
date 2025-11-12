# tests.py
import pytest
import main

# Access main's variables and functions via the module namespace

class TestThemeManagement:
    """Tests for theme management functions in interface.py"""
    
    def test_get_text_color_light_background(self):
        """Test that light backgrounds return black text"""
        import interface as face
        window = face.Window.__new__(face.Window)
        window.primary_color = '#FFFFFF'
        window.secondary_color = '#FFFFFF'
        
        result = window.get_text_color('#FFFFFF')
        assert result == 'black', "Light background should return black text"
    
    def test_get_text_color_dark_background(self):
        """Test that dark backgrounds return white text"""
        import interface as face
        window = face.Window.__new__(face.Window)
        
        result = window.get_text_color('#000000')
        assert result == 'white', "Dark background should return white text"

class TestLoadStore:
    """Test cases for main.py functions"""

    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+0000"
        main._programMemory = {f"{i:03d}": "+0000" for i in range(250)}  # Changed to 3 digits and 250 locations
        main._programCounter = 0
    
    def test_store_pass(self):
        """Test storing a value to a valid memory address"""
        main._accumulator = "+0010"
        main._programMemory = {"000": "+0000", "001": "+0000"}  # Changed to 3-digit addresses
        main.store(("21", "001", "+021001"))  # Updated instruction format
        assert main._programMemory["001"] == "+0010"
    
    def test_store_fail(self):
        """Test storing a value to an invalid memory address"""
        main._accumulator = "+0010"
        main._programMemory = {"000": "+0000", "001": "+0000"}  # Changed to 3-digit addresses
        with pytest.raises(ValueError) as e:
            main.store(("21", "bad", "+021bad"))
        assert "Invalid memory address in STORE" in str(e.value)
    
    def test_load_pass(self):
        """Test loading a value from a valid memory address"""
        main._programMemory = {"000": "+0010", "001": "+0000"}  # Changed to 3-digit addresses
        main._accumulator = "+0000"
        main.load(("20", "000", "+020000"))  # Updated instruction format
        assert main._accumulator == "+0010"
    
    def test_load_fail(self):
        """Test loading a value from an invalid memory address"""
        main._programMemory = {"000": "+0010", "001": "+0000"}  # Changed to 3-digit addresses
        main._accumulator = "+0000"
        with pytest.raises(ValueError) as e:
            main.load(("20", "bad", "+020bad"))
        assert "Invalid memory address in LOAD" in str(e.value)

class TestReadWrite:
    """Tests I/O operations for main.py"""
    def setup_method(self):
        main._programMemory = {f"{i:03d}": "+0000" for i in range(250)}  # Changed to 3 digits and 250 locations

    ## READ TESTS
    def test_read_pass(self, monkeypatch):
        main.read(("10", "000", "+010000"), "10")  # Updated instruction format
        assert main._programMemory["000"] == "+0010"

    def test_read_fail(self, monkeypatch):
        main.read(("10", "099", "+010099"), "200")  # Updated instruction format
        assert main._programMemory["099"] == "+0200"

    def test_read_error(self, monkeypatch):
        # Test None input
        with pytest.raises(ValueError, match="No input provided for READ instruction"):
            main.read(("10", "099", "+010099"), None)  # Updated instruction format

        # Test empty input
        with pytest.raises(ValueError, match="Empty input for READ instruction"):
            main.read(("10", "099", "+010099"), "  ")  # Updated instruction format

        # Test invalid memory address
        with pytest.raises(ValueError, match="Invalid memory address in READ"):
            main.read(("10", "XXX", "+010XXX"), "100")  # Updated instruction format

    ### WRITE TESTS
    def test_write_pass(self, capsys):
        main._programMemory["033"] = "+0015"  # Changed to 3-digit address
        value = main.write(("11", "033", "+011033"))  # Updated instruction format
        assert value == "+0015"

    def test_write_fail(self, capsys):
        main._programMemory["066"] = "+0000"  # Changed to 3-digit address
        value = main.write(("11", "066", "+011066"))  # Updated instruction format
        assert value == "+0000"
        main._programMemory["066"] = "+0001"  # Change after write to verify write captured original value

class TestArithmetic:
    """Tests for arithmetic operations in main.py"""

    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+0000"
        main._programMemory = {f"{i:03d}": "+0000" for i in range(250)}  # Changed to 3 digits and 250 locations
        main._programCounter = 0

    # ADD TESTS 
    def test_add_positive(self):
        main._accumulator = "+0007"
        main._programMemory["009"] = "+0005"  # Changed to 3-digit address
        main.add(("30", "009", "+030009"))  # Updated instruction format
        assert main._accumulator == "+0012"

    def test_add_negative(self):
        main._accumulator = "-0007"
        main._programMemory["009"] = "+0005"  # Changed to 3-digit address
        main.add(("30", "009", "+030009"))  # Updated instruction format
        assert main._accumulator == "-0002"

    def test_add_zero(self):
        main._accumulator = "+0000"
        main._programMemory["001"] = "+0000"  # Changed to 3-digit address
        main.add(("30", "001", "+030001"))  # Updated instruction format
        assert main._accumulator == "+0000"

    # SUBTRACT TESTS 
    def test_subtract_positive(self):
        main._accumulator = "+0010"
        main._programMemory["002"] = "+0003"  # Changed to 3-digit address
        main.subtract(("31", "002", "+031002"))  # Updated instruction format
        assert main._accumulator == "+0007"

    def test_subtract_negative_result(self):
        main._accumulator = "+0003"
        main._programMemory["002"] = "+0010"  # Changed to 3-digit address
        main.subtract(("31", "002", "+031002"))  # Updated instruction format
        assert main._accumulator == "-0007"

    def test_subtract_with_negative_operand(self):
        main._accumulator = "+0005"
        main._programMemory["002"] = "-0003"  # Changed to 3-digit address
        main.subtract(("31", "002", "+031002"))  # Updated instruction format
        assert main._accumulator == "+0008"

    # MULTIPLY TESTS 
    def test_multiply_positive(self):
        main._accumulator = "+0004"
        main._programMemory["003"] = "+0003"  # Changed to 3-digit address
        main.multiply(("33", "003", "+033003"))  # Updated instruction format
        assert main._accumulator == "+0012"

    def test_multiply_negative(self):
        main._accumulator = "-0004"
        main._programMemory["003"] = "+0003"  # Changed to 3-digit address
        main.multiply(("33", "003", "+033003"))  # Updated instruction format
        assert main._accumulator == "-0012"

    def test_multiply_by_zero(self):
        main._accumulator = "+0009"
        main._programMemory["003"] = "+0000"  # Changed to 3-digit address
        main.multiply(("33", "003", "+033003"))  # Updated instruction format
        assert main._accumulator == "+0000"

    # DIVIDE TESTS
    def test_divide_positive(self):
        main._accumulator = "+0012"
        main._programMemory["004"] = "+0003"  # Changed to 3-digit address
        main.divide(("32", "004", "+032004"))  # Updated instruction format
        assert main._accumulator == "+0004"

    def test_divide_negative(self):
        main._accumulator = "-0012"
        main._programMemory["004"] = "+0003"  # Changed to 3-digit address
        main.divide(("32", "004", "+032004"))  # Updated instruction format
        assert main._accumulator == "-0004"

    def test_divide_by_zero(self):
        main._accumulator = "+0010"
        main._programMemory["004"] = "+0000"  # Changed to 3-digit address
        with pytest.raises(Exception) as e:
            main.divide(("32", "004", "+032004"))  # Updated instruction format
        assert "Division by zero" in str(e.value)

class TestBranch:
    """Tests for branching operations in main.py"""

    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+0000"
        main._programMemory = {f"{i:03d}": "+0000" for i in range(250)}  # Changed to 3 digits and 250 locations
        main._programCounter = 0
    
    # BRANCH TESTS
    def test_branch(self):
        main._programMemory["012"] = "+0012"  # Changed to 3-digit address
        main.branch(("40", "012", "+040012"))  # Updated instruction format
        assert main._programCounter == 12  # Branch to exact address

    def test_branch_neg(self):
        main._programMemory["013"] = "+0013"  # Changed to 3-digit address
        main._accumulator = "-0001"
        main.branchneg(("41", "013", "+041013"))  # Updated instruction format
        assert main._programCounter == 13  # Branch when accumulator is negative

    def test_branch_neg_false(self):
        main._programMemory["014"] = "+0014"  # Changed to 3-digit address
        main._accumulator = "+0000"  # Not negative
        main._programCounter = 5  # Set initial position
        main.branchneg(("41", "014", "+041014"))  # Updated instruction format
        assert main._programCounter == 5  # Should not branch

    def test_branch_zero(self):
        main._programMemory["015"] = "+0015"  # Changed to 3-digit address
        main._accumulator = "+0000"
        main.branchzero(("42", "015", "+042015"))  # Updated instruction format
        assert main._programCounter == 15  # Branch when accumulator is zero

    def test_branch_zero_false(self):
        main._programMemory["016"] = "+0016"  # Changed to 3-digit address
        main._accumulator = "+0001"  # Not zero
        main._programCounter = 5  # Set initial position
        main.branchzero(("42", "016", "+042016"))  # Updated instruction format
        assert main._programCounter == 5  # Should not branch

class TestParse:
    """Tests for parsing both 4-digit and 6-digit instructions"""
    
    def test_parse_4digit_read(self):
        result = main.parse("+1025")
        assert result == ("10", "25", "+1025")
    
    def test_parse_6digit_read(self):
        result = main.parse("+010025")
        assert result == ("10", "025", "+010025")
    
    def test_parse_4digit_halt(self):
        result = main.parse("+4300")
        assert result == ("43", "00", "+4300")
    
    def test_parse_6digit_halt(self):
        result = main.parse("+043000")
        assert result == ("43", "000", "+043000")
    
    def test_parse_without_sign(self):
        result = main.parse("1025")
        assert result == ("10", "25", "+1025")
    
    def test_parse_6digit_extended_address(self):
        result = main.parse("+010150")
        assert result == ("10", "150", "+010150")

class TestConvert:
    """Tests for 4-digit to 6-digit conversion"""
    
    def test_convert_read_instruction(self):
        result = main.convert_4_to_6_digit("+1025")
        assert result == "+010025"
    
    def test_convert_halt_instruction(self):
        result = main.convert_4_to_6_digit("+4300")
        assert result == "+043000"
    
    def test_convert_raw_number(self):
        result = main.convert_4_to_6_digit("+5555")
        assert result == "+005555"
    
    def test_convert_all_opcodes(self):
        test_cases = [
            ("+1025", "+010025"),  # READ
            ("+1125", "+011025"),  # WRITE
            ("+2025", "+020025"),  # LOAD
            ("+2125", "+021025"),  # STORE
            ("+3025", "+030025"),  # ADD
            ("+3125", "+031025"),  # SUBTRACT
            ("+3225", "+032025"),  # DIVIDE
            ("+3325", "+033025"),  # MULTIPLY
            ("+4025", "+040025"),  # BRANCH
            ("+4125", "+041025"),  # BRANCHNEG
            ("+4225", "+042025"),  # BRANCHZERO
            ("+4300", "+043000"),  # HALT
        ]
        for input_val, expected in test_cases:
            assert main.convert_4_to_6_digit(input_val) == expected
    
    def test_convert_invalid_opcodes(self):
        """Test that invalid opcodes are treated as raw numbers"""
        test_cases = [
            ("+0099", "+000099"),
            ("+1234", "+001234"),  # 12 is not a valid opcode
            ("+5555", "+005555"),
            ("+9999", "+009999"),
        ]
        for input_val, expected in test_cases:
            assert main.convert_4_to_6_digit(input_val) == expected

class TestExtendedMemory:
    """Tests for extended memory addresses (100-249)"""
    
    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+0000"
        main._programMemory = {f"{i:03d}": "+0000" for i in range(250)}
        main._programCounter = 0
    
    def test_load_from_extended_address(self):
        main._programMemory["150"] = "+1234"
        main.load(("20", "150", "+020150"))
        assert main._accumulator == "+1234"
    
    def test_store_to_extended_address(self):
        main._accumulator = "+5678"
        main.store(("21", "200", "+021200"))
        assert main._programMemory["200"] == "+5678"
    
    def test_branch_to_extended_address(self):
        main.branch(("40", "150", "+040150"))
        assert main._programCounter == 150
    
    def test_read_to_extended_address(self):
        main.read(("10", "225", "+010225"), "+9999")
        assert main._programMemory["225"] == "+9999"

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])  # Verbose output
