# 🎮 Epic Games Auto Game Collector

A Python application that automatically claims free games from Epic Games accounts.

## ✨ Features

- 🔐 Secure account management (encrypted storage)
- 🍪 Cookie-based persistent login (30-day validity)
- 🔑 2FA support (manual code entry)
- 🎮 Automatic game claiming
- 📊 Game claim history
- 💾 Library management
- ⚡ Parallel multi-account execution

## 📋 Requirements

- Python 3.10+
- Windows/Linux/macOS
- Internet connection

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/TheK3R1M/Epic-Games-Auto-Game-Collector.git
cd "Epic Games Auto game collector"
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

**Windows:**
```bash
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Install Playwright browsers
```bash
playwright install
```

## 💻 Usage

### Start the application
```bash
python -m src.main
```

### Menu Options

```
1. Add new account        - Add Epic Games account
2. List accounts          - Show all added accounts
3. Delete account         - Remove account
4. Claim games            - Claim games for all accounts
5. Open GUI               - Launch graphical interface
6. Exit                   - Exit application
```

### Example Usage

#### Adding Account
```
Choose (1-6): 1
Enter email: example@gmail.com
Enter password: ****
✅ Account added successfully!
```

#### Claiming Games
```
Choose (1-6): 4
✨ Will claim games for 2 account(s)...
⚠️ NOTE: First login may require 2FA verification.

🚀 Epic Games - Auto Game Claim Started
==================================================

📧 Processing example@gmail.com...
🔐 Signing in: example@gmail.com
💾 Saved cookies found, using them...
✅ Login via cookies successful: example@gmail.com
🎮 Checking free games...
✅ Found 5 games
📚 Checking library...
✅ 3 games found in library
🎁 Claiming new games...

   [1/5] Game Name 1
   ✅ Successfully claimed
```

## 🔐 Security Features

### Password Encryption
- All passwords are encrypted using AES encryption via `cryptography` library
- A unique encryption key is generated for each installation (`data/key.key`)

### Cookie Management
- Cookies are valid for 30 days
- Stored in `data/cookies/` directory
- Expired cookies are automatically deleted

### 2FA Support
- Manual 2FA code entry during first login
- After successful login, cookies are used (2FA not required)
- Supported methods:
  - Manual (Manual code entry)
  - Email (Code sent via email)
  - TOTP (Authenticator app)

### 🤖 CAPTCHA/Bot Protection
- **Auto Detection**: Detects hCaptcha, reCAPTCHA, FunCaptcha
- **Manual Solution**: User is notified when CAPTCHA is detected
- **Wait Time**: Max 2 minutes for manual solution
- **Tips**:
  - If you see CAPTCHA, solve it manually in browser
  - Program will automatically continue
  - After first login, CAPTCHA rarely appears with cookies
  - If using VPN, try disabling it

## 📁 Directory Structure

```
epic-games-collector/
├── src/
│   ├── core/                  # Core logic
│   │   ├── account_manager.py
│   │   ├── epic_games_connector.py
│   │   └── game_claimer.py
│   ├── security/              # Encryption and security
│   │   ├── cookie_manager.py
│   │   └── twofa_handler.py
│   ├── ui/                    # Interface (future)
│   ├── database/              # Database (future)
│   ├── utils/                 # Helper functions
│   └── main.py                # Entry point
├── data/
│   ├── accounts.json          # Accounts (encrypted)
│   ├── key.key                # Encryption key
│   └── cookies/               # Saved cookies
├── memory-bank/               # Project documentation
├── tests/                     # Test files
├── requirements.txt           # Dependencies
├── .gitignore
├── README.md
└── Agents.md
```

## ⚙️ Configuration

### .env File (Optional)
```env
HEADLESS=false              # Run browser in headless mode
TIMEOUT=30000               # Page load timeout (ms)
LOG_LEVEL=INFO              # Log level
```

## 🐛 Troubleshooting

### "Chrome.exe not found" Error
```bash
playwright install
```

### "Login failed" Error
- Check your Epic Games password
- Account might be locked - try logging into Epic Games directly
- Check your IP (geographic location change)

### 2FA Required But Cannot Receive Code
- Manually log into your Epic Games account
- Change 2FA method
- Delete files in `data/cookies/`

### 🤖 CAPTCHA/Bot Protection Issues
- **CAPTCHA keeps appearing**: If using VPN, try disabling it

## 📝 First Login Manual, Then Cookie

- On first run, browser opens and user is asked to manually complete Epic Games login (including CAPTCHA/2FA).
- After successful login, cookies are saved locally.
- On subsequent runs, application silently logs in using cookies; 2FA is mostly not needed.

In short:
- First run: You will see "Login page will open, please log in and return to this console and press Enter" warning.
- After pressing Enter, login is verified and cookies are saved.
- Future runs: Application automatically attempts login with cookies.
- **CAPTCHA won't solve**: Solve manually in browser, program will continue automatically
- **Timeout error**: You must solve CAPTCHA within 2 minutes
- **Too much CAPTCHA**: Open and verify your Epic Games account from normal browser
- **CAPTCHA with cookies**: Delete old cookies (`data/cookies/`) and login again

## 📊 Data Management

### Where Are Your Accounts Saved?
- Encrypted in `data/accounts.json` file
- Encryption key in `data/key.key` file

### To Delete All Data
```bash
rm -r data/
```

## 🔒 Privacy and Local Operation

- The application stores user data (accounts and cookies) only on the local disk. No telemetry or third-party transmissions are made.
- Environment proxy variables (HTTP_PROXY/HTTPS_PROXY/ALL_PROXY) are cleared when launching the browser; this prevents traffic from being unintentionally routed to external proxies.
- Chromium startup flags disable background network traffic and default component updates (e.g., `--disable-background-networking`, `--disable-sync`, `--no-first-run`, `--disable-component-update`).
- Playwright persistent context is launched with `accept_downloads=False`; this reduces unnecessary downloads and export risks.
- Cookie files are kept in the `data/cookies/` folder; they are not automatically shared with external systems.

Optional additional security recommendations:
- Instead of headless mode (`HEADLESS=true`), test in visible mode to make CAPTCHA and bot protection behavior more human-like.
- If using VPN/proxy, keep it disabled while running the application to avoid unintentional data routing.

## 🔄 Automated Operation (Future)

Planned features:
- Daily/weekly automatic runs
- System task scheduler integration
- Discord/Telegram notifications

## 📝 Logs

Application logs are saved in `data/logs/` directory.
```bash
tail -f data/logs/latest.log
```

## 🚀 Development

### Edit Code
```bash
# Run in development mode
python -m src.main
```

### Run Tests
```bash
python -m pytest tests/
```

### Check Code
```bash
pylint src/
```

## 📚 API Documentation

For detailed API documentation, see [memory-bank/](memory-bank/) folder.

## 🤝 Contributing

1. Fork
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'Add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

This project is licensed under the MIT License.

## ⚠️ Legal Disclaimer

- This tool is for personal use only
- Read and accept Epic Games' Terms of Service
- No responsibility for account bans

## 📧 Contact

For questions: [Email or GitHub Issues]

## 🙏 Thanks

- [Playwright](https://playwright.dev/) - Web automation
- [Cryptography](https://cryptography.io/) - Encryption
- Epic Games - Free games 🎮

---

**Made with ❤️ by Kerim**

If you gave a star, thank you! ⭐
