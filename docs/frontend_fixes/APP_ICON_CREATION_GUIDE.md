# App Icon Design Guide

## Icon Specifications

### Size Requirements
- **Base Size:** 1024x1024 pixels (PNG format)
- **Foreground (Android Adaptive):** 1024x1024 pixels (PNG with transparency)
- **Background Color:** #1F1F1F (Dark Grey)

### Design Guidelines

#### Theme
- **Style:** Modern, Minimalist
- **Colors:** Red (#DC2626) on Dark Grey (#1F1F1F)
- **Shape:** Square with rounded corners (will be applied automatically)

#### Icon Elements (Choose One)
1. **Dumbbell Icon:** Simple red dumbbell silhouette
2. **Muscle Icon:** Flexed bicep in red
3. **Fitness Badge:** Circle with "GYM" text and dumbbell
4. **Barbell Weight:** Red barbell plate design

### Color Palette
```
Primary Red: #DC2626
Light Red: #EF4444
Dark Grey Background: #1F1F1F
Medium Grey: #2D2D2D
White Text: #FFFFFF
```

## Recommended Design

### Option 1: Simple Dumbbell
```
┌─────────────────────┐
│                     │
│    ┌─┬───────┬─┐    │
│    ├─┤       ├─┤    │  <- Red (#DC2626)
│    └─┴───────┴─┘    │
│                     │
└─────────────────────┘
Dark Grey Background (#1F1F1F)
```

### Option 2: Gym Badge
```
┌─────────────────────┐
│     ╔═══════╗       │
│     ║  GYM  ║       │  <- Red border
│     ║   🏋️   ║       │  <- White text
│     ╚═══════╝       │
└─────────────────────┘
Dark Grey Background (#1F1F1F)
```

## File Structure

Place icon files in:
```
assets/
  └── icon/
      ├── app_icon.png (1024x1024 - Full icon with background)
      └── app_icon_foreground.png (1024x1024 - Icon only, transparent bg)
```

## Generation Commands

### After adding icon files, run:
```cmd
cd C:\Programming\Flutter\gym_frontend
flutter pub get
flutter pub run flutter_launcher_icons
```

### Then rebuild the app:
```cmd
flutter clean
flutter pub get
flutter build apk
```

## Online Icon Generators (Free)

1. **Canva** (https://www.canva.com)
   - Template: Icon Design
   - Size: 1024x1024
   - Export: PNG with transparent background

2. **Figma** (https://www.figma.com)
   - Free design tool
   - Export at @1x (1024x1024)

3. **Icon Kitchen** (https://icon.kitchen)
   - Specialized for app icons
   - Supports adaptive icons

## Quick Icon Creation Steps

1. **Open Canva or Figma**
2. **Create new design: 1024x1024px**
3. **Set background: #1F1F1F**
4. **Add dumbbell icon/shape in red (#DC2626)**
5. **Keep design centered with 20% padding**
6. **Export as PNG**
7. **Save to:** `assets/icon/app_icon.png`
8. **Create foreground version:** Remove background, save as `app_icon_foreground.png`
9. **Run:** `flutter pub run flutter_launcher_icons`

## Testing Icons

### Android
1. Check in app drawer after installation
2. Icons should appear in all densities (mdpi, hdpi, xhdpi, etc.)

### Verification
- Icon should be visible and clear
- Colors should match theme (red on dark grey)
- No pixelation or distortion
- Icon recognizable at small sizes

## Fallback: Text-Based Icon

If you need a quick temporary icon:

```
┌─────────────────────┐
│                     │
│                     │
│        GYM          │  <- Red text (#DC2626)
│                     │     Bold, Large Font
│                     │
└─────────────────────┘
Dark Grey Background (#1F1F1F)
```

## Important Notes

- **Keep it simple:** Icon should be recognizable at 48x48px
- **High contrast:** Red on dark grey provides good visibility
- **Avoid text:** If possible, use symbols instead of text
- **Test on device:** Always verify icon looks good on actual device
- **Safe area:** Keep important elements away from edges (20% padding)

## Current Status

- ✅ Icon configuration in pubspec.yaml
- ✅ assets/icon folder created
- ⏳ Icon files need to be added
- ⏳ Icon generation needs to be run

## Next Steps

1. Create icon design (1024x1024px)
2. Save as `assets/icon/app_icon.png`
3. Create foreground version: `assets/icon/app_icon_foreground.png`
4. Run `flutter pub run flutter_launcher_icons`
5. Rebuild app and test
