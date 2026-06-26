# UGSP UI Design System & Component States

## Overview

Phase 2 of the UGSP frontend cleanup builds a structured design system layer on top of the existing single-page HTML application. This follows the previous Phase 1 work (backend DRY, CSS utility classes, basic accessibility fixes).

## Goals

- Systematic component states (loading, empty, error, disabled) applied uniformly
- Professional micro-interactions and transitions
- WCAG 2.2 AA accessibility (focus management, ARIA, keyboard nav)
- Responsive layout down to mobile (480px)
- Toast/notification system replacing ad-hoc alert panels
- No build tools, no framework — pure CSS + vanilla JS

## 1. Design Token System

### State Tokens
```
--state-loading:       color-mix(in srgb, var(--steel) 20%, transparent)
--state-error-bg:      #fef2f2
--state-error-border:  #dc2626
--state-error-text:    #991b1b
--state-success-bg:    #f0fdf4
--state-success-border: #16a34a
--state-success-text:  #166534
--state-empty-bg:      #f8f9fb
--state-disabled:      #9ca3af
--state-disabled-bg:   #e5e7eb
```

### Radius Tokens
```
--radius-full:  9999px
--radius-card:  12px
--radius-sm:    8px
```

### Motion Tokens
```
--duration-fast:   150ms
--duration-normal: 250ms
--duration-slow:   400ms
--ease-out:       cubic-bezier(0.16, 1, 0.3, 1)
--ease-spring:    cubic-bezier(0.34, 1.56, 0.64, 1)
```

### Focus Token
```
--focus-ring: 0 0 0 3px color-mix(in srgb, var(--steel) 40%, transparent)
```

## 2. Component State Architecture

### State classes (applied via JS `setComponentState(el, state)`)

Every component type gets these CSS classes:

| Class | Meaning | Visual |
|-------|---------|--------|
| `.is-loading` | Content being fetched | Skeleton shimmer or spinner |
| `.is-empty` | No data to show | Empty state illustration + message |
| `.has-error` | Validation/server error | Red border, error message |
| `.is-disabled` | Temporarily unavailable | Reduced opacity, no pointer events |
| `.is-selected` | Currently chosen item | Gold border/glow |

### Buttons
- `.btn.is-loading` — inline SVG spinner replaces label, button disabled
- `.btn.is-disabled` — opacity 0.5, cursor not-allowed
- Default → hover → active → focus transitions with `var(--duration-fast)`

### Form inputs
- `.has-error` — red border, error icon via background, `.field-error` text below
- `.is-valid` — green border, check icon
- `:focus-visible` — consistent `var(--focus-ring)` box-shadow

### Cards (`.card`, `.stat-card`, service items)
- `.is-loading` — skeleton shimmer replaces all content
- `.is-empty` — centered icon + "No data" with optional CTA
- `.is-selected` — gold border, subtle shadow elevation

### Lists (application list, payment history)
- `.is-empty` — full-width `.empty-state` block
- `.is-loading` — 3 skeleton rows stacked vertically

## 3. Loading & Skeleton States

### Button spinner
```
.btn.is-loading .btn-label { opacity: 0; }
.btn.is-loading::after {
  content: '';
  position: absolute; inset: 0; margin: auto;
  width: 20px; height: 20px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
```

### Skeleton shimmer
- Base `.skeleton` — grey gradient animated via background-position
- `.skeleton-text` — block element, ~60% width
- `.skeleton-avatar` — circle element
- `.skeleton-card` — full card outline with 3 text lines
- `aria-busy="true"` + `aria-label="Loading..."` applied programmatically

### Page transitions
- Route/state changes: fade out `150ms` → swap content → fade in `250ms`
- `.page-enter` / `.page-leave` classes managed via JS
- `transform: translateY(4px)` for subtle vertical slide

## 4. Error, Empty & Notification System

### Empty state component
```
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 48px 24px; text-align: center;
}
.empty-state-icon { font-size: 48px; opacity: 0.4; }
.empty-state-title { font-weight: 600; font-size: 1.1rem; }
.empty-state-desc { color: var(--text-secondary); font-size: 0.9rem; }
.empty-state-cta { margin-top: 16px; }
```

### Inline form validation
- `<input aria-describedby="field-email-error">`
- `<div id="field-email-error" class="field-error" role="alert">Invalid email</div>`
- `.field-error` uses `grid-template-rows: 0fr` → `1fr` transition

### Toast notification system
- Fixed top-right stack, z-index 1001
- 3 types: `success`, `error`, `info`
- Each: icon + message + close button
- Auto-dismiss after 4s, hover pauses
- `role="status"` + `aria-live="polite"`
- JS API: `function showToast(message, type, duration?)`

### Network offline bar
- Slim yellow bar at top when `navigator.onLine === false`
- CSS `@media` + `body.is-offline` class
- `position: sticky; top: 0; z-index: 999`

## 5. Accessibility & Focus Management

### Global focus ring
```
:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
  border-radius: var(--radius-sm);
}
```

### Modal focus trap
1. Save `document.activeElement` on open
2. Query all focusable children within the modal
3. Tab cycles first → last → first
4. Escape closes modal
5. On close, restore focus to trigger

### ARIA attributes
- `role="alert"` + `aria-live="assertive"` on toasts
- `aria-describedby` on inputs linked to error messages
- `aria-expanded` on sidebar toggle
- `aria-current="page"` on active nav link
- `aria-hidden="true"` on decorative icons
- `role="status"` on spinners

### Skip link
- Already exists; add `tabindex="-1"` on `<main>` so focus lands on #main-content target

## 6. Responsive & Mobile

### Breakpoints
```css
@media (max-width: 768px)  { /* tablet */ }
@media (max-width: 480px)  { /* mobile */ }
```

### Sidebar on mobile
- Collapsed by default
- Overlays content with `rgba(0,0,0,0.3)` backdrop
- `position: fixed` instead of static when collapsed

### Forms on mobile
- Grid forms stack vertically
- Inputs + buttons `width: 100%`
- Card grids: 3-col → 2-col → 1-col

### Touch targets
- Minimum 44×44px for all interactive elements
- Sidebar nav items get `padding: 12px 16px`
- Close/back buttons larger hit area

### Tables on mobile
- Horizontal scroll wrapper (`.table-scroll`)
- Scroll hint: fading gradient on right edge on hover

## Out of Scope

- No server-side changes (backend already DRY'd in Phase 1)
- No framework or build tooling
- No dark mode implementation (tokens prepared via `light-dark()` only)
- No new features — only UI/UX refinement of existing screens
