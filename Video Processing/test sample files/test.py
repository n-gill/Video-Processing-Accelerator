import sys
import numpy as np
from PIL import Image

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
    # Target your specific file
    input_filename = "image_source.png" 
    output_filename = "Video Processing/test sample files/frame.hex"
    
    try:
        # Load image and ensure it's in standard RGB format
        img = Image.open(input_filename).convert('RGB')
    except FileNotFoundError:
        print(f"Error: Could not find {input_filename}. Please ensure it is in the same directory.")
        return
        
    img_np = np.array(img)
    height, width, _ = img_np.shape
    
    print(f"Loaded {input_filename}: {width}x{height}")
    
    # 4:2:0 requires dimensions to be divisible by 2
    assert width % 2 == 0 and height % 2 == 0, "Error: Image width and height must be even numbers for 4:2:0 subsampling."
    
    # 1. Convert full image to YCbCr
    y_plane, cb_full, cr_full = rgb_to_ycbcr(img_np)
    
    # 2. Subsample Cb and Cr to 4:2:0 by averaging 2x2 blocks
    # This reshapes the array to isolate 2x2 blocks and takes the mean across them
    cb_plane = cb_full.reshape(height // 2, 2, width // 2, 2).mean(axis=(1, 3)).astype(np.uint8)
    cr_plane = cr_full.reshape(height // 2, 2, width // 2, 2).mean(axis=(1, 3)).astype(np.uint8)
    
    # 3. Write out to hex file in planar format (All Y, then All Cb, then All Cr)
    hex_lines = []
    
    # .flatten() turns the 2D arrays into 1D sequences for writing
    for plane in (y_plane, cb_plane, cr_plane):
        for val in plane.flatten():
            hex_lines.append(f"{val:02x}")
            
    # Write to file, adding the crucial trailing newline for Verilog simulators
    with open(output_filename, "w") as f:
        f.write("\n".join(hex_lines) + "\n")
        
    print(f"Y plane:  {height}x{width}  = {y_plane.size} bytes")
    print(f"Cb plane: {height//2}x{width//2} = {cb_plane.size} bytes")
    print(f"Cr plane: {height//2}x{width//2} = {cr_plane.size} bytes")
    print(f"Total: {len(hex_lines)} bytes written to {output_filename}")

if __name__ == "__main__":
    main()