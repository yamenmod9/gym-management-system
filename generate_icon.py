"""
Gym App Icon Generator
Creates app icons with dark grey background and red dumbbell symbol
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gym_icon(size=1024):
    """Create a gym app icon with dark grey background and red dumbbell"""

    # Colors
    bg_color = (31, 31, 31)  # Dark grey #1F1F1F
    red_color = (220, 38, 38)  # Red #DC2626

    # Create image
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw dumbbell
    center_x, center_y = size // 2, size // 2
    bar_width = int(size * 0.5)  # 50% of image width
    bar_height = int(size * 0.08)  # 8% of image height
    weight_size = int(size * 0.15)  # 15% of image size

    # Draw center bar
    bar_x1 = center_x - bar_width // 2
    bar_y1 = center_y - bar_height // 2
    bar_x2 = center_x + bar_width // 2
    bar_y2 = center_y + bar_height // 2
    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill=red_color)

    # Draw left weight (circle)
    left_weight_x = bar_x1
    left_weight_y = center_y
    draw.ellipse(
        [left_weight_x - weight_size, left_weight_y - weight_size,
         left_weight_x + weight_size, left_weight_y + weight_size],
        fill=red_color
    )

    # Draw right weight (circle)
    right_weight_x = bar_x2
    right_weight_y = center_y
    draw.ellipse(
        [right_weight_x - weight_size, right_weight_y - weight_size,
         right_weight_x + weight_size, right_weight_y + weight_size],
        fill=red_color
    )

    # Add some detail to weights (inner circles)
    inner_size = int(weight_size * 0.6)
    # Left inner circle
    draw.ellipse(
        [left_weight_x - inner_size, left_weight_y - inner_size,
         left_weight_x + inner_size, left_weight_y + inner_size],
        fill=bg_color
    )
    # Right inner circle
    draw.ellipse(
        [right_weight_x - inner_size, right_weight_y - inner_size,
         right_weight_x + inner_size, right_weight_y + inner_size],
        fill=bg_color
    )

    return img

def create_foreground_icon(size=1024):
    """Create foreground icon with transparency for adaptive icons"""

    # Colors
    red_color = (220, 38, 38, 255)  # Red with alpha
    transparent = (0, 0, 0, 0)

    # Create image with alpha channel
    img = Image.new('RGBA', (size, size), transparent)
    draw = ImageDraw.Draw(img)

    # Draw dumbbell (same as above but with transparency)
    center_x, center_y = size // 2, size // 2
    bar_width = int(size * 0.5)
    bar_height = int(size * 0.08)
    weight_size = int(size * 0.15)

    # Draw center bar
    bar_x1 = center_x - bar_width // 2
    bar_y1 = center_y - bar_height // 2
    bar_x2 = center_x + bar_width // 2
    bar_y2 = center_y + bar_height // 2
    draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill=red_color)

    # Draw left weight
    left_weight_x = bar_x1
    left_weight_y = center_y
    draw.ellipse(
        [left_weight_x - weight_size, left_weight_y - weight_size,
         left_weight_x + weight_size, left_weight_y + weight_size],
        fill=red_color
    )

    # Draw right weight
    right_weight_x = bar_x2
    right_weight_y = center_y
    draw.ellipse(
        [right_weight_x - weight_size, right_weight_y - weight_size,
         right_weight_x + weight_size, right_weight_y + weight_size],
        fill=red_color
    )

    # Add detail to weights
    inner_size = int(weight_size * 0.6)
    # Left inner circle (transparent)
    draw.ellipse(
        [left_weight_x - inner_size, left_weight_y - inner_size,
         left_weight_x + inner_size, left_weight_y + inner_size],
        fill=transparent
    )
    # Right inner circle (transparent)
    draw.ellipse(
        [right_weight_x - inner_size, right_weight_y - inner_size,
         right_weight_x + inner_size, right_weight_y + inner_size],
        fill=transparent
    )

    return img

def main():
    """Generate app icons"""

    # Create assets/icon directory if it doesn't exist
    os.makedirs('assets/icon', exist_ok=True)

    # Generate main icon
    print("Generating app_icon.png...")
    main_icon = create_gym_icon(1024)
    main_icon.save('assets/icon/app_icon.png', 'PNG')
    print("✓ Created assets/icon/app_icon.png")

    # Generate foreground icon
    print("Generating app_icon_foreground.png...")
    foreground_icon = create_foreground_icon(1024)
    foreground_icon.save('assets/icon/app_icon_foreground.png', 'PNG')
    print("✓ Created assets/icon/app_icon_foreground.png")

    print("\n✅ Icon generation complete!")
    print("\nNext steps:")
    print("1. Run: flutter pub run flutter_launcher_icons")
    print("2. Run: flutter run")

if __name__ == '__main__':
    main()
