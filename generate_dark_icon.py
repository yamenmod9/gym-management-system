"""
Generate a modern dark gym app icon with red and grey theme
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient_background(size, color1, color2):
    """Create a gradient background"""
    base = Image.new('RGB', (size, size), color1)
    draw = ImageDraw.Draw(base)

    for y in range(size):
        # Create vertical gradient
        ratio = y / size
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b))

    return base

def create_gym_icon(size=1024):
    """Create a modern gym icon with dark theme and red accent"""

    # Dark grey gradient background
    color1 = (30, 30, 30)  # Dark grey
    color2 = (18, 18, 18)  # Almost black
    img = create_gradient_background(size, color1, color2)
    draw = ImageDraw.Draw(img)

    # Add subtle noise texture for depth
    import random
    for _ in range(size * 50):
        x = random.randint(0, size - 1)
        y = random.randint(0, size - 1)
        brightness = random.randint(-10, 10)
        pixel = img.getpixel((x, y))
        new_pixel = tuple(max(0, min(255, c + brightness)) for c in pixel)
        img.putpixel((x, y), new_pixel)

    draw = ImageDraw.Draw(img)

    # Red accent color
    red_color = (220, 38, 38)  # Vibrant red
    light_red = (239, 68, 68)
    dark_grey = (42, 42, 42)

    center_x, center_y = size // 2, size // 2

    # Draw circular background
    circle_radius = int(size * 0.4)
    draw.ellipse(
        [center_x - circle_radius, center_y - circle_radius,
         center_x + circle_radius, center_y + circle_radius],
        fill=dark_grey,
        outline=red_color,
        width=int(size * 0.02)
    )

    # Draw dumbbell icon in red
    bar_width = int(size * 0.35)
    bar_height = int(size * 0.04)
    bar_y = center_y - bar_height // 2

    # Draw central bar
    draw.rectangle(
        [center_x - bar_width // 2, bar_y,
         center_x + bar_width // 2, bar_y + bar_height],
        fill=red_color
    )

    # Draw weight plates on both ends
    plate_width = int(size * 0.08)
    plate_height = int(size * 0.15)

    # Left plates
    for i in range(2):
        offset = i * plate_width * 0.6
        draw.rectangle(
            [center_x - bar_width // 2 - plate_width - offset,
             center_y - plate_height // 2,
             center_x - bar_width // 2 - offset,
             center_y + plate_height // 2],
            fill=light_red if i == 0 else red_color,
            outline=red_color,
            width=2
        )

    # Right plates
    for i in range(2):
        offset = i * plate_width * 0.6
        draw.rectangle(
            [center_x + bar_width // 2 + offset,
             center_y - plate_height // 2,
             center_x + bar_width // 2 + plate_width + offset,
             center_y + plate_height // 2],
            fill=light_red if i == 0 else red_color,
            outline=red_color,
            width=2
        )

    # Add small highlight circles for 3D effect
    highlight_size = int(size * 0.015)
    draw.ellipse(
        [center_x - highlight_size, center_y - bar_height // 2 - highlight_size,
         center_x + highlight_size, center_y - bar_height // 2 + highlight_size],
        fill=(255, 255, 255, 100)
    )

    return img

def save_icon_sizes(base_image, output_dir):
    """Save icon in various required sizes"""
    sizes = [
        ('android/app/src/main/res/mipmap-mdpi', 48),
        ('android/app/src/main/res/mipmap-hdpi', 72),
        ('android/app/src/main/res/mipmap-xhdpi', 96),
        ('android/app/src/main/res/mipmap-xxhdpi', 144),
        ('android/app/src/main/res/mipmap-xxxhdpi', 192),
    ]

    for folder, size in sizes:
        full_path = os.path.join(output_dir, folder)
        os.makedirs(full_path, exist_ok=True)

        resized = base_image.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(full_path, 'ic_launcher.png'))
        print(f'Generated {size}x{size} icon in {folder}')

def main():
    print("Generating dark gym app icon with red accent...")

    # Create base 1024x1024 icon
    icon = create_gym_icon(1024)

    # Save high-res version
    icon.save('app_icon_1024.png')
    print("Saved high-resolution icon: app_icon_1024.png")

    # Save Android sizes
    save_icon_sizes(icon, '.')

    # Save web icon
    web_icon = icon.resize((512, 512), Image.Resampling.LANCZOS)
    os.makedirs('web/icons', exist_ok=True)
    web_icon.save('web/icons/Icon-512.png')

    web_icon_192 = icon.resize((192, 192), Image.Resampling.LANCZOS)
    web_icon_192.save('web/icons/Icon-192.png')
    print("Saved web icons")

    print("\nIcon generation complete!")
    print("Dark theme with red accent applied successfully.")

if __name__ == '__main__':
    main()
