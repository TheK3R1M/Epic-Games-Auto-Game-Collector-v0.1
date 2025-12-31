# Future Innovations & Roadmap 🚀

This document outlines potential features, long-term goals, and "nice-to-have" ideas for the Epic Games Auto-Collector. It serves as a brainstorming board for taking the project to the next level.

## 🌟 Short-Term Features (Next v1.x)
- [ ] **Notification Webhooks**: Integration with Discord, Telegram, or Slack to notify the user when a game is successfully claimed.
- [ ] **Proxy Support**: Ability to bind specific accounts to specific HTTP proxies (essential for managing 50+ accounts without IP bans).
- [ ] **Captcha Solver Integration**: Hooks for 2Captcha or CapSolver to handle rare rigid CAPTCHA challenges automatically.
- [ ] **Theme Selector**: A simple dropdown in Settings to switch between Dark/Light/System themes in CustomTkinter.

## 🚀 Mid-Term Features (v2.0)
- [ ] **Multi-Platform Support**: "Universal Game Claimer" expanding to:
    - **GOG.com**: Auto-claim free giveaways.
    - **Amazon Prime Gaming**: Claim monthly loot (requires Amazon login).
    - **Steam**: Activate free-to-keep Limited Time offers.
- [ ] **Headless & Docker**: A fully containerized version (`Dockerfile`) optimized for running on NAS (Synology, Unraid) or Raspberry Pi 24/7 without a GUI/Monitor.
- [ ] **Web Dashboard**: If running in Docker, a lightweight React/Flask web interface to view logs and manage accounts remotely instead of a desktop GUI.

## 🔮 Long-Term Innovations (Experimental)
- [ ] **Account Generator**: Automated creation of Epic accounts (Ethical considerations required, high risk of ban).
- [ ] **Machine Learning Captcha**: A local ML model to solve puzzle captchas without paying external services (e.g., YOLO for object detection).
- [ ] **Marketplace Integration**: Automatically "purchase" free assets from the Unreal Engine Marketplace for game developers.
- [ ] **Community Configs**: Downloadable config files for selector updates if Epic changes their site structure, so users don't need to update the EXE.

## 💡 User Feedback Ideas
- **"Silent Mode"**: Option to run completely invisible (no tray icon), only accessible via hotkey.
- **"Game Filter"**: Whitelist/Blacklist specific genres or titles (e.g., "Don't claim DLCs").
