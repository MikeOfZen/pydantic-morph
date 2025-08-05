# Pydantic Variants 🔄

> **Transform your Pydantic models into multiple variants without code duplication**

Create input schemas, output DTOs, and database models from a single source of truth. Perfect for FastAPI applications where you need different model variants for different parts of your data flow.

## 🎯 Motivation

When developing APIs, the main model in your schema often contains internal data such as revision numbers, IDs, timestamps, or sensitive information. Different parts of your application need different views of the same model:

- **Input validation** - exclude system-generated fields (IDs, timestamps)
- **Update operations** - make most fields optional for PATCH requests  
- **Output responses** - hide sensitive or internal fields
- **Database models** - include all internal fields

This library avoids code duplication by creating hardcoded multiple variants of the same model. Instead, you define your schema once and use transformation pipelines to create the variants you need.

Built during a FastAPI + Beanie project where FastAPI generates automatic OpenAPI schemas from route definitions, this library provides a single source of truth for your schema without duplicating fields across model variants that are mostly overlapping.

Pipelines are defined per use case (input, output, admin), and are somewhat orthogonal to model definitions which define data schema.
pydantic-variants allows defining a few pipelines and applying them to as many models as needed.

By attaching the resulting variants to the root model, arbitrary deep variant nesting changes can be done. so the Input variant of `Customer` will also use the Input variant of `Address` for example.

## 🚀 Installation

```bash
pip install pydantic-variants
# or
uv add pydantic-variants
```

## 🏃‍♂️ Quick Start

```python
from datetime import datetime
from pydantic import BaseModel
from pydantic_variants import variants, basic_variant_pipeline
from pydantic_variants.transformers import FilterFields, MakeOptional

input_pipeline = basic_variant_pipeline('Input',
    FilterFields(exclude=['id', 'created_at', 'updated_at']),
    MakeOptional(all=True)
)

output_pipeline = basic_variant_pipeline('Output',
    FilterFields(exclude=['password_hash', 'internal_notes'])
)

update_pipeline = basic_variant_pipeline('Update',
    FilterFields(exclude=['id', 'created_at']),
    MakeOptional(all=True)
)

@variants(input_pipeline, output_pipeline, update_pipeline)
class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    full_name: str | None = None
    internal_notes: str = ""
    created_at: datetime
    updated_at: datetime

# Use the variants
user_input = User.Input(username="john", email="john@example.com")
user_output = User.Output(**user.model_dump(), id=1, created_at=datetime.now())
user_update = User.Update(full_name="John Doe")
```

## 🤔 Why Pydantic Variants?

### The Problem
Without Pydantic Variants, you'd write repetitive, error-prone code:

```python
# 😩 Multiple model definitions with duplicate fields
class UserBase(BaseModel):
    username: str
    email: str
    full_name: str | None = None

class UserInput(UserBase):
    pass

class UserOutput(UserBase):
    id: int
    created_at: datetime

class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    full_name: str | None = None

class User(UserBase):
    id: int
    password_hash: str
    internal_notes: str = ""
    created_at: datetime
    updated_at: datetime
```

### The Solution
With Pydantic Variants, define once, transform many:

```python
# 😍 Single source of truth with transformation pipelines
input_pipeline = basic_variant_pipeline('Input', 
    FilterFields(exclude=['id', 'created_at'])
)
output_pipeline = basic_variant_pipeline('Output', 
    FilterFields(exclude=['password_hash'])
)
update_pipeline = basic_variant_pipeline('Update', 
    MakeOptional(all=True)
)

@variants(input_pipeline, output_pipeline, update_pipeline)
class User(BaseModel):
    # Define once, use everywhere
    ...
```

## 🏗️ Architecture

Pydantic Variants uses a **pipeline architecture** with transformers. The architecture is designed to be easily enhanced with your own transformers.

```
BaseModel → VariantContext → [Field Transformers] → BuildVariant → [Model Transformers] → ConnectVariant
```

**Pipeline Order Matters:**
1. **VariantContext** - Opens the model into decomposed form
2. **Field Transformers** - Work with DecomposedModel (filter, rename, make optional)
3. **BuildVariant** - Converts to built Pydantic model  
4. **Model Transformers** - Work with built models (attach attributes, etc.)
5. **ConnectVariant** - Attaches variant to original model

Use `basic_variant_pipeline()` to avoid this boilerplate if desired.

## 📚 Core Concepts

### Pipeline Composition
Define reusable pipeline components:

```python
from pydantic_variants.transformers import *

# Reusable pipeline components
api_input_base = [
    FilterFields(exclude=['id', 'created_at', 'updated_at']),
    MakeOptional(exclude=['email'])  # email still required
]

public_output_base = [
    FilterFields(exclude=['password_hash', 'internal_notes', 'deleted_at'])
]

# Compose into specific pipelines
user_input_pipeline = basic_variant_pipeline('Input', *api_input_base)
user_output_pipeline = basic_variant_pipeline('Output', *public_output_base)

admin_output_pipeline = basic_variant_pipeline('AdminView',
    FilterFields(exclude=['password_hash']),  # Admin sees more fields
    SetFields({
        'admin_notes': FieldInfo(annotation=str, default="")
    })
)
```

### Available Transformers

