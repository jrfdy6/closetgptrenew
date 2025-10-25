#!/usr/bin/env python3
"""
Generate AI product images for the entire catalog using free APIs
Uses FAL.ai's free tier for high-quality product photography
"""

import json
import os
import time
import base64
import hashlib
from typing import Dict, Any, List, Optional
from pathlib import Path
import requests

# Free image generation APIs
# Option 1: FAL.ai (Flux models) - Free tier: 100 requests/day
# Option 2: Together.AI - Free tier available
# Option 3: Hugging Face - Free but slower

class AIImageGenerator:
    """Generate product images using AI"""
    
    def __init__(self, service: str = "fal", api_key: Optional[str] = None):
        self.service = service
        self.api_key = api_key or os.getenv("FAL_KEY") or os.getenv("TOGETHER_API_KEY")
        self.request_count = 0
        self.rate_limit_delay = 1.0  # seconds between requests
        
    def create_product_prompt(self, item: Dict[str, Any]) -> str:
        """Create a detailed prompt for product photography"""
        
        title = item.get("title", "")
        color = title.split()[0] if title else "neutral"
        item_type = " ".join(title.split()[1:]) if len(title.split()) > 1 else "clothing"
        
        materials = item.get("materials", [])
        material_str = materials[0] if materials else "fabric"
        
        tags = item.get("tags", [])
        style_desc = tags[0] if tags else "modern"
        
        # Create professional product photography prompt
        prompt = f"""Professional product photography of a {color} {item_type}, made of {material_str}, {style_desc} style. 
Clean white background, studio lighting, high resolution, commercial fashion photography, 
centered composition, no model, flat lay or hanging display, photorealistic, 4K quality"""
        
        return prompt
    
    def generate_with_fal(self, prompt: str, item_id: str) -> str:
        """Generate image using FAL.ai (Flux model) - Free tier"""
        
        # FAL.ai free endpoint (no API key needed for basic use)
        url = "https://fal.run/fal-ai/flux-lora"
        
        # For free usage without API key, we'll use a simpler approach
        # Generate a stable URL that will be consistent for this item
        
        # Alternative: Use FAL's public Flux Schnell (fastest, free)
        url = "https://fal.run/fal-ai/flux/schnell"
        
        payload = {
            "prompt": prompt,
            "image_size": "portrait_4_3",  # Closest to 400x600
            "num_inference_steps": 4,  # Fast for Schnell
            "num_images": 1,
            "enable_safety_checker": True,
            "seed": abs(hash(item_id)) % 2147483647  # Deterministic seed
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Key {self.api_key}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            # FAL returns image URL
            if "images" in result and len(result["images"]) > 0:
                return result["images"][0]["url"]
            
        except Exception as e:
            print(f"⚠️  FAL.ai error: {e}")
        
        return None
    
    def generate_with_together(self, prompt: str, item_id: str) -> str:
        """Generate image using Together.AI - Free tier available"""
        
        if not self.api_key:
            print("⚠️  Together.AI requires API key")
            return None
        
        url = "https://api.together.xyz/v1/images/generations"
        
        payload = {
            "model": "stabilityai/stable-diffusion-xl-base-1.0",
            "prompt": prompt,
            "width": 512,
            "height": 768,
            "steps": 20,
            "n": 1,
            "seed": abs(hash(item_id)) % 2147483647
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "data" in result and len(result["data"]) > 0:
                return result["data"][0]["url"]
                
        except Exception as e:
            print(f"⚠️  Together.AI error: {e}")
        
        return None
    
    def generate_with_huggingface(self, prompt: str, item_id: str) -> str:
        """Generate using Hugging Face Inference API (Free, no key needed)"""
        
        # Use Stable Diffusion 2.1 via HF inference
        url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "negative_prompt": "low quality, blurry, watermark, text, person, model",
                "num_inference_steps": 25,
                "guidance_scale": 7.5,
                "width": 512,
                "height": 768
            }
        }
        
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 503:
                print("⚠️  Model loading, waiting...")
                time.sleep(20)
                response = requests.post(url, json=payload, headers=headers, timeout=120)
            
            if response.status_code == 200:
                # HF returns image bytes, we need to save or convert
                image_data = response.content
                
                # Convert to base64 data URL
                base64_image = base64.b64encode(image_data).decode()
                return f"data:image/png;base64,{base64_image}"
                
        except Exception as e:
            print(f"⚠️  Hugging Face error: {e}")
        
        return None
    
    def generate_image_url(self, item: Dict[str, Any]) -> Optional[str]:
        """Generate image URL for an item"""
        
        prompt = self.create_product_prompt(item)
        item_id = item["id"]
        
        # Rate limiting
        time.sleep(self.rate_limit_delay)
        self.request_count += 1
        
        # Try selected service
        url = None
        if self.service == "fal":
            url = self.generate_with_fal(prompt, item_id)
        elif self.service == "together":
            url = self.generate_with_together(prompt, item_id)
        elif self.service == "huggingface":
            url = self.generate_with_huggingface(prompt, item_id)
        
        return url

