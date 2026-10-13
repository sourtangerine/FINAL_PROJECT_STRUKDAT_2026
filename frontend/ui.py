"""
frontend/ui.py
Antarmuka Pengguna Tkinter untuk 2EZ4U APP (Mini Delivery Engine M1 & M2).
Memiliki layout 3 bagian terpadu:
1. Panel Kiri : Navigasi Menu Berkelompok (DATA, M1-ARRAY, M1-LINKEDLIST, M2-STACK & QUEUE).
2. Panel Kanan: Form Parameter Dinamis & Area Hasil (Monospace/Tabel).
3. Panel Bawah: Riwayat COMMAND (terbaru di atas) & Bar Status Kecepatan Operasi.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time

# Pastikan root workspace ada di sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.m1_pesanan import Pesanan, Array, LinkList, muat_pesanan_ke_dua_struktur
from backend.m2_antrean import LayananAntrean, proses_kasir


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U APP - Delivery Engine (M1 & M2)")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 650)

        # State Backend
        self.arr_pesanan = None
        self.ll_pesanan = None
        self.layanan_antrean = LayananAntrean(kapasitas_awal=262144)
        self.counter_id_baru = 1

        self._buat_layout()
        self._set_status("[SISTEM] Siap. Silakan klik 'LOAD DATA (CSV)' untuk memuat data awal.")

    def _buat_layout(self):
        # 1. PanedWindow Horizontal (Kiri: Menu, Kanan: Form + Output)
        self.top_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.top_paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # --- PANEL KIRI: Menu Navigasi Berkelompok ---
        self.left_frame = ttk.Frame(self.top_paned, width=300)
        self.top_paned.add(self.left_frame, weight=0)

        self.menu_canvas = tk.Canvas(self.left_frame, borderwidth=0, highlightthickness=0, width=300)
        self.menu_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.menu_canvas.yview)
        self.scrollable_menu = ttk.Frame(self.menu_canvas)

        self.scrollable_menu.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))
        )
        self.menu_canvas.create_window((0, 0), window=self.scrollable_menu, anchor="nw")
        self.menu_canvas.configure(yscrollcommand=self.menu_scrollbar.set)

        self.menu_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.menu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._bangun_tombol_menu()

        # --- PANEL KANAN: Form Parameter Dinamis & Area Hasil ---
        self.right_frame = ttk.Frame(self.top_paned, padding=12)
        self.top_paned.add(self.right_frame, weight=1)

        self.lbl_judul_menu = ttk.Label(
            self.right_frame,
            text="Selamat Datang di 2EZ4U Engine",
            font=("Segoe UI", 13, "bold"),
            foreground="#0b5394"
        )
        self.lbl_judul_menu.pack(anchor="w", pady=(0, 6))

        # Subframe Form Parameter
        self.form_frame = ttk.LabelFrame(self.right_frame, text="Parameter Perintah", padding=10)
        self.form_frame.pack(fill=tk.X, pady=(0, 8))

        self.form_container = ttk.Frame(self.form_frame)
        self.form_container.pack(fill=tk.X)
        self.lbl_info_default = ttk.Label(self.form_container, text="Pilih menu di panel kiri untuk mengatur parameter perintah.")
        self.lbl_info_default.pack(anchor="w")

        # Subframe Area Hasil
        self.hasil_frame = ttk.LabelFrame(self.right_frame, text="Hasil Eksekusi & Data Output", padding=8)
        self.hasil_frame.pack(fill=tk.BOTH, expand=True)

        self.txt_hasil = tk.Text(self.hasil_frame, wrap="none", font=("Consolas", 10), relief=tk.SOLID, borderwidth=1)
        self.txt_scroll_y = ttk.Scrollbar(self.hasil_frame, orient="vertical", command=self.txt_hasil.yview)
        self.txt_scroll_x = ttk.Scrollbar(self.hasil_frame, orient="horizontal", command=self.txt_hasil.xview)
        self.txt_hasil.configure(yscrollcommand=self.txt_scroll_y.set, xscrollcommand=self.txt_scroll_x.set)

        self.txt_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_hasil.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- PANEL BAWAH: Panel COMMAND & Status Bar ---
        self.bottom_frame = ttk.Frame(self.root, padding=(8, 4))
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lbl_command_header = ttk.Label(
            self.bottom_frame,
            text="PANEL COMMAND (Log Eksekusi Real-time | Terbaru di Baris Teratas):",
            font=("Segoe UI", 9, "bold")
        )
        self.lbl_command_header.pack(anchor="w")

        self.txt_command = tk.Text(
            self.bottom_frame, height=5, wrap="none",
            font=("Consolas", 9), bg="#1e1e1e", fg="#00ff66", insertbackground="white"
        )
        self.cmd_scroll = ttk.Scrollbar(self.bottom_frame, orient="vertical", command=self.txt_command.yview)
        self.txt_command.configure(yscrollcommand=self.cmd_scroll.set)
        self.cmd_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_command.pack(fill=tk.X, expand=False, pady=(2, 4))

        self.status_bar = ttk.Label(
            self.bottom_frame, text="[Siap]", relief=tk.SUNKEN, anchor="w", padding=(6, 3), font=("Segoe UI", 9)
        )
        self.status_bar.pack(fill=tk.X)

    def _bangun_tombol_menu(self):
        # 1. Kelompok DATA
        grp_data = ttk.LabelFrame(self.scrollable_menu, text="DATA SISTEM", padding=6)
        grp_data.pack(fill=tk.X, padx=6, pady=4)
        btn_load = ttk.Button(grp_data, text="LOAD DATA (CSV)", command=self._form_load_data)
        btn_load.pack(fill=tk.X, pady=2)

        # 2. Kelompok M1 - DATA PESANAN (ARRAY)
        grp_m1_arr = ttk.LabelFrame(self.scrollable_menu, text="M1 - ARRAY", padding=6)
        grp_m1_arr.pack(fill=tk.X, padx=6, pady=4)
        m1_arr_actions = (
            ("ARRAY - LIHAT PESANAN", "arr_lihat"),
            ("ARRAY - TAMBAH REGULER", "arr_tambah_reg"),
            ("ARRAY - TAMBAH PRIORITAS", "arr_tambah_prio"),
            ("ARRAY - TAMBAH VIP", "arr_tambah_vip"),
            ("ARRAY - HAPUS PESANAN", "arr_hapus"),
        )
        for teks, aksi in m1_arr_actions:
            btn = ttk.Button(grp_m1_arr, text=teks, command=lambda a=aksi: self._buka_menu(a))
            btn.pack(fill=tk.X, pady=1)

        # 3. Kelompok M1 - DATA PESANAN (LINKED LIST)
        grp_m1_ll = ttk.LabelFrame(self.scrollable_menu, text="M1 - LINKEDLIST", padding=6)
        grp_m1_ll.pack(fill=tk.X, padx=6, pady=4)
        m1_ll_actions = (
            ("LINKEDLIST - LIHAT PESANAN", "ll_lihat"),
            ("LINKEDLIST - TAMBAH REGULER", "ll_tambah_reg"),
            ("LINKEDLIST - TAMBAH PRIORITAS", "ll_tambah_prio"),
            ("LINKEDLIST - TAMBAH VIP", "ll_tambah_vip"),
            ("LINKEDLIST - HAPUS PESANAN", "ll_hapus"),
        )
        for teks, aksi in m1_ll_actions:
            btn = ttk.Button(grp_m1_ll, text=teks, command=lambda a=aksi: self._buka_menu(a))
            btn.pack(fill=tk.X, pady=1)

        # 4. Kelompok M2 - STACK & QUEUE
        grp_m2 = ttk.LabelFrame(self.scrollable_menu, text="M2 - STACK & QUEUE", padding=6)
        grp_m2.pack(fill=tk.X, padx=6, pady=4)
        m2_actions = (
            ("STACK - POSTFIX (MESIN KASIR)", "postfix"),
            ("STACK - UNDO", "undo"),
            ("STACK - REDO", "redo"),
            ("QUEUE - ENQUEUE", "enqueue"),
            ("QUEUE - DEQUEUE NAIF", "dequeue_naif"),
            ("QUEUE - DEQUEUE CIRCULAR", "dequeue_circular"),
        )
        for teks, aksi in m2_actions:
            btn = ttk.Button(grp_m2, text=teks, command=lambda a=aksi: self._buka_menu(a))
            btn.pack(fill=tk.X, pady=1)

    def catat_command(self, nama_perintah, modul, durasi_detik):
        ms = durasi_detik * 1000.0
        log_line = f"{nama_perintah:<25} -> {modul:<14} {ms:10.4f} ms\n"
        self.txt_command.insert("1.0", log_line)
        self._set_status(f"[{modul}] {ms:.4f} ms")

    def _set_status(self, pesan):
        self.status_bar.config(text=pesan)

    def _tampilkan_hasil(self, teks):
        self.txt_hasil.delete("1.0", tk.END)
        self.txt_hasil.insert(tk.END, teks)

    def _bersihkan_form(self):
        for widget in self.form_container.winfo_children():
            widget.destroy()

    def _pastikan_data_siap(self):
        if self.arr_pesanan is None or self.arr_pesanan.panjang() == 0:
            messagebox.showwarning("Peringatan", "Data pesanan belum dimuat. Silakan jalankan 'LOAD DATA (CSV)' terlebih dahulu.")
            return False
        return True

    # =========================================================================
    # NAVIGASI & FORM DINAMIS
    # =========================================================================

    def _buka_menu(self, aksi):
        self._bersihkan_form()

        # Mapping form berdasarkan aksi
        if aksi == "arr_lihat":
            self.lbl_judul_menu.config(text="M1 - Array: Lihat Pesanan ke-i (O(1))")
            self._form_lihat(struktur_tipe="array")
        elif aksi == "ll_lihat":
            self.lbl_judul_menu.config(text="M1 - LinkList: Lihat Pesanan ke-i (O(n) Telusur)")
            self._form_lihat(struktur_tipe="linklist")
        elif aksi == "arr_tambah_reg":
            self.lbl_judul_menu.config(text="M1 - Array: Tambah Pesanan REGULER di Belakang (O(1) Amortized)")
            self._form_tambah(struktur_tipe="array", prioritas=3)
        elif aksi == "ll_tambah_reg":
            self.lbl_judul_menu.config(text="M1 - LinkList: Tambah Pesanan REGULER di Belakang Tail (O(1))")
            self._form_tambah(struktur_tipe="linklist", prioritas=3)
        elif aksi == "arr_tambah_prio":
            self.lbl_judul_menu.config(text="M1 - Array: Tambah Pesanan PRIORITAS di Tengah n//2 (O(n) Geser)")
            self._form_tambah(struktur_tipe="array", prioritas=2)
        elif aksi == "ll_tambah_prio":
            self.lbl_judul_menu.config(text="M1 - LinkList: Tambah Pesanan PRIORITAS di Tengah n//2 (O(n) Telusur)")
            self._form_tambah(struktur_tipe="linklist", prioritas=2)
        elif aksi == "arr_tambah_vip":
            self.lbl_judul_menu.config(text="M1 - Array: Tambah Pesanan VIP di Depan Indeks 0 (O(n) Geser)")
            self._form_tambah(struktur_tipe="array", prioritas=1)
        elif aksi == "ll_tambah_vip":
            self.lbl_judul_menu.config(text="M1 - LinkList: Tambah Pesanan VIP di Depan Head (O(1))")
            self._form_tambah(struktur_tipe="linklist", prioritas=1)
        elif aksi == "arr_hapus":
            self.lbl_judul_menu.config(text="M1 - Array: Hapus Pesanan ke-i (O(n) Geser Kiri)")
            self._form_hapus(struktur_tipe="array")
        elif aksi == "ll_hapus":
            self.lbl_judul_menu.config(text="M1 - LinkList: Hapus Pesanan ke-i (O(n) Telusur)")
            self._form_hapus(struktur_tipe="linklist")
        elif aksi == "postfix":
            self.lbl_judul_menu.config(text="M2 - Stack: Mesin Kasir Postfix (Infix -> Postfix -> Total)")
            self._form_postfix()
        elif aksi == "enqueue":
            self.lbl_judul_menu.config(text="M2 - Queue: Enqueue Pesanan ke Kedua Antrean (O(1))")
            self._form_enqueue()
        elif aksi == "dequeue_naif":
            self.lbl_judul_menu.config(text="M2 - Queue: Dequeue Antrean Naif (O(n) Geser Loop)")
            self._form_dequeue(metode="naif")
        elif aksi == "dequeue_circular":
            self.lbl_judul_menu.config(text="M2 - Queue: Dequeue Antrean Melingkar / Circular (O(1))")
            self._form_dequeue(metode="circular")
        elif aksi == "undo":
            self.lbl_judul_menu.config(text="M2 - Stack: Undo Aksi Terakhir")
            self._form_undo_redo(tipe="undo")
        elif aksi == "redo":
            self.lbl_judul_menu.config(text="M2 - Stack: Redo Aksi Terakhir")
            self._form_undo_redo(tipe="redo")

    # =========================================================================
    # FORM 0: LOAD DATA
    # =========================================================================

    def _form_load_data(self):
        self.lbl_judul_menu.config(text="DATA: Muat Berkas CSV ke Array, LinkList & Antrean M2")
        self._bersihkan_form()

        path_default = os.path.join(BASE_DIR, "data", "pesanan.csv")
        lbl_info = ttk.Label(self.form_container, text=f"Target Berkas: {path_default}\nMemuat 200.000 baris ke struktur data buatan sendiri.")
        lbl_info.pack(anchor="w", pady=(0, 6))

        btn = ttk.Button(self.form_container, text="PROSES MEMUAT DATA", command=self._jalankan_load_data)
        btn.pack(anchor="w")

    def _jalankan_load_data(self):
        path = os.path.join(BASE_DIR, "data", "pesanan.csv")
        if not os.path.exists(path):
            messagebox.showerror("Galat", f"Berkas tidak ditemukan: {path}")
            return

        self._set_status("Sedang memproses pemuatan 200.000 baris...")
        self.root.update_idletasks()

        arr, ll, durasi = muat_pesanan_ke_dua_struktur(path)
        self.arr_pesanan = arr
        self.ll_pesanan = ll

        # Muat pesanan ANTRE ke kedua antrean M2
        dimuat_antre = self.layanan_antrean.muat_dari_array(arr)

        self.catat_command("LOAD_CSV_DATA", "m1_pesanan", durasi)

        teks_hasil = (
            f"======================================================================\n"
            f"                      SUKSES MEMUAT DATA PESANAN                      \n"
            f"======================================================================\n"
            f"Berkas Sumber        : {path}\n"
            f"Total Baris Dimuat   : {arr.panjang():,} baris\n"
            f"Waktu Muat Total     : {durasi:.4f} detik ({durasi * 1000:.2f} ms)\n\n"
            f"[STATUS STRUKTUR DATA M1]\n"
            f"  - Array Dinamis    : {arr.panjang():,} pesanan (Kapasitas Buffer: {arr.kapasitas:,})\n"
            f"  - Linked List      : {ll.panjang():,} pesanan (Head: {ll.head.nilai.oid}, Tail: {ll.tail.nilai.oid})\n\n"
            f"[STATUS STRUKTUR DATA M2 (ANTRE)]\n"
            f"  - Pesanan Status ANTRE Masuk ke Antrean: {dimuat_antre:,} pesanan\n"
            f"  - Panjang Antrean Naif     : {self.layanan_antrean.antrean_naif.panjang():,}\n"
            f"  - Panjang Antrean Circular : {self.layanan_antrean.antrean_circular.panjang():,}\n"
            f"  - Kapasitas Antrean        : {self.layanan_antrean.antrean_circular.kapasitas:,}\n"
            f"======================================================================\n"
        )
        self._tampilkan_hasil(teks_hasil)

    # =========================================================================
    # FORM M1: LIHAT, TAMBAH, HAPUS
    # =========================================================================

    def _form_lihat(self, struktur_tipe):
        f = ttk.Frame(self.form_container)
        f.pack(fill=tk.X, pady=2)

        ttk.Label(f, text="Indeks Pesanan (0-indexed):").pack(side=tk.LEFT, padx=(0, 6))
        ent_idx = ttk.Entry(f, width=12)
        ent_idx.insert(0, "0")
        ent_idx.pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(
            f, text="LIHAT PESANAN",
            command=lambda: self._jalankan_lihat(struktur_tipe, ent_idx.get())
        )
        btn.pack(side=tk.LEFT)

    def _jalankan_lihat(self, struktur_tipe, str_idx):
        if not self._pastikan_data_siap():
            return
        try:
            idx = int(str_idx)
        except ValueError:
            messagebox.showerror("Galat", "Indeks harus berupa bilangan bulat.")
            return

        struktur = self.arr_pesanan if struktur_tipe == "array" else self.ll_pesanan
        nama_cmd = "ARRAY_LIHAT" if struktur_tipe == "array" else "LL_LIHAT"
        label_metrik = "Jumlah Geseran" if struktur_tipe == "array" else "Langkah Telusur"

        hasil, durasi, metrik = struktur.lihat(idx)
        self.catat_command(nama_cmd, "m1_pesanan", durasi)

        if hasil is None:
            self._tampilkan_hasil(f"[GALAT] Indeks {idx} berada di luar jangkauan (Ukuran struktur: {struktur.panjang():,}).")
            return

        teks = (
            f"=== HASIL OPERASI LIHAT PESANAN ({struktur_tipe.upper()}) ===\n"
            f"Indeks Dicari    : {idx}\n"
            f"Waktu Operasi    : {durasi * 1000:.6f} ms ({durasi:.8f} s)\n"
            f"{label_metrik:<17}: {metrik:,}\n\n"
            f"[DETAIL PESANAN]\n{hasil.ringkasan()}\n"
        )
        self._tampilkan_hasil(teks)

    def _form_tambah(self, struktur_tipe, prioritas):
        f1 = ttk.Frame(self.form_container)
        f1.pack(fill=tk.X, pady=2)

        prio_label = "VIP (Indeks 0)" if prioritas == 1 else ("PRIORITAS (Indeks n//2)" if prioritas == 2 else "REGULER (Belakang)")

        ttk.Label(f1, text="Pelanggan:").pack(side=tk.LEFT, padx=(0, 4))
        ent_nama = ttk.Entry(f1, width=20)
        ent_nama.insert(0, f"Pelanggan Baru {self.counter_id_baru}")
        ent_nama.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(f1, text="Menu:").pack(side=tk.LEFT, padx=(0, 4))
        ent_menu = ttk.Entry(f1, width=18)
        ent_menu.insert(0, "nasi-goreng-spesial")
        ent_menu.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(f1, text="Harga (Rp):").pack(side=tk.LEFT, padx=(0, 4))
        ent_harga = ttk.Entry(f1, width=10)
        ent_harga.insert(0, "25000")
        ent_harga.pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(
            f1, text=f"TAMBAH {prio_label}",
            command=lambda: self._jalankan_tambah(struktur_tipe, prioritas, ent_nama.get(), ent_menu.get(), ent_harga.get())
        )
        btn.pack(side=tk.LEFT)

    def _jalankan_tambah(self, struktur_tipe, prioritas, nama, menu, harga_str):
        if not self._pastikan_data_siap():
            return
        try:
            harga = int(harga_str)
        except ValueError:
            messagebox.showerror("Galat", "Harga harus berupa angka.")
            return

        oid = f"O-BARU-{self.counter_id_baru:04d}"
        self.counter_id_baru += 1
        pesanan = Pesanan(oid, nama, "kafe-teknik", menu, harga, prioritas, int(time.time()), None, "ANTRE")

        struktur = self.arr_pesanan if struktur_tipe == "array" else self.ll_pesanan
        prio_str = "VIP" if prioritas == 1 else ("PRIORITAS" if prioritas == 2 else "REGULER")
        cmd_name = f"{'ARRAY' if struktur_tipe == 'array' else 'LL'}_TAMBAH_{prio_str}"
        label_metrik = "Jumlah Geseran" if struktur_tipe == "array" else "Langkah Telusur"

        if prioritas == 1:
            hasil, durasi, metrik = struktur.tambah_vip(pesanan)
            posisi_str = "Indeks 0 (Paling Depan)"
        elif prioritas == 2:
            hasil, durasi, metrik = struktur.tambah_prioritas(pesanan)
            posisi_str = f"Indeks {struktur.panjang() // 2} (Tengah)"
        else:
            hasil, durasi, metrik = struktur.tambah_reguler(pesanan)
            posisi_str = f"Indeks {struktur.panjang() - 1} (Paling Belakang)"

        self.catat_command(cmd_name, "m1_pesanan", durasi)

        teks = (
            f"=== HASIL OPERASI TAMBAH PESANAN ({struktur_tipe.upper()}) ===\n"
            f"Jenis Prioritas  : {prioritas} ({prio_str})\n"
            f"Posisi Sisip     : {posisi_str}\n"
            f"Total Elemen Baru: {struktur.panjang():,} elemen\n"
            f"Waktu Operasi    : {durasi * 1000:.6f} ms ({durasi:.8f} s)\n"
            f"{label_metrik:<17}: {metrik:,}\n\n"
            f"[DETAIL PESANAN DISISIPKAN]\n{pesanan.ringkasan()}\n"
        )
        self._tampilkan_hasil(teks)

    def _form_hapus(self, struktur_tipe):
        f = ttk.Frame(self.form_container)
        f.pack(fill=tk.X, pady=2)

        ttk.Label(f, text="Indeks yang Ingin Dihapus:").pack(side=tk.LEFT, padx=(0, 6))
        ent_idx = ttk.Entry(f, width=12)
        ent_idx.insert(0, "0")
        ent_idx.pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(
            f, text="HAPUS PESANAN",
            command=lambda: self._jalankan_hapus(struktur_tipe, ent_idx.get())
        )
        btn.pack(side=tk.LEFT)

    def _jalankan_hapus(self, struktur_tipe, str_idx):
        if not self._pastikan_data_siap():
            return
        try:
            idx = int(str_idx)
        except ValueError:
            messagebox.showerror("Galat", "Indeks harus bilangan bulat.")
            return

        struktur = self.arr_pesanan if struktur_tipe == "array" else self.ll_pesanan
        cmd_name = "ARRAY_HAPUS" if struktur_tipe == "array" else "LL_HAPUS"
        label_metrik = "Jumlah Geseran" if struktur_tipe == "array" else "Langkah Telusur"

        terhapus, durasi, metrik = struktur.hapus_dengan_metrik(idx)
        self.catat_command(cmd_name, "m1_pesanan", durasi)

        if terhapus is None:
            self._tampilkan_hasil(f"[GALAT] Gagal menghapus. Indeks {idx} tidak valid (Ukuran: {struktur.panjang():,}).")
            return

        teks = (
            f"=== HASIL OPERASI HAPUS PESANAN ({struktur_tipe.upper()}) ===\n"
            f"Indeks Dihapus   : {idx}\n"
            f"Sisa Elemen      : {struktur.panjang():,} elemen\n"
            f"Waktu Operasi    : {durasi * 1000:.6f} ms ({durasi:.8f} s)\n"
            f"{label_metrik:<17}: {metrik:,}\n\n"
            f"[DETAIL PESANAN YANG DIHAPUS]\n{terhapus.ringkasan()}\n"
        )
        self._tampilkan_hasil(teks)

    # =========================================================================
    # FORM M2: POSTFIX MESIN KASIR
    # =========================================================================

    def _form_postfix(self):
        f = ttk.Frame(self.form_container)
        f.pack(fill=tk.X, pady=2)

        ttk.Label(f, text="Ekspresi Kasir (Infix):").pack(side=tk.LEFT, padx=(0, 6))
        ent_exp = ttk.Entry(f, width=45)
        ent_exp.insert(0, "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        ent_exp.pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(f, text="HITUNG TOTAL KASIR", command=lambda: self._jalankan_postfix(ent_exp.get()))
        btn.pack(side=tk.LEFT)

    def _jalankan_postfix(self, ekspresi):
        if not ekspresi.strip():
            messagebox.showerror("Galat", "Ekspresi matematika tidak boleh kosong.")
            return

        t_awal = time.perf_counter()
        try:
            str_postfix, total_int, str_rp, tabel_langkah = proses_kasir(ekspresi)
        except Exception as e:
            durasi = time.perf_counter() - t_awal
            self.catat_command("POSTFIX_KASIR_GALAT", "m2_stack", durasi)
            self._tampilkan_hasil(f"[GALAT EVALUASI KASIR]\n{str(e)}")
            return

        durasi = time.perf_counter() - t_awal
        self.catat_command("POSTFIX_KASIR", "m2_stack", durasi)

        garis = "=" * 105
        hasil_teks = (
            f"{garis}\n"
            f"                          MESIN KASIR 2EZ4U - POSTFIX ENGINE\n"
            f"{garis}\n"
            f"Ekspresi Infix   : {ekspresi}\n"
            f"Bentuk Postfix   : {str_postfix}\n"
            f"Waktu Evaluasi   : {durasi * 1000:.4f} ms\n"
            f"{garis}\n"
            f"{'Langkah':<8} | {'Token':<8} | {'Tindakan':<46} | {'Isi Stack':<18} | {'Output':<18}\n"
            f"{'-'*8}-+-{'-'*8}-+-{'-'*46}-+-{'-'*18}-+-{'-'*18}\n"
        )

        for i in range(tabel_langkah.panjang()):
            step = tabel_langkah.get(i)
            hasil_teks += f"{step.langkah:<8} | {step.token:<8} | {step.tindakan:<46} | {step.stack_str:<18} | {step.output_str:<18}\n"

        hasil_teks += (
            f"{garis}\n"
            f"TOTAL : {str_rp}\n"
            f"{garis}\n"
        )
        self._tampilkan_hasil(hasil_teks)

    # =========================================================================
    # FORM M2: QUEUE ENQUEUE & DEQUEUE
    # =========================================================================

    def _form_enqueue(self):
        f = ttk.Frame(self.form_container)
        f.pack(fill=tk.X, pady=2)

        ttk.Label(f, text="Nama Pelanggan:").pack(side=tk.LEFT, padx=(0, 4))
        ent_nama = ttk.Entry(f, width=20)
        ent_nama.insert(0, f"Customer Antre {self.counter_id_baru}")
        ent_nama.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(f, text="Resto:").pack(side=tk.LEFT, padx=(0, 4))
        ent_resto = ttk.Entry(f, width=16)
        ent_resto.insert(0, "warung-bu-ida")
        ent_resto.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(f, text="Menu:").pack(side=tk.LEFT, padx=(0, 4))
        ent_menu = ttk.Entry(f, width=16)
        ent_menu.insert(0, "ayam-geprek")
        ent_menu.pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(
            f, text="ENQUEUE KE DUA ANTREAN",
            command=lambda: self._jalankan_enqueue(ent_nama.get(), ent_resto.get(), ent_menu.get())
        )
        btn.pack(side=tk.LEFT)

    def _jalankan_enqueue(self, nama, resto, menu):
        oid = f"O-Q-{self.counter_id_baru:05d}"
        self.counter_id_baru += 1
        pesanan = Pesanan(oid, nama, resto, menu, 20000, 3, int(time.time()), None, "ANTRE")

        p, durasi = self.layanan_antrean.enqueue(pesanan)
        self.catat_command("QUEUE_ENQUEUE", "m2_queue", durasi)

        stats = self.layanan_antrean.stats()
        teks = (
            f"=== HASIL OPERASI ENQUEUE (KEDUA ANTREAN) ===\n"
            f"Waktu Operasi            : {durasi * 1000:.4f} ms\n"
            f"Panjang Antrean Naif     : {stats.queue_len_naif:,}\n"
            f"Panjang Antrean Circular : {stats.queue_len_circular:,}\n"
            f"Kapasitas Antrean        : {stats.queue_capacity_circular:,}\n"
            f"Kedalaman Tumpukan Undo  : {stats.undo_depth}\n"
            f"Kedalaman Tumpukan Redo  : {stats.redo_depth} (Dikosongkan otomatis saat aksi baru)\n\n"
            f"[DETAIL PESANAN DI-ENQUEUE]\n{pesanan.ringkasan()}\n"
        )
        self._tampilkan_hasil(teks)

    def _form_dequeue(self, metode):
        f = ttk.Frame(self.form_container)
        f.pack(fill=tk.X, pady=2)

        ttk.Label(f, text=f"Jumlah Pesanan yang Di-dequeue ({metode.upper()}):").pack(side=tk.LEFT, padx=(0, 6))
        ent_n = ttk.Entry(f, width=10)
        ent_n.insert(0, "100")
        ent_n.pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(
            f, text=f"JALANKAN DEQUEUE {metode.upper()}",
            command=lambda: self._jalankan_dequeue(metode, ent_n.get())
        )
        btn.pack(side=tk.LEFT)

    def _jalankan_dequeue(self, metode, str_n):
        try:
            n = int(str_n)
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Galat", "Jumlah dequeue harus berupa bilangan bulat positif.")
            return

        if self.layanan_antrean.antrean_circular.is_empty():
            messagebox.showwarning("Peringatan", "Antrean kosong. Tidak ada pesanan untuk di-dequeue.")
            return

        cmd_name = "DEQUEUE_NAIF" if metode == "naif" else "DEQUEUE_CIRCULAR"

        if metode == "naif":
            daftar_keluar, durasi, geseran = self.layanan_antrean.dequeue_naif(n)
        else:
            daftar_keluar, durasi, geseran = self.layanan_antrean.dequeue_circular(n)

        self.catat_command(cmd_name, "m2_queue", durasi)

        stats = self.layanan_antrean.stats()
        garis = "=" * 80
        teks = (
            f"{garis}\n"
            f"               HASIL OPERASI DEQUEUE ({metode.upper()})\n"
            f"{garis}\n"
            f"Pesanan Berhasil Keluar  : {daftar_keluar.panjang():,} pesanan\n"
            f"Waktu Eksekusi           : {durasi * 1000:.4f} ms ({durasi:.6f} s)\n"
            f"Elemen Digeser Operasi Ini: {geseran:,}\n"
            f"Total Geseran Kumulatif Naif : {stats.total_geseran_naif:,}\n"
            f"Total Geseran Circular       : {stats.total_geseran_circular:,}\n"
            f"Sisa Panjang Antrean     : {stats.queue_len_circular:,}\n"
            f"Kedalaman Tumpukan Undo  : {stats.undo_depth}\n"
            f"Kedalaman Tumpukan Redo  : {stats.redo_depth} (Dikosongkan otomatis)\n"
            f"{garis}\n"
            f"SAMPEL PESANAN YANG KELUAR (Maksimal 10 pertama ditampilkan):\n"
        )

        tampil_maks = 10 if daftar_keluar.panjang() > 10 else daftar_keluar.panjang()
        for i in range(tampil_maks):
            p = daftar_keluar.get(i)
            teks += f"  [{i+1:>2}] {p.oid:<10} | Pelanggan: {p.pelanggan:<20} | Menu: {p.menu:<18} | Rp {p.harga:,}\n"

        if daftar_keluar.panjang() > 10:
            teks += f"  ... dan {daftar_keluar.panjang() - 10} pesanan lainnya.\n"

        teks += f"{garis}\n"
        self._tampilkan_hasil(teks)

    # =========================================================================
    # FORM M2: UNDO & REDO
    # =========================================================================

    def _form_undo_redo(self, tipe):
        f = ttk.Frame(self.form_container)
        f.pack(fill=tk.X, pady=2)

        label_teks = "Batalkan aksi terakhir (Undo)" if tipe == "undo" else "Ulang aksi yang baru dibatalkan (Redo)"
        ttk.Label(f, text=label_teks).pack(side=tk.LEFT, padx=(0, 10))

        btn = ttk.Button(
            f, text=f"JALANKAN {tipe.upper()}",
            command=lambda: self._jalankan_undo_redo(tipe)
        )
        btn.pack(side=tk.LEFT)

    def _jalankan_undo_redo(self, tipe):
        cmd_name = "STACK_UNDO" if tipe == "undo" else "STACK_REDO"

        if tipe == "undo":
            sukses, pesan, durasi = self.layanan_antrean.undo_last()
        else:
            sukses, pesan, durasi = self.layanan_antrean.redo_last()

        self.catat_command(cmd_name, "m2_stack", durasi)
        stats = self.layanan_antrean.stats()

        garis = "=" * 70
        teks = (
            f"{garis}\n"
            f"               STATUS OPERASI {tipe.upper()}\n"
            f"{garis}\n"
            f"Status                   : {'BERHASIL' if sukses else 'GAGAL / KOSONG'}\n"
            f"Keterangan               : {pesan}\n"
            f"Waktu Operasi            : {durasi * 1000:.4f} ms\n"
            f"Panjang Antrean Terkini  : {stats.queue_len_circular:,}\n"
            f"Kedalaman Tumpukan Undo  : {stats.undo_depth}\n"
            f"Kedalaman Tumpukan Redo  : {stats.redo_depth}\n"
            f"{garis}\n"
        )
        self._tampilkan_hasil(teks)


def main():
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
