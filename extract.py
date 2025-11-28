import cv2
import numpy as np
from PIL import Image
import os
from tqdm import tqdm

OUTPUT_FOLDER = "text"

def get_image_list(path: str) -> list[tuple[str, str]] | None:
    files = os.listdir(path)
    images = []
    masks = os.path.join(path, "mask")
    if not os.path.isdir(masks):
        return
    for file in files:
        if file.endswith(("jpg", "jpeg", "png")):
            ext = file.split(".")[-1]
            image = os.path.join(path, file)
            mask = os.path.join(masks, file.replace(ext, "png"))
            images.append((image, mask))
    return images


def extract_text(path):

    if images:= get_image_list(path):
        os.makedirs(os.path.join(path, OUTPUT_FOLDER), exist_ok=True)   
        for image, mask in tqdm(images):
            file = mask.split("\\")[-1]
            page = Image.open(image).convert("RGBA")
            _mask = Image.open(mask).convert("L")
            mask = np.array(_mask)
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)[:,:,0]
            
            # expand strokes into blobs (tune kernel size)
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (30,30))
            dilated = cv2.dilate(mask, kernel)

            # find external contours and fill them to make solid blobs
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            filled = np.zeros_like(dilated)
            cv2.drawContours(filled, contours, -1, 255, cv2.FILLED)

            # convert to a PIL mask in memory and composite
            pil_mask = Image.fromarray(filled).convert("L")
            canvas = Image.new("RGBA", page.size, (255,255,255,0))
            text_only = Image.composite(page, canvas, pil_mask)
            output_path = os.path.join(path, OUTPUT_FOLDER, file)
            text_only.save(output_path)



if __name__ == "__main__":

    folder = input("(Balloon) Comic folder:").strip('"')
    extract_text(path=folder)   