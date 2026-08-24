# nu_demo — Odoo 19 Community (Docker)

A from-scratch Odoo 19.0 **Community** instance, run via Docker Compose using the
official `odoo:19` image (no source checkout, no Enterprise addons). Infrastructure
is production-shaped (secrets, TLS, backups, SMTP); the *data* in it is a fictional
demo dataset — see "Demo data" below for how to erase it before going live.

Repo: https://github.com/Kair97/nu_demo

## Run it locally

```
cp .env.example .env            # fill in real values
cp config/odoo.conf.example config/odoo.conf   # fill in a real admin_passwd
docker compose up -d
```

- App: http://localhost:8069 (bound to `127.0.0.1` only — not reachable from other
  machines, kept for local convenience) or https://localhost:8443 (via nginx —
  browser will warn on the self-signed cert, that's expected locally)
- Login: an admin account exists (`admin` login — password was rotated off the
  default; see the vault or ask whoever ran the last session for it), or one of the
  seeded demo users (see PROJECT.md in the vault for the demo user list and password)

Stop it with `docker compose down` (add `-v` to also wipe the database + backups volumes).

## Layout

- `docker-compose.yml` — four services:
  - `db` — Postgres 16
  - `odoo` — official Odoo 19 Community image, production-configured (`workers=2`,
    `proxy_mode=True`, `list_db=False`, `dbfilter` locked to `nu_demo`), port 8069
    bound to `127.0.0.1` only (nginx is the only externally-reachable entry point)
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
- **Outgoing email** is configured (Settings → Technical → Email → Outgoing Mail
  Servers), a real Gmail account with an app password, verified working via a live
  SMTP connection test. The credential lives only in the database (`ir.mail_server`
  record) — it is not in any file, not in git, not in this README.

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

**Do NOT just delete the `nu_demo_seed_data` folder from disk instead of uninstalling
it** — that removes the code but leaves every record it created sitting in the
database, untouched. Uninstall through the Apps screen first; only delete the folder
afterward if you want to.

## Deploying to the team's server

1. Clone this repo to the server (`git clone https://github.com/Kair97/nu_demo.git`).
2. Generate **fresh** secrets for `.env` and `config/odoo.conf` on the server — never
   reuse the local dev secrets committed to nobody's history but sitting in this
   machine's `.env`/`config/odoo.conf` right now.
3. Replace `nginx/certs/fullchain.pem` + `privkey.pem` with a real certificate
   (Let's Encrypt via certbot, or whatever the team already uses) and change
   `nginx/nginx.conf` + the `nginx` service's `ports:` to listen on 80/443 instead of
   8080/8443.
4. Outgoing email already works via the configured Gmail account — swap to a real
   company mail account when one exists (Settings → Technical → Outgoing Mail Servers).
5. Once the team lead approves going live, uninstall `nu_demo_seed_data` (see above)
   before entering any real business data.
6. Set up an **off-site** backup destination — right now backups only land in
   `./backups/` on this one machine; if the server's disk dies, the backups die too.

## Known remaining gaps (not fixable until real deployment)

- TLS cert is self-signed — needs a real domain + real certificate.
- Local-only backups — needs an off-site target (S3, another server, etc.), not yet decided.
- Not yet decided which of the currently-installed apps (Website, Survey, HR, etc. —
  installed by an earlier exploratory session) the business actually wants kept for
  the real deployment.
