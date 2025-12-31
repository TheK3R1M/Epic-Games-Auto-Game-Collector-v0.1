# Feature Specifications & Brainstorming 🧠

This document details the "Selected" features for future development. These are distinct from the immediate QoL improvements.

## 1. Advanced Notifications System 🔔
**Goal:** Keep the user informed without needing to check the UI.
*   **Channels:**
    *   **Desktop Toast:** Windows 10/11 native notifications (via PowerShell or `winsdk`).
    *   **Webhooks:** Discord/Slack integration (User provides Webhook URL in Settings).
    *   **Email:** (Optional) Send summary email via SMTP (lower priority due to complexity).
*   **Triggers:**
    *   "New Game Detected" (with image preview).
    *   "Claim Successful" (Account X claimed Game Y).
    *   "Session Expired" (Urgent Action Required).

## 2. Game Analytics & Statistics 📊
**Goal:** Visualize the value provided by the application.
*   **Metrics:**
    *   **Total Value Claimed:** Scrape the original price (crossed out) and sum it up (e.g., "You saved $450 this year").
    *   **Most Active Account:** Which account has the most claims.
    *   **Genre Distribution:** Pie chart of claimed games (Action, RPG, Indie).
*   **Implementation:**
    *   Store `price` and `genre` in `claimed_history.json`.
    *   Use `matplotlib` or `customtkinter` canvas for simple charts.

## 3. Web Dashboard 🌐
**Goal:** Remote management for headless/docker deployments.
*   **Tech Stack:** `Flask` or `FastAPI` (Python lightweight backend) + `React` (Frontend).
*   **Features:**
    *   View Logs live (WebSocket).
    *   Add/Remove Accounts remotely.
    *   Trigger "Claim Now" button.
*   **Security:** Basic Auth (Username/Password) to prevent unauthorized access on local network.

## 4. Scheduling Enhancements 📅
**Goal:** More control than just "Auto-Pilot".
*   **Cron-style Scheduling:** "Check every Day at 17:00" (Epic drops usually happen at specific times).
*   **"Smart Wake"**: Automatically schedule the next wake-up based on the `Unlocking in...` timer from the store (Planned for v1.4 QoL).

## 9. AI & Machine Learning Features (The "Optimal Time" Model) 🤖
**Goal:** Predict the best time to claim to avoid server loads or CAPTCHA spikes.
*   **Concept:**
    *   Collect data on "Success Rate" vs "Time of Day" locally.
    *   If 17:05 (Drop time) has 40% Captcha rate, but 19:00 has 5%, the AI suggests waiting 2 hours.
*   **Implementation:**
    *   Simple lightweight Regression model (scikit-learn) or just Heuristic analysis (Moving Average).
    *   **Privacy:** ALL training happens locally. No data sent to cloud.

## 10. Advanced Game Management 🎮
**Goal:** Manage the library effectively.
*   **Hide/Ignore:** specific titles (e.g. "DLCs", "Demos").
*   **Auto-Install:** (Experimental) Trigger Epic Launcher to install the game after claiming.
*   **Categorization:** Tag accounts (e.g., "Main", "Smurf", "Storage").
