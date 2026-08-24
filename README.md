# nu_demo — Odoo 19 Community (Docker)

A from-scratch Odoo 19.0 **Community** instance, run via Docker Compose using the
official `odoo:19` image (no source checkout, no Enterprise addons). Infrastructure
is production-shaped (secrets, TLS, backups); the *data* in it is a fictional demo
dataset — see "Demo data" below for how to erase it before going live.

## Run it locally

```
cp .env.example .env            # fill in real values
cp config/odoo.conf.example config/odoo.conf   # fill in a real admin_passwd
docker compose up -d
```

- App: http://localhost:8069 (direct, kept for convenience) or https://localhost:8443
  (via nginx — browser will warn on the self-signed cert, that's expected locally)
- Login: `admin` / `admin` (technical superuser) or one of the seeded demo users
  (see WORKLOG/PROJECT.md in the vault for the demo user list and password)

Stop it with `docker compose down` (add `-v` to also wipe the database + backups volumes).

## Layout

- `docker-compose.yml` — four services:
  - `db` — Postgres 16
  - `odoo` — official Odoo 19 Community image, production-configured (`workers=2`,
    `proxy_mode=True`, `list_db=False`, `dbfilter` locked to `nu_demo`)
  - `nginx` — TLS-terminating reverse proxy (8080→8443 redirect, self-signed cert for
    now at `nginx/certs/`)
  - `backup` — runs `scripts/backup.sh` in a loop: daily `pg_dump` + filestore tar to
    `./backups/`, 14-day retention
- `.env` / `config/odoo.conf` — real secrets, **gitignored**. `.env.example` /
  `config/odoo.conf.example` are the checked-in templates.
- `addons/` — custom modules, mounted to `/mnt/extra-addons`:
  - `custom_home_dashboard/` — Enterprise-style Home Menu (app grid, search, navbar
    click-through) replicated for Community
  - `nu_demo_seed_data/` — the demo dataset (see below)

## Demo data

`addons/nu_demo_seed_data/` seeds a full fictional dataset modeled on a university
industry-partnerships office (Nazarbayev University): contacts, CRM pipeline (teams,
stages, tags, opportunities), projects with tasks and subtasks, departments and
employees, calendar events, and surveys. Every record it creates is tracked via
`ir.model.data` under that module's name.

**To erase all demo data once real production data is ready:** uninstall the module
(Settings → Apps → search "NU Demo Seed Data" → Uninstall). Odoo will cleanly remove
every record it created — no manual data hunting needed. The company record itself
(name, currency, website) was also set by this module and will need to be corrected
manually afterward if it should point at a different real company.

## Deploying to the team's server

1. Copy this directory to the server (or `git push` to a repo there).
2. Generate fresh secrets for `.env` and `config/odoo.conf` on the server — never
   reuse the local dev secrets.
3. Replace `nginx/certs/fullchain.pem` + `privkey.pem` with a real certificate
   (Let's Encrypt via certbot, or whatever the team already uses) and change
   `nginx/nginx.conf` to listen on 80/443 instead of 8080/8443.
4. Remove the direct `8069:8069` port mapping in `docker-compose.yml` once nginx is
   confirmed working, so only 80/443 are reachable from outside.
5. Set up real SMTP (Settings → Technical → Email → Outgoing Mail Servers) — not yet
   configured, so system emails (invites, notifications, password resets) don't send
   from this instance.
6. Once the team lead approves going live, uninstall `nu_demo_seed_data` (see above)
   before entering any real business data.
