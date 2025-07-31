# Pydantic Documentation Index

This index provides quick access to Pydantic documentation pages with all full-name objects for easy reference.

## Core API Documentation

### BaseModel API
**URL**: https://docs.pydantic.dev/latest/api/base_model/

**Main Headers**:
- `__init__` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.__init__
- `model_config` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_config
- `model_fields` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_fields
- `model_computed_fields` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_computed_fields
- `__pydantic_core_schema__` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.__pydantic_core_schema__
- `model_extra` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_extra
- `model_fields_set` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_fields_set
- `model_construct` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_construct
- `model_copy` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_copy
- `model_dump` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_dump
- `model_dump_json` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_dump_json
- `model_json_schema` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_json_schema
- `model_parametrized_name` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_parametrized_name
- `model_post_init` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_post_init
- `model_rebuild` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_rebuild
- `model_validate` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_validate
- `model_validate_json` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_validate_json
- `model_validate_strings` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.BaseModel.model_validate_strings
- `create_model` - https://docs.pydantic.dev/latest/api/base_model/#pydantic.create_model

**Core Objects**:
- `pydantic.BaseModel` - Base class for creating Pydantic models
- `pydantic.BaseModel.__init__` - Model initialization method
- `pydantic.BaseModel.model_config` - Configuration for the model (ConfigDict)
- `pydantic.BaseModel.model_fields` - Mapping of field names to FieldInfo instances
- `pydantic.BaseModel.model_computed_fields` - Mapping of computed field names to ComputedFieldInfo instances
- `pydantic.BaseModel.__pydantic_core_schema__` - Core schema of the model
- `pydantic.BaseModel.model_extra` - Extra fields set during validation
- `pydantic.BaseModel.model_fields_set` - Set of explicitly set fields
- `pydantic.BaseModel.model_construct` - Create models without validation
- `pydantic.BaseModel.model_copy` - Copy model instance
- `pydantic.BaseModel.model_dump` - Generate dictionary representation
- `pydantic.BaseModel.model_dump_json` - Generate JSON string representation
- `pydantic.BaseModel.model_json_schema` - Generate JSON schema
- `pydantic.BaseModel.model_parametrized_name` - Compute class name for parametrizations
- `pydantic.BaseModel.model_post_init` - Additional initialization after __init__
- `pydantic.BaseModel.model_rebuild` - Rebuild model schema
- `pydantic.BaseModel.model_validate` - Validate data against model
- `pydantic.BaseModel.model_validate_json` - Validate JSON data against model
- `pydantic.BaseModel.model_validate_strings` - Validate string data against model
- `pydantic.create_model` - Dynamically create Pydantic models

### Models Concepts
**URL**: https://docs.pydantic.dev/latest/concepts/models/

**Main Headers**:
- Validation - https://docs.pydantic.dev/latest/concepts/models/#validation
- Basic model usage - https://docs.pydantic.dev/latest/concepts/models/#basic-model-usage
- Model methods and properties - https://docs.pydantic.dev/latest/concepts/models/#model-methods-and-properties
- Data conversion - https://docs.pydantic.dev/latest/concepts/models/#data-conversion
- Extra data - https://docs.pydantic.dev/latest/concepts/models/#extra-data
- Nested models - https://docs.pydantic.dev/latest/concepts/models/#nested-models
- Rebuilding model schema - https://docs.pydantic.dev/latest/concepts/models/#rebuilding-model-schema
- Arbitrary class instances - https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
- Nested attributes - https://docs.pydantic.dev/latest/concepts/models/#nested-attributes
- Error handling - https://docs.pydantic.dev/latest/concepts/models/#error-handling
- Validating data - https://docs.pydantic.dev/latest/concepts/models/#validating-data
- Creating models without validation - https://docs.pydantic.dev/latest/concepts/models/#creating-models-without-validation
- Generic models - https://docs.pydantic.dev/latest/concepts/models/#generic-models
- Validation of unparametrized type variables - https://docs.pydantic.dev/latest/concepts/models/#validation-of-unparametrized-type-variables
- Serialization of unparametrized type variables - https://docs.pydantic.dev/latest/concepts/models/#serialization-of-unparametrized-type-variables
- Dynamic model creation - https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation
- RootModel and custom root types - https://docs.pydantic.dev/latest/concepts/models/#rootmodel-and-custom-root-types
- Faux immutability - https://docs.pydantic.dev/latest/concepts/models/#faux-immutability
- Abstract base classes - https://docs.pydantic.dev/latest/concepts/models/#abstract-base-classes
- Field ordering - https://docs.pydantic.dev/latest/concepts/models/#field-ordering
- Automatically excluded attributes - https://docs.pydantic.dev/latest/concepts/models/#automatically-excluded-attributes
- Class variables - https://docs.pydantic.dev/latest/concepts/models/#class-variables
- Private model attributes - https://docs.pydantic.dev/latest/concepts/models/#private-model-attributes
- Model signature - https://docs.pydantic.dev/latest/concepts/models/#model-signature
- Structural pattern matching - https://docs.pydantic.dev/latest/concepts/models/#structural-pattern-matching
- Attribute copies - https://docs.pydantic.dev/latest/concepts/models/#attribute-copies

