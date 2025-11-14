# tests.py
import pytest
import main

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
        main._accumulator = "+000000"  # Changed to 6 digits
        main._programMemory = {f"{i:03d}": "+000000" for i in range(250)}
        main._programCounter = 0
    
    def test_store_pass(self):
        """Test storing a value to a valid memory address"""
        main._accumulator = "+000010"  # 6 digits
        main._programMemory = {"000": "+000000", "001": "+000000"}
        main.store(("21", "001", "+021001"))
        assert main._programMemory["001"] == "+000010"
    
    def test_store_fail(self):
        """Test storing a value to an invalid memory address"""
        main._accumulator = "+000010"  # 6 digits
        main._programMemory = {"000": "+000000", "001": "+000000"}
        with pytest.raises(ValueError) as e:
            main.store(("21", "bad", "+021bad"))
        assert "Invalid memory address in STORE" in str(e.value)
    
    def test_load_pass(self):
        """Test loading a value from a valid memory address"""
        main._programMemory = {"000": "+000010", "001": "+000000"}  # 6 digits
        main._accumulator = "+000000"
        main.load(("20", "000", "+020000"))
        assert main._accumulator == "+000010"
    
    def test_load_fail(self):
        """Test loading a value from an invalid memory address"""
        main._programMemory = {"000": "+000010", "001": "+000000"}
        main._accumulator = "+000000"
        with pytest.raises(ValueError) as e:
            main.load(("20", "bad", "+020bad"))
        assert "Invalid memory address in LOAD" in str(e.value)

class TestReadWrite:
    """Tests I/O operations for main.py"""
    def setup_method(self):
        main._programMemory = {f"{i:03d}": "+000000" for i in range(250)}

    ## READ TESTS
    def test_read_pass(self):
        main.read(("10", "000", "+010000"), "10")
        # read() function stores as 4-digit format based on current implementation
        assert main._programMemory["000"] == "+0010"

    def test_read_large_number(self):
        main.read(("10", "099", "+010099"), "200")
        assert main._programMemory["099"] == "+0200"

    def test_read_error_none(self):
        # Test None input
        with pytest.raises(ValueError, match="No input provided for READ instruction"):
            main.read(("10", "099", "+010099"), None)

    def test_read_error_empty(self):
        # Test empty input
        with pytest.raises(ValueError, match="Empty input for READ instruction"):
            main.read(("10", "099", "+010099"), "  ")

    def test_read_error_invalid_address(self):
        # Test invalid memory address
        with pytest.raises(ValueError, match="Invalid memory address in READ"):
            main.read(("10", "XXX", "+010XXX"), "100")

    ### WRITE TESTS
    def test_write_pass(self):
        main._programMemory["033"] = "+000015"  # 6 digits
        value = main.write(("11", "033", "+011033"))
        assert value == "+000015"

    def test_write_zero(self):
        main._programMemory["066"] = "+000000"
        value = main.write(("11", "066", "+011066"))
        assert value == "+000000"

class TestArithmetic:
    """Tests for arithmetic operations in main.py"""

    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+000000"  # 6 digits
        main._programMemory = {f"{i:03d}": "+000000" for i in range(250)}
        main._programCounter = 0

    # ADD TESTS 
    def test_add_positive(self):
        main._accumulator = "+0007"  # Using 4-digit for compatibility with _overflow_value
        main._programMemory["009"] = "+0005"
        main.add(("30", "009", "+030009"))
        assert main._accumulator == "+0012"

    def test_add_negative(self):
        main._accumulator = "-0007"
        main._programMemory["009"] = "+0005"
        main.add(("30", "009", "+030009"))
        assert main._accumulator == "-0002"

    def test_add_zero(self):
        main._accumulator = "+0000"
        main._programMemory["001"] = "+0000"
        main.add(("30", "001", "+030001"))
        assert main._accumulator == "+0000"

    # SUBTRACT TESTS 
    def test_subtract_positive(self):
        main._accumulator = "+0010"
        main._programMemory["002"] = "+0003"
        main.subtract(("31", "002", "+031002"))
        assert main._accumulator == "+0007"

    def test_subtract_negative_result(self):
        main._accumulator = "+0003"
        main._programMemory["002"] = "+0010"
        main.subtract(("31", "002", "+031002"))
        assert main._accumulator == "-0007"

    # MULTIPLY TESTS 
    def test_multiply_positive(self):
        main._accumulator = "+0004"
        main._programMemory["003"] = "+0003"
        main.multiply(("33", "003", "+033003"))
        assert main._accumulator == "+0012"

    def test_multiply_negative(self):
        main._accumulator = "-0004"
        main._programMemory["003"] = "+0003"
        main.multiply(("33", "003", "+033003"))
        assert main._accumulator == "-0012"

    def test_multiply_by_zero(self):
        main._accumulator = "+0009"
        main._programMemory["003"] = "+0000"
        main.multiply(("33", "003", "+033003"))
        assert main._accumulator == "+0000"

    # DIVIDE TESTS
    def test_divide_positive(self):
        main._accumulator = "+0012"
        main._programMemory["004"] = "+0003"
        main.divide(("32", "004", "+032004"))
        assert main._accumulator == "+0004"

    def test_divide_negative(self):
        main._accumulator = "-0012"
        main._programMemory["004"] = "+0003"
        main.divide(("32", "004", "+032004"))
        assert main._accumulator == "-0004"

    def test_divide_by_zero(self):
        main._accumulator = "+0010"
        main._programMemory["004"] = "+0000"
        with pytest.raises(ValueError) as e:
            main.divide(("32", "004", "+032004"))
        assert "Division by zero" in str(e.value)

