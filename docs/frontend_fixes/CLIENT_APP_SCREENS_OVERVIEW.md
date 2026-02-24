# 📱 CLIENT APP - SCREENS OVERVIEW

## Visual Flow & Features

---

## 🔐 Authentication Flow

### Screen 1: Welcome Screen (`/welcome`)

**Layout:**
```
┌─────────────────────────┐
│                         │
│      🏋️ [GYM ICON]      │
│                         │
│    Welcome to           │
│    Gym Client           │
│                         │
│  Enter phone/email      │
│  to continue            │
│                         │
│  ┌─────────────────┐    │
│  │ Phone or Email  │    │
│  └─────────────────┘    │
│                         │
│  ┌─────────────────┐    │
│  │ Request Code    │    │
│  └─────────────────┘    │
│                         │
│  ℹ️ You'll receive a    │
│     6-digit code        │
│                         │
└─────────────────────────┘
```

**Features:**
- ✅ Single input field (phone or email)
- ✅ Validation (not empty)
- ✅ Loading state on button
- ✅ Success/error messages
- ✅ Auto-navigate to activation

---

### Screen 2: Activation Screen (`/activation`)

**Layout:**
```
┌─────────────────────────┐
│    ← Back               │
├─────────────────────────┤
│                         │
│      🔒 [LOCK ICON]     │
│                         │
│  Enter Activation Code  │
│                         │
│  Code sent to:          │
│  01234567890            │
│                         │
│  ┌──┐ ┌──┐ ┌──┐ ┌──┐   │
│  │1 │ │2 │ │3 │ │4 │   │
│  └──┘ └──┘ └──┘ └──┘   │
│  ┌──┐ ┌──┐              │
│  │5 │ │6 │              │
│  └──┘ └──┘              │
│                         │
│  ┌─────────────────┐    │
│  │     Verify      │    │
│  └─────────────────┘    │
│                         │
│  Didn't receive code?   │
│       Resend            │
│                         │
│  ⚠️ Code expires in     │
│     10 minutes          │
│                         │
└─────────────────────────┘
```

**Features:**
- ✅ 6 separate input fields
- ✅ Auto-advance on input
- ✅ Auto-backspace on delete
- ✅ Numeric keyboard
- ✅ Auto-verify on 6th digit
- ✅ Manual verify button
- ✅ Resend code option
- ✅ Expiry warning
- ✅ Loading states

---

## 🏠 Main App Flow

### Screen 3: Home Dashboard (`/home`)

**Layout:**
```
┌─────────────────────────┐
│  Dashboard       [🚪]   │
├─────────────────────────┤
│  👋 Welcome Back!       │
│                         │
│  John Doe               │
│  ───────────────        │
│                         │
│  📊 SUBSCRIPTION        │
│  ┌─────────────────┐    │
│  │  ✅ Active       │    │
│  │                 │    │
│  │  💰 45 Coins    │    │
│  │  📅 15 days left│    │
│  └─────────────────┘    │
│                         │
│  ⚡ QUICK ACTIONS        │
│  ┌───────┐ ┌───────┐    │
│  │  📱   │ │  📋   │    │
│  │  QR   │ │ Sub.  │    │
│  │ Code  │ │Details│    │
│  └───────┘ └───────┘    │
│  ┌───────┐              │
│  │  📜   │              │
│  │Entry  │              │
│  │History│              │
│  └───────┘              │
│                         │
└─────────────────────────┘
```

**Status Variations:**
```
Active:   ✅ Green badge
Frozen:   ❄️ Blue badge with warning
Stopped:  ⛔ Red badge with alert
Expiring: ⚠️ Orange badge (< 7 days)
```

**Features:**
- ✅ Personalized welcome
- ✅ Status card with color coding
- ✅ Coins counter
- ✅ Days remaining
- ✅ Visual alerts
- ✅ 3 quick action buttons
- ✅ Logout button
- ✅ Pull to refresh

---

### Screen 4: QR Code Screen (`/qr`)

