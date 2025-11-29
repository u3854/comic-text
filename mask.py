from paddleocr import TextDetection
import numpy as np
import cv2
import os
from tqdm import tqdm


def mask_text(path: str):

    images = os.listdir(path)
    mask_folder = os.path.join(path, "mask")
    os.makedirs(mask_folder, exist_ok=True)
    model = TextDetection(model_name="PP-OCRv5_server_det")

    for image in tqdm(images):
        if image.endswith(("jpg", "jpeg", "png")):
            filename = image.split(".")[0]
            img_path = os.path.join(path, image)
            output_path = os.path.join(mask_folder, filename + ".png")

            results = model.predict(img_path, batch_size=1)
            res = results[0]

            text_polygons = res['dt_polys'] if isinstance(res, dict) else res.json['dt_polys']

            # Read the original image to get dimensions
            img = cv2.imread(img_path)
            h, w, _ = img.shape

            # Create a black mask
            mask = np.zeros((h, w), dtype=np.uint8)
            # Draw the text polygons onto the mask
            # text_polygons is already a numpy array of points, perfect for fillPoly
            # We explicitly cast to int32 to be safe
            polygons_np = [np.array(poly).astype(np.int32) for poly in text_polygons]

            # Fill the detected text areas with white (255)
            cv2.fillPoly(mask, polygons_np, 255)

            # Save or use the mask
            cv2.imwrite(output_path, mask)


if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:
        folder = sys.argv[1].strip('"')
    else:
        folder = input("(Balloon) Comic folder:").strip('"')
    mask_text(path=folder)