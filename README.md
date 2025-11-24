# 📧 SMTP Lab GUI


### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

### First-Time Usage

1. **Launch GUI** → `python run.py`
2. **Server Tab** → Click "▶ Start Server"
3. **Send Email Tab** → Compose and send
4. **Mailbox Tab** → View received emails

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **GUI Interface** | Clean, intuitive graphical interface |
| 📬 **SMTP Server** | Built-in server to receive emails |
| 📧 **Email Client** | Send emails with attachments |
| 📊 **Real-time Logs** | Monitor server activity live |
| 📎 **Attachments** | Support for multiple file attachments |
| 👥 **Multiple Recipients** | Send to multiple addresses |
| 💾 **Local Storage** | Emails stored in local mailboxes |

---

## 📦 Installation

### Prerequisites

- **Python 3.7+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)

### Install Dependencies

**Windows:**
```bash
pip install -r requirements.txt
```

**Mac/Linux:**
```bash
pip3 install -r requirements.txt
```

---

## 🎯 Usage

### Launch Application

**Windows:**
```bash
python run.py
# or double-click run.bat
```

**Mac/Linux:**
```bash
python3 run.py
# or: ./run.sh
```

### How to Use

#### 1️⃣ Start the Server
- Open **Server** tab
- Click **"▶ Start Server"**
- Wait for status: **🟢 Server Running**

#### 2️⃣ Send an Email
- Go to **Send Email** tab
- Fill in the form:
  - **From:** sender@example.com
  - **To:** recipient@example.com
  - **Subject:** Your subject
  - **Message:** Your message
- Add attachments (optional)
- Click **"📤 Send Email"**

#### 3️⃣ View Received Emails
- Go to **Mailbox** tab
- Click **"🔄 Refresh"**
- Select a mailbox
- Click on an email to read it

---

## 📁 Project Structure

```
smtp-lab-gui/
├── smtp_gui.py         # Main GUI application
├── smtp_server.py      # Server backend
├── smtp_client.py      # Client backend
├── run.py             # Universal launcher
├── run.sh             # Mac/Linux script
├── run.bat            # Windows script
├── README.md          # Documentation
├── MAC_SETUP.md       # Mac setup guide
└── requirements.txt   # Dependencies
```

---

## ⚙️ Configuration

**Default Settings:**
- **Server:** 127.0.0.1 (localhost)
- **Port:** 1025
- **Mailbox:** ./mailboxes/

Change these in the GUI before starting the server.

```python
# Server Configuration
SERVER_CONFIG = {
    'host': '127.0.0.1',      # Server host
    'port': 1025,              # Server port
    'mailbox_dir': 'mailboxes' # Mailbox storage directory
}

# Client Configuration
CLIENT_CONFIG = {
    'default_server_host': '127.0.0.1',
    'default_server_port': 1025,
    'timeout': 30
}

# Email Validation Rules
EMAIL_VALIDATION = {
    'max_subject_length': 200,
    'max_body_length': 10000,
    'max_recipients': 50
}

# Attachment Configuration
ATTACHMENT_CONFIG = {
    'enabled': True,
    'max_file_size_mb': 10,
    'max_attachments': 5
---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Connection refused** | Start the server first (Server tab) |
| **Port already in use** | Change port to 1026, 1027, etc. |
| **Module not found** | Run `pip install -r requirements.txt` |
| **GUI won't start (Linux)** | Install tkinter: `sudo apt-get install python3-tk` |

---

## 📚 Learn More

This project demonstrates:
- ✅ SMTP protocol implementation
- ✅ Client-server architecture
- ✅ GUI programming with tkinter
- ✅ Email message structure (MIME)
- ✅ Asynchronous I/O with Python

Perfect for **computer science students** and **networking courses**!

---

## 🎓 For Mac Users

See [MAC_SETUP.md](MAC_SETUP.md) for detailed Mac-specific instructions.

---

## 📄 License

MIT License - Free for educational and personal use.

---

## 🤝 Contributing

Contributions welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

---

## 📞 Support

Having issues? Check:
1. Server is running (Server tab)
2. Port 1025 is not blocked by firewall
3. All dependencies installed: `pip install -r requirements.txt`

---

## ⭐ Star This Project

If you find this helpful, give it a star! ⭐


