#!/usr/bin/env python3
"""
Add real product images to the style catalog
Uses multiple image services with smart search terms
"""

import json
import hashlib
import time
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

# Free image services (no API key required)
IMAGE_SERVICES = {
    "unsplash": "https://source.unsplash.com/400x600/?{query}",
    "picsum": "https://picsum.photos/seed/{seed}/400/600",
}

# Curated Unsplash collections for fashion
FASHION_COLLECTIONS = {
    "tops": "1163637",
    "bottoms": "1462375", 
    "outerwear": "1163637",
    "footwear": "1362449",
    "dresses": "1362449",
    "accessories": "1163637"
}

def generate_search_query(item: Dict[str, Any]) -> str:
    """Generate a smart search query for the item"""
    
    # Extract key attributes
    title = item.get("title", "")
    category = item.get("categories", [""])[0]
    materials = item.get("materials", [])
    tags = item.get("tags", [])
    
    # Build search terms
    search_terms = []
    
    # Add main item type (from title)
    item_type = title.split()[-1] if title else category
    search_terms.append(item_type.lower())
    
    # Add primary material
    if materials:
        search_terms.append(materials[0].lower())
    
    # Add style descriptor from tags
    style_tags = [t for t in tags if t in ["luxury", "casual", "elegant", "modern", "vintage"]]
    if style_tags:
        search_terms.append(style_tags[0])
    
    # Join terms
    query = "+".join(search_terms[:3])  # Max 3 terms for best results
    
    return query

def generate_unsplash_url(item: Dict[str, Any], use_collection: bool = False) -> str:
    """Generate Unsplash image URL with specific search terms"""
    
    # Build a specific search query from item attributes
    title = item.get("title", "").lower()
    materials = item.get("materials", [])
    tags = item.get("tags", [])
    
    # Extract key terms
    search_terms = []
    
    # Add item type (from title)
    title_words = title.split()
    if len(title_words) >= 2:
        # Get the item type (usually last word)
        item_type = title_words[-1]
        search_terms.append(item_type)
    
    # Add color if it's a common color
    color = title_words[0] if title_words else ""
    common_colors = ["black", "white", "grey", "gray", "blue", "navy", "red", "burgundy", 
                     "green", "brown", "tan", "beige", "pink", "purple", "yellow", "orange"]
    if color in common_colors:
        search_terms.append(color)
    
    # Add material if relevant
    if materials and len(search_terms) < 3:
        mat = materials[0].lower()
        if mat in ["leather", "denim", "wool", "silk", "cotton", "suede"]:
            search_terms.append(mat)
    
    # Add style tag for context
    style_tags = ["minimalist", "vintage", "modern", "casual", "luxury", "classic"]
    for tag in tags:
        if tag.lower() in style_tags and len(search_terms) < 3:
            search_terms.append(tag.lower())
            break
    
    # Build query string
    query = "+".join(search_terms[:3]) if search_terms else "fashion"
    
    # Use item ID to get consistent but varied images
    seed = abs(hash(item["id"]))
    
    # Use different approaches for variety
    item_num = int(item["id"].split("_")[1])
    
    if item_num % 4 == 0:
        # Method 1: Direct search with sig
        return f"https://source.unsplash.com/400x600/?{query}&sig={seed}"
    elif item_num % 4 == 1:
        # Method 2: Random with specific query
        return f"https://source.unsplash.com/random/400x600/?{query}&t={seed}"
    elif item_num % 4 == 2:
        # Method 3: Featured with query
        return f"https://source.unsplash.com/featured/400x600/?{query}&sig={seed}"
    else:
        # Method 4: Use Picsum for maximum variety
        return f"https://picsum.photos/seed/{item['id']}-{query.replace('+', '-')}/400/600"

def generate_pexels_fallback(item: Dict[str, Any]) -> str:
    """Generate Pexels image URL as fallback"""
    # Pexels requires API key for search, so we use a generic fashion image service
    seed = abs(hash(item["id"])) % 100000
    return f"https://images.pexels.com/photos/{seed}/pexels-photo-{seed}.jpeg?auto=compress&cs=tinysrgb&w=400&h=600"

def get_real_image_url(item: Dict[str, Any], prefer_unsplash: bool = True) -> str:
    """
    Get a real, deterministic image URL for an item
    
    Uses item ID as seed to ensure same item always gets same image
    Uses specific search terms based on item attributes for variety
    """
    
    # Always use the new search-based approach for better variety
    return generate_unsplash_url(item, use_collection=False)

