AGPlus Cafe & Restaurant System

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
Screenshots are available in the repository under the /screenshots folder.

🛠️ Technologies Used
Python 3
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

