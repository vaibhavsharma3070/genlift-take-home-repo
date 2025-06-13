# Dynamic Regex Pattern Generalization

A robust tool for extracting and generalizing regex patterns from structured dot-separated keys commonly found in logs, flattened JSONs, and event payloads.

## Problem Overview

When processing structured data keys like `users.0.id`, `orders.12.items.3.price`, we need to:
- Identify recurring structural patterns
- Replace numeric indices with regex patterns
- Generalize similar patterns when appropriate
- Support downstream use cases like schema inference and alert grouping

## Solution Architecture

### Two-Phase Approach

**Phase 1: Basic Pattern Extraction**
- Parse dot-separated keys into segments  
- Replace numeric segments with `\d+` regex
- Properly escape special regex characters
- Deduplicate identical patterns

**Phase 2: Advanced Generalization**
- Group patterns by structural similarity (same prefix, different final segment)
- Apply frequency-based generalization rules
- Replace final segments with `\w+` when appropriate

### Generalization Rules

- **< 75% frequency**: Keep patterns separate (insufficient similarity)
- **75-95% frequency**: Generalize final segment to `\w+` (optimal generalization)  
- **≥ 95% frequency**: Keep patterns separate (assume intentional specificity)

## Installation & Usage

```bash
git clone https://github.com/vaibhavsharma3070/genlift-take-home-repo.git
cd pattern-extractor
python -m pytest tests/
```

```python
from pattern_extractor import extract_generalized_patterns

keys = [
    "users.0.id",
    "users.1.name", 
    "orders.12.items.3.price"
]

patterns = extract_generalized_patterns(keys)
print(patterns)
# {'users\\.\\d+\\.id', 'users\\.\\d+\\.name', 'orders\\.\\d+\\.items\\.\\d+\\.price'}
```

## Implementation Details

The core algorithm handles several edge cases:
- Special regex characters in static segments (dots, brackets, etc.)
- Nested numeric indices at multiple levels
- Mixed data structures with varying depths
- Performance optimization for large key sets

## Testing Strategy

Comprehensive test suite covering:
- Basic pattern extraction accuracy
- Advanced generalization logic
- Edge cases and malformed inputs
- Performance benchmarks
- Real-world data scenarios

## Performance Characteristics

- **Time Complexity**: O(n * m) where n = number of keys, m = average key length
- **Space Complexity**: O(n) for pattern storage
