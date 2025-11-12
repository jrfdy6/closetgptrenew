"""
Easy Outfit MCP Server - Apps SDK Integration
Model Context Protocol server for ChatGPT Apps SDK
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        CallToolResult,
    )
except ImportError:
    print("⚠️ MCP SDK not installed. Install with: pip install mcp")
    print("See: https://github.com/modelcontextprotocol/python-sdk")
    raise

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("easyoutfit-mcp")

# Configuration
MAIN_API_URL = os.getenv("MAIN_API_URL", "https://closetgptrenew-production.railway.app")
API_KEY = os.getenv("API_KEY", "")

# Initialize MCP server
server = Server("easy_outfit")

# ============================================
# HELPER FUNCTIONS
# ============================================

async def fetch_wardrobe_from_api(user_id: str, filters: Optional[Dict] = None) -> List[Dict]:
    """Fetch wardrobe items from main API"""
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            params = filters or {}
            response = await client.get(
                f"{MAIN_API_URL}/api/wardrobe",
                params=params,
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
            else:
                logger.error(f"API error: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Failed to fetch wardrobe: {e}")
        return []

def create_outfit_card(outfit: Dict) -> Dict:
    """Create inline card UI component for an outfit"""
    items = outfit.get("items", [])
    
    # Build card structure
    card = {
        "type": "inline_card",
        "title": outfit.get("name", "Outfit Suggestion"),
        "image": items[0].get("imageUrl") if items else None,
        "metadata": [
            {"label": "Occasion", "value": outfit.get("occasion", "Casual")},
            {"label": "Style", "value": outfit.get("style", "Modern")},
        ],
        "badge": outfit.get("season", "All Seasons"),
        "actions": [
            {
                "type": "primary",
                "label": "Wear This",
                "tool": "mark_outfit_worn",
                "params": {"outfit_id": outfit.get("id")}
            }
        ]
    }
    
    # Add item details
    if items:
        card["description"] = " + ".join([
            f"{item.get('name', 'Item')} ({item.get('color', '')})"
            for item in items[:3]
        ])
    
    return card

def create_wardrobe_item_card(item: Dict) -> Dict:
    """Create inline card UI component for a wardrobe item"""
    return {
        "type": "inline_card",
        "image": item.get("imageUrl") or item.get("image_url"),
        "title": item.get("name", "Clothing Item"),
        "metadata": [
            {"label": "Type", "value": item.get("type", "Unknown")},
            {"label": "Color", "value": item.get("color", "Unknown")},
            {"label": "Worn", "value": f"{item.get('wearCount', 0)} times"},
        ],
        "badge": " • ".join(item.get("style", [])),
        "actions": [
            {
                "type": "secondary",
                "label": "View Details",
                "tool": "get_item_details",
                "params": {"item_id": item.get("id")}
            }
        ]
    }

def create_carousel(items: List[Dict], item_type: str = "outfit") -> Dict:
    """Create inline carousel UI component"""
    cards = []
    
    for item in items[:8]:  # Max 8 items per carousel
        if item_type == "outfit":
            cards.append(create_outfit_card(item))
        else:
            cards.append(create_wardrobe_item_card(item))
    
    return {
        "type": "inline_carousel",
        "cards": cards
    }

# ============================================
# TOOL DEFINITIONS
# ============================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools for ChatGPT"""
    return [
        Tool(
            name="get_wardrobe",
            description="Get user's wardrobe items with optional filters. Returns a visual carousel of clothing items.",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "description": "Filter by clothing type (e.g., 'shirt', 'pants', 'dress')",
                        "enum": ["shirt", "pants", "dress", "skirt", "jacket", "sweater", "shoes", "accessory", "all"]
                    },
                    "style": {
                        "type": "string",
                        "description": "Filter by style (e.g., 'casual', 'formal', 'athletic')"
                    },
                    "color": {
                        "type": "string",
                        "description": "Filter by color"
                    },
                    "season": {
                        "type": "string",
                        "description": "Filter by season",
                        "enum": ["spring", "summer", "fall", "winter", "all"]
                    }
                }
            }
        ),
        Tool(
            name="suggest_outfits",
            description="Generate personalized outfit recommendations based on occasion, weather, and user preferences. Returns a carousel of complete outfit suggestions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "occasion": {
                        "type": "string",
                        "description": "The occasion or event (e.g., 'work', 'date', 'gym', 'casual')",
                        "enum": ["work", "date", "party", "gym", "casual", "formal", "wedding", "interview"]
                    },
                    "weather": {
                        "type": "string",
                        "description": "Current weather or temperature",
                        "enum": ["hot", "warm", "cool", "cold", "rainy", "snowy"]
                    },
                    "style": {
                        "type": "string",
                        "description": "Preferred style aesthetic",
                        "enum": ["casual", "professional", "trendy", "classic", "athletic", "bohemian"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of outfit suggestions (1-5)",
                        "default": 3
                    }
                },
                "required": ["occasion"]
            }
        ),
        Tool(
            name="add_wardrobe_item",
            description="Add a new clothing item to the user's wardrobe. Can analyze uploaded images or accept manual descriptions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name or description of the item"
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of clothing",
                        "enum": ["shirt", "pants", "dress", "skirt", "jacket", "sweater", "shoes", "accessory", "other"]
                    },
                    "color": {
                        "type": "string",
                        "description": "Primary color of the item"
                    },
                    "style": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Style tags (e.g., ['casual', 'summer'])"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "URL of item image (if available)"
                    }
                },
                "required": ["name", "type", "color"]
            }
        ),
        Tool(
            name="get_wardrobe_stats",
            description="Get statistics and insights about the user's wardrobe (total items, most worn, style breakdown).",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="mark_outfit_worn",
            description="Mark an outfit as worn and update wear counts for all items in the outfit.",
            inputSchema={
                "type": "object",
                "properties": {
                    "outfit_id": {
                        "type": "string",
                        "description": "ID of the outfit that was worn"
                    }
                },
                "required": ["outfit_id"]
            }
        ),
        Tool(
            name="get_item_details",
            description="Get detailed information about a specific wardrobe item including wear history and styling suggestions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "ID of the wardrobe item"
                    }
                },
                "required": ["item_id"]
            }
        )
    ]

