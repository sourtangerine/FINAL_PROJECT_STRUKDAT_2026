"""
app.py
Titik masuk utama untuk menjalankan aplikasi 2EZ4U APP.
Membuka antarmuka grafis Tkinter.
"""

import sys
import os

# Pastikan direktori root proyek berada dalam pencarian modul Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from frontend.ui import main

if __name__ == "__main__":
    main()
