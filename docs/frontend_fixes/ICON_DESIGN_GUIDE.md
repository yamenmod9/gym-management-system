# App Icon Design Guide

## Icon Requirements

### Main Icon (`app_icon.png`)
- **Size:** 1024x1024 pixels
- **Format:** PNG with transparency
- **Background:** Dark grey (#1F1F1F)
- **Primary Color:** Red (#DC2626)
- **Design Elements:**
  - Gym dumbbell or fitness icon
  - App name (optional)
  - Clean, modern design
  - High contrast for visibility

### Foreground Icon (`app_icon_foreground.png`)
- **Size:** 1024x1024 pixels
- **Format:** PNG with transparency
- **Content:** Main icon element only (no background)
- **Safe Area:** Keep important elements within 66% of canvas (avoid edges)

## Design Suggestions

### Option 1: Dumbbell Icon
```
Background: Dark grey gradient
Icon: Red dumbbell silhouette
Style: Minimalist, modern
```

### Option 2: Gym Letter Logo
```
Background: Dark grey solid
Icon: Stylized "G" in red
Style: Bold, geometric
```

### Option 3: Fitness Symbol
```
Background: Dark grey with subtle pattern
Icon: Abstract fitness/strength symbol in red
Style: Dynamic, energetic
```

## Color Palette

- **Dark Grey:** `#1F1F1F` (Background)
- **Medium Grey:** `#2D2D2D` (Shadows/depth)
- **Primary Red:** `#DC2626` (Main icon)
- **Light Red:** `#EF4444` (Highlights)
- **White:** `#FFFFFF` (Small text/details)

## Creation Tools

### Online Tools (Free):
1. **Canva** - https://canva.com
   - Use 1024x1024 custom size
   - Import icons from library
   - Export as PNG

2. **Figma** - https://figma.com
   - Professional design tool
   - Vector graphics support
   - Export in multiple formats

3. **Icon Kitchen** - https://icon.kitchen
   - Specialized for app icons
   - Automatic adaptive icon generation
   - Preview on different devices

### Desktop Software:
1. **Adobe Illustrator** - Vector graphics (professional)
2. **GIMP** - Free alternative to Photoshop
3. **Inkscape** - Free vector graphics editor

## Quick Start with Icon Kitchen

1. Go to https://icon.kitchen
2. Upload or select a fitness/gym icon
3. Set background color to `#1F1F1F`
4. Set icon color to `#DC2626`
5. Adjust size and padding
6. Download the complete icon package
7. Extract files to your project

## Installation Steps

### 1. Create the folder structure:
```bash
mkdir -p assets/icon
```

### 2. Add your icons:
- Place `app_icon.png` in `assets/icon/`
- Place `app_icon_foreground.png` in `assets/icon/`

### 3. Install dependencies:
```bash
flutter pub get
```

### 4. Generate launcher icons:
```bash
flutter pub run flutter_launcher_icons
```

### 5. Build and test:
```bash
flutter clean
flutter build apk --release
```

## Verification

After generating icons, check:
- [ ] Android icon appears in `android/app/src/main/res/mipmap-*` folders
- [ ] iOS icon appears in `ios/Runner/Assets.xcassets/AppIcon.appiconset/`
- [ ] Icon looks good on device home screen
- [ ] Icon matches dark theme aesthetic
- [ ] Icon is visible on both light and dark system themes

## Troubleshooting

### Icon not updating on device:
1. Uninstall the app completely
2. Run `flutter clean`
3. Rebuild and reinstall: `flutter run --release`

### Icon looks blurry:
- Ensure source image is at least 1024x1024
- Use PNG format with high quality
- Avoid JPEG (lossy compression)

### Adaptive icon issues (Android):
- Ensure foreground icon has transparent background
- Keep important elements in the safe area (center 66%)
- Test on different Android launchers

## Example Icon Code (SVG)

If you want to create a simple icon programmatically:

```xml
<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="1024" height="1024" fill="#1F1F1F"/>
  
  <!-- Dumbbell Icon -->
  <g transform="translate(512, 512)">
    <!-- Left weight -->
    <rect x="-350" y="-80" width="100" height="160" rx="20" fill="#DC2626"/>
    <!-- Bar -->
    <rect x="-250" y="-20" width="500" height="40" rx="20" fill="#EF4444"/>
    <!-- Right weight -->
    <rect x="250" y="-80" width="100" height="160" rx="20" fill="#DC2626"/>
  </g>
</svg>
```

## Need Help?

If you need a custom icon designed:
1. Use one of the online tools mentioned above
2. Search for "gym fitness icons" on sites like:
   - Icons8 (https://icons8.com)
   - Flaticon (https://flaticon.com)
   - Font Awesome (https://fontawesome.com)
3. Customize colors to match the theme
4. Export and use in your app

## Preview

Before finalizing, preview your icon:
- On different Android devices (various launchers)
- On iOS devices
- In both light and dark system themes
- At different sizes (notification, settings, home screen)

## Final Checklist

- [ ] Icon designed with dark grey and red colors
- [ ] Both main and foreground icons created
- [ ] Icons placed in `assets/icon/` folder
- [ ] `flutter_launcher_icons` package added to pubspec.yaml
- [ ] Icon generation command run successfully
- [ ] App rebuilt and tested on device
- [ ] Icon looks good on home screen
- [ ] Icon matches app's dark theme