```python
# Filter out fields
filter_sensitive = FilterFields(exclude=['password', 'internal_id'])
keep_public = FilterFields(include_only=['name', 'email'])

# Filter fields by metadata tags
filter_internal = FilterTag('internal')  # Removes fields tagged with Tag('internal')
filter_multiple = FilterTag(['internal', 'deprecated'])  # Multiple tag keys

# Make fields optional
all_optional = MakeOptional(all=True)
except_required = MakeOptional(exclude=['id'])
specific_optional = MakeOptional(include_only=['description'])

# Rename fields
rename_legacy = RenameFields(mapping={'user_id': 'id', 'email_addr': 'email'})

# Modify field properties
update_validation = ModifyFields({
    'email': {'validation_alias': 'email_address'},
    'name': {'default': 'Anonymous'}
})

# Switch nested model variants
use_input_variants = SwitchVariant('Input')
```

## 🌟 Advanced Features

### Nested Model Variants
Automatically transform nested models using variants attached to the root model under the `_variants` dict attribute:

```python
address_input = basic_variant_pipeline('Input',
    FilterFields(exclude=['id'])
)

@variants(address_input)
class Address(BaseModel):
    id: int
    street: str
    city: str
    country: str

user_input = basic_variant_pipeline('Input',
    FilterFields(exclude=['id']),
    SwitchVariant('Input')  # Uses Address.Input for address field
)

@variants(user_input)
class User(BaseModel):
    id: int
    name: str
    address: Address  # Becomes Address.Input in User.Input variant
```

### Custom Advanced Pipelines
Build complex pipelines with the full pipeline API:

```python
from pydantic_variants import VariantPipe, VariantContext
from pydantic_variants.transformers import *

# Advanced pipeline with custom logic
admin_pipeline = VariantPipe(
    VariantContext('Admin'),
    FilterFields(exclude=['password_hash']),
    SetFields({
        'admin_notes': FieldInfo(annotation=str, default=""),
        'permissions': FieldInfo(annotation=list[str], default_factory=list)
    }),
    SwitchVariant('Admin'),  # Use Admin variants of nested models
    BuildVariant(name_suffix="Admin"),
    ConnectVariant()
)

@variants(admin_pipeline)
class User(BaseModel):
    # Your model definition
    ...
```

### Dynamic Field Logic
Create complex field transformation logic:

```python
def smart_optional_logic(name: str, field: FieldInfo) -> tuple[bool, Any]:
    """Custom logic for making fields optional"""
    if name.endswith('_id'):
        return True, None
    elif name == 'created_at':
        return True, DefaultFactoryTag(datetime.now)
    elif name.startswith('internal_'):
        return True, ""
    return False, None

smart_optional = basic_variant_pipeline('SmartOptional',
    MakeOptional(optional_func=smart_optional_logic)
)
```

## 🔧 FastAPI Integration

Perfect integration with FastAPI's automatic OpenAPI schema generation:

```python
from fastapi import FastAPI

app = FastAPI()

# Define pipelines clearly
create_pipeline = basic_variant_pipeline('Create',
    FilterFields(exclude=['id', 'created_at'])
)

response_pipeline = basic_variant_pipeline('Response',
    FilterFields(exclude=['password_hash'])
)

@variants(create_pipeline, response_pipeline)
class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    created_at: datetime

@app.post("/users/", response_model=User.Response)
async def create_user(user: User.Create):
    # FastAPI automatically generates:
    # - User.Create schema for request body validation
    # - User.Response schema for response documentation
    return User.Response(**user.model_dump(), id=123, created_at=datetime.now())
```

## ⚠️ Schema Rebuilding

If your schema has forward references, use the delayed decorator and call `_build_variants()` **after** the schema is completely defined and rebuilt:

```python
# Define all models with delayed_build=True
@variants(user_pipeline, delayed_build=True)
class User(BaseModel):
    name: str
    posts: list['Post']

@variants(post_pipeline, delayed_build=True)
class Post(BaseModel):
    title: str
    author: User

# Rebuild models to resolve forward references
User.model_rebuild()
Post.model_rebuild()

# Build variants after all models are well defined
User._build_variants()
Post._build_variants()
```

## 📖 Complete API Reference

### Decorators
- `@variants(*pipelines)` - Main decorator for creating variants
- `basic_variant_pipeline(name, *transformers)` - Helper for common transformation patterns

### Core Classes
- `VariantPipe(*operations)` - Immutable pipeline for chaining transformations
- `VariantContext(name)` - Initializes transformation context
- `DecomposedModel` - Internal representation for field manipulation

### Field Transformers (work with DecomposedModel)
- `FilterFields(exclude/include_only/filter_func)` - Remove/keep specific fields
- `MakeOptional(all/exclude/include_only/optional_func)` - Make fields optional
- `RenameFields(mapping/rename_func)` - Rename fields
- `ModifyFields(field_modifications)` - Modify field properties  
- `SetFields(fields)` - Add or replace fields
- `SwitchVariant(variant_name)` - Use variants of nested models

### Model Transformers (work with built models)
- `BuildVariant(base, name_suffix, doc)` - Build final Pydantic model
- `ConnectVariant(attach_directly, attach_root)` - Attach variant to original model
- `SetAttribute(variant_attrs, root_attrs)` - Set class attributes


## 🤝 Contributing

We welcome contributions! The architecture is designed to be easily enhanced with your own transformers.


## 📄 License

This project is licensed under the Apache V2.0 

## 🔗 Related Projects

- [Pydantic](https://pydantic.dev/) - Data validation using Python type hints
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for APIs  
- [Beanie](https://beanie-odm.dev/) - Async ODM for MongoDB

## 🎉 Acknowledgments

Built during a FastAPI + Beanie project, inspired by the need for a single source of truth in API schema design.

---

⭐ **Star this repo if Pydantic Variants helps you build better APIs!**