def generate_images_for_catalog(
    catalog_path: str,
    output_path: str,
    service: str = "huggingface",
    api_key: Optional[str] = None,
    max_items: Optional[int] = None,
    start_index: int = 0
):
    """
    Generate AI images for catalog items
    
    Args:
        catalog_path: Path to catalog JSON
        output_path: Output path for updated catalog
        service: Image generation service (fal, together, huggingface)
        api_key: API key if required
        max_items: Maximum items to process (for testing)
        start_index: Start from this index (for resuming)
    """
    
    print(f"Loading catalog from {catalog_path}...")
    with open(catalog_path, 'r') as f:
        catalog = json.load(f)
    
    items = catalog["items"]
    total = len(items) if not max_items else min(max_items, len(items))
    
    print(f"\n{'='*80}")
    print(f"AI IMAGE GENERATION")
    print(f"{'='*80}")
    print(f"Service: {service}")
    print(f"Total items: {total}")
    print(f"Starting at index: {start_index}")
    print(f"API key provided: {bool(api_key)}")
    print(f"{'='*80}\n")
    
    generator = AIImageGenerator(service=service, api_key=api_key)
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i in range(start_index, min(start_index + total, len(items))):
        item = items[i]
        
        if i % 10 == 0:
            print(f"\n📊 Progress: {i}/{total} ({i*100//total}%)")
            print(f"   ✅ Success: {success_count} | ❌ Failed: {failed_count} | ⏭️  Skipped: {skipped_count}")
        
        try:
            print(f"🎨 Generating: {item['title']} ({item['id']})")
            
            image_url = generator.generate_image_url(item)
            
            if image_url:
                item["image_url"] = image_url
                item["ai_generated"] = True
                success_count += 1
                print(f"   ✅ Generated")
            else:
                failed_count += 1
                print(f"   ❌ Failed to generate")
            
            # Save progress every 50 items
            if (i + 1) % 50 == 0:
                print(f"\n💾 Saving checkpoint...")
                with open(output_path, 'w') as f:
                    json.dump(catalog, f, indent=2)
                print(f"   ✅ Saved to {output_path}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed_count += 1
            continue
    
    # Final save
    print(f"\n💾 Saving final catalog...")
    catalog["image_generation_service"] = service
    catalog["ai_generated_images"] = success_count
    catalog["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    
    with open(output_path, 'w') as f:
        json.dump(catalog, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully generated: {success_count}")
    print(f"❌ Failed: {failed_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"📦 Output: {output_path}")
    print(f"{'='*80}\n")
    
    return {
        "success": success_count,
        "failed": failed_count,
        "skipped": skipped_count
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate AI product images for catalog")
    parser.add_argument("--catalog", type=str, default="../src/data/style_inspiration_catalog.json", help="Input catalog path")
    parser.add_argument("--output", type=str, help="Output catalog path (default: overwrites input)")
    parser.add_argument("--service", type=str, default="huggingface", choices=["fal", "together", "huggingface"], help="AI service to use")
    parser.add_argument("--api-key", type=str, help="API key (optional for HuggingFace)")
    parser.add_argument("--max-items", type=int, help="Maximum items to process (for testing)")
    parser.add_argument("--start-index", type=int, default=0, help="Start from this index")
    
    args = parser.parse_args()
    
    catalog_path = Path(__file__).parent / args.catalog
    output_path = args.output or catalog_path
    
    print("\n⚠️  AI IMAGE GENERATION - FREE TIER LIMITS:")
    print("=" * 80)
    print("HuggingFace (Recommended): Free, unlimited, but slower (~30s per image)")
    print("FAL.ai: Free tier limited to 100 images/day")
    print("Together.AI: Requires API key, free tier available")
    print("=" * 80)
    print(f"\nUsing: {args.service}")
    print(f"Estimated time for 2100 images: {2100 * 30 / 3600:.1f} hours (HuggingFace)")
    print("=" * 80)
    
    response = input("\nContinue? (yes/no): ")
    if response.lower() != "yes":
        print("Aborted.")
        exit(0)
    
    generate_images_for_catalog(
        catalog_path=catalog_path,
        output_path=output_path,
        service=args.service,
        api_key=args.api_key or os.getenv("FAL_KEY") or os.getenv("TOGETHER_API_KEY") or os.getenv("HF_TOKEN"),
        max_items=args.max_items,
        start_index=args.start_index
    )
    
    print("\n✨ Done! AI-generated images are ready.")

