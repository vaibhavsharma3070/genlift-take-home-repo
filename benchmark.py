"""
Performance benchmarking for pattern extraction.
"""
import time
import random
import string
from pattern_extractor import extract_generalized_patterns


def generate_test_keys(num_keys: int, max_depth: int = 5) -> list:
    """Generate realistic test keys for benchmarking."""
    prefixes = ['users', 'orders', 'products', 'api', 'logs', 'metrics', 'cache']
    suffixes = ['id', 'name', 'status', 'value', 'data', 'config', 'meta']
    
    keys = []
    for _ in range(num_keys):
        depth = random.randint(2, max_depth)
        segments = []
        
        # Add prefix
        segments.append(random.choice(prefixes))
        
        # Add middle segments (mix of numbers and strings)
        for i in range(depth - 2):
            if random.random() < 0.4:  # 40% chance of numeric segment
                segments.append(str(random.randint(0, 100)))
            else:
                segments.append(f"section{i}")
        
        # Add suffix
        segments.append(random.choice(suffixes))
        
        keys.append('.'.join(segments))
    
    return keys


def benchmark_performance():
    """Run performance benchmarks."""
    test_sizes = [100, 500, 1000, 5000, 10000]
    
    print("Pattern Extraction Performance Benchmark")
    print("=" * 50)
    
    for size in test_sizes:
        keys = generate_test_keys(size)
        
        start_time = time.time()
        patterns = extract_generalized_patterns(keys)
        end_time = time.time()
        
        duration = end_time - start_time
        keys_per_second = size / duration if duration > 0 else float('inf')
        
        print(f"Keys: {size:5d} | Time: {duration:.4f}s | Rate: {keys_per_second:.0f} keys/s | Patterns: {len(patterns)}")


if __name__ == "__main__":
    benchmark_performance()