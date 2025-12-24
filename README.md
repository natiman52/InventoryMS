
# Sales Inventory Management

## Overview
Sales Inventory Management is a Django-based web application for managing inventory, sales, billing, and simple production workflows. It provides tools for tracking items, clients, invoices/audits, and daily operational costs. The app focuses on usability and quick daily reporting for small manufacturing or metal-cutting operations.

## What the app does
- Track manufactured items (thickness, quantity, DXF files, completion status).
- Create audits/invoices for completed items that calculate: unit totals, scrap adjustments, gross revenue, gross cost, allocated operational cost, gross profit, and net profit.
- Record daily operational bills (rent, logistics, payroll, electric, overtime) and distribute those costs across produced units.
- Show daily summaries: total sheets (lamera), client counts, per-thickness aggregates, and per-client debts.
- Prepare an audit list (items completed but not yet invoiced) with quick links to create or view audits.

## Key apps and responsibilities
- `store` — Manages items, clients, and file attachments (DXF). Items are the primary production records.
- `invoice` — Stores `Invoice` records linked to `Item`. Computes financial metrics on save and provides list/detail/create/update/delete views and templates.
- `bills` — Stores daily operational bills and helper functions to aggregate them.
- `accounts` — User and profile management (permissions used for restricting updates/deletes).

## How invoices & the detail page work (high level)
- When you create an invoice for an `Item`, the `Invoice.save()` method computes derived fields:
	- total = quantity * unit_price
	- gross_revenue = total + (scrap_value * quantity)
	- gross_cost = sheet_metal_cost * quantity
	- gross_profit = gross_revenue - gross_cost
	- opertional_cost is calculated by reading the day's Bills, summing them, and allocating the daily operational cost proportionally across the total sheets produced that day.
	- net_profit = gross_profit - opertional_cost
- The detail page (`/audit/<id>/`) simply reads these persisted fields and displays them (net_profit, breakdown of costs, scrap info, dimensions, etc.).

## Tech stack and libraries
- Python, Django (web framework)
- django-crispy-forms (forms layout)
- django-tables2 (tabular listing and export)
- django-extensions (AutoSlugField used in invoices)
- Bootstrap (front-end styling)
- Standard Django ORM — works with any supported database (PostgreSQL, MySQL, SQLite) depending on your settings.

## Development — how to run locally
1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run migrations and start the dev server

```bash
python manage.py migrate
python manage.py runserver
```

4. (Optional) Load sample data or import backups (project backups are stored under `backups/` as database dumps).

## Project structure (high-level)
- `accounts/` — authentication, profiles, signals, filters
- `store/` — item model, file storage, production records
- `invoice/` — invoice/audit creation, views, templates, calculation helpers
- `bills/` — daily bills, algebra helpers, and aggregation functions
- `templates/` — app templates including invoice views
- `manage.py`, `requirements.txt`, and `README.md`

## Notes, caveats and recommended improvements
- The invoices compute operational allocations at save time; if bills or items change later, the stored invoice values may become inconsistent unless invoices are updated.
- There are a few known places to harden the code: guard against division by zero when allocating operational cost, ensure `InvoiceUpdateView` fields match the model, and make the invoice table model consistent.

## Contributing
Please open issues or pull requests. If you add features, include tests and update `requirements.txt` where appropriate.

## License
This repository doesn't include a formal license file — add one if you plan to publish the project.