class TestBranch:
    """Tests for branching operations in main.py"""

    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+000000" # 6 digits
        main._programMemory = {f"{i:03d}": "+000000" for i in range(250)}
        main._programCounter = 0
    
    # BRANCH TESTS
    def test_branch(self):
        main._programMemory["012"] = "+000012"
        main.branch(("40", "012", "+040012"))
        assert main._programCounter == 12

    def test_branch_to_zero(self):
        main._programCounter = 10
        main.branch(("40", "000", "+040000"))
        assert main._programCounter == 0

    def test_branch_neg_true(self):
        main._programMemory["013"] = "+000013"
        main._accumulator = "-0001"
        result = main.branchneg(("41", "013", "+041013"))
        assert main._programCounter == 13
        assert result == True # Branch occurred

    def test_branch_neg_false(self):
        main._programMemory["014"] = "+000014"
        main._accumulator = "+0000" # Not negative
        main._programCounter = 5
        result = main.branchneg(("41", "014", "+041014"))
        assert main._programCounter == 5 # Should not branch
        assert result == False # Branch did not occur

    def test_branch_neg_positive_accumulator(self):
        main._accumulator = "+0010"
        main._programCounter = 5
        result = main.branchneg(("41", "020", "+041020"))
        assert main._programCounter == 5 # Should not branch
        assert result == False

    def test_branch_zero_true(self):
        main._programMemory["015"] = "+000015"
        main._accumulator = "+0000"
        result = main.branchzero(("42", "015", "+042015"))
        assert main._programCounter == 15
        assert result == True # Branch occurred

    def test_branch_zero_false(self):
        main._programMemory["016"] = "+000016"
        main._accumulator = "+0001" # Not zero
        main._programCounter = 5
        result = main.branchzero(("42", "016", "+042016"))
        assert main._programCounter == 5 # Should not branch
        assert result == False # Branch did not occur

    def test_branch_invalid_address(self):
        """Test branching to invalid address raises error"""
        with pytest.raises(ValueError, match="Invalid branch address"):
            main.branch(("40", "999", "+040999")) # Address out of range

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
    
    def test_parse_negative_instruction(self):
        result = main.parse("-1025")
        assert result == ("10", "25", "-1025")
    
    def test_parse_empty_string(self):
        with pytest.raises(ValueError, match="Empty word instruction"):
            main.parse("")
    
    def test_parse_too_short(self):
        with pytest.raises(ValueError, match="Instruction too short"):
            main.parse("+12")
    
    def test_parse_invalid_characters(self):
        with pytest.raises(Exception, match="invalid characters"):
            main.parse("+10XX")
    
    def test_parse_invalid_length(self):
        with pytest.raises(ValueError, match="Invalid instruction length"):
            main.parse("+12345678")

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
            ("+1025", "+010025"), # READ
            ("+1125", "+011025"), # WRITE
            ("+2025", "+020025"), # LOAD
            ("+2125", "+021025"), # STORE
            ("+3025", "+030025"), # ADD
            ("+3125", "+031025"), # SUBTRACT
            ("+3225", "+032025"), # DIVIDE
            ("+3325", "+033025"), # MULTIPLY
            ("+4025", "+040025"), # BRANCH
            ("+4125", "+041025"), # BRANCHNEG
            ("+4225", "+042025"), # BRANCHZERO
            ("+4300", "+043000"), # HALT
        ]
        for input_val, expected in test_cases:
            assert main.convert_4_to_6_digit(input_val) == expected
    
    def test_convert_invalid_opcodes(self):
        """Test that invalid opcodes are treated as raw numbers"""
        test_cases = [
            ("+0099", "+000099"),
            ("+1234", "+001234"), # 12 is not a valid opcode
            ("+5555", "+005555"),
            ("+9999", "+009999"),
        ]
        for input_val, expected in test_cases:
            assert main.convert_4_to_6_digit(input_val) == expected
    
class TestExtendedMemory:
    """Tests for extended memory addresses (100-249)"""
    
    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+000000"
        main._programMemory = {f"{i:03d}": "+000000" for i in range(250)}
        main._programCounter = 0
    
    def test_load_from_extended_address(self):
        main._programMemory["150"] = "+001234"
        main.load(("20", "150", "+020150"))
        assert main._accumulator == "+001234"
    
    def test_store_to_extended_address(self):
        main._accumulator = "+005678"
        main.store(("21", "200", "+021200"))
        assert main._programMemory["200"] == "+005678"
    
    def test_branch_to_extended_address(self):
        main.branch(("40", "150", "+040150"))
        assert main._programCounter == 150
    
    def test_read_to_extended_address(self):
        main.read(("10", "225", "+010225"), "+9999")
        assert main._programMemory["225"] == "+9999"
    
    def test_write_from_extended_address(self):
        main._programMemory["249"] = "+007890"
        value = main.write(("11", "249", "+011249"))
        assert value == "+007890"
    
    def test_arithmetic_with_extended_address(self):
        main._accumulator = "+0100"
        main._programMemory["200"] = "+0050"
        main.add(("30", "200", "+030200"))
        assert main._accumulator == "+0150"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])  # Verbose output
