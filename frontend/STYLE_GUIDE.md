# MENA Signal Design System

A modern, premium design system for a VC-backed AI funding intelligence platform.

## Design Principles

1. **Clarity over decoration** - Every element serves a purpose
2. **Generous whitespace** - Let content breathe
3. **Strong hierarchy** - Clear visual order guides the eye
4. **Subtle sophistication** - Premium feel without over-design
5. **Consistent rhythm** - Predictable spacing and sizing

---

## Typography

### Font Family
- **Primary**: Inter (Google Fonts)
- **Fallback**: system-ui, -apple-system, sans-serif

### Scale
| Element | Size | Weight | Letter-spacing |
|---------|------|--------|----------------|
| H1 (Page title) | 28px | 600 | -0.025em |
| H2 (Section header) | 24px | 600 | -0.02em |
| H3 (Card title) | 18px | 500 | -0.015em |
| Body | 15px | 400 | -0.011em |
| Small / Meta | 13px | 400 | normal |
| Caption / Label | 12px | 500 | normal |

### Line Heights
- Headings: 1.2-1.3
- Body text: 1.6
- UI elements: 1.4

---

## Spacing

### Base Unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| 1 | 4px | Micro gaps |
| 2 | 8px | Icon gaps, tight padding |
| 3 | 12px | Component inner padding |
| 4 | 16px | Section gaps |
| 5 | 20px | Card padding |
| 6 | 24px | Between elements |
| 8 | 32px | Section spacing |
| 10 | 40px | Page margins |

### Common Patterns
- Card padding: 20-24px
- Row padding: 20-24px horizontal, 16-20px vertical
- Page content max-width: 1024px (max-w-5xl)
- Sidebar width: 256px (w-64)

---

## Colors

### Dark Mode (Primary)

```css
/* Backgrounds */
--background: 225 15% 6%;      /* Page background */
--card: 225 15% 8%;            /* Card/elevated surfaces */
--muted: 225 12% 12%;          /* Subtle backgrounds */

/* Text */
--foreground: 220 15% 95%;     /* Primary text */
--muted-foreground: 220 10% 55%; /* Secondary text */

/* Borders */
--border: 225 12% 14%;         /* Default borders */

/* Score Colors */
--score-high: 152 55% 48%;     /* Green: 70-100 */
--score-medium: 38 85% 55%;    /* Amber: 40-69 */
--score-low: 0 60% 58%;        /* Red: 0-39 */
```

### Usage Guidelines
- Borders: Use `border-border/60` for subtle, `border-border` for prominent
- Hover states: `bg-foreground/[0.02]` for rows, `bg-muted/50` for buttons
- Focus rings: `ring-ring/50` with `ring-offset-background`

---

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| sm | 6px | Small badges, tags |
| md | 8px | Inputs, small buttons |
| lg | 12px | Standard buttons, inputs |
| xl | 14px | Cards, larger elements |
| 2xl | 18px | Large cards, modals |
| full | 9999px | Pills, switches |

---

## Shadows

### Soft Shadow (Primary)
```css
.shadow-soft {
  box-shadow: 
    0 1px 2px hsl(var(--foreground) / 0.04),
    0 4px 12px hsl(var(--foreground) / 0.04);
}
```

### Large Soft Shadow
```css
.shadow-soft-lg {
  box-shadow: 
    0 2px 4px hsl(var(--foreground) / 0.03),
    0 8px 24px hsl(var(--foreground) / 0.06);
}
```

---

## Components

### Buttons
- Height: 40px (h-10) standard, 44px (h-11) for forms
- Border radius: 14px (rounded-xl)
- Font: 14px, medium weight
- Padding: 20px horizontal

### Inputs
- Height: 44px (h-11)
- Border radius: 14px (rounded-xl)
- Border: `border-border/60`
- Focus: subtle ring, border color change

### Cards
- Border radius: 18px (rounded-2xl)
- Border: `border-border/60`
- Background: `bg-card`
- Shadow: `shadow-soft`

### Item Rows
- Padding: 24px horizontal, 20px vertical
- Border bottom: `border-border/40`
- Hover: `bg-foreground/[0.02]`

### Score Pills
- Border radius: 14px (rounded-xl)
- Height: 32px (md) / 28px (sm) / 40px (lg)
- Includes progress bar indicator
- Color-coded by score range

---

## Animation

### Transitions
- Default duration: 150ms
- Easing: ease-out for entrances, ease-in-out for state changes

### Keyframes
```css
/* Fade in with slide */
@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Stagger children */
.stagger-children > *:nth-child(1) { animation-delay: 0ms; }
.stagger-children > *:nth-child(2) { animation-delay: 30ms; }
/* ... etc */
```

### Motion Guidelines
- Use for feedback (hover, focus, loading)
- Stagger list items on load
- Keep animations under 300ms
- Prefer opacity + transform over complex animations

---

## Icons

Using **Lucide React** icons consistently:

| Size | Class | Usage |
|------|-------|-------|
| 16px | h-4 w-4 | Inline with text, buttons |
| 18px | h-[18px] w-[18px] | Standalone in rows |
| 20px | h-5 w-5 | Menu items, larger UI |
| 28px | h-7 w-7 | Feature icons |

### Common Icons
- Dashboard: `LayoutDashboard`
- Favorites: `Star`
- Sources: `Database`
- Search: `Search`
- Filter: `SlidersHorizontal`
- External link: `ExternalLink`
- Menu: `Menu`
- Close: `X`
- Add: `Plus`
- Refresh: `RefreshCw`
- Arrow: `ChevronRight`

---

## Accessibility

### Focus States
- All interactive elements have visible focus rings
- Use `focus-visible` for keyboard-only focus
- Focus ring offset for contrast

### ARIA
- Icon buttons require `aria-label`
- Loading states announced with `aria-busy`
- Modals trap focus and have proper labels

### Color Contrast
- Text meets WCAG AA (4.5:1 minimum)
- Interactive elements: 3:1 contrast
- Don't rely solely on color for meaning

---

## Responsive Breakpoints

| Name | Width | Behavior |
|------|-------|----------|
| Default | < 640px | Mobile: sidebar hidden, stacked layout |
| sm | ≥ 640px | Small adjustments |
| md | ≥ 768px | Tablet adaptations |
| lg | ≥ 1024px | Desktop: sidebar visible |

### Mobile Considerations
- Sidebar becomes slide-over sheet
- Touch targets minimum 44x44px
- Simplified filter bar
- Single column layouts

