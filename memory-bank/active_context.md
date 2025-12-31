# Active Context & Project Status 🧠

## Current Status: v1.3 (Stable / Polished)
The application has reached a "Gold Master" state for the initial release. It is fully functional as a standalone executable with no external dependencies required for the end user.

## Recent Achievements
1.  **Auto-Pilot Mode**: Successfully implemented a background loop that hides the GUI and wakes up every 6 hours.
2.  **System Tray Integration**: Added `pystray` support so users can manage the hidden application from the taskbar.
3.  **No-Console Polish**: Removed the debugging command prompt window for a professional feel.
4.  **Scraper Hotfixes**: Solved critical 404 errors by implementing DOM-based `href` scraping and "Coming Soon" filtering.

## Current Focus
*   **Documentation**: Establishing this Memory Bank to ensure future features (v2.0) are built on solid architectural understanding.
*   **Maintenance**: Monitoring user feedback for potential edge cases in the "Auto-Pilot" logic (e.g., does it wake up correctly after PC sleep?).

## Open Questions / Risks
*   **2FA Challenges**: Frequent re-logins might trigger Epic's 2FA or Captcha challenges. The current "Cookie-First" approach mitigates this, but *session invalidation* is the biggest long-term risk.
*   **DrissionPage Detection**: While currently undetected, Chromium automation is an arms race. Future updates might need `stealth.min.js` enhancements.

## Next Steps (Immediate)
*   Push v1.3 changes to GitHub.
*   Create a Release tag.
*   Brainstorm "Proxy Support" for the v1.4 update.
