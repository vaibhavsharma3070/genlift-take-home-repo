"""
Usage examples demonstrating different scenarios.
"""
from pattern_extractor import extract_generalized_patterns


def example_basic_usage():
    """Demonstrate basic pattern extraction."""
    print("=== Basic Usage Example ===")
    
    keys = [
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
    
    patterns = extract_generalized_patterns(keys)
    
    print("Input keys:")
    for key in keys:
        print(f"  {key}")
    
    print("\nGenerated patterns:")
    for pattern in sorted(patterns):
        print(f"  {pattern}")


def example_advanced_generalization():
    """Demonstrate advanced generalization with frequency rules."""
    print("\n=== Advanced Generalization Example ===")
    
    keys = [
        "users.1.name", "users.1.email", "users.1.age",
        "users.1.phone", "users.1.address", "users.1.country",
        "users.1.postal_code", "users.1.preferences", 
        "users.1.is_active", "users.1.metadata",  # 10 users keys
        "orders.3.total", "orders.3.currency", "orders.3.created_at"  # 3 orders keys
    ]
    
    patterns = extract_generalized_patterns(keys)
    
    print("Input keys:")
    for key in keys:
        print(f"  {key}")
    
    print(f"\nAnalysis:")
    print(f"  Total keys: {len(keys)}")
    print(f"  Users pattern frequency: {10}/{len(keys)} = {10/len(keys)*100:.1f}%")
    print(f"  Orders pattern frequency: {3}/{len(keys)} = {3/len(keys)*100:.1f}%")
    
    print(f"\nGenerated patterns:")
    for pattern in sorted(patterns):
        print(f"  {pattern}")
    
    print(f"\nExplanation:")
    print(f"  - Users pattern (76.9%) is between 75-95%, so generalized to \\w+")
    print(f"  - Orders pattern (23.1%) is below 75%, so kept separate")


def example_special_characters():
    """Demonstrate handling of special regex characters."""
    print("\n=== Special Characters Example ===")
    
    keys = [
        "api[v1].users.0.data",
        "cache(redis).keys.1.value", 
        "logs+debug.2.message",
        "query*.results.5.item"
    ]
    
    patterns = extract_generalized_patterns(keys)
    
    print("Input keys with special characters:")
    for key in keys:
        print(f"  {key}")
    
    print("\nGenerated patterns (properly escaped):")
    for pattern in sorted(patterns):
        print(f"  {pattern}")


if __name__ == "__main__":
    example_basic_usage()
    example_advanced_generalization() 
    example_special_characters()