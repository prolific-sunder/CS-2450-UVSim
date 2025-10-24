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
    # Test cases for main.py functions
    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+0000"
        main._programMemory = {f"{i:02d}": "+0000" for i in range(100)}
        main._programCounter = 0
    
    def test_store_pass(self):
        """Test storing a value to a valid memory address"""
        main._accumulator = "+0010"  # Setting accumulator value
        main._programMemory = {"00": "+0000", "01": "+0000"}  # Initializing program memory
        main.store(("21", "01", "+2101"))  # Storing accumulator value to memory address 01
        assert main._programMemory["01"] == "+0010"  # Asserting memory address 01 has the correct value
    
    def test_store_fail(self):
        """Test storing a value to an invalid memory address"""
        main._accumulator = "+0010"  # Setting accumulator value
        main._programMemory = {"00": "+0000", "01": "+0000"}  # Initializing program memory
        with pytest.raises(ValueError) as e:  # Expecting ValueError for invalid memory address
            main.store(("21", "bad", "+21bad"))  # Attempting to store to an invalid memory address
        assert "Invalid memory address in STORE" in str(e.value)  # Asserting the error message
    
    def test_load_pass(self):
        """Test loading a value from a valid memory address"""
        main._programMemory = {"00": "+0010", "01": "+0000"}  # Initializing program memory
        main._accumulator = "+0000"  # Setting accumulator value
        main.load(("20", "00", "+2000"))  # Loading value from memory address 00 to accumulator
        assert main._accumulator == "+0010"  # Asserting accumulator has the correct value
    
    def test_load_fail(self):
        """Test loading a value from an invalid memory address"""
        main._programMemory = {"00": "+0010", "01": "+0000"}  # Initializing program memory
        main._accumulator = "+0000"  # Setting accumulator value
        with pytest.raises(ValueError) as e:  # Expecting ValueError for invalid memory address
            main.load(("20", "bad", "+20bad"))  # Attempting to load from an invalid memory address
        assert "Invalid memory address in LOAD" in str(e.value)  # Asserting the error message

class TestReadWrite:
    """Tests I/O operations for main.py"""
    def setup_method(self):
        main._programMemory = {f"{i:02d}": "+0000" for i in range(100)}

    ## READ TESTS
    def test_read_pass(self, monkeypatch):
        main.read(("10", "00", "+1000"), "10")
        assert main._programMemory["00"] == "+0010"

    def test_read_fail(self, monkeypatch):
        main.read(("10", "99", "+1099"), "200")
        assert main._programMemory["99"] == "+0200"

    def test_read_error(self, monkeypatch):
        # Test None input
        with pytest.raises(ValueError, match="No input provided for READ instruction"):
            main.read(("10", "99", "+1099"), None)

        # Test empty input
        with pytest.raises(ValueError, match="Empty input for READ instruction"):
            main.read(("10", "99", "+1099"), "  ")

        # Test invalid memory address
        with pytest.raises(ValueError, match="Invalid memory address in READ"):
            main.read(("10", "XX", "+10XX"), "100")

    ### WRITE TESTS
    def test_write_pass(self, capsys):
        main._programMemory["33"] = "+0015"
        value = main.write(("11", "33", "+1033"))
        assert value == "+0015"

    def test_write_fail(self, capsys):
        main._programMemory["66"] = "+0000"
        value = main.write(("11", "66", "+1066"))
        assert value == "+0000"
        main._programMemory["66"] = "+0001"  # Change after write to verify write captured original value

class TestArithmetic:
    def setup_method(self):
        """Reset globals before each test"""
        main._accumulator = "+0000"
        main._programMemory = {f"{i:02d}": "+0000" for i in range(100)}
        main._programCounter = 0

    # ADD TESTS 
    def test_add_positive(self):
        main._accumulator = "+0007"
        main._programMemory["09"] = "+0005"
        main.add(("30", "09", "+3009"))
        assert main._accumulator == "+0012"

    def test_add_negative(self):
        main._accumulator = "-0007"
        main._programMemory["09"] = "+0005"
        main.add(("30", "09", "+3009"))
        assert main._accumulator == "-0002"

    def test_add_zero(self):
        main._accumulator = "+0000"
        main._programMemory["01"] = "+0000"
        main.add(("30", "01", "+3001"))
        assert main._accumulator == "+0000"

    # SUBTRACT TESTS 
    def test_subtract_positive(self):
        main._accumulator = "+0010"
        main._programMemory["02"] = "+0003"
        main.subtract(("31", "02", "+3102"))
        assert main._accumulator == "+0007"

    def test_subtract_negative_result(self):
        main._accumulator = "+0003"
        main._programMemory["02"] = "+0010"
        main.subtract(("31", "02", "+3102"))
        assert main._accumulator == "-0007"

    def test_subtract_with_negative_operand(self):
        main._accumulator = "+0005"
        main._programMemory["02"] = "-0003"
        main.subtract(("31", "02", "+3102"))
        assert main._accumulator == "+0008"

    # MULTIPLY TESTS 
    def test_multiply_positive(self):
        main._accumulator = "+0004"
        main._programMemory["03"] = "+0003"
        main.multiply(("33", "03", "+3303"))
        assert main._accumulator == "+0012"

    def test_multiply_negative(self):
        main._accumulator = "-0004"
        main._programMemory["03"] = "+0003"
        main.multiply(("33", "03", "+3303"))
        assert main._accumulator == "-0012"

    def test_multiply_by_zero(self):
        main._accumulator = "+0009"
        main._programMemory["03"] = "+0000"
        main.multiply(("33", "03", "+3303"))
        assert main._accumulator == "+0000"

    # DIVIDE TESTS
    def test_divide_positive(self):
        main._accumulator = "+0012"
        main._programMemory["04"] = "+0003"
        main.divide(("32", "04", "+3204"))
        assert main._accumulator == "+0004"

    def test_divide_negative(self):
        main._accumulator = "-0012"
        main._programMemory["04"] = "+0003"
        main.divide(("32", "04", "+3204"))
        assert main._accumulator == "-0004"

    def test_divide_by_zero(self):
        main._accumulator = "+0010"
        main._programMemory["04"] = "+0000"
        with pytest.raises(Exception) as e:
            main.divide(("32", "04", "+3204"))
        assert "Division by zero" in str(e.value)

class TestBranch:
    # BRANCH TESTS
    def test_branch(self):
        main._programMemory["12"] = "+0012"
        main.branch(("40", "12", "+4012"))
        assert main._programCounter == 12  # Branch to exact address

    def test_branch_neg(self):
        main._programMemory["13"] = "+0013"
        main._accumulator = "-0001"
        main.branchneg(("41", "13", "+4013"))
        assert main._programCounter == 13  # Branch when accumulator is negative

    def test_branch_neg_false(self):
        main._programMemory["14"] = "+0014"
        main._accumulator = "+0000"  # Not negative
        main._programCounter = 5  # Set initial position
        main.branchneg(("41", "14", "+4114"))
        assert main._programCounter == 5  # Should not branch

    def test_branch_zero(self):
        main._programMemory["15"] = "+0015"
        main._accumulator = "+0000"
        main.branchzero(("42", "15", "+4215"))
        assert main._programCounter == 15  # Branch when accumulator is zero

    def test_branch_zero_false(self):
        main._programMemory["16"] = "+0016"
        main._accumulator = "+0001"  # Not zero
        main._programCounter = 5  # Set initial position
        main.branchzero(("42", "16", "+4216"))
        assert main._programCounter == 5  # Should not branch

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) # Verbose output
