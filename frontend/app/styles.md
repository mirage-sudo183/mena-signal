# MENA Signal Design System

A clean, investor-grade design system inspired by Bloomberg and Notion.

## Typography

### Font Stack
- **Primary**: Inter (Google Font)
- **Monospace**: System monospace for tabular data

### Scale
| Name | Size | Weight | Usage |
|------|------|--------|-------|
| h1 | 24px (1.5rem) | 600 | Page titles |
| h2 | 20px (1.25rem) | 600 | Section headers |
| h3 | 18px (1.125rem) | 500 | Card titles |
| h4 | 16px (1rem) | 500 | Subsection headers |
| body | 14px (0.875rem) | 400 | Default text |
| small | 12px (0.75rem) | 400 | Meta, captions |
| xs | 11px (0.6875rem) | 400 | Labels, badges |

### Line Heights
- Tight: 1.25 (headings)
- Normal: 1.5 (body)
- Relaxed: 1.625 (long-form text)

## Spacing

### Base Unit: 4px

| Token | Value | Usage |
|-------|-------|-------|
| 0.5 | 2px | Micro gaps |
| 1 | 4px | Icon gaps |
| 1.5 | 6px | Tight padding |
| 2 | 8px | Small gaps |
| 3 | 12px | Component padding |
| 4 | 16px | Card padding |
| 6 | 24px | Section gaps |
| 8 | 32px | Page margins |

## Colors

### Semantic Tokens (Dark Mode)
```css
--background: 220 13% 4%;      /* Near black */
--foreground: 220 13% 98%;     /* Near white */
--card: 220 13% 6%;            /* Slightly lighter */
--muted: 220 13% 10%;          /* Muted backgrounds */
--muted-foreground: 220 9% 55%; /* Secondary text */
--border: 220 13% 15%;          /* Subtle borders */
--primary: 0 0% 100%;           /* White accent */
```

### Score Colors
| Range | Color | Class |
|-------|-------|-------|
| 70-100 | Emerald | `score-high` |
| 40-69 | Amber | `score-medium` |
| 0-39 | Red | `score-low` |

## Components

### Item Row
Compact row for feed items:
- Height: ~56-80px depending on content
- Score pill on left
- Title + meta + summary in center
- Actions on right
- Hover: subtle background tint

### Score Pill
- Rounded badge with score number
- Optional progress bar indicator
- Color-coded by score range
- Tooltip on hover

### Filter Bar
- Search input with icon
- Date range select
- Min score slider popover
- Clear filters button

### Empty State
- Centered content
- Geometric icon placeholder
- Title + description
- Optional action button

### Page Header
- Title (h1)
- Optional description
- Right-aligned actions

## Patterns

### Hover States
```css
.row-hover {
  @apply hover:bg-muted/50 transition-colors duration-100;
}
```

### Focus Rings
```css
.focus-ring {
  @apply focus:outline-none focus-visible:ring-2 focus-visible:ring-ring 
         focus-visible:ring-offset-2 focus-visible:ring-offset-background;
}
```

### Transitions
```css
.transition-default {
  @apply transition-all duration-150 ease-in-out;
}
```

## Layout

### App Shell
- Fixed sidebar: 240px (hidden on mobile)
- Top bar: 56px height
- Content: max-width 896px (4xl), centered

### Responsive Breakpoints
| Name | Width |
|------|-------|
| sm | 640px |
| md | 768px |
| lg | 1024px |

### Mobile Adaptations
- Sidebar becomes sheet overlay
- Tables hide less-critical columns
- Filter bar wraps naturally

## Icons

Use Lucide React icons consistently:
- Size: 16px (h-4 w-4) for inline
- Size: 20px (h-5 w-5) for standalone
- Color: `text-muted-foreground` default
- Hover: `text-foreground`

### Common Icons
| Purpose | Icon |
|---------|------|
| Dashboard | LayoutDashboard |
| Favorites | Star |
| Sources | Database |
| Search | Search |
| Filter | SlidersHorizontal |
| External link | ExternalLink |
| Menu | Menu |
| Close | X |
| Add | Plus |
| Refresh | RefreshCw |

## Accessibility

### Focus Management
- All interactive elements have visible focus states
- Tab order follows visual layout
- Keyboard navigation for all actions

### ARIA
- Icon buttons have `aria-label`
- Modals trap focus
- Loading states announced

### Color Contrast
- Text meets WCAG AA (4.5:1 minimum)
- Interactive elements meet 3:1 contrast

