# deploy-onprem

On-premise deployment of **ERPNext** (POS, inventory, invoicing, accounting) for a
single branch, plus a small custom app, `zatca_core`, that prepares invoices for
Saudi e-invoicing (ZATCA / Fatoora). Everything runs in Docker on the branch server.

> Status: the files are syntax-checked but have not been run end to end.
> ZATCA Phase 2 submission is **not implemented yet** (see "ZATCA" below).

## Components

| Service | Image | Purpose |
|---|---|---|
| `db` | mariadb:10.6 | Database (ERPNext uses MariaDB, not PostgreSQL) |
| `redis-cache` | redis:6.2 | Cache |
| `redis-queue` | redis:6.2 | Background job queue and realtime |
| `configurator` | built here | One-shot job that writes bench config, then exits |
| `backend` | built here | Web application (gunicorn) |
| `websocket` | built here | Realtime updates (socket.io) |
| `scheduler` | built here | Runs scheduled jobs (incl. the ZATCA queue every 5 min) |
| `worker` | built here | Runs background jobs |
| `frontend` | built here | nginx, serves the UI on port 8080 |
| `zatca_core` | custom app | ZATCA fields, invoice hash chain, submission queue |

"Built here" means one image: `frappe/erpnext` + `apps/zatca_core` (see `Dockerfile`).

## Repository layout

```
docker-compose.yml     services and volumes
Dockerfile             ERPNext + zatca_core
.env.example           configuration template
scripts/               install, backup, restore, update
apps/zatca_core/       custom Frappe app
tools/                 zatca_qr_demo.py (QR simulator, no hardware needed)
```

## Hardware (per branch, minimum)

- 4 CPU cores, 8 GB RAM (16 GB recommended), SSD with 100 GB+ free
- A UPS, and a second disk or NAS for backups

## Install on Ubuntu 22.04 / 24.04 (recommended for production)

```bash
# 1. Tools
sudo apt update && sudo apt install -y git rsync openssl curl

# 2. Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker            # or log out and back in

# 3. Get the code (replace with your repo URL, or unzip deploy-onprem.zip)
git clone <your-repo-url> deploy-onprem
cd deploy-onprem

# 4. Install (creates .env with random passwords, builds, creates the site)
./scripts/install.sh
```

Open `http://<server-ip>:8080`. Login: `Administrator`, password is `ADMIN_PASSWORD` in `.env`.

Schedule backups:

```bash
crontab -e
# add:
0 2 * * * /home/<user>/deploy-onprem/scripts/backup.sh >> /var/log/erp-backup.log 2>&1
```

## Install on Windows 10/11 (development or small sites)

Use WSL2. Do not run the scripts from PowerShell or from `C:\`.

1. Open PowerShell **as Administrator** and run: `wsl --install -d Ubuntu`, then reboot.
2. Install **Docker Desktop** and enable
   *Settings > General > Use the WSL 2 based engine* and
   *Settings > Resources > WSL Integration > Ubuntu*.
3. Open the **Ubuntu** app and run:

```bash
sudo apt update && sudo apt install -y git rsync openssl
cd ~
git clone <your-repo-url> deploy-onprem     # or copy the folder into ~ (not /mnt/c)
cd deploy-onprem
./scripts/install.sh
```

4. Open `http://localhost:8080` in your Windows browser.

Notes for Windows:
- Keep the project inside the WSL filesystem (`~/...`). Files under `/mnt/c` are slow and break permissions.
- If you see `bad interpreter: /usr/bin/env bash^M`, the scripts have Windows line endings. Run `sed -i 's/\r$//' scripts/*.sh`.
- For a real customer server, prefer Ubuntu. Windows is fine for development and demos.

## First-time setup in ERPNext

In the setup wizard choose: Country **Saudi Arabia**, Currency **SAR**, Language **Arabic**
(you can switch the UI language per user later). Then create the company, warehouses,
items, and the POS Profile (*Retail > Point of Sale > POS Profile*).

## Daily operations

| Task | Command |
|---|---|
| Start / stop | `docker compose up -d` / `docker compose down` |
| Logs | `docker compose logs -f backend` |
| Backup now | `./scripts/backup.sh` |
| Restore | `./scripts/restore.sh backups/<folder>` |
| Update | set `ERPNEXT_VERSION` in `.env`, then `./scripts/update.sh` |
| Shell inside the app | `docker compose exec backend bash` |

Backups go to `backups/<date>/` (database + files). Set `BACKUP_REMOTE` in `.env`
(e.g. `user@hq-server:/srv/backups/branch1`) to also copy them off-site with rsync.
**Test a restore on another machine before going live.**

## ZATCA: what is and is not here

Saudi law requires electronic invoices in two phases:

- **Phase 1 (generation):** every invoice carries a QR code. It is created locally; no internet needed.
  ERPNext generates this QR itself for Saudi companies (verify in your version's print preview).
- **Phase 2 (integration):** invoices are signed digitally and sent to ZATCA's Fatoora platform.
  Simplified (B2C) invoices are *reported* within 24 hours; standard (B2B) invoices must be *cleared* first.

What `zatca_core` does today:
1. Adds fields to Sales Invoice: ZATCA Status, Invoice Hash, Previous Invoice Hash, ZATCA Error.
2. On submit, chains the invoice to the previous one and sets status `Pending`.
3. Every 5 minutes, sends pending invoices in order and stops at the first failure.
   Disabled until you run: `docker compose exec backend bench --site <SITE_NAME> set-config zatca_enabled 1`

What is **not** done: `apps/zatca_core/zatca_core/zatca_client.py` is a stub. Phase 2 needs UBL 2.1 XML,
XAdES signing, CSID onboarding and the Fatoora APIs. The hash in `invoice.py` is a placeholder.

## Testing without a printer or any hardware

1. **See the QR logic:** `python3 tools/zatca_qr_demo.py` prints the encoded payload and decodes it field by field.
   For a scannable PNG: `python3 -m venv .venv && . .venv/bin/activate && pip install "qrcode[pil]"` first
   (on Ubuntu 24.04 plain `pip install` is blocked, hence the venv).
2. **See a real invoice:** create a Sales Invoice (or a POS sale) in ERPNext, open *Print > Print Preview*
   or download the PDF. Scan the QR on screen with a phone camera or a ZATCA-compatible QR reader.
3. **Phase 2:** use ZATCA's Fatoora **sandbox / simulation** environment and the official SDK
   (request developer access on the Fatoora portal). Never test with production credentials.
4. **Receipts:** ERPNext POS prints through the browser. Use "Save as PDF" as a virtual printer.

## Before going to production

- Pin `ERPNEXT_VERSION` to an exact tag (check Docker Hub for `frappe/erpnext`).
- Keep `.env` private and back it up separately (it holds the database password).
- Put the server behind a UPS; test power-loss recovery.
- Add HTTPS (e.g. a reverse proxy) if the server is reachable beyond the local network.
- Complete the Phase 2 client and pass the ZATCA sandbox compliance checks.
