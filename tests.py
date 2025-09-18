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

if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) # Verbose output