**Layout:**
```
┌─────────────────────────┐
│  ← QR Code              │
├─────────────────────────┤
│                         │
│  ┌─────────────────┐    │
│  │                 │    │
│  │   ▓▓▓▓▓▓▓▓▓     │    │
│  │   ▓▓    ▓▓▓     │    │
│  │   ▓▓▓▓▓▓▓▓▓     │    │
│  │   ▓▓    ▓▓▓     │    │
│  │   ▓▓▓▓▓▓▓▓▓     │    │
│  │                 │    │
│  │   [✅ Active]    │    │
│  └─────────────────┘    │
│                         │
│  ⏱️ Expires in:          │
│     59:45               │
│                         │
│  ┌─────────────────┐    │
│  │   🔄 Refresh    │    │
│  └─────────────────┘    │
│                         │
│  📌 Show this code at   │
│     gym entrance        │
│                         │
└─────────────────────────┘
```

**States:**
- ✅ **Active:** Green badge, QR enabled
- ⛔ **Frozen:** Blue badge, QR disabled
- ❌ **Stopped:** Red badge, QR disabled

**Features:**
- ✅ Large QR code (high contrast)
- ✅ Status badge overlay
- ✅ Countdown timer (1 hour)
- ✅ Refresh button
- ✅ Disabled state (grey overlay)
- ✅ Usage instructions
- ✅ Back navigation

---

### Screen 5: Subscription Details (`/subscription`)

**Layout:**
```
┌─────────────────────────┐
│  ← Subscription         │
├─────────────────────────┤
│                         │
│  ╔═══════════════════╗  │
│  ║ Gold Membership   ║  │
│  ║ [✅ Active]        ║  │
│  ╚═══════════════════╝  │
│                         │
│  📅 DATES                │
│  Start:  Jan 1, 2026    │
│  Expiry: Mar 31, 2026   │
│  Remaining: 15 days ⚠️  │
│                         │
│  💰 COINS                │
│  Remaining: 45 coins    │
│                         │
│  🎯 ALLOWED SERVICES     │
│  [Gym] [Pool] [Classes] │
│                         │
│  ❄️ FREEZE HISTORY       │
│  ┌─────────────────┐    │
│  │ Jan 15 - Jan 20 │    │
│  │ Reason: Travel  │    │
│  └─────────────────┘    │
│  ┌─────────────────┐    │
│  │ Feb 5 - Feb 10  │    │
│  │ Reason: Injury  │    │
│  └─────────────────┘    │
│                         │
└─────────────────────────┘
```

**Features:**
- ✅ Subscription type header
- ✅ Status badge
- ✅ Start/expiry dates
- ✅ Days remaining (color coded)
- ✅ Coins counter
- ✅ Service chips
- ✅ Freeze history timeline
- ✅ Pull to refresh

---

### Screen 6: Entry History (`/history`)

**Layout:**
```
┌─────────────────────────┐
│  ← Entry History        │
├─────────────────────────┤
│                         │
│  ┌─────────────────┐    │
│  │ Feb 10, 2026    │    │
│  │ 09:30 AM        │    │
│  │ ───────────     │    │
│  │ 📍 Main Branch   │    │
│  │ 🏋️ Gym Floor     │    │
│  │ 💰 3 coins used  │    │
│  └─────────────────┘    │
│                         │
│  ┌─────────────────┐    │
│  │ Feb 9, 2026     │    │
│  │ 18:45 PM        │    │
│  │ ───────────     │    │
│  │ 📍 Main Branch   │    │
│  │ 🏊 Swimming      │    │
│  │ 💰 5 coins used  │    │
│  └─────────────────┘    │
│                         │
│  ┌─────────────────┐    │
│  │ Feb 8, 2026     │    │
│  │ 07:00 AM        │    │
│  │ ───────────     │    │
│  │ 📍 Downtown     │    │
│  │ 🧘 Yoga Class    │    │
│  │ 💰 4 coins used  │    │
│  └─────────────────┘    │
│                         │
└─────────────────────────┘
```

