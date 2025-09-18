# tests.py
import pytest
import main

# Access main's variables and functions via the module namespace

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
        with pytest.raises(SystemExit) as e:  # Expecting SystemExit for invalid memory address
            main.store(("21", "bad", "+21bad"))  # Attempting to store to an invalid memory address
        assert e.type == SystemExit  # Asserting the exception type
        assert e.value.code == 1  # Asserting the exit code
    
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
        with pytest.raises(SystemExit) as e:  # Expecting SystemExit for invalid memory address
            main.load(("20", "bad", "+20bad"))  # Attempting to load from an invalid memory address
        assert e.type == SystemExit  # Asserting the exception type
        assert e.value.code == 1  # Asserting the exit code

class TestReadWrite:
    """Tests I/O operations for main.py"""
    def setup_method(self):
        main._programMemory = {f"{i:02d}": "+0000" for i in range(100)}

    ## READ TESTS
    def test_read_pass(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: 10)
        main.read(("10", "00", "+1000"))
        assert main._programMemory["00"] == 10

    def test_read_fail(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: 200)
        main.read(("10", "99", "+1099"))
        assert main._programMemory["99"] != 10

    def test_read_error(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda _: "I will fail")
        with pytest.raises(ValueError):
            main.read(("10", "99", "+1099"))

    ### WRITE TESTS
    def test_write_pass(self, capsys):
        main._programMemory["33"] = 15
        main.write(("11", "33", "+1033"))

        captured = capsys.readouterr()
        output_value = int(captured.out.strip())
        assert output_value == 15

    def test_write_fail(self, capsys):
        main._programMemory["66"] = 0
        main.write(("11", "66", "+1066"))
        main._programMemory["66"] = 1

        captured = capsys.readouterr()
        output_value = int(captured.out.strip())
        assert output_value != 1

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


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) # Verbose output
