"""
backend/m1_pesanan.py
Milestone 1: Dynamic Array vs Singly Linked List untuk Manajemen Data Pesanan.

Aturan Keras:
- Dilarang dict, set, sorted, .sort(), heapq, bisect, collections, literal {}
- List primitif hanya dipakai sebagai array berkapasitas tetap [None] * kapasitas
- Tanpa list.append, list.insert, list.pop, list.remove, list.extend, slicing geser
- Semua geseran elemen dan pertumbuhan kapasitas diatur manual dengan perulangan
"""

import time
import csv


class Pesanan:
    """
    Representasi satu entitas pesanan.
    Menggunakan __slots__ untuk efisiensi memori dan menghindari penggunaan dictionary.
    """
    __slots__ = (
        'oid', 'pelanggan', 'resto', 'menu', 'harga',
        'prioritas', 't_masuk_detik', 't_selesai_detik', 'status'
    )

    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk_detik, t_selesai_detik, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = int(harga) if harga is not None and str(harga).strip() != "" else 0
        self.prioritas = int(prioritas) if prioritas is not None and str(prioritas).strip() != "" else 3
        self.t_masuk_detik = int(t_masuk_detik) if t_masuk_detik is not None and str(t_masuk_detik).strip() != "" else 0
        self.t_selesai_detik = int(t_selesai_detik) if t_selesai_detik is not None and str(t_selesai_detik).strip() != "" else None
        self.status = status

    def __repr__(self):
        return f"Pesanan({self.oid}, {self.pelanggan}, {self.menu}, Rp{self.harga:,}, P:{self.prioritas}, {self.status})"

    def ringkasan(self):
        t_selesai_str = str(self.t_selesai_detik) if self.t_selesai_detik is not None else "-"
        prio_label = "VIP" if self.prioritas == 1 else ("Prioritas" if self.prioritas == 2 else "Reguler")
        return (
            f"ID: {self.oid} | Pelanggan: {self.pelanggan} | Resto: {self.resto}\n"
            f"Menu: {self.menu} | Harga: Rp {self.harga:,} | Prioritas: {self.prioritas} ({prio_label})\n"
            f"Masuk: {self.t_masuk_detik}s | Selesai: {t_selesai_str}s | Status: {self.status}"
        )


class Array:
    """
    Dynamic Array buatan sendiri dengan pertumbuhan kapasitas 2x.
    Mengelola buffer berukuran tetap [None] * kapasitas.
    """
    def __init__(self, kapasitas_awal=8):
        # Kapasitas minimum 4
        if kapasitas_awal < 4:
            kapasitas_awal = 4
        self.kapasitas = kapasitas_awal
        self.ukuran = 0
        self.data = [None] * self.kapasitas
        self.geseran = 0
        self.waktu_operasi = 0.0

    # O(1): baca ukuran yang dikelola sendiri
    def panjang(self):
        return self.ukuran

    # O(n): alokasi buffer baru 2x lipat dan salin isi dengan perulangan eksplisit
    def _tumbuh(self):
        kapasitas_baru = self.kapasitas * 2
        buffer_baru = [None] * kapasitas_baru
        for i in range(self.ukuran):
            buffer_baru[i] = self.data[i]
        self.data = buffer_baru
        self.kapasitas = kapasitas_baru

    # O(1) amortized: masukkan ke indeks paling belakang
    def append(self, v):
        if self.ukuran == self.kapasitas:
            self._tumbuh()
        self.data[self.ukuran] = v
        self.ukuran += 1
        self.geseran = 0

    # O(n): geser elemen dari indeks i ke kanan dengan perulangan eksplisit
    def insert(self, i, v):
        if i < 0:
            i = 0
        if i > self.ukuran:
            i = self.ukuran

        if self.ukuran == self.kapasitas:
            self._tumbuh()

        # Geser ke kanan dari indeks paling belakang
        jumlah_geser = self.ukuran - i
        for j in range(self.ukuran, i, -1):
            self.data[j] = self.data[j - 1]

        self.data[i] = v
        self.ukuran += 1
        self.geseran = jumlah_geser

    # O(1): akses langsung berdasarkan indeks
    def get(self, i):
        self.geseran = 0
        if i < 0 or i >= self.ukuran:
            return None
        return self.data[i]

    # O(n): geser elemen setelah indeks i ke kiri dengan perulangan eksplisit
    def hapus(self, i):
        if i < 0 or i >= self.ukuran:
            self.geseran = 0
            self.waktu_operasi = 0.0
            return (None, 0.0, 0)

        t_awal = time.perf_counter()
        terhapus = self.data[i]
        jumlah_geser = self.ukuran - 1 - i

        for j in range(i, self.ukuran - 1):
            self.data[j] = self.data[j + 1]

        self.data[self.ukuran - 1] = None
        self.ukuran -= 1
        self.geseran = jumlah_geser
        self.waktu_operasi = time.perf_counter() - t_awal
        return (terhapus, self.waktu_operasi, self.geseran)

    # O(1): ambil dan buang elemen terakhir (berguna untuk Tumpukan)
    def pop_belakang(self):
        if self.ukuran == 0:
            self.geseran = 0
            return None
        self.ukuran -= 1
        val = self.data[self.ukuran]
        self.data[self.ukuran] = None
        self.geseran = 0
        return val

    # --- 5 Operasi Utama dengan Pengukuran Waktu & Metrik Kerja ---

    # O(1): lihat pesanan ke-i
    def lihat(self, i):
        t_awal = time.perf_counter()
        hasil = self.get(i)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (hasil, self.waktu_operasi, self.geseran)

    # O(1) amortized: tambah REGULER di paling belakang
    def tambah_reguler(self, v):
        t_awal = time.perf_counter()
        self.append(v)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (v, self.waktu_operasi, self.geseran)

    # O(n): tambah PRIORITAS di tengah (indeks n // 2)
    def tambah_prioritas(self, v):
        t_awal = time.perf_counter()
        posisi = self.ukuran // 2
        self.insert(posisi, v)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (v, self.waktu_operasi, self.geseran)

    # O(n): tambah VIP di paling depan (indeks 0)
    def tambah_vip(self, v):
        t_awal = time.perf_counter()
        self.insert(0, v)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (v, self.waktu_operasi, self.geseran)