**Empty State:**
```
┌─────────────────────────┐
│  ← Entry History        │
├─────────────────────────┤
│                         │
│                         │
│      📜                 │
│                         │
│   No entry history      │
│   yet                   │
│                         │
│   Your gym visits       │
│   will appear here      │
│                         │
│                         │
└─────────────────────────┘
```

**Features:**
- ✅ Chronological list (newest first)
- ✅ Date & time display
- ✅ Branch location
- ✅ Service used
- ✅ Coins consumed
- ✅ Card-based layout
- ✅ Pull to refresh
- ✅ Empty state message

---

## 🎨 Color Coding Guide

### Status Colors

| Status | Badge Color | Background | Use Case |
|--------|-------------|------------|----------|
| Active | 🟢 Green | Light green | Normal subscription |
| Frozen | 🔵 Blue | Light blue | Temporarily paused |
| Stopped | 🔴 Red | Light red | Expired/inactive |
| Expiring | 🟠 Orange | Light orange | < 7 days remaining |

### Component Colors

| Element | Color | Hex Code |
|---------|-------|----------|
| Primary | Red | #DC143C |
| Background | Dark Grey | #1F1F1F |
| Cards | Medium Grey | #2D2D2D |
| Inputs | Light Grey | #3D3D3D |
| Text Primary | White | #FFFFFF |
| Text Secondary | Grey | #B0B0B0 |

---

## 📱 Interaction Patterns

### Tap Targets
- Minimum size: **56dp x 56dp**
- Buttons: **48dp height** minimum
- Cards: **Full width** with 16dp padding

### Navigation
- **Back button:** Always visible (except welcome)
- **Bottom navigation:** Not used (single-purpose app)
- **Quick actions:** Large cards on home screen

### Feedback
- **Loading:** CircularProgressIndicator
- **Success:** Green SnackBar
- **Error:** Red SnackBar
- **Warning:** Orange SnackBar
- **Info:** Blue Card

### Gestures
- **Pull to refresh:** All data screens
- **Tap:** All buttons and cards
- **Swipe:** No swipe gestures (clarity)

---

## 🔄 State Management

### Loading States
```
┌─────────────────────────┐
│                         │
│         ⏳              │
│                         │
│    Loading...           │
│                         │
└─────────────────────────┘
```

### Error States
```
┌─────────────────────────┐
│                         │
│         ⚠️              │
│                         │
│  Connection failed      │
│                         │
│  ┌─────────────────┐    │
│  │     Retry       │    │
│  └─────────────────┘    │
│                         │
└─────────────────────────┘
```

### Empty States
```
┌─────────────────────────┐
│                         │
│         📭              │
│                         │
│  No data yet            │
│                         │
│  Content will appear    │
│  here when available    │
│                         │
└─────────────────────────┘
```

---

## 🚀 Navigation Flow

```
Welcome Screen
     ↓
  (Request code)
     ↓
Activation Screen
     ↓
  (Verify code)
     ↓
Home Dashboard ←──────────┐
     ↓                    │
  ┌──┼──┬─────────────┐   │
  ↓  ↓  ↓             ↓   │
 QR  Sub Entry      (All  │
Code scr History   have   │
  ↓  ↓  ↓           back  │
  └──┴──┴───────────→ btn)┘
     
Logout → Welcome Screen
```

---

## ✅ Accessibility Features

- ✅ Large text support
- ✅ High contrast mode ready
- ✅ Clear labels on all buttons
- ✅ Semantic labels for screen readers
- ✅ Minimum 44pt tap targets
- ✅ Clear error messages
- ✅ Loading indicators
- ✅ Form validation feedback

---

## 📋 Summary

**Total Screens:** 6
- 2 Authentication screens
- 4 Main app screens

**Total Routes:** 6
- `/welcome`
- `/activation`
- `/home`
- `/qr`
- `/subscription`
- `/history`

**Design System:** Material 3
**Theme:** Dark (Grey + Red)
**Min Target Size:** 56dp
**Max Thumb Reach:** One-handed optimized

---

**All screens are implemented and ready to use! 🎉**