**Key Concepts**:
- Basic model usage and field definitions
- Model methods and properties
- Data conversion and type coercion
- Extra data handling (`extra='allow'`, `extra='forbid'`, `extra='ignore'`)
- Nested models and hierarchical data structures
- Model schema rebuilding with `model_rebuild()`
- Arbitrary class instances (from_attributes config)
- Error handling and ValidationError
- Data validation methods (`model_validate`, `model_validate_json`, `model_validate_strings`)
- Generic models with TypeVar support
- Dynamic model creation with `create_model()`
- RootModel for custom root types
- Model immutability (frozen config)
- Abstract base classes integration
- Field ordering and serialization
- Class variables and private attributes
- Model signatures and structural pattern matching
- Attribute copying behavior

## Related Core APIs

### Fields API
**URL**: https://docs.pydantic.dev/latest/api/fields/
- `pydantic.fields.Field` - Field configuration function
- `pydantic.fields.FieldInfo` - Field information class
- `pydantic.fields.ComputedFieldInfo` - Computed field information class
- `pydantic.fields.PrivateAttr` - Private attribute configuration

### Configuration API
**URL**: https://docs.pydantic.dev/latest/api/config/
- `pydantic.config.ConfigDict` - Model configuration dictionary
- Configuration options: `extra`, `frozen`, `from_attributes`, `revalidate_instances`, etc.

### RootModel API
**URL**: https://docs.pydantic.dev/latest/api/root_model/
- `pydantic.RootModel` - Model with custom root type

### Validation and Errors
**URL**: https://docs.pydantic.dev/latest/api/pydantic_core/
- `pydantic_core.ValidationError` - Validation error exception

## Extended Concepts

### JSON Schema
**URL**: https://docs.pydantic.dev/latest/concepts/json_schema/
- JSON schema generation and customization

### Serialization
**URL**: https://docs.pydantic.dev/latest/concepts/serialization/
- Model serialization with `model_dump` and `model_dump_json`
- SerializeAsAny annotation for flexible serialization

### Validators
**URL**: https://docs.pydantic.dev/latest/concepts/validators/
- Field validators and model validators
- Custom validation logic

### Type Adapter
**URL**: https://docs.pydantic.dev/latest/concepts/type_adapter/
- TypeAdapter for validating non-model types

### Strict Mode
**URL**: https://docs.pydantic.dev/latest/concepts/strict_mode/
- Strict validation without type coercion

## Usage Examples

For implementation examples and usage patterns, refer to:
- **Models**: https://docs.pydantic.dev/latest/concepts/models/
- **BaseModel API**: https://docs.pydantic.dev/latest/api/base_model/

## Quick Reference

**Most Common Objects**:
1. `pydantic.BaseModel` - Main model base class
2. `pydantic.BaseModel.model_validate` - Validate data
3. `pydantic.BaseModel.model_dump` - Serialize to dict
4. `pydantic.BaseModel.model_dump_json` - Serialize to JSON
5. `pydantic.fields.Field` - Configure model fields
6. `pydantic.config.ConfigDict` - Model configuration
7. `pydantic_core.ValidationError` - Validation errors
8. `pydantic.create_model` - Dynamic model creation
