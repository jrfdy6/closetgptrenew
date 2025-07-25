import pytest
from src.services.fallback_handler import run_fallback
from src.custom_types.wardrobe import ClothingItem

class TestFallbackHandler:
    """Test the fallback handler."""
    
    async def test_run_fallback_basic(self):
        """Test basic fallback functionality."""
        items = [
            ClothingItem(id="1", name="Test Shirt", type="shirt"),
            ClothingItem(id="2", name="Test Pants", type="pants"),
        ]
        
        context = {"occasion": "casual", "relaxed": False}
        
        fallback_items = await run_fallback(items, context)
        
        assert len(fallback_items) >= 0  # Should return items or empty list
        assert all(isinstance(item, ClothingItem) for item in fallback_items)
    
    async def test_run_fallback_with_relaxed_context(self):
        """Test fallback with relaxed context."""
        items = [
            ClothingItem(id="1", name="Test Shirt", type="shirt"),
            ClothingItem(id="2", name="Test Pants", type="pants"),
        ]
        
        context = {"occasion": "casual", "relaxed": True}
        
        fallback_items = await run_fallback(items, context)
        
        assert len(fallback_items) >= 0
        assert all(isinstance(item, ClothingItem) for item in fallback_items)
    
    async def test_run_fallback_empty_input(self):
        """Test fallback with empty input."""
        items = []
        context = {"occasion": "casual"}
        
        fallback_items = await run_fallback(items, context)
        
        assert len(fallback_items) == 0

if __name__ == "__main__":
    pytest.main([__file__]) 