from PIL import Image
import os
from tqdm import tqdm
import zipfile


RESULT_FOLDER = "translated"

def save_overlay(path: str):

    output_folder = os.path.join(path, RESULT_FOLDER)
    os.makedirs(output_folder, exist_ok=True)
    originals = os.listdir(path)
    images = [f for f in originals if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    # make zip
    zip_path = path + ".zip"
    z = zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED)

    for file in tqdm(images):
        if file.endswith(("jpg", "jpeg", "png")):
            ext = file.split(".")[-1]
            translated_text = Image.open(os.path.join(path, "text", file.replace(ext, "png")))
            page = Image.open(os.path.join(path, file)).convert("RGBA")
            
            # choose highest resolution
            w = max(translated_text.width, page.width)
            h = max(translated_text.height, page.height)
            # resize only if an image exceeds chosen max size
            if translated_text.width < w or translated_text.height < h:
                translated_text = translated_text.resize((w, h), Image.Resampling.LANCZOS)
            if page.width < w or page.height < h:
                page = page.resize((w, h), Image.Resampling.LANCZOS)

            combined = Image.alpha_composite(page, translated_text)
            output_path = os.path.join(output_folder, file.replace(ext, "webp"))
            combined.save(output_path, "WEBP", quality=90)
            # add to zip
            z.write(output_path, arcname=os.path.basename(output_path))

if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:
        folder = sys.argv[1].strip('"')
    else:
        folder = input("(Balloon) Comic folder: ").strip('"')
    save_overlay(path=folder)