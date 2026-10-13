"""
frontend/ui.py
Antarmuka Pengguna Tkinter untuk 2EZ4U APP.
Memiliki layout 3 bagian:
1. Panel Kiri: Navigasi Menu berkelompok (DATA, M1, M2).
2. Panel Kanan: Form parameter dinamis & Area Hasil (tampilan monospace/tabel).
3. Panel Bawah: Log riwayat COMMAND & Bar Status kecepatan operasi.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Tambahkan root repo ke sys.path jika belum ada
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U APP - Mini Delivery Engine (M1 & M2)")
        self.root.geometry("1100, 720")
        self.root.minsize(950, 600)

        # Referensi backend state
        self.arr_pesanan = None
        self.ll_pesanan = None
        self.antrean_naif = None
        self.antrean_circular = None
        self.undo_stack = None
        self.redo_stack = None

        self._buat_layout()
        self._set_status("Siap. Silakan muat data pesanan melalui menu DATA.")

    def _buat_layout(self):
        # Frame Utama: Atas (Kiri Menu + Kanan Form/Hasil) dan Bawah (Command Log + Status)
        self.top_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.top_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- 1. PANEL KIRI: Menu Berkelompok ---
        self.left_frame = ttk.Frame(self.top_paned, width=280)
        self.top_paned.add(self.left_frame, weight=0)

        # Canvas dengan scrollbar untuk menu kiri agar fleksibel pada layar kecil
        self.menu_canvas = tk.Canvas(self.left_frame, borderwidth=0, highlightthickness=0, width=280)
        self.menu_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.menu_canvas.yview)
        self.scrollable_menu = ttk.Frame(self.menu_canvas)

        self.scrollable_menu.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))
        )
        self.menu_canvas.create_window((0, 0), window=self.scrollable_menu, anchor="nw")
        self.menu_canvas.configure(xscrollcommand=None, yscrollcommand=self.menu_scrollbar.set)

        self.menu_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.menu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._bangun_tombol_menu()

        # --- 2. PANEL KANAN: Form Parameter & Hasil ---
        self.right_frame = ttk.Frame(self.top_paned, padding=10)
        self.top_paned.add(self.right_frame, weight=1)

        # Label Judul Menu Aktif
        self.lbl_judul_menu = ttk.Label(
            self.right_frame,
            text="Selamat Datang di 2EZ4U Engine",
            font=("Segoe UI", 12, "bold")
        )
        self.lbl_judul_menu.pack(anchor="w", pady=(0, 5))

        # Subframe untuk Parameter Form (dinamis)
        self.form_frame = ttk.LabelFrame(self.right_frame, text="Parameter Perintah", padding=8)
        self.form_frame.pack(fill=tk.X, pady=(0, 8))

        # Konten default form
        self.form_container = ttk.Frame(self.form_frame)
        self.form_container.pack(fill=tk.X)
        self.lbl_info_form = ttk.Label(self.form_container, text="Pilih menu di panel kiri untuk memulai operasi.")
        self.lbl_info_form.pack(anchor="w")

        # Subframe untuk Hasil Output
        self.hasil_frame = ttk.LabelFrame(self.right_frame, text="Hasil Operasi & Detail Data", padding=8)
        self.hasil_frame.pack(fill=tk.BOTH, expand=True)

        # Area Teks Monospace dengan Scrollbar
        self.txt_hasil = tk.Text(self.hasil_frame, wrap="none", font=("Consolas", 10), relief=tk.SOLID, borderwidth=1)
        self.txt_scroll_y = ttk.Scrollbar(self.hasil_frame, orient="vertical", command=self.txt_hasil.yview)
        self.txt_scroll_x = ttk.Scrollbar(self.hasil_frame, orient="horizontal", command=self.txt_hasil.xview)
        self.txt_hasil.configure(yscrollcommand=self.txt_scroll_y.set, xscrollcommand=self.txt_scroll_x.set)

        self.txt_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_hasil.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- 3. PANEL BAWAH: Command Log & Status Bar ---
        self.bottom_frame = ttk.Frame(self.root, padding=(6, 4))
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_command_title = ttk.Label(self.bottom_frame, text="PANEL COMMAND (Riwayat Perintah):", font=("Segoe UI", 9, "bold"))
        self.lbl_command_title.pack(anchor="w")

        self.txt_command = tk.Text(self.bottom_frame, height=5, wrap="none", font=("Consolas", 9), bg="#1e1e1e", fg="#00ff66")
        self.cmd_scroll = ttk.Scrollbar(self.bottom_frame, orient="vertical", command=self.txt_command.yview)
        self.txt_command.configure(yscrollcommand=self.cmd_scroll.set)
        self.cmd_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_command.pack(fill=tk.X, expand=False, pady=(2, 4))

        # Status Bar di paling bawah
        self.status_bar = ttk.Label(self.bottom_frame, text="[Siap]", relief=tk.SUNKEN, anchor="w", padding=(4, 2))
        self.status_bar.pack(fill=tk.X)

    def _bangun_tombol_menu(self):
        # 1. Kelompok DATA
        grp_data = ttk.LabelFrame(self.scrollable_menu, text="DATA", padding=6)
        grp_data.pack(fill=tk.X, padx=6, pady=4)
        btn_load = ttk.Button(grp_data, text="LOAD DATA (CSV)", command=self._menu_load_data)
        btn_load.pack(fill=tk.X, pady=2)

        # 2. Kelompok M1 - DATA PESANAN (ARRAY)
        grp_m1_arr = ttk.LabelFrame(self.scrollable_menu, text="M1 - ARRAY", padding=6)
        grp_m1_arr.pack(fill=tk.X, padx=6, pady=4)
        m1_arr_actions = (
            ("ARRAY - LIHAT PESANAN", "lihat_arr"),
            ("ARRAY - TAMBAH REGULER", "tambah_reg_arr"),
            ("ARRAY - TAMBAH PRIORITAS", "tambah_prio_arr"),
            ("ARRAY - TAMBAH VIP", "tambah_vip_arr"),
            ("ARRAY - HAPUS PESANAN", "hapus_arr"),
        )
        for teks, aksi in m1_arr_actions:
            btn = ttk.Button(grp_m1_arr, text=teks, command=lambda a=aksi: self._pilih_menu(a))
            btn.pack(fill=tk.X, pady=1)

        # 3. Kelompok M1 - DATA PESANAN (LINKED LIST)
        grp_m1_ll = ttk.LabelFrame(self.scrollable_menu, text="M1 - LINKEDLIST", padding=6)
        grp_m1_ll.pack(fill=tk.X, padx=6, pady=4)
        m1_ll_actions = (
            ("LINKEDLIST - LIHAT PESANAN", "lihat_ll"),
            ("LINKEDLIST - TAMBAH REGULER", "tambah_reg_ll"),
            ("LINKEDLIST - TAMBAH PRIORITAS", "tambah_prio_ll"),
            ("LINKEDLIST - TAMBAH VIP", "tambah_vip_ll"),
            ("LINKEDLIST - HAPUS PESANAN", "hapus_ll"),
        )
        for teks, aksi in m1_ll_actions:
            btn = ttk.Button(grp_m1_ll, text=teks, command=lambda a=aksi: self._pilih_menu(a))
            btn.pack(fill=tk.X, pady=1)

        # 4. Kelompok M2 - STACK & QUEUE
        grp_m2 = ttk.LabelFrame(self.scrollable_menu, text="M2 - STACK & QUEUE", padding=6)
        grp_m2.pack(fill=tk.X, padx=6, pady=4)
        m2_actions = (
            ("STACK - POSTFIX (KASIR)", "postfix"),
            ("STACK - UNDO", "undo"),
            ("STACK - REDO", "redo"),
            ("QUEUE - ENQUEUE", "enqueue"),
            ("QUEUE - DEQUEUE NAIF", "dequeue_naif"),
            ("QUEUE - DEQUEUE CIRCULAR", "dequeue_circular"),
        )
        for teks, aksi in m2_actions:
            btn = ttk.Button(grp_m2, text=teks, command=lambda a=aksi: self._pilih_menu(a))
            btn.pack(fill=tk.X, pady=1)

    def catat_command(self, nama_perintah, modul, durasi_detik):
        ms = durasi_detik * 1000.0
        log_line = f"{nama_perintah} -> {modul:<14} {ms:.4f} ms\n"
        # Tampilkan terbaru di paling atas (indeks 1.0)
        self.txt_command.insert("1.0", log_line)
        self._set_status(f"[{modul}] {ms:.2f} ms")

    def _set_status(self, pesan):
        self.status_bar.config(text=pesan)

    def _tampilkan_hasil(self, teks):
        self.txt_hasil.delete("1.0", tk.END)
        self.txt_hasil.insert(tk.END, teks)

    def _bersihkan_form(self):
        for widget in self.form_container.winfo_children():
            widget.destroy()

    def _pilih_menu(self, aksi):
        self.lbl_judul_menu.config(text=f"Operasi: {aksi}")
        self._bersihkan_form()
        lbl = ttk.Label(self.form_container, text=f"Form untuk operasi '{aksi}' siap dikonfigurasi.")
        lbl.pack(anchor="w")

    def _menu_load_data(self):
        self.lbl_judul_menu.config(text="Memuat Data CSV (200.000 Baris)")
        self._bersihkan_form()
        lbl = ttk.Label(self.form_container, text="Klik tombol di bawah untuk memuat data/pesanan.csv ke memori:")
        lbl.pack(anchor="w", pady=(0, 4))
        btn = ttk.Button(self.form_container, text="Mulai Muat CSV", command=self._jalankan_load_csv)
        btn.pack(anchor="w")

    def _jalankan_load_csv(self):
        import time
        from backend.m1_pesanan import muat_pesanan_ke_dua_struktur
        path = os.path.join(BASE_DIR, "data", "pesanan.csv")
        if not os.path.exists(path):
            messagebox.showerror("Galat", f"Berkas tidak ditemukan: {path}")
            return
        self._set_status("Sedang memuat 200.000 baris ke memori...")
        self.root.update_idletasks()
        
        arr, ll, durasi = muat_pesanan_ke_dua_struktur(path)
        self.arr_pesanan = arr
        self.ll_pesanan = ll
        self.catat_command("LOAD_DATA", "m1_pesanan", durasi)
        self._tampilkan_hasil(
            f"=== SUKSES MEMUAT DATA ===\n"
            f"Path Berkas   : {path}\n"
            f"Total Baris   : {arr.panjang():,} baris\n"
            f"Kapasitas Arr : {arr.kapasitas:,}\n"
            f"Waktu Muat    : {durasi:.4f} detik ({durasi * 1000:.2f} ms)\n"
            f"Struktur M1   : Array & LinkList telah terisi secara identik.\n"
        )


def main():
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
