import pytest
from pattern_extractor import (
    extract_generalized_patterns,
    _extract_basic_patterns,
    _escape_regex_chars,
    _apply_frequency_generalization
)


class TestBasicPatternExtraction:
    """Test Phase 1: Basic pattern extraction functionality."""
    
    def test_simple_numeric_replacement(self):
        """Test basic numeric segment replacement."""
        keys = ["users.0.id", "users.1.id", "products.5.name"]
        result = extract_generalized_patterns(keys)
        
        expected = {
            "users\\.\\d+\\.id",
            "products\\.\\d+\\.name"
        }
        assert result == expected
    
    def test_multiple_numeric_segments(self):
        """Test patterns with multiple numeric segments."""
        keys = [
            "orders.0.items.3.price",
            "orders.1.items.5.quantity",
            "data.10.nested.20.value"
        ]
        result = extract_generalized_patterns(keys)
        
        expected = {
            "orders\\.\\d+\\.items\\.\\d+\\.price",
            "orders\\.\\d+\\.items\\.\\d+\\.quantity", 
            "data\\.\\d+\\.nested\\.\\d+\\.value"
        }
        assert result == expected
    
    def test_special_character_escaping(self):
        """Test proper escaping of regex special characters."""
        keys = [
            "api[v1].users.0.data",
            "cache(redis).keys.1.value",
            "logs+debug.2.message"
        ]
        result = extract_generalized_patterns(keys)
        
        # Should properly escape brackets, parentheses, plus signs
        expected = {
            "api\\[v1\\]\\.users\\.\\d+\\.data",
            "cache\\(redis\\)\\.keys\\.\\d+\\.value",
            "logs\\+debug\\.\\d+\\.message"
        }
        assert result == expected
    
    def test_empty_and_invalid_inputs(self):
        """Test handling of edge cases."""
        # Empty input
        assert extract_generalized_patterns([]) == set()
        
        # Empty strings
        result = extract_generalized_patterns(["", "  ", "valid.1.key"])
        assert result == {"valid\\.\\d+\\.key"}
        
        # Single segment keys
        result = extract_generalized_patterns(["standalone", "another"])
        assert result == {"standalone", "another"}


class TestAdvancedGeneralization:
    """Test Phase 2: Advanced frequency-based generalization."""
    
    def test_generalization_75_to_95_percent(self):
        """Test generalization when frequency is between 75-95%."""
        # 10 out of 13 keys follow users.X.field pattern = 76.9%
        keys = [
            "users.1.name", "users.1.email", "users.1.age",
            "users.1.phone", "users.1.address", "users.1.country", 
            "users.1.postal_code", "users.1.preferences", 
            "users.1.is_active", "users.1.metadata",
            "orders.3.total", "orders.3.currency", "orders.3.created_at"
        ]
        
        result = extract_generalized_patterns(keys)
        
        # Should generalize users pattern, keep orders separate
        expected = {
            "users\\.\\d+\\.\\w+",
            "orders\\.\\d+\\.total",
            "orders\\.\\d+\\.currency", 
            "orders\\.\\d+\\.created_at"
        }
        assert result == expected
    
    def test_no_generalization_below_75_percent(self):
        """Test no generalization when frequency is below 75%."""
        keys = [
            "users.1.name", "users.1.email",  # 2 out of 7 = 28.6%
            "orders.1.total", "orders.1.status",
            "products.1.price", "logs.1.message", "cache.1.key"
        ]
        
        result = extract_generalized_patterns(keys)
        
        # Should keep all patterns separate
        expected = {
            "users\\.\\d+\\.name", "users\\.\\d+\\.email",
            "orders\\.\\d+\\.total", "orders\\.\\d+\\.status",
            "products\\.\\d+\\.price", "logs\\.\\d+\\.message", 
            "cache\\.\\d+\\.key"
        }
        assert result == expected
    
    def test_no_generalization_above_95_percent(self):
        """Test no generalization when frequency is 95% or above."""
        keys = [
            "users.1.id", "users.2.id", "users.3.id",
            "users.4.id", "users.5.id", "users.6.id",
            "users.7.id", "users.8.id", "users.9.id",
            "users.10.id",  # 10 out of 10 = 100%
        ]
        
        result = extract_generalized_patterns(keys)
        
        # Should NOT generalize due to 100% frequency
        expected = {"users\\.\\d+\\.id"}
        assert result == expected
    
    def test_mixed_generalization_scenarios(self):
        """Test multiple groups with different generalization outcomes."""
        keys = [
            # Group 1: users.X.field - 8 out of 15 = 53.3% (below 75%, keep separate)
            "users.1.name", "users.1.email", "users.1.age", "users.1.phone",
            "users.1.address", "users.1.country", "users.1.postal", "users.1.active",
            
            # Group 2: orders.X.field - 4 out of 15 = 26.7% (below 75%, keep separate)  
            "orders.1.total", "orders.1.currency", "orders.1.status", "orders.1.date",
            
            # Group 3: products.X.field - 3 out of 15 = 20% (below 75%, keep separate)
            "products.1.name", "products.1.price", "products.1.category"
        ]
        
        result = extract_generalized_patterns(keys)
        
        # All should remain separate since no group reaches 75%
        expected = {
            "users\\.\\d+\\.name", "users\\.\\d+\\.email", "users\\.\\d+\\.age", "users\\.\\d+\\.phone",
            "users\\.\\d+\\.address", "users\\.\\d+\\.country", "users\\.\\d+\\.postal", "users\\.\\d+\\.active",
            "orders\\.\\d+\\.total", "orders\\.\\d+\\.currency", "orders\\.\\d+\\.status", "orders\\.\\d+\\.date",
            "products\\.\\d+\\.name", "products\\.\\d+\\.price", "products\\.\\d+\\.category"
        }
        assert result == expected


