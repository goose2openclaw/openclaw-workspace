# GO2SE DESIGN.md — 北斗七鑫量化交易平台

GO2SE is a crypto quantitative trading platform with a professional financial dashboard aesthetic. Dark theme with emerald green accents, designed for real-time market monitoring and automated trading.

## Design Philosophy

GO2SE embodies "precision meets velocity" — a trading terminal that feels alive with market data while remaining calm and focused. The interface should feel like a professional trader's cockpit: information-dense but never overwhelming.

## Color Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Background Primary | Void Black | `#0A0E17` | Main background |
| Background Secondary | Deep Navy | `#111827` | Cards, panels |
| Background Tertiary | Slate | `#1F2937` | Elevated surfaces |
| Accent Primary | Emerald Green | `#00D4AA` | Positive signals, CTAs, highlights |
| Accent Secondary | Violet | `#7C3AED` | Secondary actions, AI elements |
| Accent Tertiary | Amber Gold | `#F59E0B` | Warnings, Bitcoin, premium features |
| Text Primary | White | `#FFFFFF` | Headings, key numbers |
| Text Secondary | Gray | `#9CA3AF` | Body text, labels |
| Text Muted | Dark Gray | `#6B7280` | Hints, timestamps |
| Success | Green | `#10B981` | Profit, success states |
| Danger | Red | `#EF4444` | Loss, errors, stop-loss |
| Warning | Yellow | `#FBBF24` | Caution, pending |

## Typography

| Element | Font | Weight | Size |
|---------|------|--------|------|
| Display | JetBrains Mono | 700 | 32px |
| Heading 1 | Inter | 700 | 24px |
| Heading 2 | Inter | 600 | 18px |
| Heading 3 | Inter | 600 | 16px |
| Body | Inter | 400 | 14px |
| Label | Inter | 500 | 12px |
| Mono/Number | JetBrains Mono | 400 | 14px |
| Caption | JetBrains Mono | 400 | 11px |

## Typography Scale

```
Display: 32px / 1.2
H1: 24px / 1.3
H2: 18px / 1.4
H3: 16px / 1.4
Body: 14px / 1.5
Small: 12px / 1.4
Caption: 11px / 1.3
```

## Spacing System

Base unit: 4px

| Token | Value |
|-------|-------|
| xs | 4px |
| sm | 8px |
| md | 16px |
| lg | 24px |
| xl | 32px |
| 2xl | 48px |

## Border Radius

| Element | Radius |
|---------|--------|
| Card | 12px |
| Button | 8px |
| Input | 6px |
| Badge | 4px |
| Full | 9999px (pills) |

## Shadows

```css
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.5);
--shadow-glow: 0 0 20px rgba(0, 212, 170, 0.3);
```

## Visual Language

### Gradients

- **Hero gradient**: `linear-gradient(135deg, #0A0E17 0%, #111827 50%, #1F2937 100%)`
- **Accent glow**: `radial-gradient(circle, rgba(0, 212, 170, 0.15) 0%, transparent 70%)`
- **Card shimmer**: `linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent)`

### Animations

| Animation | Duration | Easing | Usage |
|-----------|----------|--------|-------|
| Fade in | 300ms | ease-out | Page transitions |
| Slide up | 400ms | cubic-bezier(0.16, 1, 0.3, 1) | Cards appearing |
| Pulse | 2s | ease-in-out | Live indicators |
| Glow | 1.5s | ease-in-out | Signal highlights |
| Number tick | 150ms | linear | Price updates |

### Motion Principles

1. **Subtle aliveness**: Prices and signals should feel alive, not static
2. **Confidence through stability**: No excessive bouncing or distraction
3. **Data-forward**: Animation serves information, not decoration
4. **Responsive**: Micro-interactions on every clickable element

## Component Specifications

### Cards

- Background: `#111827`
- Border: `1px solid rgba(255, 255, 255, 0.05)`
- Border radius: 12px
- Padding: 20px
- Shadow: `--shadow-md`
- Hover: `border-color: rgba(0, 212, 170, 0.3)`

