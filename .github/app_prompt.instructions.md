---
applyTo: '**/*.py'
---
# Pydantic Variants Library Development Prompt

You are developing a Python library for creating and manipulating Pydantic BaseModel variations.
This library provides APIs to decompose, transform, and rebuild Pydantic models with different field configurations. Please ensure all code follows these principles and standards:

## Code Quality Standards
- **Clean Code**: Write self-documenting code with meaningful names, small focused functions, and clear logic flow
- **Pythonic Design**: Use Python idioms, list comprehensions where appropriate, context managers, and follow PEP 8
- **Best Practice OOP**: Apply SOLID principles, proper encapsulation, inheritance, and composition where beneficial. Classes should be nouns. Don't overdo it if it increases complexity.

## Function Rules
- One function = one responsibility
- Maximum 3 parameters (use objects for more)
- Return early to avoid deep nesting
- No side effects unless explicitly intended
- Pure functions when possible
- Always handle exceptions explicitly
- Fail fast - validate inputs early
- Use specific exception types
- Provide meaningful error messages
- Never ignore or suppress errors silently
- Properly use classmethod and staticmethods, or just a global method where appropriate
- if some long name variable is repeated more than 3 times make a shorter version of it.
## Forbidden Practices
- No functions longer than 50 lines
- Avoid classes with more than 7 methods
- Avoid deep inheritance (>3 levels)
- Avoid tight coupling between classes
- Avoid ignoring exceptions

## Pydantic Library Specific Requirements
- Maintain Pydantic field validation and serialization behavior in transformed models
- Support all Pydantic field types including complex annotations
- Implement proper error handling for invalid field transformations
- Use Protocol classes for defining transformer interfaces
- Support chaining with pipeline for fluent API design

## Model Transformation Architecture
- **DecomposedModel**: Core class for model decomposition and rebuilding
- **VariantPipe**: Pipeline pattern for chaining transformations

## Pipeline & Transformation Design
- Follow pipeline pattern with clear separation of concerns
- Each transformer should be focused on a single transformation type
- Final transformer builds the actual model

## API Design Principles
- Provide fluent APIs for method chaining
- Include concise error messages for invalid transformations
- Document properly which version of pydantic is required
- keep names short but meaningful
- Match the style and verbosity level of existing transformers in the workspace

## Documentation Standards
- Include Concise docstrings for public interfaces only with examples
- Document any breaking changes or compatibility issues

## typing ##
- Include type information in all function signatures
- In type hints consider the most inclusive type that fits

## Error Handling Strategy
- Include helpful error messages with suggestions for fixes
- Validate transformation inputs upon init

## Code Style Guidelines
- Use list, dict, and generator expressions where applicable
- Use map, filter, reduce appropriately
- Don't create variables if their only use is in a single expression!
- Prefer immutable data structures where possible
- Use context managers for resource management
- Use logical operators where it fits (XOR, AND, OR, NOT)
- don not mutate objects directly, use proper constructors and methods

## Library Structure
```
variant_pipeline.py      # Core classes and protocols
transformers/           # Built-in transformation implementations
tests/                # Comprehensive test suite
README.md           # Library documentation and usage examples
```

## Answer Style
- Explain design decisions and trade-offs in chat only
- Reference existing code patterns from the workspace