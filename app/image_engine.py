import hashlib
import os
from typing import Optional
from PIL import Image
from app.config import TRANSFORMED_DIR


def process_image(
    original_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    rotate: Optional[int] = None,
) -> str:

    cache_string = f"{original_path}_w{width or 'auto'}_h{height or 'auto'}_r{rotate or 0}"
    cache_key = hashlib.md5(cache_string.encode("utf-8")).hexdigest()

    _, ext = os.path.splitext(original_path)
    output_filename = f"{cache_key}{ext}"
    output_path = os.path.join(TRANSFORMED_DIR, output_filename)

    
    if os.path.exists(output_path):
        return output_path

    
    with Image.open(original_path) as img:
        
        if rotate:
            
            img = img.rotate(-rotate, expand=True)
        
        if width or height:
            orig_w, orig_h = img.size
            new_w = width if width else int(orig_w * (height / orig_h))
            new_h = height if height else int(orig_h * (width / orig_w))

            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        
        if img.mode in ("RGBA", "P") and ext.lower() in [".jpg", ".jpeg"]:
            img = img.convert("RGB")

        
        img.save(output_path)

    return output_path