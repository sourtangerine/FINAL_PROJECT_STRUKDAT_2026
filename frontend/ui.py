"""
frontend/ui.py
Antarmuka Pengguna Tkinter untuk 2EZ4U Food Delivery.
Desain disesuaikan persis dengan antarmuka acuan:
- Header bar warna biru gelap: '2EZ4U Food Delivery'
- Panel kiri: Tombol navigasi berkelompok (DATA, M1, M2, M3-M4, M5, M6)
  * M3 ke atas menampilkan popup 'Fitur ini masih dikerjakan'
- Panel kanan: Form parameter dengan judul & deskripsi singkat, tombol aksi biru gelap,
  area hasil monospaced dengan bingkai tegas, panel COMMAND (latar putih, log rapi),
  dan lencana status 'siap' di pojok kiri bawah.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import time

# Pastikan root direktori ada di sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.m1_pesanan import Pesanan, Array, LinkList, muat_pesanan_ke_dua_struktur
from backend.m2_antrean import LayananAntrean, proses_kasir


class AppUI:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1100x720")
        self.root.minsize(980, 640)
        self.root.configure(bg="#ffffff")

        # Palet warna sesuai antarmuka acuan
        self.COLOR_HEADER_BG = "#1b3a5b"      # Biru gelap elegan
        self.COLOR_HEADER_FG = "#ffffff"
        self.COLOR_SIDEBAR_BG = "#f5f6f8"     # Abu-abu muda bersih
        self.COLOR_BTN_BG = "#ffffff"
        self.COLOR_BTN_HOVER = "#e8eef5"
        self.COLOR_BTN_ACTIVE = "#d5e3f3"     # Highlight tombol terpilih
        self.COLOR_PRIMARY_BTN = "#1b3a5b"    # Tombol aksi utama form
        self.COLOR_BORDER = "#cccccc"
        self.COLOR_TEXT_MAIN = "#111827"
        self.COLOR_TEXT_MUTED = "#555555"

        # State Backend
        self.arr_pesanan = None
        self.ll_pesanan = None
        self.layanan_antrean = LayananAntrean(kapasitas_awal=262144)
        self.counter_id_baru = 1

        self.tombol_menu_dict = []  # Menyimpan referensi tombol menu untuk penyorotan
        self.menu_aktif = None

        self._buat_layout()
        # Default buka form Load Data
        self._pilih_menu("load")

    def _buat_layout(self):
        # 1. TOP HEADER BANNER (Biru gelap penuh)
        self.top_banner = tk.Frame(self.root, bg=self.COLOR_HEADER_BG, height=44)
        self.top_banner.pack(side=tk.TOP, fill=tk.X)
        self.top_banner.pack_propagate(False)

        self.lbl_banner = tk.Label(
            self.top_banner,
            text="2EZ4U Food Delivery",
            bg=self.COLOR_HEADER_BG,
            fg=self.COLOR_HEADER_FG,
            font=("Segoe UI", 12, "bold"),
            padx=14
        )
        self.lbl_banner.pack(side=tk.LEFT, fill=tk.Y)

        # 2. MAIN WORKSPACE CONTAINER
        self.main_container = tk.Frame(self.root, bg="#ffffff")
        self.main_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Split: Kiri (Menu Navigasi) dan Kanan (Konten Kerja)
        self.left_sidebar = tk.Frame(self.main_container, bg=self.COLOR_SIDEBAR_BG, width=270, bd=1, relief="solid")
        self.left_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.left_sidebar.pack_propagate(False)

        self.right_workspace = tk.Frame(self.main_container, bg="#ffffff", padx=18, pady=14)
        self.right_workspace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # --- MEMBANGUN SIDEBAR MENU KIRI ---
        self._bangun_sidebar_menu()

        # --- MEMBANGUN WORKSPACE KANAN ---
        self._bangun_workspace_kanan()

    def _bangun_sidebar_menu(self):
        # Canvas scrollable untuk daftar tombol menu
        self.menu_canvas = tk.Canvas(self.left_sidebar, bg=self.COLOR_SIDEBAR_BG, highlightthickness=0, borderwidth=0)
        self.menu_scrollbar = ttk.Scrollbar(self.left_sidebar, orient="vertical", command=self.menu_canvas.yview)
        self.menu_inner_frame = tk.Frame(self.menu_canvas, bg=self.COLOR_SIDEBAR_BG)

        self.menu_inner_frame.bind(
            "<Configure>",
            lambda e: self.menu_canvas.configure(scrollregion=self.menu_canvas.bbox("all"))
        )
        self.canvas_window = self.menu_canvas.create_window((0, 0), window=self.menu_inner_frame, anchor="nw", width=252)

        self.menu_canvas.configure(yscrollcommand=self.menu_scrollbar.set)
        self.menu_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.menu_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Definisi Kelompok Menu persis sesuai gambar acuan
        struktur_menu = (
            ("DATA", [
                ("Load", "load"),
            ]),
            ("M1 - DATA PESANAN", [
                ("ARRAY - LIHAT PESANAN", "arr_lihat"),
                ("ARRAY - TAMBAH PESANAN REGULER", "arr_tambah_reg"),
                ("ARRAY - TAMBAH PESANAN PRIORITAS", "arr_tambah_prio"),
                ("ARRAY - TAMBAH PESANAN VIP", "arr_tambah_vip"),
                ("ARRAY - HAPUS PESANAN", "arr_hapus"),
                ("LINKEDLIST - LIHAT PESANAN", "ll_lihat"),
                ("LINKEDLIST - TAMBAH PESANAN REGULER", "ll_tambah_reg"),
                ("LINKEDLIST - TAMBAH PESANAN PRIORITAS", "ll_tambah_prio"),
                ("LINKEDLIST - TAMBAH PESANAN VIP", "ll_tambah_vip"),
                ("LINKEDLIST - HAPUS PESANAN", "ll_hapus"),
            ]),
            ("M2 - ANTREAN DAN UNDO", [
                ("Isi antrean FIFO", "m2_isi_fifo"),
                ("Layani berikutnya", "m2_layani"),
                ("Undo", "m2_undo"),
                ("Redo", "m2_redo"),
                ("Mesin kasir (Postfix)", "m2_postfix"),
            ]),
            ("M3 DAN M4 - LAPORAN DAN PENCARIAN", [
                ("Laporan harian", "m3_laporan"),
                ("Cari di laporan", "m3_cari_laporan"),
                ("Bangun indeks hash", "m3_hash"),
                ("Cari pesanan (oid)", "m3_cari_oid"),
            ]),
            ("M5 - KATALOG DAN PRIORITAS", [
                ("Menu per rentang harga", "m5_katalog"),
                ("Isi antrean prioritas", "m5_antrean_prio"),
            ]),
            ("M6 - PETA DAN RUTE", [
                ("Muat peta", "m6_peta"),
            ]),
        )

        for judul_grup, daftar_tombol in struktur_menu:
            lbl_grup = tk.Label(
                self.menu_inner_frame,
                text=judul_grup,
                bg=self.COLOR_SIDEBAR_BG,
                fg=self.COLOR_TEXT_MUTED,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
                padx=8,
                pady=4
            )
            lbl_grup.pack(fill=tk.X, padx=4, pady=(6, 2))

            for teks_btn, aksi_id in daftar_tombol:
                btn = tk.Button(
                    self.menu_inner_frame,
                    text=teks_btn,
                    bg=self.COLOR_BTN_BG,
                    activebackground=self.COLOR_BTN_HOVER,
                    fg=self.COLOR_TEXT_MAIN,
                    font=("Segoe UI", 8),
                    anchor="w",
                    bd=1,
                    relief="solid",
                    padx=6,
                    pady=2,
                    cursor="hand2",
                    command=lambda a=aksi_id: self._pilih_menu(a)
                )
                btn.pack(fill=tk.X, padx=8, pady=1)
                self.tombol_menu_dict.append((aksi_id, btn))

    def _bangun_workspace_kanan(self):
        # 1. Header Informasi Menu Terpilih (Judul & Subtitle Deskriptif)
        self.frame_header_kanan = tk.Frame(self.right_workspace, bg="#ffffff")
        self.frame_header_kanan.pack(fill=tk.X, pady=(0, 6))

        self.lbl_judul_aksi = tk.Label(
            self.frame_header_kanan,
            text="Array: pesanan REGULER, masuk paling belakang",
            bg="#ffffff",
            fg="#111827",
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        self.lbl_judul_aksi.pack(anchor="w")

        self.lbl_subjudul_aksi = tk.Label(
            self.frame_header_kanan,
            text="append: pesanan biasa mengantre di barisan paling belakang.",
            bg="#ffffff",
            fg=self.COLOR_TEXT_MUTED,
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.lbl_subjudul_aksi.pack(anchor="w", pady=(1, 4))

        # 2. Form Parameter Dinamis
        self.frame_form_dinamis = tk.Frame(self.right_workspace, bg="#ffffff")
        self.frame_form_dinamis.pack(fill=tk.X, pady=(0, 8))

        # Garis pemisah abu-abu tipis
        self.sep_line = tk.Frame(self.right_workspace, bg="#e5e7eb", height=1)
        self.sep_line.pack(fill=tk.X, pady=(2, 8))

        # 3. Area Teks Hasil Utama
        self.frame_hasil = tk.Frame(self.right_workspace, bg="#ffffff")
        self.frame_hasil.pack(fill=tk.BOTH, expand=True, pady=(0, 8))

        self.txt_hasil = tk.Text(
            self.frame_hasil,
            bg="#ffffff",
            fg="#111827",
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            wrap="none"
        )
        self.scroll_hasil_y = ttk.Scrollbar(self.frame_hasil, orient="vertical", command=self.txt_hasil.yview)
        self.scroll_hasil_x = ttk.Scrollbar(self.frame_hasil, orient="horizontal", command=self.txt_hasil.xview)
        self.txt_hasil.configure(yscrollcommand=self.scroll_hasil_y.set, xscrollcommand=self.scroll_hasil_x.set)

        self.scroll_hasil_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_hasil_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.txt_hasil.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 4. Bagian COMMAND (Riwayat Eksekusi)
        self.frame_command = tk.Frame(self.right_workspace, bg="#ffffff")
        self.frame_command.pack(fill=tk.X, side=tk.BOTTOM)

        self.lbl_command_title = tk.Label(
            self.frame_command,
            text="COMMAND",
            bg="#ffffff",
            fg="#374151",
            font=("Segoe UI", 9, "bold"),
            anchor="w"
        )
        self.lbl_command_title.pack(anchor="w", pady=(0, 2))

        self.frame_command_box = tk.Frame(self.frame_command, bg="#ffffff")
        self.frame_command_box.pack(fill=tk.X, pady=(0, 4))

        self.txt_command = tk.Text(
            self.frame_command_box,
            height=3,
            bg="#ffffff",
            fg="#111827",
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            wrap="none"
        )
        self.scroll_cmd = ttk.Scrollbar(self.frame_command_box, orient="vertical", command=self.txt_command.yview)
        self.txt_command.configure(yscrollcommand=self.scroll_cmd.set)
        self.scroll_cmd.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_command.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Lencana status di pojok kiri bawah: 'siap'
        self.status_container = tk.Frame(self.frame_command, bg="#ffffff")
        self.status_container.pack(anchor="w", pady=(2, 0))

        self.badge_status = tk.Label(
            self.status_container,
            text="siap",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Consolas", 9, "bold"),
            padx=16,
            pady=3,
            relief="flat"
        )
        self.badge_status.pack(side=tk.LEFT)

    def _sorot_tombol_menu(self, aksi_terpilih):
        for aksi_id, btn in self.tombol_menu_dict:
            if aksi_id == aksi_terpilih:
                btn.config(bg=self.COLOR_BTN_ACTIVE, font=("Segoe UI", 8, "bold"))
            else:
                btn.config(bg=self.COLOR_BTN_BG, font=("Segoe UI", 8))

    def catat_command(self, nama_perintah, modul, durasi_detik):
        ms = durasi_detik * 1000.0
        # Format sesuai screenshot acuan:
        # load                      -> M1 - larik       261.06 ms
        # array_get                 -> M1 - array         0.05 ms
        line = f"{nama_perintah:<25} -> {modul:<14} {ms:10.2f} ms\n"
        self.txt_command.insert("1.0", line)
        self.badge_status.config(text=f"[{modul}] {ms:.2f} ms")

    def _set_status_badge(self, teks):
        self.badge_status.config(text=teks)

    def _tampilkan_hasil(self, teks):
        self.txt_hasil.delete("1.0", tk.END)
        self.txt_hasil.insert(tk.END, teks)

    def _bersihkan_form(self):
        for w in self.frame_form_dinamis.winfo_children():
            w.destroy()

    def _pastikan_data_siap(self):
        if self.arr_pesanan is None or self.arr_pesanan.panjang() == 0:
            messagebox.showwarning(
                "Peringatan",
                "Data pesanan belum dimuat ke memori.\nSilakan jalankan menu 'Load' terlebih dahulu."
            )
            return False
        return True

    # =========================================================================
    # LOGIKA NAVIGASI MENU
    # =========================================================================

    def _pilih_menu(self, aksi):
        self.menu_aktif = aksi
        self._sorot_tombol_menu(aksi)
        self._bersihkan_form()

        # Tangani M3 ke atas: Tampilkan popup khusus
        if aksi in ("m3_laporan", "m3_cari_laporan", "m3_hash", "m3_cari_oid",
                    "m5_katalog", "m5_antrean_prio", "m6_peta"):
            self._tangani_m3_keatas(aksi)
            return

        # DATA
        if aksi == "load":
            self._setup_view_load()
        # M1 - ARRAY
        elif aksi == "arr_lihat":
            self._setup_view_lihat(tipe_str="array")
        elif aksi == "arr_tambah_reg":
            self._setup_view_tambah(tipe_str="array", prioritas=3)
        elif aksi == "arr_tambah_prio":
            self._setup_view_tambah(tipe_str="array", prioritas=2)
        elif aksi == "arr_tambah_vip":
            self._setup_view_tambah(tipe_str="array", prioritas=1)
        elif aksi == "arr_hapus":
            self._setup_view_hapus(tipe_str="array")
        # M1 - LINKEDLIST
        elif aksi == "ll_lihat":
            self._setup_view_lihat(tipe_str="linklist")
        elif aksi == "ll_tambah_reg":
            self._setup_view_tambah(tipe_str="linklist", prioritas=3)
        elif aksi == "ll_tambah_prio":
            self._setup_view_tambah(tipe_str="linklist", prioritas=2)
        elif aksi == "ll_tambah_vip":
            self._setup_view_tambah(tipe_str="linklist", prioritas=1)
        elif aksi == "ll_hapus":
            self._setup_view_hapus(tipe_str="linklist")
        # M2 - ANTREAN & UNDO
        elif aksi == "m2_isi_fifo":
            self._setup_view_isi_fifo()
        elif aksi == "m2_layani":
            self._setup_view_layani()
        elif aksi == "m2_undo":
            self._setup_view_undo_redo(mode="undo")
        elif aksi == "m2_redo":
            self._setup_view_undo_redo(mode="redo")
        elif aksi == "m2_postfix":
            self._setup_view_postfix()

    def _tangani_m3_keatas(self, aksi):
        nama_map = {
            "m3_laporan": ("Laporan Harian", "M3 - laporan"),
            "m3_cari_laporan": ("Cari di Laporan", "M3 - laporan"),
            "m3_hash": ("Bangun Indeks Hash", "M4 - hash"),
            "m3_cari_oid": ("Cari Pesanan (OID)", "M4 - hash"),
            "m5_katalog": ("Menu per Rentang Harga", "M5 - bst"),
            "m5_antrean_prio": ("Isi Antrean Prioritas", "M5 - heap"),
            "m6_peta": ("Muat Peta & Rute", "M6 - graf"),
        }
        judul, modul = nama_map.get(aksi, ("Fitur Lanjutan", "M3+"))

        self.lbl_judul_aksi.config(text=f"{judul}")
        self.lbl_subjudul_aksi.config(text=f"Fitur {modul} dijadwalkan untuk milestone berikutnya.")

        lbl_info = tk.Label(
            self.frame_form_dinamis,
            text=f"Modul '{judul}' belum diaktifkan pada Milestone 1 dan 2.\nSilakan konfirmasi penyelesaian M1 & M2 terlebih dahulu.",
            bg="#ffffff",
            fg=self.COLOR_TEXT_MUTED,
            font=("Segoe UI", 9)
        )
        lbl_info.pack(anchor="w", pady=4)

        self.catat_command(aksi, modul, 0.0)
        self._tampilkan_hasil(
            f"======================================================================\n"
            f"                   PEMBERITAHUAN FITUR MILESTONE LANJUTAN              \n"
            f"======================================================================\n"
            f"Modul        : {modul}\n"
            f"Operasi      : {judul}\n"
            f"Status       : Fitur ini masih dikerjakan (Milestone 3 ke atas).\n"
            f"Keterangan   : Berkas spesifikasi 'Project' saat ini difokuskan pada\n"
            f"               penuntasan Milestone 1 (Array vs LL) & Milestone 2 (Stack & Queue).\n"
            f"======================================================================\n"
        )

        # Popup sesuai permintaan pengguna:
        messagebox.showinfo("2EZ4U Food Delivery", "Fitur ini masih dikerjakan")

    # =========================================================================
    # FORM 1: LOAD DATA
    # =========================================================================

    def _setup_view_load(self):
        self.lbl_judul_aksi.config(text="DATA: Muat Berkas CSV ke Memori")
        self.lbl_subjudul_aksi.config(text="load: membaca 200.000 baris pesanan ke Array dan LinkList.")

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl_entry = tk.Label(f, text="Path berkas pesanan", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl_entry.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_path = tk.Entry(sub_f, width=40, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_path.insert(0, "data/pesanan.csv")
        ent_path.pack(side=tk.LEFT, padx=(0, 16))

        btn_load = tk.Button(
            sub_f,
            text="LOAD",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_load_csv(ent_path.get())
        )
        btn_load.pack(side=tk.LEFT)

        lbl_desc = tk.Label(f, text="berkas CSV yang disediakan berisi 200.000 baris pesanan", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_desc.pack(anchor="w")

    def _aksi_load_csv(self, rel_path):
        full_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(full_path):
            messagebox.showerror("Galat", f"Berkas tidak ditemukan: {full_path}")
            return

        self._set_status_badge("memuat...")
        self.root.update_idletasks()

        arr, ll, durasi = muat_pesanan_ke_dua_struktur(full_path)
        self.arr_pesanan = arr
        self.ll_pesanan = ll

        # Isi kedua antrean M2 dari pesanan ANTRE
        dimuat_antre = self.layanan_antrean.muat_dari_array(arr)

        self.catat_command("load", "M1 - larik", durasi)
        self._set_status_badge("siap")

        self._tampilkan_hasil(
            f"Memuat {full_path} ...\n"
            f"Selesai dalam {durasi * 1000:.2f} ms ({durasi:.4f} detik)\n"
            f"Jumlah baris dimuat        : {arr.panjang():,} baris\n"
            f"Kapasitas buffer Array     : {arr.kapasitas:,}\n"
            f"Head Linked List           : {ll.head.nilai.oid} ({ll.head.nilai.pelanggan})\n"
            f"Tail Linked List           : {ll.tail.nilai.oid} ({ll.tail.nilai.pelanggan})\n\n"
            f"[STATUS ANTREAN M2]\n"
            f"Pesanan status ANTRE masuk : {dimuat_antre:,} pesanan\n"
            f"Panjang Antrean Naif       : {self.layanan_antrean.antrean_naif.panjang():,}\n"
            f"Panjang Antrean Melingkar  : {self.layanan_antrean.antrean_circular.panjang():,}\n"
        )

    # =========================================================================
    # FORM M1: LIHAT PESANAN
    # =========================================================================

    def _setup_view_lihat(self, tipe_str):
        if tipe_str == "array":
            self.lbl_judul_aksi.config(text="Array: lihat pesanan ke-i")
            self.lbl_subjudul_aksi.config(text="get: akses langsung berdasarkan indeks ke-i (O(1)).")
            cmd_nama = "array_get"
            modul_tag = "M1 - array"
        else:
            self.lbl_judul_aksi.config(text="LinkList: lihat pesanan ke-i")
            self.lbl_subjudul_aksi.config(text="get: menelusuri rantai simpul dari head sampai indeks ke-i (O(n)).")
            cmd_nama = "ll_get"
            modul_tag = "M1 - linklist"

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text="Indeks pesanan", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_idx = tk.Entry(sub_f, width=16, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_idx.insert(0, "0")
        ent_idx.pack(side=tk.LEFT, padx=(0, 16))

        btn = tk.Button(
            sub_f,
            text="LIHAT",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_lihat(tipe_str, ent_idx.get(), cmd_nama, modul_tag)
        )
        btn.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text="indeks pesanan yang ingin dilihat (0 sampai n-1)", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_lihat(self, tipe_str, str_idx, cmd_nama, modul_tag):
        if not self._pastikan_data_siap():
            return
        try:
            idx = int(str_idx)
        except ValueError:
            messagebox.showerror("Galat", "Indeks harus berupa bilangan bulat.")
            return

        struktur = self.arr_pesanan if tipe_str == "array" else self.ll_pesanan
        hasil, durasi, metrik = struktur.lihat(idx)
        self.catat_command(cmd_nama, modul_tag, durasi)

        if hasil is None:
            self._tampilkan_hasil(f"[GALAT] Indeks {idx} berada di luar jangkauan (Ukuran total: {struktur.panjang():,}).")
            return

        label_metrik = "Jumlah geseran" if tipe_str == "array" else "Langkah telusur"
        self._tampilkan_hasil(
            f"=== HASIL OPERASI LIHAT PESANAN ({tipe_str.upper()}) ===\n"
            f"Indeks         : {idx}\n"
            f"Waktu          : {durasi * 1000:.4f} ms ({durasi:.6f} s)\n"
            f"{label_metrik:<15}: {metrik:,}\n\n"
            f"Detail Pesanan :\n{hasil.ringkasan()}\n"
        )

    # =========================================================================
    # FORM M1: TAMBAH PESANAN (REGULER, PRIORITAS, VIP)
    # =========================================================================

    def _setup_view_tambah(self, tipe_str, prioritas):
        prio_label = "REGULER" if prioritas == 3 else ("PRIORITAS" if prioritas == 2 else "VIP")
        if tipe_str == "array":
            if prioritas == 3:
                self.lbl_judul_aksi.config(text="Array: pesanan REGULER, masuk paling belakang")
                self.lbl_subjudul_aksi.config(text="append: pesanan biasa mengantre di barisan paling belakang.")
                cmd_nama = "array_insert_reguler"
            elif prioritas == 2:
                self.lbl_judul_aksi.config(text="Array: pesanan PRIORITAS, masuk di tengah")
                self.lbl_subjudul_aksi.config(text="insert: pesanan prioritas disisipkan di indeks n // 2.")
                cmd_nama = "array_insert_prioritas"
            else:
                self.lbl_judul_aksi.config(text="Array: pesanan VIP, masuk paling depan")
                self.lbl_subjudul_aksi.config(text="insert: pesanan VIP disisipkan di indeks 0 paling depan.")
                cmd_nama = "array_insert_vip"
            modul_tag = "M1 - array"
        else:
            if prioritas == 3:
                self.lbl_judul_aksi.config(text="LinkList: pesanan REGULER, masuk paling belakang")
                self.lbl_subjudul_aksi.config(text="append: menambahkan simpul baru di ujung tail (O(1)).")
                cmd_nama = "ll_insert_reguler"
            elif prioritas == 2:
                self.lbl_judul_aksi.config(text="LinkList: pesanan PRIORITAS, masuk di tengah")
                self.lbl_subjudul_aksi.config(text="insert: menelusuri hingga simpul n // 2 lalu menyisipkan (O(n)).")
                cmd_nama = "ll_insert_prioritas"
            else:
                self.lbl_judul_aksi.config(text="LinkList: pesanan VIP, masuk paling depan")
                self.lbl_subjudul_aksi.config(text="tambah_depan: simpul baru disisipkan di head (O(1)).")
                cmd_nama = "ll_insert_vip"
            modul_tag = "M1 - linklist"

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text="Nama pelanggan", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_nama = tk.Entry(sub_f, width=28, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_nama.insert(0, f"Pelanggan Baru {self.counter_id_baru}")
        ent_nama.pack(side=tk.LEFT, padx=(0, 16))

        btn = tk.Button(
            sub_f,
            text="TAMBAH",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_tambah(tipe_str, prioritas, ent_nama.get(), cmd_nama, modul_tag)
        )
        btn.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text="nama untuk pesanan yang akan dibuat", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_tambah(self, tipe_str, prioritas, nama, cmd_nama, modul_tag):
        if not self._pastikan_data_siap():
            return

        oid = f"O-ADD-{self.counter_id_baru:04d}"
        self.counter_id_baru += 1
        pesanan = Pesanan(oid, nama, "kafe-teknik", "mie-goreng-spesial", 20000, prioritas, int(time.time()), None, "ANTRE")

        struktur = self.arr_pesanan if tipe_str == "array" else self.ll_pesanan

        if prioritas == 1:
            _, durasi, metrik = struktur.tambah_vip(pesanan)
            posisi_str = "Indeks 0 (Paling Depan)"
        elif prioritas == 2:
            _, durasi, metrik = struktur.tambah_prioritas(pesanan)
            posisi_str = f"Indeks {struktur.panjang() // 2} (Tengah)"
        else:
            _, durasi, metrik = struktur.tambah_reguler(pesanan)
            posisi_str = f"Indeks {struktur.panjang() - 1} (Paling Belakang)"

        self.catat_command(cmd_nama, modul_tag, durasi)

        label_metrik = "Jumlah geseran" if tipe_str == "array" else "Langkah telusur"
        self._tampilkan_hasil(
            f"=== TAMBAH PESANAN ({tipe_str.upper()}) ===\n"
            f"Tipe Prioritas : {prioritas} ({'VIP' if prioritas == 1 else ('PRIORITAS' if prioritas == 2 else 'REGULER')})\n"
            f"Posisi Sisip   : {posisi_str}\n"
            f"Total Elemen   : {struktur.panjang():,} pesanan\n"
            f"Waktu          : {durasi * 1000:.4f} ms ({durasi:.6f} s)\n"
            f"{label_metrik:<15}: {metrik:,}\n\n"
            f"Detail Pesanan :\n{pesanan.ringkasan()}\n"
        )

    # =========================================================================
    # FORM M1: HAPUS PESANAN
    # =========================================================================

    def _setup_view_hapus(self, tipe_str):
        if tipe_str == "array":
            self.lbl_judul_aksi.config(text="Array: hapus pesanan ke-i")
            self.lbl_subjudul_aksi.config(text="hapus: menghapus pesanan pada indeks i dan menggeser sisa ke kiri.")
            cmd_nama = "array_hapus"
            modul_tag = "M1 - array"
        else:
            self.lbl_judul_aksi.config(text="LinkList: hapus pesanan ke-i")
            self.lbl_subjudul_aksi.config(text="hapus: menelusuri simpul ke-i lalu menghubungkan ulang pointer (O(n)).")
            cmd_nama = "ll_hapus"
            modul_tag = "M1 - linklist"

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text="Indeks pesanan yang akan dihapus", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_idx = tk.Entry(sub_f, width=16, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_idx.insert(0, "0")
        ent_idx.pack(side=tk.LEFT, padx=(0, 16))

        btn = tk.Button(
            sub_f,
            text="HAPUS",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_hapus(tipe_str, ent_idx.get(), cmd_nama, modul_tag)
        )
        btn.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text="indeks pesanan yang ingin dihapus (0 sampai n-1)", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_hapus(self, tipe_str, str_idx, cmd_nama, modul_tag):
        if not self._pastikan_data_siap():
            return
        try:
            idx = int(str_idx)
        except ValueError:
            messagebox.showerror("Galat", "Indeks harus berupa bilangan bulat.")
            return

        struktur = self.arr_pesanan if tipe_str == "array" else self.ll_pesanan
        terhapus, durasi, metrik = struktur.hapus_dengan_metrik(idx)
        self.catat_command(cmd_nama, modul_tag, durasi)

        if terhapus is None:
            self._tampilkan_hasil(f"[GALAT] Gagal menghapus. Indeks {idx} tidak valid (Total elemen: {struktur.panjang():,}).")
            return

        label_metrik = "Jumlah geseran" if tipe_str == "array" else "Langkah telusur"
        self._tampilkan_hasil(
            f"=== HAPUS PESANAN ({tipe_str.upper()}) ===\n"
            f"Indeks Terhapus: {idx}\n"
            f"Sisa Elemen    : {struktur.panjang():,} pesanan\n"
            f"Waktu          : {durasi * 1000:.4f} ms ({durasi:.6f} s)\n"
            f"{label_metrik:<15}: {metrik:,}\n\n"
            f"Pesanan Dihapus:\n{terhapus.ringkasan()}\n"
        )

    # =========================================================================
    # FORM M2: ANTREAN (FIFO, LAYANI, UNDO, REDO, POSTFIX)
    # =========================================================================

    def _setup_view_isi_fifo(self):
        self.lbl_judul_aksi.config(text="Antrean: isi pesanan berstatus ANTRE ke antrean FIFO")
        self.lbl_subjudul_aksi.config(text="enqueue: memasukkan pesanan ke kedua antrean (Naif & Circular).")

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text="Nama pelanggan untuk pesanan baru", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_nama = tk.Entry(sub_f, width=28, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_nama.insert(0, f"Customer FIFO {self.counter_id_baru}")
        ent_nama.pack(side=tk.LEFT, padx=(0, 16))

        btn = tk.Button(
            sub_f,
            text="ENQUEUE",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=18,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_enqueue_fifo(ent_nama.get())
        )
        btn.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text="pesanan baru berstatus ANTRE akan dimasukkan ke antrean", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_enqueue_fifo(self, nama):
        oid = f"O-FIFO-{self.counter_id_baru:04d}"
        self.counter_id_baru += 1
        pesanan = Pesanan(oid, nama, "kedai-kopi", "roti-bakar", 12000, 3, int(time.time()), None, "ANTRE")

        _, durasi = self.layanan_antrean.enqueue(pesanan)
        self.catat_command("fifo_enqueue", "M2 - antrean", durasi)

        stats = self.layanan_antrean.stats()
        self._tampilkan_hasil(
            f"=== ENQUEUE PESANAN KE ANTREAN FIFO ===\n"
            f"Waktu Eksekusi           : {durasi * 1000:.4f} ms\n"
            f"Panjang Antrean Naif     : {stats.queue_len_naif:,}\n"
            f"Panjang Antrean Circular : {stats.queue_len_circular:,}\n"
            f"Kedalaman Tumpukan Undo  : {stats.undo_depth}\n"
            f"Kedalaman Tumpukan Redo  : {stats.redo_depth} (dikosongkan otomatis)\n\n"
            f"Detail Pesanan Masuk:\n{pesanan.ringkasan()}\n"
        )

    def _setup_view_layani(self):
        self.lbl_judul_aksi.config(text="Antrean: layani pesanan berikutnya (Dequeue)")
        self.lbl_subjudul_aksi.config(text="dequeue: melayani pesanan dari antrean depan (bandingkan Naif vs Circular).")

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text="Jumlah pesanan yang dilayani", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_n = tk.Entry(sub_f, width=12, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_n.insert(0, "1")
        ent_n.pack(side=tk.LEFT, padx=(0, 12))

        btn_circ = tk.Button(
            sub_f,
            text="LAYANI (CIRCULAR O(1))",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_layani(ent_n.get(), mode="circular")
        )
        btn_circ.pack(side=tk.LEFT, padx=(0, 8))

        btn_naif = tk.Button(
            sub_f,
            text="LAYANI (NAIF O(N))",
            bg="#4b5563",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_layani(ent_n.get(), mode="naif")
        )
        btn_naif.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text="masukkan jumlah pesanan untuk membandingkan efisiensi pergeseran", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_layani(self, str_n, mode):
        try:
            n = int(str_n)
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Galat", "Jumlah pesanan harus berupa bilangan bulat positif.")
            return

        if self.layanan_antrean.antrean_circular.is_empty():
            messagebox.showwarning("Peringatan", "Antrean kosong. Tidak ada pesanan untuk dilayani.")
            return

        if mode == "circular":
            daftar_keluar, durasi, geseran = self.layanan_antrean.dequeue_circular(n)
            cmd_nama = "dequeue_circular"
        else:
            daftar_keluar, durasi, geseran = self.layanan_antrean.dequeue_naif(n)
            cmd_nama = "dequeue_naif"

        self.catat_command(cmd_nama, "M2 - antrean", durasi)
        stats = self.layanan_antrean.stats()

        hasil_teks = (
            f"=== LAYANI PESANAN ({mode.upper()}) ===\n"
            f"Jumlah Dilayani          : {daftar_keluar.panjang():,} pesanan\n"
            f"Waktu Eksekusi           : {durasi * 1000:.4f} ms ({durasi:.6f} s)\n"
            f"Elemen Digeser Saat Ini  : {geseran:,}\n"
            f"Total Geseran Kum. Naif  : {stats.total_geseran_naif:,}\n"
            f"Total Geseran Circular   : {stats.total_geseran_circular:,}\n"
            f"Sisa Antrean             : {stats.queue_len_circular:,}\n"
            f"Kedalaman Undo           : {stats.undo_depth}\n\n"
            f"Daftar Pesanan yang Dilayani:\n"
        )

        limit = min(8, daftar_keluar.panjang())
        for i in range(limit):
            p = daftar_keluar.get(i)
            hasil_teks += f"  [{i+1}] {p.oid} | {p.pelanggan:<20} | {p.menu:<16} | Rp {p.harga:,}\n"
        if daftar_keluar.panjang() > limit:
            hasil_teks += f"  ... dan {daftar_keluar.panjang() - limit} pesanan lainnya.\n"

        self._tampilkan_hasil(hasil_teks)

    def _setup_view_undo_redo(self, mode):
        if mode == "undo":
            self.lbl_judul_aksi.config(text="Tumpukan: Undo aksi antrean terakhir")
            self.lbl_subjudul_aksi.config(text="undo: membatalkan aksi enqueue (buang belakang) atau dequeue (kembalikan ke depan).")
            btn_text = "UNDO"
        else:
            self.lbl_judul_aksi.config(text="Tumpukan: Redo aksi yang baru dibatalkan")
            self.lbl_subjudul_aksi.config(text="redo: mengulang kembali aksi yang baru dibatalkan.")
            btn_text = "REDO"

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text=f"Tindakan {btn_text}", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        btn = tk.Button(
            sub_f,
            text=btn_text,
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_undo_redo(mode)
        )
        btn.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text=f"klik untuk menjalankan operasi {btn_text.lower()} pada tumpukan LIFO", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_undo_redo(self, mode):
        if mode == "undo":
            sukses, pesan, durasi = self.layanan_antrean.undo_last()
            cmd_nama = "undo_last"
        else:
            sukses, pesan, durasi = self.layanan_antrean.redo_last()
            cmd_nama = "redo_last"

        self.catat_command(cmd_nama, "M2 - stack", durasi)
        stats = self.layanan_antrean.stats()

        self._tampilkan_hasil(
            f"=== OPERASI {mode.upper()} ===\n"
            f"Status                   : {'BERHASIL' if sukses else 'GAGAL / KOSONG'}\n"
            f"Keterangan               : {pesan}\n"
            f"Waktu Operasi            : {durasi * 1000:.4f} ms\n"
            f"Panjang Antrean Terkini  : {stats.queue_len_circular:,}\n"
            f"Kedalaman Tumpukan Undo  : {stats.undo_depth}\n"
            f"Kedalaman Tumpukan Redo  : {stats.redo_depth}\n"
        )

    def _setup_view_postfix(self):
        self.lbl_judul_aksi.config(text="Kasir: evaluasi ekspresi harga kasir (Infix -> Postfix)")
        self.lbl_subjudul_aksi.config(text="postfix: menghitung total harga pesanan menggunakan tumpukan operator dan angka.")

        f = tk.Frame(self.frame_form_dinamis, bg="#ffffff")
        f.pack(fill=tk.X, pady=2)

        lbl = tk.Label(f, text="Ekspresi kasir (infix)", bg="#ffffff", font=("Segoe UI", 9, "bold"))
        lbl.pack(anchor="w")

        sub_f = tk.Frame(f, bg="#ffffff")
        sub_f.pack(fill=tk.X, pady=(2, 0))

        ent_exp = tk.Entry(sub_f, width=42, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_exp.insert(0, "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        ent_exp.pack(side=tk.LEFT, padx=(0, 16))

        btn = tk.Button(
            sub_f,
            text="HITUNG",
            bg=self.COLOR_PRIMARY_BTN,
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=lambda: self._aksi_hitung_kasir(ent_exp.get())
        )
        btn.pack(side=tk.LEFT)

        lbl_hint = tk.Label(f, text="contoh: ( 3 * 12000 ) + ( 2 * 8500 ) - 5000", bg="#ffffff", fg=self.COLOR_TEXT_MUTED, font=("Segoe UI", 8))
        lbl_hint.pack(anchor="w")

    def _aksi_hitung_kasir(self, ekspresi):
        if not ekspresi.strip():
            messagebox.showerror("Galat", "Ekspresi kasir tidak boleh kosong.")
            return

        t_awal = time.perf_counter()
        try:
            str_postfix, total_int, str_rp, tabel_langkah = proses_kasir(ekspresi)
        except Exception as e:
            durasi = time.perf_counter() - t_awal
            self.catat_command("postfix_galat", "M2 - stack", durasi)
            self._tampilkan_hasil(f"[GALAT EVALUASI KASIR]\n{str(e)}")
            return

        durasi = time.perf_counter() - t_awal
        self.catat_command("postfix_kasir", "M2 - stack", durasi)

        hasil_teks = (
            f"Ekspresi Infix : {ekspresi}\n"
            f"Bentuk Postfix : {str_postfix}\n"
            f"Waktu Evaluasi : {durasi * 1000:.4f} ms\n"
            f"--------------------------------------------------------------------------------------------------\n"
            f"{'Langkah':<8} | {'Token':<8} | {'Tindakan':<46} | {'Stack':<16} | {'Output':<16}\n"
            f"--------------------------------------------------------------------------------------------------\n"
        )

        for i in range(tabel_langkah.panjang()):
            step = tabel_langkah.get(i)
            hasil_teks += f"{step.langkah:<8} | {step.token:<8} | {step.tindakan:<46} | {step.stack_str:<16} | {step.output_str:<16}\n"

        hasil_teks += (
            f"--------------------------------------------------------------------------------------------------\n"
            f"TOTAL : {str_rp}\n"
            f"--------------------------------------------------------------------------------------------------\n"
        )
        self._tampilkan_hasil(hasil_teks)


def main():
    root = tk.Tk()
    app = AppUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
