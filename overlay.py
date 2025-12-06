from PIL import Image
import os
import numpy as np
from tqdm import tqdm
import zipfile

RESULT_FOLDER = "translated"
LONG_SIDE_TARGET = 1920

def make_white_transparent(img, threshold=240):
    """
    Turns white (and near-white) pixels transparent.
    threshold: 0-255. Higher means only stricter whites become transparent.
    """
    data = np.array(img)
    
    r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
    
    white_areas = (r > threshold) & (g > threshold) & (b > threshold)
    
    data[:, :, 3][white_areas] = 0
    
    return Image.fromarray(data)


def save_overlay(path: str):
    output_folder = os.path.join(path, RESULT_FOLDER)
    os.makedirs(output_folder, exist_ok=True)
    
    originals = os.listdir(path)
    images = [f for f in originals if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    
    zip_path = path + ".zip"
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for file in tqdm(images):
            filename_no_ext = os.path.splitext(file)[0]
            
            # Paths
            target_png = filename_no_ext + ".png"
            text_path_result = os.path.join(path, "text", "result", target_png)
            text_path_base = os.path.join(path, "text", target_png)
            final_text_path = text_path_result if os.path.exists(text_path_result) else text_path_base
            page_path = os.path.join(path, "inpainted", target_png)
            final_page_path = page_path if os.path.exists(page_path) else os.path.join(path, file)
            
            if not os.path.exists(final_text_path):
                continue

            try:
                # 1. Open both as RGBA
                translated_text = Image.open(final_text_path).convert("RGBA")
                page = Image.open(final_page_path).convert("RGBA")

                # 2. Make white transparent here
                translated_text = make_white_transparent(translated_text)

            except Exception as e:
                print(f"Error processing {file}: {e}")
                continue

            # 3. Resize logic (Matching text layer to page layer)
            w = max(translated_text.width, page.width)
            h = max(translated_text.height, page.height)

            if translated_text.width != w or translated_text.height != h:
                translated_text = translated_text.resize((w, h), Image.Resampling.LANCZOS)
            
            if page.width != w or page.height != h:
                page = page.resize((w, h), Image.Resampling.LANCZOS)

            # 4. Composite
            combined = Image.alpha_composite(page, translated_text)
            
            # 5. NEW: Resize to max 1920px on the long side
            target_long_side = LONG_SIDE_TARGET
            cur_w, cur_h = combined.size
            
            # Only resize if the image is actually larger than the target
            if max(cur_w, cur_h) > target_long_side:
                if cur_w > cur_h:
                    # Landscape orientation
                    new_w = target_long_side
                    new_h = int(cur_h * (target_long_side / cur_w))
                else:
                    # Portrait or Square orientation
                    new_h = target_long_side
                    new_w = int(cur_w * (target_long_side / cur_h))
                
                combined = combined.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Save
            output_filename = filename_no_ext + ".webp"
            output_path = os.path.join(output_folder, output_filename)
            combined.save(output_path, "WEBP", quality=90)
            z.write(output_path, arcname=output_filename)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        folder = sys.argv[1].strip('"')
    else:
        folder = input("(Balloon) Comic folder: ").strip('"')
        
    save_overlay(path=folder)