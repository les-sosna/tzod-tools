import argparse
import glob
import os
from PIL import Image
import math

def find_grid_dimensions(n):
    """Find the grid dimensions (rows, columns) closest to a square for n images."""
    rows = int(math.sqrt(n))
    while n % rows != 0:
        rows -= 1
    columns = n // rows
    return rows, columns

def stitch_images_in_grid(input_prefix, output_filename):
    """Stitch images from input directory matching the input_prefix into a grid atlas."""
    pattern = f"{input_prefix}*.png"
    files = sorted(glob.glob(pattern))
    
    if not files:
        print("No matching images found.")
        return

    images = [Image.open(filename) for filename in files]

    # Assume all images have the same dimensions
    img_width, img_height = images[0].size
    total_images = len(images)
    rows, cols = find_grid_dimensions(total_images)

    # Create a new image with the correct size
    atlas_width = cols * img_width
    atlas_height = rows * img_height
    atlas = Image.new('RGBA', (atlas_width, atlas_height))

    # Place each image in its grid position
    for index, image in enumerate(images):
        row = index // cols
        col = index % cols
        atlas.paste(image, (col * img_width, row * img_height))

    # Save the final image
    atlas.save(output_filename, format='TGA')

def main():
    parser = argparse.ArgumentParser(description='Stitch images into a grid atlas.')
    parser.add_argument('input_prefix', type=str, help='Prefix for input images')
    parser.add_argument('output_filename', type=str, help='Filename for the output image')
    
    args = parser.parse_args()

    stitch_images_in_grid(args.input_prefix, args.output_filename)

if __name__ == "__main__":
    main()

