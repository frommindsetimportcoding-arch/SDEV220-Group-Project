# DonationAssist AI Coding Guidelines

## Architecture Overview
- **Django 6.0.1** project with MTV pattern
- **inventory** app: Core functionality for item management, prioritization, and donation cart
- **Service Layer**: `InventoryLogic` handles business logic; `PriceSimulator` manages vendor pricing
- **Session-Based State**: Cart and price caches stored in Django sessions (no database persistence for cart)

## Key Patterns
- **Priority Calculation**: Items have urgency levels (1-5) based on quantity/max_quantity thresholds. Calculated automatically in `Item.save()` via `calculate_urgency` property
- **Price Simulation**: Random prices generated for 3 vendors (Amazon, Walmart, Target) within 70-130% of unit_price. Cached in session for 10 seconds
- **Cart Management**: Items added to session dict with vendor/price snapshot. No DB storage for cart
- **Model Fields**: `items` (name), `category`, `description`, `quantity`, `max_quantity`, `priority_level`, `unit_price`, threshold levels (lvl_1-lvl_5 as %)

## Developer Workflows
- **Run Server**: `python manage.py runserver` (uses SQLite by default)
- **Migrations**: `python manage.py makemigrations inventory && python manage.py migrate`
- **Admin Setup**: `python manage.py createsuperuser` for Django admin access
- **Virtual Env**: Always activate `.venv` before running commands
- **Testing**: No tests implemented yet; add to `inventory/tests.py`

## Conventions
- **Imports**: Standard Django imports + `from .services import InventoryLogic`
- **Views**: Use service layer for logic; render templates from `inventory/templates/`
- **Templates**: Extend `inventory/base.html`; use Bootstrap 5.3 + custom rainbow CSS
- **URLs**: App-level in `inventory/urls.py`; included in main `urls.py`
- **Static Files**: CSS in `inventory/static/inventory/css/`

## Integration Points
- **No External APIs**: Self-contained Django app
- **Database**: SQLite for development; configure in `settings.py`
- **Sessions**: Used for cart and price caching; ensure `SESSION_ENGINE` is default

## Common Tasks
- Adding items: Create via admin or fixtures; priority auto-calculates
- Modifying cart: Update session dict in views; mark `session.modified = True`
- Price updates: Clear session cache or wait TTL for fresh prices