def verify_image_url(url: str, timeout: int = 5) -> bool:
    """Verify that an image URL is accessible"""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def update_catalog_images(
    catalog_path: str,
    output_path: Optional[str] = None,
    verify_urls: bool = False,
    sample_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    Update all images in the catalog
    
    Args:
        catalog_path: Path to catalog JSON
        output_path: Output path (defaults to same as input)
        verify_urls: Whether to verify URLs are accessible (slow)
        sample_size: If set, only update this many items (for testing)
    """
    
    print(f"Loading catalog from {catalog_path}...")
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    items = catalog["items"]
    total_items = len(items) if not sample_size else min(sample_size, len(items))
    
    print(f"Updating images for {total_items} items...")
    print(f"Verify URLs: {verify_urls}")
    
    updated_count = 0
    failed_count = 0
    
    for i, item in enumerate(items[:total_items]):
        if i % 100 == 0:
            print(f"  Progress: {i}/{total_items} ({i*100//total_items}%)")
        
        # Generate new image URL
        new_url = get_real_image_url(item, prefer_unsplash=True)
        
        # Verify if requested
        if verify_urls:
            if verify_image_url(new_url):
                item["image_url"] = new_url
                updated_count += 1
            else:
                # Try fallback
                fallback_url = get_real_image_url(item, prefer_unsplash=False)
                if verify_image_url(fallback_url):
                    item["image_url"] = fallback_url
                    updated_count += 1
                else:
                    failed_count += 1
                    print(f"    ⚠️  Failed to find working image for {item['id']}")
        else:
            # Just update without verification
            item["image_url"] = new_url
            updated_count += 1
    
    print(f"\n✅ Updated {updated_count} images")
    if failed_count > 0:
        print(f"⚠️  Failed to verify {failed_count} images")
    
    # Update metadata
    catalog["catalog_version"] = "2.1"
    catalog["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    catalog["image_source"] = "unsplash+pexels+picsum"
    
    # Save
    output_path = output_path or catalog_path
    print(f"\nSaving updated catalog to {output_path}...")
    with open(output_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    file_size = Path(output_path).stat().st_size / 1024 / 1024
    print(f"✅ Catalog saved ({file_size:.2f} MB)")
    
    return {
        "total_items": total_items,
        "updated": updated_count,
        "failed": failed_count,
        "output_path": output_path
    }

def show_sample_urls(catalog_path: str, count: int = 10):
    """Show sample image URLs from the catalog"""
    
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    items = catalog["items"][:count]
    
    print(f"\n{'='*80}")
    print(f"SAMPLE IMAGE URLS (first {count} items)")
    print(f"{'='*80}\n")
    
    for item in items:
        print(f"ID: {item['id']}")
        print(f"Title: {item['title']}")
        print(f"Category: {item['categories'][0]}")
        print(f"Image: {item['image_url']}")
        print(f"-" * 80)

def create_image_html_preview(catalog_path: str, output_html: str = "catalog_preview.html", sample_size: int = 50):
    """Create an HTML preview of catalog images"""
    
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    items = catalog["items"][:sample_size]
    
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Style Catalog Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .item {{
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .item img {{
            width: 100%%;
            height: 300px;
            object-fit: cover;
        }}
        .item-info {{
            padding: 15px;
        }}
        .item-title {{
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        .item-brand {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .item-price {{
            color: #000;
            font-weight: bold;
            font-size: 18px;
        }}
        .item-tags {{
            margin-top: 10px;
        }}
        .tag {{
            display: inline-block;
            background: #e0e0e0;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-right: 5px;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <h1>Style Catalog Preview ({} items)</h1>
    <div class="grid">
""".format(len(items))
    
    for item in items:
        price = f"${item['price_cents']/100:.2f}"
        tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in item['tags'][:3]])
        
        html += f"""
        <div class="item">
            <img src="{item['image_url']}" alt="{item['title']}" onerror="this.src='https://via.placeholder.com/400x600?text=Image+Not+Found'">
            <div class="item-info">
                <div class="item-title">{item['title']}</div>
                <div class="item-brand">{item['brand']}</div>
                <div class="item-price">{price}</div>
                <div class="item-tags">{tags_html}</div>
            </div>
        </div>
        """
    
    html += """
    </div>
</body>
</html>
    """
    
    with open(output_html, 'w') as f:
        f.write(html)
    
    print(f"✅ HTML preview saved to {output_html}")
    print(f"   Open in browser to view images")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Add real images to style catalog")
    parser.add_argument("--catalog", type=str, default="../src/data/style_inspiration_catalog.json", help="Path to catalog JSON")
    parser.add_argument("--output", type=str, help="Output path (default: overwrite input)")
    parser.add_argument("--verify", action="store_true", help="Verify URLs are accessible (slow)")
    parser.add_argument("--sample", type=int, help="Only update N items (for testing)")
    parser.add_argument("--show-sample", type=int, help="Show N sample URLs and exit")
    parser.add_argument("--preview", type=int, help="Create HTML preview with N items")
    
    args = parser.parse_args()
    
    catalog_path = Path(__file__).parent / args.catalog
    
    if args.show_sample:
        show_sample_urls(catalog_path, args.show_sample)
    elif args.preview:
        create_image_html_preview(catalog_path, sample_size=args.preview)
    else:
        result = update_catalog_images(
            catalog_path=catalog_path,
            output_path=args.output,
            verify_urls=args.verify,
            sample_size=args.sample
        )
        
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total items processed: {result['total_items']}")
        print(f"Successfully updated: {result['updated']}")
        if result['failed'] > 0:
            print(f"Failed: {result['failed']}")
        print(f"Output: {result['output_path']}")
        print("="*80)

