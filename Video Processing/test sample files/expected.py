import os
import sys
import numpy as np
from PIL import Image

# Always write output next to this script, regardless of what directory
# the interpreter was launched from (fixes IDE "Run" button / double-click
# writing files to an unexpected working directory).
OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def rgb_to_ycbcr(img_rgb):
    """Vectorized BT.601 full-range RGB -> YCbCr."""
    # Convert to float for accurate math
    r = img_rgb[:, :, 0].astype(float)
    g = img_rgb[:, :, 1].astype(float)
    b = img_rgb[:, :, 2].astype(float)
    
    # BT.601 conversion logic
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = 128 - 0.168736 * r - 0.331264 * g + 0.5 * b
    cr = 128 + 0.5 * r - 0.418688 * g - 0.081312 * b
    
    # Clip and round back to uint8 bytes
    y = np.clip(np.round(y), 0, 255).astype(np.uint8)
    cb = np.clip(np.round(cb), 0, 255).astype(np.uint8)
    cr = np.clip(np.round(cr), 0, 255).astype(np.uint8)
    
    return y, cb, cr

def main():
    input_filename = "image_source.png" 
    input_path = os.path.join(OUT_DIR, input_filename)
    
    try:
        # Load image and ensure it's in standard RGB format
        img = Image.open(input_path).convert('RGB')
    except FileNotFoundError:
        print(f"Error: Could not find {input_filename} in {OUT_DIR}.")
        sys.exit(1)
        
    img_np = np.array(img)
    height, width, _ = img_np.shape
    
    print(f"Loaded {input_filename}: {width}x{height}")
    
    # 4:2:0 requires dimensions to be divisible by 2
    assert width % 2 == 0 and height % 2 == 0, "Error: Image width and height must be even numbers for 4:2:0 subsampling."
    
    chroma_w = width // 2
    chroma_h = height // 2

    # 1. Convert full image to YCbCr
    y_plane, cb_full, cr_full = rgb_to_ycbcr(img_np)
    
    # 2. Subsample Cb and Cr to 4:2:0 by averaging 2x2 blocks
    cb_plane = cb_full.reshape(chroma_h, 2, chroma_w, 2).mean(axis=(1, 3)).astype(np.uint8)
    cr_plane = cr_full.reshape(chroma_h, 2, chroma_w, 2).mean(axis=(1, 3)).astype(np.uint8)
    
    # 3. Create frame.hex (Planar order: all Y, then all Cb, then all Cr)
    hex_lines = []
    for plane in (y_plane, cb_plane, cr_plane):
        for val in plane.flatten():
            hex_lines.append(f"{val:02x}")
            
    # 4. Create expected_stream.hex (Packed 24-bit {Y,Cb,Cr} per pixel, raster order)
    # This reconstructs the 4:4:4 representation your Verilog outputs via nearest-neighbor
    stream_lines = []
    for y in range(height):
        for x in range(width):
            yc = int(y_plane[y, x])
            cb = int(cb_plane[y // 2, x // 2])
            cr = int(cr_plane[y // 2, x // 2])
            packed = (yc << 16) | (cb << 8) | cr
            stream_lines.append(f"{packed:06x}")

    # Set up output paths
    frame_path  = os.path.join(OUT_DIR, "frame.hex")
    stream_path = os.path.join(OUT_DIR, "expected_stream.hex")
    
    # Write to files
    with open(frame_path, "w") as f:
        f.write("\n".join(hex_lines) + "\n")
        
    with open(stream_path, "w") as f:
        f.write("\n".join(stream_lines) + "\n")
        
    # Print summary
    print(f"Y plane:  {height}x{width}  = {y_plane.size} bytes")
    print(f"Cb plane: {chroma_h}x{chroma_w} = {cb_plane.size} bytes")
    print(f"Cr plane: {chroma_h}x{chroma_w} = {cr_plane.size} bytes")
    print(f"Total: {len(hex_lines)} bytes written to: {frame_path}")
    print(f"Expected reconstructed pixel stream ({len(stream_lines)} pixels) written to: {stream_path}")

if __name__ == "__main__":
    main()