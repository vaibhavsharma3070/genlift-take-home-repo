# Algorithm Explanation

## Overview

The pattern extraction algorithm operates in two distinct phases to balance accuracy with generalization. This document provides a detailed walkthrough of the implementation logic and design decisions.

## Phase 1: Basic Pattern Extraction

### Objective
Transform raw dot-separated keys into standardized regex patterns by replacing numeric segments with `\d+` and properly escaping special characters.

### Process Flow

1. **Input Parsing**
   ```python
   "users.0.id" → ["users", "0", "id"]
   ```

2. **Segment Classification**
   - Numeric segments: `segment.isdigit()` → Replace with `\d+`
   - Static segments: Escape regex special characters

3. **Regex Character Escaping**
   ```python
   Special characters: . ^ $ * + ? { } [ ] | ( )
   "api[v1]" → "api\\[v1\\]"
   "cache(redis)" → "cache\\(redis\\)"
   ```

4. **Pattern Assembly**
   ```python
   ["users", "\d+", "id"] → "users\\.\\d+\\.id"
   ```

5. **Deduplication**
   Multiple input keys may produce identical patterns:
   ```python
   "users.0.id" → "users\\.\\d+\\.id"
   "users.1.id" → "users\\.\\d+\\.id"  # Same pattern
   "users.5.id" → "users\\.\\d+\\.id"  # Same pattern
   ```

### Implementation Details

```python
def _extract_basic_patterns(keys: List[str]) -> Dict[str, int]:
    pattern_counts = defaultdict(int)
    
    for key in keys:
        segments = key.split('.')
        processed_segments = []
        
        for segment in segments:
            if segment.isdigit():
                processed_segments.append('\\d+')
            else:
                escaped_segment = _escape_regex_chars(segment)
                processed_segments.append(escaped_segment)
        
        pattern = '\\.'.join(processed_segments)
        pattern_counts[pattern] += 1
    
    return pattern_counts
```

## Phase 2: Advanced Generalization

### Objective
Identify groups of patterns that differ only in their final segment and apply frequency-based generalization rules to reduce pattern proliferation while maintaining meaningful distinctions.

### Grouping Strategy

1. **Prefix Extraction**
   ```python
   "users\\.\\d+\\.id"   → prefix: "users\\.\\d+", final: "id"
   "users\\.\\d+\\.name" → prefix: "users\\.\\d+", final: "name"
   "users\\.\\d+\\.email"→ prefix: "users\\.\\d+", final: "email"
   ```

2. **Group Formation**
   Patterns sharing the same prefix form a candidate group for generalization.

### Frequency Analysis

The algorithm calculates what percentage of the **original input keys** each pattern group represents:

```python
frequency_percentage = (total_group_keys / total_original_keys) * 100
```

**Example Calculation:**
- Original input: 13 keys
- Group "users.X.field": represents 10 original keys
- Frequency: 10/13 = 76.9%

### Generalization Rules

The three-tier frequency system balances between over-generalization and under-generalization:

#### Rule 1: Below 75% - Keep Separate
**Rationale:** Insufficient similarity suggests these are genuinely different patterns that happen to share a prefix by coincidence.

```python
# Example: 3 out of 15 keys = 20%
["users.1.name", "users.1.email", "users.1.age", 
 "orders.1.total", "products.1.price", ...]
# Keep: users\\.\\d+\\.name, users\\.\\d+\\.email, users\\.\\d+\\.age
```

#### Rule 2: 75-95% - Generalize with \\w+
**Rationale:** Strong pattern similarity indicates a structural relationship. The final segments represent variations of the same concept (user fields, order properties, etc.).

```python
# Example: 10 out of 13 keys = 76.9%
["users.1.name", "users.1.email", "users.1.age", ..., 
 "orders.3.total", "orders.3.currency", "orders.3.created_at"]
# Generalize: users\\.\\d+\\.\\w+
```

#### Rule 3: 95%+ - Keep Separate (Avoid Over-generalization)
**Rationale:** When nearly all keys follow the same pattern, it's likely an intentional, specific schema. Generalization would lose important structural information.

```python
# Example: 10 out of 10 keys = 100%
["users.1.id", "users.2.id", "users.3.id", ...]
# Keep: users\\.\\d+\\.id (specific pattern is meaningful)
```

### Implementation Logic

```python
def _apply_frequency_generalization(pattern_counts: Dict[str, int], total_keys: int) -> Set[str]:
    prefix_groups = defaultdict(list)
    
    # Group patterns by prefix
    for pattern, count in pattern_counts.items():
        segments = pattern.split('\\.')
        if len(segments) > 1:
            prefix = '\\.'.join(segments[:-1])
            final_segment = segments[-1]
            prefix_groups[prefix].append((pattern, final_segment, count))
    
    final_patterns = set()
    
    for prefix, group_patterns in prefix_groups.items():
        total_group_keys = sum(count for _, _, count in group_patterns)
        frequency_percentage = (total_group_keys / total_keys) * 100
        
        if frequency_percentage < 75 or frequency_percentage >= 95:
            # Keep individual patterns
            for pattern, _, _ in group_patterns:
                final_patterns.add(pattern)
        else:
            # Generalize final segment
            generalized_pattern = prefix + '\\.' + '\\w+'
            final_patterns.add(generalized_pattern)
    
    return final_patterns
```

## Edge Cases and Considerations

### Single Segment Keys
Keys without dots (e.g., `"standalone"`) cannot be meaningfully grouped or generalized, so they're preserved as-is.

### Empty/Invalid Input
- Empty strings are filtered out during processing
- Empty input lists return empty pattern sets
- Malformed keys are handled gracefully

### Complex Nesting
The algorithm handles arbitrary nesting levels:
```python
"api.v1.users.123.orders.456.items.789.details" 
→ "api\\.v1\\.users\\.\\d+\\.orders\\.\\d+\\.items\\.\\d+\\.details"
```

### Performance Characteristics
- **Time Complexity:** O(n × m) where n = number of keys, m = average key length
- **Space Complexity:** O(n) for pattern storage
- **Scalability:** Linear growth with input size

## Design Rationale

### Why Two Phases?
Separating basic extraction from advanced generalization allows for:
- Clear separation of concerns
- Easier testing and debugging
- Flexibility to adjust generalization rules independently
- Better performance through early deduplication

### Why Frequency-Based Rules?
The three-tier system addresses common real-world scenarios:
- **Random coincidences** (< 75%): Don't over-generalize
- **Structural patterns** (75-95%): Beneficial generalization
- **Intentional schemas** (≥ 95%): Preserve specificity

### Why \\w+ for Final Segments?
- Matches common field naming conventions (alphanumeric + underscore)
- More restrictive than `.*` but flexible enough for real data
- Aligns with typical JSON/API field patterns

This approach provides robust pattern extraction suitable for schema inference, alert grouping, and anomaly detection while maintaining the semantic meaning of the original data structure.