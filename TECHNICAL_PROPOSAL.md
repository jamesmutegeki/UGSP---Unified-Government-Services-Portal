# UGSP — Technical Proposal

## Overview
Unified Government Services Portal (UGSP) — a single-entry digital government platform inspired by the Uganda Revenue Authority's vision for a comprehensive e-government portal. Built with Python FastAPI backend and vanilla HTML/CSS/JS frontend, served at same origin.

## Architecture
- **Backend**: Python 3.11+, FastAPI, uvicorn (port 8000)
- **Frontend**: Vanilla HTML/CSS/JS, inline (`app/static/index.html`, ~1520 lines)
- **Auth**: NIN-based login → 2FA → `ugpass_` Bearer tokens
- **Data**: In-memory dictionaries (resets on restart)
- **Seed**: `seed_fast.py` — 38 steps, 15 users, 45 apps, 15 payments, 25 ministries, 29 services
- **Tests**: `smoke_test.py` — 95 tests, `verify_frontend.py` — 12 checks

## Routing (Frontend)
- **Hash-based**: `navigateTo()` sets `location.hash`; `hashchange` listener routes pages
- **Page aliases**: `PAGE_ALIASES` maps short names (e.g. `catalogue` → `services`)
- **Pages**: Applications, Services, Payments, Documents, Settings, News, Help, Activity, About, Feedback
- **Dashboard conditional routing**: Stats redirect to Applications with `?filter=approved|pending`
- **I18N**: `data-i18n` attributes on all sidebar navs; `setLanguage()` updates text + re-renders

## Features Implemented
### 1. Global Navigation & Routing
- Hash-based SPA routing with page aliases
- Signup button `type="button"` + `id` on login card

### 2. Dashboard Conditional Routing
- "In Progress" stat clickable → Applications with `filter='pending'`
- "Approved" stat clickable → Applications with `filter='approved'`
- `filterAppsTable(filter)` + `renderAppsTable()` handle filtered view

### 3. View Action Lifecycle
- `showAppAction(id, action)` renders status-appropriate buttons:
  - `submitted` / `under_review` → Resume
  - `draft` → Edit or Delete
  - `approved` / `rejected` / `cancelled` / `completed` → View

### 4. Payment Gateway Conditional Fields
- `PAY_FIELD_CONFIG` — schema per channel:
  - `mobile_money` → phone number
  - `card` → card number, expiry, CVV
  - `bank_transfer` → bank name, account number
- `updatePayFields(channel)` dynamically renders fields in checkout modal

### 5. Notification Engine
- `loadNotifHistory()` / `saveNotifHistory()` — localStorage persistence (`ugsp_notif_history`)
- Visual hierarchy: unread = tinted bg + left border; read = `opacity:0.75`
- `timeSince()` for relative timestamps; `markNotifRead(i)` updates state

### 6. Refresh Buttons
- `showRefresh(elId)` — shows "Updated HH:MM:SS" indicator for 2.5s
- Scoped: Documents (`docRefresh`), Payments (`payRefresh`)

### 7. i18n Instant Sync
- 14 sidebar nav items with `data-i18n` attributes
- `setLanguage()` handles icon+text child patterns, triggers `loadDashboard` + `loadApplications`

### 8. Responsive Sidebar
- Hamburger button on mobile toggles `.sidebar.open`
- Collapse chevron toggles `.sidebar-collapsed` on layout
- CSS: `.sidebar-collapsed .sidebar:not(.open)` to avoid specificity conflict

### 9. Custom Scrollbars
- Yellow-thumb (`var(--gold)`) Webkit scrollbars on `sidebar-nav` and `login-card`

### 10. UI/UX Polish
- Fade-in page animation (0.25s)
- Card hover elevated borders
- Stat-value color change on hover
- Input focus shadow ring `0 0 0 3px rgba(46,107,158,0.12)`
- Button press `::after` overlay
- Badge scale animation on load
- Refresh indicator styling
- Letter-spacing on headings
- 480px responsive breakpoint

### 11. Login Enhancements
- "Remember me" checkbox — persists NIN to `localStorage('ugsp_remember_nin')`
- Loading spinner on login button (`#loginSpinner`)
- "Forgot password?" inline link in login form

## Key Files
| File | Description |
|------|-------------|
| `app/static/index.html` | Single-page frontend (~1520 lines, all inline JS/CSS) |
| `app/static/manifest.json` | PWA manifest |
| `app/static/sw.js` | Service worker (static cache-first, API network-first) |
| `app/main.py` | FastAPI app entry point |
| `app/api/v1/auth.py` | Auth, 2FA, profile, feedback, documents, payments, notifications |
| `app/api/v1/payments.py` | Checkout, PRN, payment status |
| `app/api/v1/applications.py` | CRUD applications with status flow |
| `app/api/v1/catalogue.py` | 29 services, 25 ministries |
| `seed_fast.py` | 38-step seeder |
| `smoke_test.py` | 95 tests (all passing) |
| `verify_frontend.py` | 12 frontend checks |
| `run.py` | Uvicorn launcher |

## Demo Credentials
| NIN | Password | Name | Category |
|-----|----------|------|----------|
| T1234567890 | pass123 | Grace Akello | citizen |
| T1000000001 | newseed123 | Amos Muwonge | citizen |
| T1000000003 | seed123 | Peter Kaggwa | business |
| T1000000006 | seed123 | Grace Achieng | visitor |

## Running
```bash
python run.py          # Start server at http://localhost:8000
python seed_fast.py    # Seed demo data
python smoke_test.py   # Run 95 tests
python verify_frontend.py  # Run 12 frontend checks
```

## Future Work
- Supabase PostgreSQL migration (see `SUPABASE_MIGRATION.md`)
- Cloud Run deployment (see `Dockerfile`)
- 404 page handler
- End-to-end application status flow (approve/reject via admin)
