AGPlus Cafe & Restaurant System V1.0.0

A modern, lightweight POS and restaurant management system built with Python and Tkinter.
Designed for cafés, restaurants, poolside service, and small hospitality businesses.

✨ Features
🔐 PIN-based login screen
🪑 Table management (Garden, Pool, Apartment — 20 tables each)
📋 Order management with category & product listing
📦 Product & category management
💳 Payment handling (Cash / Card)
📊 Daily report screen
📁 Automatic day-end report saving (with timestamped folders)
💾 Persistent data storage in AppData/Roaming/AGPlusAdisyon/data.json
🖥️ Modern clean UI built on Tkinter
📜 Scrollable table and product views
🔄 Stable and optimized structure for Windows setups

📌 Screenshots
## 📸 Screenshots

### 1. PIN Login Screen
![Screenshot 1](screenshots/1.png)

### 2. Table Management (Garden – 20 tables)
![Screenshot 2](screenshots/2.png)

### 3. Active Tables & Order Status
![Screenshot 3](screenshots/3.png)

### 4. Product Management – Add / Edit Product
![Screenshot 4](screenshots/4.png)

### 5. End-of-Day Summary Screen
![Screenshot 5](screenshots/5.png)

### 6. Order Screen for Selected Table
![Screenshot 6](screenshots/6.png)

### 7. Occupied Table Indicator
![Screenshot 7](screenshots/7.png)

### 8. Payment Screen
![Screenshot 8](screenshots/8.png)

### 9. Daily Sales Report
![Screenshot 9](screenshots/9.png)

### 10. End-of-Day Confirmation
![Screenshot 10](screenshots/10.png)

### 11. End-of-Day Success Notification
![Screenshot 11](screenshots/11.png)

🛠️ Technologies Used
Python3
Tkinter
JSON storage
PyInstaller (for building .exe)
Inno Setup (for installer creation)

📁 File Structure (Important)
AGPlus-Cafe-Restaurant-System/
│
├── adisyon_test.py              # Main application
├── screens/                     # Screenshots folder
├── LICENSE                      # License file
└── README.md                    # This file

📦 Build Instructions
1) Create EXE with PyInstaller
    pyinstaller --noconsole --onefile --icon=logo.ico adisyon_test.py
2) Setup Package (Optional)
    Use Inno Setup to generate an installer for end users.

📄 License
This project is licensed under the MIT License — you are free to use, modify, and distribute the software.

❤️ Contributions
Contributions, issues, and pull requests are warmly welcomed.

