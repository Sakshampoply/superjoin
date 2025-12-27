# Superjoin: Real-time Google Sheet ⇄ PostgreSQL Sync

A robust, production-ready system that establishes a live, bi-directional data synchronization between a Google Sheet and a PostgreSQL database.

**🚀 Live Demo:** [https://superjoin-ko0j.onrender.com](https://superjoin-ko0j.onrender.com)

**📊 Live Google Sheet:** [View Spreadsheet](https://docs.google.com/spreadsheets/d/1QhT4hiNXbiT-7_TmYHk8hJGF1M_s3D_r5KHgitrpss0/edit?usp=sharing)

---

## 📸 Screenshots

### 1. Dashboard (Database View)

![Dashboard UI](images/UI.png)

> View and manage database records directly. Edits here sync to Google Sheets instantly.

### 2. Google Sheet View

![Google Sheet](images/Sheet.png)

> Changes made here are captured via triggers and sent to the database in real-time.

---

## Architecture

The system uses a **Push-Push** architecture to ensure real-time consistency without polling.

```mermaid
graph LR
    User[User] -- Edits --> Sheet[Google Sheet]
    Sheet -- Webhook (Batch) --> API[FastAPI Backend]
    API -- Async Write --> DB[(PostgreSQL)]

    User2[User/System] -- Edits --> API
    API -- Background Task --> GAPI[Google Sheets API]
    GAPI -- Update Row --> Sheet
```

### Key Components

1.  **Inbound Sync (Sheet → DB)**:
    - **Trigger**: Google Apps Script Installable Trigger (`syncToBackend`) detects changes.
    - **Optimization**: Implements **Batch Processing** to handle multi-row edits (e.g., copy-paste) in a single HTTP request, preventing rate limits.
    - **Transport**: Sends JSON payloads via HTTP POST to the FastAPI `/sync/batch-from-sheet` endpoint.
2.  **Outbound Sync (DB → Sheet)**:
    - **Trigger**: FastAPI endpoints (`/api/records`) trigger a background task immediately after a successful DB commit.
    - **Transport**: Uses Google Sheets API (Service Account) to update specific rows.
3.  **Consistency & Safety**:
    - **Loop Prevention**: A `last_sync_source` flag ("SHEET" vs "DB") prevents infinite update loops.
    - **Conflict Resolution**: "Last-Write-Wins" strategy using timestamps.

---

## 🛠 Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Database**: PostgreSQL, SQLAlchemy (Async), Asyncpg
- **Frontend**: Jinja2 Templates, Bootstrap 5
- **Google Integration**: Google Apps Script (JavaScript), Google Client Library
- **Deployment**: Render (Web Service), Neon/Supabase (Database)

---

## 🚀 Local Setup Guide

### Prerequisites

- Python 3.11+
- PostgreSQL installed locally
- Google Cloud Console Account

### 1. Clone & Install

```bash
git clone https://github.com/Sakshampoply/superjoin.git
cd superjoin
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Setup

Create a local PostgreSQL database:

```sql
CREATE DATABASE sync_db;
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```ini
# Database Connection
DATABASE_URL=postgresql+asyncpg://user:password@localhost/sync_db

# Google Sheets Config
GOOGLE_SHEET_ID=your_sheet_id_here
GOOGLE_CREDENTIALS_FILE=credentials.json
```

### 4. Google Cloud Setup (Service Account)

1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a project and enable the **Google Sheets API**.
3.  Create a **Service Account** and download the JSON key.
4.  Save the key as `credentials.json` in the project root.
5.  **Crucial**: Open your Google Sheet and **Share** it with the `client_email` found in your `credentials.json` (give "Editor" access).

### 5. Google Apps Script Setup (The "Listener")

1.  Open your Google Sheet.
2.  Go to **Extensions > Apps Script**.
3.  Copy the code from `google_apps_script.js` in this repo.
4.  **Expose Localhost**: Since Google can't see `localhost`, use ngrok:
    ```bash
    ngrok http 8000
    ```
5.  Update the `API_URL` in the Apps Script to your ngrok URL:
    ```javascript
    const API_URL =
      "https://your-ngrok-url.ngrok-free.dev/sync/batch-from-sheet";
    ```
6.  Save and Run the `onEdit` function once to accept permissions.

### 6. Run the App

```bash
uvicorn app.main:app --reload
```

Visit `http://localhost:8000` to see the dashboard.

---

## ☁️ Deployment (Render)

This project is configured for easy deployment on Render.

1.  **Database**: Create a free Postgres database on **Neon.tech** or **Supabase**.
2.  **Web Service**: Connect your repo to Render.
3.  **Environment Variables**:
    - `DATABASE_URL`: Your Neon/Supabase connection string (ensure `postgresql+asyncpg://`).
    - `GOOGLE_SHEET_ID`: Your Sheet ID.
    - `PYTHON_VERSION`: `3.11.0`
    - `GOOGLE_CREDENTIALS_JSON`: Paste the **content** of your `credentials.json` file here (minified JSON string).
4.  **Update Apps Script**: Change the `API_URL` in Google Apps Script to your Render URL:
    ```javascript
    const API_URL = "https://superjoin-ko0j.onrender.com/sync/batch-from-sheet";
    ```

---
