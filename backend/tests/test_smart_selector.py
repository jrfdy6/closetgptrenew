import pytest
from src.services.smart_selector import select_items, score_items, pick_top_ranked_items
from tests.test_helpers import create_test_clothing_item

class TestSmartSelector:
    """Test the smart selection phase."""
    
    def test_score_items(self):
        items = [
            create_test_clothing_item(id="1", name="Test Shirt", type="shirt"),
            create_test_clothing_item(id="2", name="Test Pants", type="pants"),
        ]
        context = {"occasion": "casual", "style": "casual"}
        scored = score_items(items, context)
        assert len(scored) == 2
        assert all("item" in entry for entry in scored)
        assert all("score" in entry for entry in scored)
    
    def test_pick_top_ranked_items(self):
        items = [
            create_test_clothing_item(id="1", name="Test Shirt", type="shirt"),
            create_test_clothing_item(id="2", name="Test Pants", type="pants"),
        ]
        scored = [
            {"item": items[0], "score": 0.9},
            {"item": items[1], "score": 0.7},
        ]
        selected = pick_top_ranked_items(scored)
        assert len(selected) == 2
        assert selected[0].id == "1"
        assert selected[1].id == "2"
    
    # To run async tests, use pytest-asyncio
    # @pytest.mark.asyncio
    # async def test_select_items_integration(self):
    #     items = [
    #         create_test_clothing_item(id="1", name="Test Shirt", type="shirt"),
    #         create_test_clothing_item(id="2", name="Test Pants", type="pants"),
    #     ]
    #     context = {"occasion": "casual", "style": "casual"}
    #     selected = await select_items(items, context)
    #     assert len(selected) == 2
    #     assert all(isinstance(item, ClothingItem) for item in selected)

if __name__ == "__main__":
    pytest.main([__file__]) 