class Node:
    """
    Simpul untuk Single Linked List.
    """
    __slots__ = ('nilai', 'next')

    def __init__(self, nilai, next=None):
        self.nilai = nilai
        self.next = next


class LinkList:
    """
    Singly Linked List dengan penunjuk head dan tail.
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.ukuran = 0
        self.langkah_telusur = 0
        self.waktu_operasi = 0.0

    # O(1): baca ukuran yang dikelola sendiri
    def panjang(self):
        return self.ukuran

    # O(1): tambah di belakang memakai penunjuk tail
    def append(self, v):
        simpul_baru = Node(v)
        if self.ukuran == 0:
            self.head = simpul_baru
            self.tail = simpul_baru
        else:
            self.tail.next = simpul_baru
            self.tail = simpul_baru
        self.ukuran += 1
        self.langkah_telusur = 0

    # O(1): tambah di depan (head)
    def tambah_depan(self, v):
        simpul_baru = Node(v, self.head)
        self.head = simpul_baru
        if self.tail is None:
            self.tail = simpul_baru
        self.ukuran += 1
        self.langkah_telusur = 0

    # O(n): sisip pada indeks i dengan penelusuran
    def insert(self, i, v):
        if i <= 0:
            self.tambah_depan(v)
            return
        if i >= self.ukuran:
            self.append(v)
            return

        # Telusur sampai indeks i - 1
        curr = self.head
        langkah = 0
        for _ in range(i - 1):
            curr = curr.next
            langkah += 1

        simpul_baru = Node(v, curr.next)
        curr.next = simpul_baru
        self.ukuran += 1
        self.langkah_telusur = langkah + 1

    # O(n): telusur dari head sampai indeks i
    def get(self, i):
        if i < 0 or i >= self.ukuran:
            self.langkah_telusur = 0
            return None

        curr = self.head
        langkah = 0
        for _ in range(i):
            curr = curr.next
            langkah += 1

        self.langkah_telusur = langkah
        return curr.nilai

    # O(n): hapus pada indeks i dengan penelusuran (menjaga head dan tail)
    def hapus(self, i):
        if i < 0 or i >= self.ukuran:
            self.langkah_telusur = 0
            self.waktu_operasi = 0.0
            return (None, 0.0, 0)

        t_awal = time.perf_counter()
        if i == 0:
            terhapus = self.head.nilai
            self.head = self.head.next
            if self.head is None:
                self.tail = None
            self.ukuran -= 1
            self.langkah_telusur = 0
            self.waktu_operasi = time.perf_counter() - t_awal
            return (terhapus, self.waktu_operasi, 0)

        # Telusur sampai sebelum simpul yang dihapus
        curr = self.head
        langkah = 0
        for _ in range(i - 1):
            curr = curr.next
            langkah += 1

        terhapus = curr.next.nilai
        curr.next = curr.next.next
        if curr.next is None:
            # Simpul yang dihapus adalah tail lama
            self.tail = curr

        self.ukuran -= 1
        self.langkah_telusur = langkah + 1
        self.waktu_operasi = time.perf_counter() - t_awal
        return (terhapus, self.waktu_operasi, self.langkah_telusur)

    # --- 5 Operasi Utama dengan Pengukuran Waktu & Metrik Kerja ---

    # O(n): telusur ke simpul indeks i
    def lihat(self, i):
        t_awal = time.perf_counter()
        hasil = self.get(i)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (hasil, self.waktu_operasi, self.langkah_telusur)

    # O(1): tambah REGULER di paling belakang menggunakan tail
    def tambah_reguler(self, v):
        t_awal = time.perf_counter()
        self.append(v)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (v, self.waktu_operasi, self.langkah_telusur)

    # O(n): tambah PRIORITAS di tengah (indeks n // 2) dengan penelusuran
    def tambah_prioritas(self, v):
        t_awal = time.perf_counter()
        posisi = self.ukuran // 2
        self.insert(posisi, v)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (v, self.waktu_operasi, self.langkah_telusur)

    # O(1): tambah VIP di paling depan
    def tambah_vip(self, v):
        t_awal = time.perf_counter()
        self.tambah_depan(v)
        self.waktu_operasi = time.perf_counter() - t_awal
        return (v, self.waktu_operasi, self.langkah_telusur)


def tambah(struktur, pesanan):
    """
    Fungsi pembungkus untuk menambah pesanan ke struktur (Array atau LinkList)
    berdasarkan tingkat prioritasnya:
    - 1 = VIP -> tambah_vip (indeks 0)
    - 2 = Prioritas -> tambah_prioritas (indeks n // 2)
    - 3 = Reguler -> tambah_reguler (paling belakang)
    Mengembalikan tuple: (pesanan, waktu_detik, metrik_kerja)
    """
    if pesanan.prioritas == 1:
        return struktur.tambah_vip(pesanan)
    elif pesanan.prioritas == 2:
        return struktur.tambah_prioritas(pesanan)
    else:
        return struktur.tambah_reguler(pesanan)


def muat_pesanan(path_csv, max_baris=None):
    """
    Membaca berkas CSV dan memuat seluruh data ke dalam objek Array buatan sendiri.
    Mengembalikan tuple: (array_pesanan, waktu_baca_detik)
    """
    arr = Array(kapasitas_awal=256)
    t_awal = time.perf_counter()

    with open(path_csv, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)  # Abaikan header baris pertama
        if header is None:
            return (arr, 0.0)

        baris_terbaca = 0
        for baris in reader:
            if max_baris is not None and baris_terbaca >= max_baris:
                break
            # Parsing kolom tanpa menggunakan dictionary
            # oid, pelanggan, resto, menu, harga, prioritas, t_masuk_detik, t_selesai_detik, status
            if len(baris) >= 9:
                oid = baris[0]
                pelanggan = baris[1]
                resto = baris[2]
                menu = baris[3]
                harga = baris[4]
                prioritas = baris[5]
                t_masuk = baris[6]
                t_selesai = baris[7]
                status = baris[8]

                p = Pesanan(oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status)
                arr.append(p)
                baris_terbaca += 1

    t_total = time.perf_counter() - t_awal
    return (arr, t_total)


def muat_pesanan_ke_dua_struktur(path_csv, max_baris=None):
    """
    Membaca berkas CSV dan memuat data secara simultan ke Array dan LinkList.
    Mengembalikan tuple: (array_pesanan, linklist_pesanan, waktu_detik)
    """
    arr = Array(kapasitas_awal=256)
    ll = LinkList()
    t_awal = time.perf_counter()

    with open(path_csv, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None:
            return (arr, ll, 0.0)

        baris_terbaca = 0
        for baris in reader:
            if max_baris is not None and baris_terbaca >= max_baris:
                break
            if len(baris) >= 9:
                p = Pesanan(
                    baris[0], baris[1], baris[2], baris[3],
                    baris[4], baris[5], baris[6], baris[7], baris[8]
                )
                arr.append(p)
                ll.append(p)
                baris_terbaca += 1

    t_total = time.perf_counter() - t_awal
    return (arr, ll, t_total)