# ============================================
# TOOL IMPLEMENTATIONS
# ============================================

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from ChatGPT"""
    
    logger.info(f"Tool called: {name} with args: {arguments}")
    
    if name == "get_wardrobe":
        return await handle_get_wardrobe(arguments)
    elif name == "suggest_outfits":
        return await handle_suggest_outfits(arguments)
    elif name == "add_wardrobe_item":
        return await handle_add_item(arguments)
    elif name == "get_wardrobe_stats":
        return await handle_get_stats(arguments)
    elif name == "mark_outfit_worn":
        return await handle_mark_worn(arguments)
    elif name == "get_item_details":
        return await handle_item_details(arguments)
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def handle_get_wardrobe(args: Dict) -> List[TextContent]:
    """Handle get_wardrobe tool call"""
    
    # Fetch items from API
    filters = {k: v for k, v in args.items() if v and v != "all"}
    items = await fetch_wardrobe_from_api("user_id", filters)
    
    if not items:
        return [TextContent(
            type="text",
            text="Your wardrobe is empty. Try adding some items first!"
        )]
    
    # Create carousel UI component
    carousel = create_carousel(items, item_type="item")
    
    # Return as embedded resource (UI component)
    return [
        TextContent(
            type="text",
            text=json.dumps({
                "display": "inline_carousel",
                "component": carousel,
                "summary": f"Found {len(items)} items in your wardrobe"
            })
        )
    ]

async def handle_suggest_outfits(args: Dict) -> List[TextContent]:
    """Handle suggest_outfits tool call"""
    
    occasion = args.get("occasion", "casual")
    weather = args.get("weather")
    style = args.get("style")
    limit = args.get("limit", 3)
    
    # Fetch user's wardrobe
    items = await fetch_wardrobe_from_api("user_id")
    
    if not items:
        return [TextContent(
            type="text",
            text="I need some items in your wardrobe first to create outfits!"
        )]
    
    # Generate outfits (simplified for now - call your outfit generation service)
    outfits = generate_outfits(items, occasion, weather, style, limit)
    
    # Create carousel of outfits
    carousel = create_carousel(outfits, item_type="outfit")
    
    return [
        TextContent(
            type="text",
            text=json.dumps({
                "display": "inline_carousel",
                "component": carousel,
                "summary": f"Here are {len(outfits)} outfit suggestions for {occasion}"
            })
        )
    ]

async def handle_add_item(args: Dict) -> List[TextContent]:
    """Handle add_wardrobe_item tool call"""
    
    # Add item via API
    import httpx
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{MAIN_API_URL}/api/wardrobe/add",
                json=args,
                headers={"Authorization": f"Bearer {API_KEY}"},
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                item = data.get("item", {})
                
                # Create success card
                card = create_wardrobe_item_card(item)
                
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "display": "inline_card",
                        "component": card,
                        "summary": f"✅ Added {args['name']} to your wardrobe!"
                    })
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Failed to add item: {response.status_code}"
                )]
    except Exception as e:
        logger.error(f"Error adding item: {e}")
        return [TextContent(
            type="text",
            text=f"Error adding item: {str(e)}"
        )]

async def handle_get_stats(args: Dict) -> List[TextContent]:
    """Handle get_wardrobe_stats tool call"""
    
    items = await fetch_wardrobe_from_api("user_id")
    
    if not items:
        return [TextContent(
            type="text",
            text="Your wardrobe is empty!"
        )]
    
    # Calculate stats
    total = len(items)
    types = {}
    colors = {}
    total_wears = sum(item.get("wearCount", 0) for item in items)
    
    for item in items:
        item_type = item.get("type", "unknown")
        types[item_type] = types.get(item_type, 0) + 1
        
        color = item.get("color", "unknown")
        colors[color] = colors.get(color, 0) + 1
    
    most_common_type = max(types.items(), key=lambda x: x[1])[0] if types else "none"
    most_common_color = max(colors.items(), key=lambda x: x[1])[0] if colors else "none"
    
    # Create stats card
    card = {
        "type": "inline_card",
        "title": "Your Wardrobe Stats",
        "metadata": [
            {"label": "Total Items", "value": str(total)},
            {"label": "Most Common Type", "value": most_common_type.title()},
            {"label": "Most Common Color", "value": most_common_color.title()},
            {"label": "Total Wears", "value": str(total_wears)},
        ]
    }
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "display": "inline_card",
            "component": card,
            "summary": f"You have {total} items in your wardrobe"
        })
    )]

async def handle_mark_worn(args: Dict) -> List[TextContent]:
    """Handle mark_outfit_worn tool call"""
    outfit_id = args.get("outfit_id")
    
    # Update wear counts via API
    # TODO: Implement actual API call
    
    return [TextContent(
        type="text",
        text=f"✅ Marked outfit as worn!"
    )]

async def handle_item_details(args: Dict) -> List[TextContent]:
    """Handle get_item_details tool call"""
    item_id = args.get("item_id")
    
    # Fetch item details via API
    # TODO: Implement actual API call
    
    return [TextContent(
        type="text",
        text=f"Item details for {item_id}"
    )]

# ============================================
# HELPER: OUTFIT GENERATION
# ============================================

def generate_outfits(items: List[Dict], occasion: str, weather: Optional[str], style: Optional[str], limit: int) -> List[Dict]:
    """Simple outfit generation logic"""
    
    # Group items by type
    tops = [i for i in items if i.get("type") in ["shirt", "blouse", "sweater", "jacket"]]
    bottoms = [i for i in items if i.get("type") in ["pants", "jeans", "shorts", "skirt"]]
    shoes = [i for i in items if i.get("type") == "shoes"]
    
    outfits = []
    
    # Generate simple combinations
    for i, top in enumerate(tops[:limit]):
        if i >= len(bottoms):
            break
            
        bottom = bottoms[i]
        shoe = shoes[0] if shoes else None
        
        outfit_items = [top, bottom]
        if shoe:
            outfit_items.append(shoe)
        
        outfits.append({
            "id": f"outfit_{i}",
            "name": f"{top.get('name')} + {bottom.get('name')}",
            "items": outfit_items,
            "occasion": occasion,
            "style": style or "casual",
            "season": top.get("season", ["all"])[0]
        })
    
    return outfits[:limit]

# ============================================
# MAIN ENTRY POINT
# ============================================

async def main():
    """Run the MCP server"""
    logger.info("🚀 Starting Easy Outfit MCP Server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