### Buttons

**Primary**
- Background: `#00D4AA`
- Text: `#0A0E17`
- Hover: brightness(1.1)
- Active: scale(0.98)
- Disabled: opacity(0.5)

**Secondary**
- Background: `transparent`
- Border: `1px solid rgba(255, 255, 255, 0.1)`
- Text: `#FFFFFF`
- Hover: background `rgba(255, 255, 255, 0.05)`

**Danger**
- Background: `#EF4444`
- Text: `#FFFFFF`

### Badges

| Type | Background | Text |
|------|-----------|------|
| Success | `rgba(16, 185, 129, 0.15)` | `#10B981` |
| Danger | `rgba(239, 68, 68, 0.15)` | `#EF4444` |
| Warning | `rgba(251, 191, 36, 0.15)` | `#FBBF24` |
| Info | `rgba(124, 58, 237, 0.15)` | `#7C3AED` |
| Neutral | `rgba(156, 163, 175, 0.15)` | `#9CA3AF` |

### Tables

- Header: Background `#1F2937`, text uppercase, font-weight 600, font-size 11px
- Row: Background transparent, border-bottom `1px solid rgba(255,255,255,0.03)`
- Row hover: Background `rgba(0, 212, 170, 0.03)`
- Cell padding: 12px 16px

### Charts

- Grid lines: `rgba(255, 255, 255, 0.05)`
- Axis labels: `#6B7280`, 11px JetBrains Mono
- Line colors: Use accent palette (emerald for up, red for down)
- Area fill: Gradient from line color to transparent (opacity 0.1)

## Page Structure

### Navigation

- Sidebar: 64px width collapsed, 240px expanded
- Active item: Background `rgba(0, 212, 170, 0.1)`, left border 3px `#00D4AA`
- Icons: 20px, Lucide icon set

### Page Hierarchy

1. **Dashboard (总览)**: 4-column metric cards + chart + recent signals
2. **Market (市场)**: Full-width table + RSI chart
3. **Strategies (策略)**: Card grid 3-column
4. **Signals (信号)**: List view with confidence bars
5. **Trading (交易)**: Two-column layout (form + positions)
6. **Wallet (钱包)**: Balance + allocation chart
7. **Settings (设置)**: Form sections with dividers

## Responsive Breakpoints

| Breakpoint | Target |
|------------|--------|
| < 640px | Mobile, single column |
| 640-1024px | Tablet, 2-column |
| 1024-1440px | Laptop, 3-column |
| > 1440px | Desktop, 4-column, max-width 1600px |

## Dark Mode

This design is **dark-mode only**. No light mode support.

Background layers from darkest to lightest:
1. `#0A0E17` — page background
2. `#111827` — cards
3. `#1F2937` — elevated elements
4. `#374151` — hover states

## Iconography

- **Library**: Lucide Icons
- **Size**: 16px (inline), 20px (standalone), 24px (feature)
- **Stroke**: 1.5px
- **Color**: inherit from text color

## Data Visualization Colors

| Data Type | Color |
|-----------|-------|
| Profit/Up | `#10B981` |
| Loss/Down | `#EF4444` |
| Neutral | `#6B7280` |
| BTC | `#F7931A` |
| ETH | `#627EEA` |
| Volume | `#7C3AED` |
| Confidence High | `#00D4AA` |
| Confidence Low | `#EF4444` |

## Accessibility

- Minimum contrast ratio: 4.5:1 for body text
- Focus indicators: 2px `#00D4AA` outline
- All interactive elements keyboard accessible
- Screen reader labels for icons and charts

## Implementation Notes

- Use CSS custom properties for all colors
- Numbers always in JetBrains Mono
- Prices: 2 decimal places for USD, 8 for small crypto amounts
- Percentages: 1 decimal place
- Timestamps: UTC, format `HH:mm:ss`
- Dates: ISO format `YYYY-MM-DD`

---

*This DESIGN.md defines the visual language for GO2SE. Any AI agent building on this platform should follow these specifications for consistent UI.*
