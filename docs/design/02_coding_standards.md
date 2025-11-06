# AdvEngine - Coding Standards

## 1. Introduction

This document defines the coding standards and conventions for the AdvEngine project. Adhering to these standards is mandatory for all contributions to the codebase. The goal of these standards is to ensure that the codebase is clean, consistent, and easy to maintain.

## 2. Python Coding Style

### 2.1. PEP8 Compliance

All Python code must adhere to the [PEP8 style guide](https://www.python.org/dev/peps/pep-0008/). This includes, but is not limited to:

*   **Indentation:** Use 4 spaces per indentation level.
*   **Line Length:** Limit all lines to a maximum of 79 characters.
*   **Imports:** Imports should be grouped in the following order:
    1.  Standard library imports.
    2.  Related third-party imports.
    3.  Local application/library specific imports.
*   **Naming Conventions:**
    *   `lowercase` for variables and functions.
    *   `UPPERCASE` for constants.
    *   `PascalCase` for classes.
    *   `_leading_underscore` for internal use.

### 2.2. Docstrings

All modules, classes, and functions must have Google-style docstrings. This is to ensure that the code is well-documented and that the documentation can be easily parsed by automated tools.

**Example:**

```python
"""A brief description of the module."""

class MyClass:
    """A brief description of the class."""

    def my_method(self, arg1, arg2):
        """A brief description of the method.

        Args:
            arg1 (str): A description of the first argument.
            arg2 (int): A description of the second argument.

        Returns:
            bool: A description of the return value.
        """
        pass
```

## 3. User Interface Guidelines

### 3.1. GNOME Human Interface Guidelines (HIG)

The user interface of AdvEngine must follow the [GNOME Human Interface Guidelines (HIG)](https://developer.gnome.org/hig/). This is to ensure that the application provides a consistent and intuitive user experience.

### 3.2. Libadwaita Widgets

Wherever possible, the UI should be built using Libadwaita widgets. This is to ensure that the application has a modern, clean, and responsive design.

### 3.3. No Custom CSS

The application should not use any custom CSS. The UI should rely entirely on the default Libadwaita theme to ensure a consistent user experience, including support for light and dark modes.

## 4. Markdown and Documentation

All Markdown files, including documentation and this document, must be linted and formatted to an 80-character line limit. This ensures that the documentation is easy to read and maintain.
