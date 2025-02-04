# Conventions to be used to keep code consistent

## API Calls between Components

All code required to be used by another component of the program should be placed and documented in `api.py` in the component's root directory. This file is exported via `__init__.py` to be accessible in other components as follows:

```Python
# __init__.py

from api import *
```

## Common Structures

All custom data types required by multiple components should be defined in the `common` directory in an associated file, and exported/accessed via `__init__.py`

## Naming

- File names should follow `underscore_naming`
- Directories should use `camelCase`
- Classes should use `CamelCase`
- Functions and Variables should use `camelCase`
