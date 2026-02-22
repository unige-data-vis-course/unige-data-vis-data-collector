# Junie guidelines 


# Code design
* use classes when you need to carry elements with 3 por more properties
* Target at not having functions longer than 12 lines of code (without comments an newlines). Breakout in smaller function or methods that can be individually tested and reused
* Do not write obvious comment statements in the code. Only add comment when the logic is not trivial

# library use
* use pydantic v2 when needing pydantic
* Do not ensure package backwards compatibility

## Testing
* your are using a TDD approach
* You are using pytest
* test files location is in in test and then mirror the file structure of the tested class or functions
* You are using unitest TestCase classes
* Use parameterized tests whenever relevant
* use unittest.patch to mock external dependencies whenever needed
