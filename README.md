# 🎮 Epic Games Auto Game Collector

A robust, secure, and fully automated tool to claim free weekly games from the Epic Games Store. Designed with privacy and reliability in mind, running entirely locally on your machine.

## ✨ Key Features

- **🛡️ Privacy First**: All data (credentials, cookies) is stored locally on your device. Zero telemetry.
- **🍪 Persistent Sessions**: Uses intelligent cookie management to maintain login sessions for up to 30 days.
- **🔐 Secure Storage**: AES-256 encryption protects your account credentials at rest.
- **⚡ DrissionPage Engine**: Utilizes advanced browser automation to bypass bot detection and CAPTCHAs reliability.
- **🔄 Multi-Account Support**: Seamlessly iterate through and claim games for unlimited accounts.
- **🔑 2FA Compatible**: Supports Two-Factor Authentication during the initial setup.

## 📋 Requirements

- **OS**: Windows, macOS, or Linux
- **Python**: 3.10 or higher
- **Browser**: Google Chrome (installed standardly)

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/YourUsername/Epic-Games-Auto-Game-Collector.git
cd Epic-Games-Auto-Game-Collector
python -m venv venv
# Windows
.\venv\Scripts\activate 
# Mac/Linux
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Create a `.env` file for headless operation settings:
```env
HEADLESS=false   # Set to true to run in background
DEBUG=false      # Enable verbose logging
```

### 3. Run the Collector
```bash
python -m src.main
```

## 💻 Usage

On the main menu, you will see options to manage accounts and start the claiming process.

### Adding an Account
1. Select **Add Account**.
2. Enter your email and password.
3. The tool will open a browser window for the **first login**.
4. Complete any CAPTCHA or 2FA challenges manually.
5. Once logged in, the session cookies are securely saved, and future runs will be automatic.

### Claiming Games
1. Select **Claim Games**.
2. The bot will iterate through all saved accounts.
3. It detects free games, skips already owned ones, and claims new ones automatically.

## 🔒 Security & Privacy

This project is built to be "Open Source Safe".

- **Local Encryption**: Credentials are encrypted using a locally generated key (`data/key.key`).
- **No External Servers**: The code only communicates with `epicgames.com`.
- **Exclusion**: The `.gitignore` is pre-configured to exclude `data/` and `.env` files, preventing accidental leaks of personal information if you fork the repo.

## 🛠️ Architecture

- **`src/core/`**: Main logic for browser automation (`DrissionPage`) and game claiming.
- **`src/security/`**: Encryption handlers and secure cookie management.
- **`data/`**: Local storage for encrypted accounts and cookies (Git-ignored).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Disclaimer

This tool is for educational and personal use only. The developers are not responsible for any account consequences resulting from the use of this software. Please use responsibly and adhere to the Epic Games Terms of Service.

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.
