"""
tools/generate_data.py
Skrip pembantu untuk menghasilkan berkas data/pesanan.csv (200.000 baris acak)
jika berkas data asli belum tersedia di lingkungan lokal.
HANYA untuk pengujian lokal/cadangan, jangan diimpor di backend.
"""

import os
import random
import csv

def generate_pesanan_csv(output_path="data/pesanan.csv", total_baris=200000):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    nama_depan = ("Budi", "Siti", "Andi", "Dewi", "Eko", "Rina", "Agus", "Maya", "Rizky", "Putri",
                  "Fajar", "Lestari", "Doni", "Tari", "Hadi", "Nur", "Wahyu", "Mega", "Irfan", "Ayu")
    nama_belakang = ("Santoso", "Wijaya", "Saputra", "Pratama", "Kusuma", "Hidayat", "Lestari", "Siregar",
                     "Nasution", "Simanjuntak", "Utami", "Wahyudi", "Firmansyah", "Pangestu", "Setiawan")
    
    resto_list = ("kafe-teknik", "kedai-kopi", "warung-bu-ida", "bakso-pak-yon", "kantin-asrama", "kantin-pusat")
    menu_list = (
        ("roti-bakar", 12000), ("bubur-ayam", 11000), ("mie-goreng", 13000),
        ("nasi-padang", 25000), ("nasi-campur", 20000), ("ayam-geprek", 19000),
        ("kentang-goreng", 14000), ("iga-penyet", 27000), ("sate-ayam", 24000),
        ("gado-gado", 15000), ("pecel-lele", 18000), ("es-teh", 5000)
    )
    
    status_choices = ("DONE", "DONE", "DONE", "DONE", "CANCEL", "CANCEL", "ANTRE")
    prioritas_choices = (1, 2, 2, 3, 3, 3, 3)
    
    print(f"Menghasilkan {total_baris} data pesanan ke {output_path}...")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["oid", "pelanggan", "resto", "menu", "harga", "prioritas", "t_masuk_detik", "t_selesai_detik", "status"])
        
        for i in range(1, total_baris + 1):
            oid = f"O-{i:06d}"
            pelanggan = f"{random.choice(nama_depan)} {random.choice(nama_belakang)}"
            resto = random.choice(resto_list)
            menu, harga = random.choice(menu_list)
            prioritas = random.choice(prioritas_choices)
            t_masuk = random.randint(28800, 75600)  # 08:00 - 21:00
            status = random.choice(status_choices)
            if status == "DONE":
                t_selesai = t_masuk + random.randint(600, 3600)
            else:
                t_selesai = ""
            
            writer.writerow([oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status])
            
    print(f"Selesai! Berkas disimpan di {output_path}")

if __name__ == "__main__":
    generate_pesanan_csv()
