import re
from typing import List, Set, Dict, Tuple
from collections import defaultdict, Counter


def extract_generalized_patterns(keys: List[str]) -> Set[str]:
    """
    Extract generalized regex patterns from structured dot-separated keys.
    
    Args:
        keys: List of dot-separated keys (e.g., ['users.0.id', 'orders.12.total'])
    
    Returns:
        Set of regex patterns with numeric segments replaced by \\d+ and 
        optionally generalized final segments using \\w+
    """
    if not keys:
        return set()
    
    # Phase 1: Basic pattern extraction
    basic_patterns = _extract_basic_patterns(keys)
    
    # Phase 2: Advanced generalization based on frequency
    generalized_patterns = _apply_frequency_generalization(basic_patterns, len(keys))
    
    return generalized_patterns


def _extract_basic_patterns(keys: List[str]) -> Dict[str, int]:
    """
    Phase 1: Extract basic patterns by replacing numeric segments with \\d+
    
    Returns:
        Dict mapping pattern -> count of original keys it represents
    """
    pattern_counts = defaultdict(int)
    
    for key in keys:
        if not key.strip():
            continue
            
        segments = key.split('.')
        processed_segments = []
        
        for segment in segments:
            # Check if segment is purely numeric
            if segment.isdigit():
                processed_segments.append('\\d+')
            else:
                # Escape special regex characters in non-numeric segments
                escaped_segment = _escape_regex_chars(segment)
                processed_segments.append(escaped_segment)
        
        # Join with escaped dots
        pattern = '\\.'.join(processed_segments)
        pattern_counts[pattern] += 1
    
    return pattern_counts


def _escape_regex_chars(segment: str) -> str:
    """
    Escape special regex characters in static segments.
    
    Args:
        segment: Raw segment that may contain regex special chars
        
    Returns:
        Escaped segment safe for regex use
    """
    # Characters that need escaping in regex
    special_chars = r'\.^$*+?{}[]|()'
    
    escaped = ""
    for char in segment:
        if char in special_chars:
            escaped += '\\' + char
        else:
            escaped += char
    
    return escaped


def _apply_frequency_generalization(pattern_counts: Dict[str, int], total_keys: int) -> Set[str]:
    """
    Phase 2: Apply frequency-based generalization to patterns that differ only in final segment.
    
    Args:
        pattern_counts: Dict of pattern -> count from Phase 1
        total_keys: Total number of original input keys
        
    Returns:
        Set of final patterns with appropriate generalizations applied
    """
    # Group patterns by their prefix (everything except last segment)
    prefix_groups = defaultdict(list)
    
    for pattern, count in pattern_counts.items():
        segments = pattern.split('\\.')
        if len(segments) > 1:
            prefix = '\\.'.join(segments[:-1])
            final_segment = segments[-1]
            prefix_groups[prefix].append((pattern, final_segment, count))
        else:
            # Single segment patterns can't be generalized
            prefix_groups[pattern].append((pattern, "", count))
    
    final_patterns = set()
    
    for prefix, group_patterns in prefix_groups.items():
        if len(group_patterns) == 1:
            # Single pattern in group - keep as is
            pattern, _, _ = group_patterns[0]
            final_patterns.add(pattern)
            continue
        
        # Calculate total keys represented by this prefix group
        total_group_keys = sum(count for _, _, count in group_patterns)
        frequency_percentage = (total_group_keys / total_keys) * 100
        
        # Apply generalization rules
        if frequency_percentage < 75:
            # Below 75% - keep all patterns separate
            for pattern, _, _ in group_patterns:
                final_patterns.add(pattern)
        elif frequency_percentage >= 95:
            # 95%+ - assume intentional, keep separate
            for pattern, _, _ in group_patterns:
                final_patterns.add(pattern)
        else:
            # 75-95% - generalize final segment
            if prefix:  # Ensure we have a meaningful prefix
                generalized_pattern = prefix + '\\.' + '\\w+'
                final_patterns.add(generalized_pattern)
            else:
                # Fallback to individual patterns if no prefix
                for pattern, _, _ in group_patterns:
                    final_patterns.add(pattern)
    
    return final_patterns


def _analyze_pattern_groups(pattern_counts: Dict[str, int]) -> Dict[str, List[Tuple[str, str, int]]]:
    """
    Helper function to analyze and group patterns for debugging/testing.
    
    Returns:
        Dict mapping prefix -> list of (full_pattern, final_segment, count)
    """
    prefix_groups = defaultdict(list)
    
    for pattern, count in pattern_counts.items():
        segments = pattern.split('\\.')
        if len(segments) > 1:
            prefix = '\\.'.join(segments[:-1])
            final_segment = segments[-1]
            prefix_groups[prefix].append((pattern, final_segment, count))
    
    return dict(prefix_groups)


# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    sample_keys = [
        "users.0.id",
        "users.1.name",
        "users.2.email",
        "orders.0.items.3.price",
        "orders.0.items.3.quantity",
        "orders.2.total",
        "products.10.name",
        "products.12.price",
        "users.10.id"
    ]
    
    result = extract_generalized_patterns(sample_keys)
    print("Basic extraction result:")
    for pattern in sorted(result):
        print(f"  {pattern}")
    
    # Test advanced generalization
    advanced_keys = [
        "users.1.name",
        "users.1.email", 
        "users.1.age",
        "users.1.phone",
        "users.1.address",
        "users.1.country",
        "users.1.postal_code",
        "users.1.preferences",
        "users.1.is_active",
        "users.1.metadata",
        "orders.3.total",
        "orders.3.currency",
        "orders.3.created_at"
    ]
    
    advanced_result = extract_generalized_patterns(advanced_keys)
    print("\nAdvanced generalization result:")
    for pattern in sorted(advanced_result):
        print(f"  {pattern}")