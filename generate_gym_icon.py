#!/usr/bin/env python3
"""
App Icon Generator for Gym Management System
Creates app icons with dark grey background and red theme
"""

from PIL import Image, ImageDraw
import os


def create_gym_icon(size, output_path):
    """
    Create a gym app icon with dark grey background and red dumbbell
    """
    # Colors
    bg_color = (31, 31, 31)  # Dark grey #1F1F1F
    primary_red = (220, 38, 38)  # Red #DC2626
    accent_red = (239, 68, 68)  # Light red #EF4444

    # Create image
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Calculate dimensions
    center = size // 2

    # Draw dumbbell icon
    # Main bar (horizontal)
    bar_height = size // 8
    bar_width = int(size // 1.8)
    bar_y = center - bar_height // 2
    bar_x = center - bar_width // 2

    draw.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
        radius=bar_height // 3,
        fill=primary_red
    )

    # Left weight plates
    plate_width = size // 6
    plate_height = size // 3

    # Outer left plate
    left_outer_x = bar_x - plate_width + 10
    left_outer_y = center - plate_height // 2
    draw.rounded_rectangle(
        [left_outer_x, left_outer_y, left_outer_x + plate_width, left_outer_y + plate_height],
        radius=10,
        fill=accent_red
    )

    # Inner left plate
    left_inner_x = bar_x - plate_width // 2 + 5
    left_inner_y = center - int(plate_height // 2.5)
    draw.rounded_rectangle(
        [left_inner_x, left_inner_y, left_inner_x + plate_width // 2, left_inner_y + int(plate_height // 1.25)],
        radius=8,
        fill=primary_red
    )

    # Right weight plates
    # Outer right plate
    right_outer_x = bar_x + bar_width - 10
    right_outer_y = center - plate_height // 2
    draw.rounded_rectangle(
        [right_outer_x, right_outer_y, right_outer_x + plate_width, right_outer_y + plate_height],
        radius=10,
        fill=accent_red
    )

    # Inner right plate
    right_inner_x = bar_x + bar_width - plate_width // 2 + 5
    right_inner_y = center - int(plate_height // 2.5)
    draw.rounded_rectangle(
        [right_inner_x, right_inner_y, right_inner_x + plate_width // 2, right_inner_y + int(plate_height // 1.25)],
        radius=8,
        fill=primary_red
    )

    # Save image
    img.save(output_path, quality=95)
    print(f"Created: {output_path}")


def create_foreground_icon(size, output_path):
    """
    Create foreground icon (for adaptive icons) with transparent background
    """
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colors
    primary_red = (220, 38, 38, 255)  # Red #DC2626
    accent_red = (239, 68, 68, 255)  # Light red #EF4444

    # Calculate dimensions (slightly larger for foreground)
    center = size // 2
    scale = 1.2  # Scale up for adaptive icon

    # Draw dumbbell icon
    # Main bar (horizontal)
    bar_height = int(size // 8 * scale)
    bar_width = int(size // 1.8 * scale)
    bar_y = center - bar_height // 2
    bar_x = center - bar_width // 2

    draw.rounded_rectangle(
        [bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
        radius=bar_height // 3,
        fill=primary_red
    )

    # Left weight plates
    plate_width = int(size // 6 * scale)
    plate_height = int(size // 3 * scale)

    # Outer left plate
    left_outer_x = bar_x - plate_width + 10
    left_outer_y = center - plate_height // 2
    draw.rounded_rectangle(
        [left_outer_x, left_outer_y, left_outer_x + plate_width, left_outer_y + plate_height],
        radius=10,
        fill=accent_red
    )

    # Inner left plate
    left_inner_x = bar_x - plate_width // 2 + 5
    left_inner_y = center - int(plate_height // 2.5)
    draw.rounded_rectangle(
        [left_inner_x, left_inner_y, left_inner_x + plate_width // 2, left_inner_y + int(plate_height // 1.25)],
        radius=8,
        fill=primary_red
    )

    # Right weight plates
    # Outer right plate
    right_outer_x = bar_x + bar_width - 10
    right_outer_y = center - plate_height // 2
    draw.rounded_rectangle(
        [right_outer_x, right_outer_y, right_outer_x + plate_width, right_outer_y + plate_height],
        radius=10,
        fill=accent_red
    )

    # Inner right plate
    right_inner_x = bar_x + bar_width - plate_width // 2 + 5
    right_inner_y = center - int(plate_height // 2.5)
    draw.rounded_rectangle(
        [right_inner_x, right_inner_y, right_inner_x + plate_width // 2, right_inner_y + int(plate_height // 1.25)],
        radius=8,
        fill=primary_red
    )

    # Save image
    img.save(output_path)
    print(f"Created: {output_path}")


def main():
    # Create assets directory if it doesn't exist
    icon_dir = os.path.join('assets', 'icon')
    os.makedirs(icon_dir, exist_ok=True)

    print("Generating Gym Management System app icons...")
    print("Theme: Dark Grey (#1F1F1F) with Red (#DC2626)")
    print()

    # Generate main icon (1024x1024)
    create_gym_icon(1024, os.path.join(icon_dir, 'app_icon.png'))

    # Generate foreground icon for adaptive icons
    create_foreground_icon(1024, os.path.join(icon_dir, 'app_icon_foreground.png'))

    print()
    print("✓ Icon generation complete!")
    print()
    print("Next steps:")
    print("1. Run: flutter pub run flutter_launcher_icons")
    print("2. This will generate all platform-specific icons")


if __name__ == '__main__':
    main()
