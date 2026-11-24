import sys
from PIL import Image

def make_white_bg(image_path):
    try:
        img = Image.open(image_path)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # Create a white background image
            background = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the image on top of the background
            background.paste(img, mask=img.split()[3]) # 3 is the alpha channel
            background.save(image_path, 'PNG')
            print(f"Fixed {image_path}")
        else:
            print(f"No alpha channel in {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

make_white_bg('concept_diagram.png')
make_white_bg('model_architecture.png')
make_white_bg('figure4_lobe_stratification.png')
make_white_bg('figure5_model_benchmark.png')
