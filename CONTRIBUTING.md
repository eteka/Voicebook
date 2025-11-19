# Contributing to Voicebook

Thank you for considering contributing to Voicebook! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## 🤝 Code of Conduct

By participating in this project, you agree to:

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/Voicebook.git
cd Voicebook
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 🔄 Development Workflow

### 1. Make Your Changes

Follow the code standards outlined below.

### 2. Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_cost_calculator.py

# Run tests in parallel
pytest tests/ -n auto
```

### 3. Check Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type check
mypy src/

# Security check
bandit -r src/
```

**Or run all checks at once:**

```bash
pre-commit run --all-files
```

### 4. Commit Changes

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in cache"
# or
git commit -m "docs: update README"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## 📏 Code Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length:** 100 characters (enforced by Black)
- **Formatting:** Black (automatic formatting)
- **Import Sorting:** isort with Black profile
- **Docstrings:** Google style or NumPy style
- **Type Hints:** Required for public functions

### Code Quality Requirements

✅ **Must Pass:**
- All tests (pytest)
- Code formatting (black)
- Import sorting (isort)
- Linting (flake8)
- Security checks (bandit)

⚠️ **Should Pass:**
- Type checking (mypy)
- Docstring coverage (interrogate)
- Code complexity (radon)

### Example Code

```python
"""Module docstring explaining the module's purpose."""

from typing import Optional

def calculate_cost(text: str, quality: str = "standard") -> float:
    """
    Calculate the cost of generating audio.

    Args:
        text: The input text to convert
        quality: Either "standard" or "hd"

    Returns:
        The estimated cost in USD

    Raises:
        ValueError: If quality is not recognized

    Example:
        >>> calculate_cost("Hello world", "standard")
        0.0002
    """
    if quality not in ["standard", "hd"]:
        raise ValueError(f"Invalid quality: {quality}")

    # Implementation here
    return 0.0
```

## 🧪 Testing Requirements

### Test Coverage

- **Minimum Coverage:** 80% overall
- **New Code:** Must have 90%+ coverage
- **Critical Paths:** Must have 100% coverage

### Writing Tests

```python
"""Tests for cost calculator module."""

import pytest
from src.utils.cost_calculator import CostCalculator


class TestCostCalculator:
    """Test suite for CostCalculator class."""

    def test_estimate_cost_standard_quality(self):
        """Test cost estimation for standard quality."""
        text = "A" * 1_000_000
        cost = CostCalculator.estimate_cost(text, "standard")
        assert cost == 15.00

    @pytest.mark.parametrize("quality,expected_rate", [
        ("standard", 15.00),
        ("hd", 30.00),
    ])
    def test_estimate_cost_different_qualities(self, quality, expected_rate):
        """Test cost estimation across different quality levels."""
        text = "A" * 100_000
        cost = CostCalculator.estimate_cost(text, quality)
        expected = round((100_000 / 1_000_000) * expected_rate, 4)
        assert cost == expected
```

### Test Categories

- **Unit Tests:** Fast, isolated tests for individual functions
- **Integration Tests:** Tests for component interactions
- **End-to-End Tests:** Complete workflow tests

Use appropriate markers:

```python
@pytest.mark.unit
def test_unit_function():
    pass

@pytest.mark.integration
def test_integration_workflow():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

## 🔍 Pull Request Process

### Before Submitting

- ✅ All tests pass locally
- ✅ Code is formatted (Black)
- ✅ Imports are sorted (isort)
- ✅ No linting errors (Flake8)
- ✅ Coverage is maintained or improved
- ✅ Documentation is updated
- ✅ CHANGELOG.md is updated (if applicable)

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing locally

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review performed
- [ ] Comments added to hard-to-understand areas
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests provide good coverage
- [ ] CHANGELOG.md updated (if applicable)
```

### Review Process

1. **Automated Checks:** GitHub Actions will run tests, linting, and security scans
2. **Code Review:** At least one maintainer will review your code
3. **Changes Requested:** Address feedback and push updates
4. **Approval:** Once approved, your PR will be merged

### After Merge

- Your contribution will be credited in the CHANGELOG
- Delete your feature branch
- Pull the latest main branch

## 🐛 Reporting Bugs

### Before Reporting

1. Check existing issues
2. Verify it's reproducible
3. Collect relevant information

### Bug Report Template

```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- OS: [e.g. macOS 12.0]
- Python version: [e.g. 3.11]
- Voicebook version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation ideas**
If you have ideas on how to implement this, share them here.
```

## 📚 Additional Resources

- [Project README](README.md)
- [Test Documentation](tests/README.md)
- [GitHub Actions Workflows](.github/workflows/)
- [Python Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

## ❓ Questions?

If you have questions:

1. Check the [README](README.md)
2. Search existing issues
3. Create a new discussion
4. Ask in pull request comments

## 🙏 Thank You!

Your contributions make Voicebook better for everyone. We appreciate your time and effort!

---

**Happy Coding! 🚀**
