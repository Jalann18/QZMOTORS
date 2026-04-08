import sys
from PIL import Image

def process_logo(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    
    min_x, min_y = img.width, img.height
    max_x, max_y = 0, 0
    
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = img.getpixel((x, y))
            if r > 50 and r > g + 30 and r > b + 30:
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y
                
    pad = 5
    min_x = max(0, min_x - pad)
    min_y = max(0, min_y - pad)
    max_x = min(img.width, max_x + pad)
    max_y = min(img.height, max_y + pad)
    
    cropped = img.crop((min_x, min_y, max_x, max_y))
    
    final_data = []
    for r, g, b, a in cropped.getdata():
        if r > g + 20 and r > b + 20: 
            # It's a red pixel (could be antialiased)
            alpha = r
            if alpha == 0:
                final_data.append((0, 0, 0, 0))
            else:
                r_new = min(255, int(r * 255 / alpha))
                g_new = min(255, int(g * 255 / alpha))
                b_new = min(255, int(b * 255 / alpha))
                final_data.append((r_new, g_new, b_new, alpha))
        else:
            final_data.append((0, 0, 0, 0))
            
    cropped.putdata(final_data)
    cropped.save(output_path, "PNG")
    print(f"Logo created successfully at {output_path}")

if __name__ == "__main__":
    process_logo(sys.argv[1], sys.argv[2])
