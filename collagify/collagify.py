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

def srgb_to_linear(srgb):
    if srgb <= 0.04045:
        return srgb / 12.92
    else:
        return ((srgb + 0.055) / 1.055) ** 2.4

def linear_to_srgb(linear):
    if linear <= 0.0031308:
        return linear * 12.92
    else:
        return 1.055 * (linear ** (1/2.4)) - 0.055

def stitch_images_in_grid(input_pattern, output_filename, premultiply_alpha=False):
    """Stitch images from input directory matching the pattern into a grid atlas."""
    files = sorted(glob.glob(input_pattern))
    
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

    # Premultiply alpha
    if premultiply_alpha:
        print("Premultiplying alpha...")
        pixels = atlas.load()
        for y in range(atlas_height):
            for x in range(atlas_width):
                r, g, b, a = pixels[x, y]
                r = srgb_to_linear(r / 255)
                g = srgb_to_linear(g / 255)
                b = srgb_to_linear(b / 255)
                r *= a / 255
                g *= a / 255
                b *= a / 255
                r = linear_to_srgb(r) * 255
                g = linear_to_srgb(g) * 255
                b = linear_to_srgb(b) * 255
                pixels[x, y] = (round(r), round(g), round(b), a)

    # Save the final image
    atlas.save(output_filename, format='TGA')

    print(f"Stitched {total_images} images into {output_filename}.")

def main():
    parser = argparse.ArgumentParser(description='Stitch images into a grid atlas.')
    parser.add_argument('input_prefix', type=str, help='Prefix for input images')
    parser.add_argument('output_filename', type=str, help='Filename for the output image')
    parser.add_argument('--premultiply', action='store_true', help='Premultiply alpha channel')

    args = parser.parse_args()

    stitch_images_in_grid(args.input_prefix, args.output_filename, args.premultiply)

if __name__ == "__main__":
    main()