class TestHelperFunctions:
    """Test individual helper functions."""
    
    def test_escape_regex_chars(self):
        """Test regex character escaping."""
        assert _escape_regex_chars("normal") == "normal"
        assert _escape_regex_chars("api[v1]") == "api\\[v1\\]"
        assert _escape_regex_chars("cache(redis)") == "cache\\(redis\\)"
        assert _escape_regex_chars("logs+debug") == "logs\\+debug"
        assert _escape_regex_chars("data.nested") == "data\\.nested"
        assert _escape_regex_chars("query*") == "query\\*"
    
    def test_basic_pattern_extraction(self):
        """Test Phase 1 pattern extraction with counts."""
        keys = ["users.0.id", "users.1.id", "orders.5.total"]
        result = _extract_basic_patterns(keys)
        
        expected = {
            "users\\.\\d+\\.id": 2,
            "orders\\.\\d+\\.total": 1
        }
        assert result == expected


class TestRealWorldScenarios:
    """Test with realistic data patterns."""
    
    def test_api_endpoint_patterns(self):
        """Test patterns similar to API endpoints."""
        keys = [
            "api.v1.users.123.profile",
            "api.v1.users.456.settings", 
            "api.v1.orders.789.items.0.details",
            "api.v1.orders.101.status",
            "api.v2.products.202.reviews.5.rating"
        ]
        
        result = extract_generalized_patterns(keys)
        
        expected = {
            "api\\.v1\\.users\\.\\d+\\.profile",
            "api\\.v1\\.users\\.\\d+\\.settings",
            "api\\.v1\\.orders\\.\\d+\\.items\\.\\d+\\.details", 
            "api\\.v1\\.orders\\.\\d+\\.status",
            "api\\.v2\\.products\\.\\d+\\.reviews\\.\\d+\\.rating"
        }
        assert result == expected
    
    def test_log_message_patterns(self):
        """Test patterns from log messages."""
        keys = [
            "app.service1.thread.0.error",
            "app.service1.thread.1.warning",
            "app.service2.cache.hit.10.key", 
            "metrics.cpu.core.0.usage",
            "metrics.cpu.core.1.temperature"
        ]
        
        result = extract_generalized_patterns(keys)
        
        expected = {
            "app\\.service1\\.thread\\.\\d+\\.error",
            "app\\.service1\\.thread\\.\\d+\\.warning",
            "app\\.service2\\.cache\\.hit\\.\\d+\\.key",
            "metrics\\.cpu\\.core\\.\\d+\\.usage",
            "metrics\\.cpu\\.core\\.\\d+\\.temperature"
        }
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])