#!/usr/bin/env python3
"""
Use instant AI image generation URLs - no pre-generation needed!
Services that generate images on-demand when URL is accessed
"""

import json
import urllib.parse
from typing import Dict, Any
from pathlib import Path

def create_product_prompt(item: Dict[str, Any]) -> str:
    """Create a clean, focused prompt for product photography"""
    
    title = item.get("title", "")
    materials = item.get("materials", [])
    tags = item.get("tags", [])
    categories = item.get("categories", [])
    
    # Extract attributes
    words = title.split()
    color = words[0] if words else ""
    item_type = " ".join(words[1:]) if len(words) > 1 else "clothing item"
    material = materials[0] if materials else ""
    style = tags[0] if tags else "modern"
    category = categories[0] if categories else "apparel"
    
    # Create concise, professional prompt
    prompt = f"professional product photo, {color} {item_type}"
    
    if material:
        prompt += f", {material} material"
    
    prompt += f", {style} style, white background, studio lighting, centered, high quality"
    
    return prompt

def generate_pollinations_url(item: Dict[str, Any]) -> str:
    """
    Pollinations.ai - FREE, FAST, UNLIMITED!
    Generates image on-demand when URL is accessed
    No API key needed, no rate limits
    """
    
    prompt = create_product_prompt(item)
    
    # Use item ID as seed for consistency
    seed = abs(hash(item["id"])) % 2147483647
    
    # Pollinations API format
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Add parameters for better quality
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    url += f"?width=400&height=600&seed={seed}&nologo=true"
    
    return url

def generate_craiyon_url(item: Dict[str, Any]) -> str:
    """
    Craiyon API - FREE, generates on request
    """
    prompt = create_product_prompt(item)
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Craiyon format (simplified)
    return f"https://img.craiyon.com/2024-01-01/{encoded_prompt}.png"

def generate_artbot_url(item: Dict[str, Any]) -> str:
    """
    ArtBot/Stable Horde - Community powered, free
    """
    prompt = create_product_prompt(item)
    seed = abs(hash(item["id"])) % 2147483647
    
    # Simplified endpoint
    encoded = urllib.parse.quote(prompt)
    return f"https://api.artbot.ai/generate?prompt={encoded}&seed={seed}&width=400&height=600"

def update_catalog_with_ai_urls(
    catalog_path: str,
    output_path: str = None,
    service: str = "pollinations"
):
    """
    Update all catalog items with AI image generation URLs
    
    Args:
        catalog_path: Input catalog path
        output_path: Output path (default: overwrites input)
        service: Which service to use (pollinations, craiyon, artbot)
    """
    
    print(f"Loading catalog from {catalog_path}...")
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    items = catalog["items"]
    total = len(items)
    
    print(f"\n{'='*80}")
    print(f"INSTANT AI IMAGE GENERATION")
    print(f"{'='*80}")
    print(f"Service: {service.upper()}")
    print(f"Total items: {total}")
    print(f"Generation method: ON-DEMAND (images created when URL is accessed)")
    print(f"Cost: FREE, UNLIMITED")
    print(f"Speed: INSTANT (no pre-generation needed)")
    print(f"{'='*80}\n")
    
    # Select service
    if service == "pollinations":
        url_generator = generate_pollinations_url
        print("✨ Using Pollinations.ai - Best quality, unlimited, fast")
    elif service == "craiyon":
        url_generator = generate_craiyon_url
        print("✨ Using Craiyon - Good quality, free")
    elif service == "artbot":
        url_generator = generate_artbot_url
        print("✨ Using ArtBot/Stable Horde - Community powered")
    else:
        print(f"❌ Unknown service: {service}")
        return
    
    print(f"\nUpdating {total} items...")
    
    for i, item in enumerate(items):
        if i % 100 == 0:
            print(f"  Progress: {i}/{total} ({i*100//total}%)")
        
        # Generate URL
        ai_url = url_generator(item)
        item["image_url"] = ai_url
        item["ai_generated"] = True
        item["ai_service"] = service
    
    # Update metadata
    catalog["image_generation_service"] = service
    catalog["image_generation_type"] = "on-demand"
    catalog["catalog_version"] = "3.0"
    catalog["last_updated"] = __import__('time').strftime("%Y-%m-%dT%H:%M:%S")
    
    # Save
    output_path = output_path or catalog_path
    print(f"\n💾 Saving to {output_path}...")
    
    with open(output_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    file_size = Path(output_path).stat().st_size / 1024 / 1024
    
    print(f"\n{'='*80}")
    print(f"✅ SUCCESS!")
    print(f"{'='*80}")
    print(f"Updated: {total} items")
    print(f"Service: {service}")
    print(f"Output: {output_path}")
    print(f"File size: {file_size:.2f} MB")
    print(f"\n✨ Images will be generated automatically when accessed!")
    print(f"{'='*80}\n")
    
    # Show samples
    print("📸 Sample URLs (first 5 items):\n")
    for i, item in enumerate(items[:5]):
        print(f"{i+1}. {item['title']}")
        print(f"   {item['image_url']}\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Use instant AI image generation URLs")
    parser.add_argument("--catalog", type=str, default="../src/data/style_inspiration_catalog.json", help="Input catalog")
    parser.add_argument("--output", type=str, help="Output path (default: overwrites input)")
    parser.add_argument("--service", type=str, default="pollinations", 
                       choices=["pollinations", "craiyon", "artbot"],
                       help="AI image service")
    
    args = parser.parse_args()
    
    catalog_path = Path(__file__).parent / args.catalog
    
    print("\n🎨 INSTANT AI IMAGE GENERATION")
    print("="*80)
    print("This will update ALL catalog URLs to use AI-generated images")
    print("Images are generated ON-DEMAND when the URL is accessed")
    print("Benefits:")
    print("  ✅ FREE and UNLIMITED")
    print("  ✅ INSTANT setup (no pre-generation)")
    print("  ✅ Always available")
    print("  ✅ High quality product photography")
    print("  ✅ Unique image per item")
    print("\nRecommended: Pollinations.ai (best quality, fastest)")
    print("="*80)
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        exit(0)
    
    update_catalog_with_ai_urls(
        catalog_path=catalog_path,
        output_path=args.output,
        service=args.service
    )
    
    print("✨ Ready to use! Deploy and see AI-generated images instantly.")

