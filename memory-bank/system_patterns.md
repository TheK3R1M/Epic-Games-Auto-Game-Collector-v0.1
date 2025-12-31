# System Architecture & Design Patterns 🏗️

This document documents the core architectural decisions and design patterns used in the Epic Games Auto-Collector.

## 1. Core Technology Stack
*   **Automation Engine**: `DrissionPage` (Chromium Driver). chosen over Selenium/Playwright for its superior undetectability by anti-bot systems (Cloudflare/Akamai) and direct CDP access.
*   **GUI Framework**: `CustomTkinter`. Chosen for its modern, "Dark Mode" native look on Windows compared to standard Tkinter, while remaining lightweight (no Electron bloat).
*   **Concurrency**: `asyncio` + `threading`. The GUI runs on the main thread, while blocking automation tasks run in daemon threads to prevent UI freezing.
*   **Packaging**: `PyInstaller`. Used to bundle the Python environment and dependencies into a single, portable `.exe` file.

## 2. Design Patterns
### The "Headless Browser" Pattern
Instead of using API requests which require complex signature generation (hcaptcha tokens), we use a real browser instance to navigate the DOM. This ensures 100% fidelity with user actions.
*   **Hybrid Approach**: We prioritize DOM scraping (reading `href` from `<a>` tags) but maintain an API fallback logic for extracting game lists if the DOM structure changes unexpectedly.

### "Cookie-First" Authentication
The system is designed to never store passwords locally if possible.
1.  **Manual Login**: User logs in once via a guided browser window.
2.  **Cookie Stealing**: The app captures the `EPIC_BEARER_TOKEN` and session cookies.
3.  **Session Restore**: On subsequent runs, cookies are injected. If valid, login is skipped. If invalid, the cookie file is deleted to force a clean re-login.

### The "Auto-Pilot" Loop
*   **State Management**: `dashboard.py` maintains a `pilot_var` (BooleanVar).
*   **Visibility Control**: When Auto-Pilot is active, `root.withdraw()` is called to hide the window, and a `SystemTrayIcon` (pystray) is spawned.
*   **Polling**: A background thread sleep-loops for 6 hours. Upon waking, it reuses the existing `EpicDrissionConnector` instance to perform checks.

## 3. Directory Structure
```text
/src
  /core       -> Logic (DrissionPage connector, AccountManager)
  /gui        -> UI (Dashboard, Login, History frames)
  /utils      -> Helpers (Paths, Logger, Encryption)
  /security   -> Sensitive data handling (CookieManager)
/data
  /cookies    -> JSON cookie jars (one per account)
  accounts.json -> Encrypted paths references
```

## 4. Key Constraints & Rules
*   **No Hardcoded Credentials**: All passwords must be loaded from `.env` or encrypted local storage.
*   **Path Robustness**: `get_data_dir()` must be used for all I/O to ensure compatibility between Source (Python) and Frozen (EXE) modes.
