"""
backend/m2_antrean.py
Milestone 2: Stack (Tumpukan), Mesin Kasir Postfix, Antrean Naif vs Melingkar, dan Undo/Redo.

Aturan Keras:
- Dilarang dict, set, sorted, .sort(), heapq, bisect, collections, literal {}
- List primitif hanya dipakai sebagai array berkapasitas tetap [None] * kapasitas
- Tanpa list.append, list.insert, list.pop, list.remove, list.extend, slicing geser
- Tumpukan dibangun di atas Array milik M1
- Antrean Naif & Melingkar mengelola buffer sendiri tanpa method tersembunyi
"""

import time
from backend.m1_pesanan import Array, Pesanan


class Tumpukan:
    """
    Struktur Data Tumpukan (LIFO / Stack) dibangun di atas Dynamic Array M1.
    Operasi: push, pop, peek, kosong, panjang.
    """
    def __init__(self, kapasitas_awal=8):
        self._arr = Array(kapasitas_awal=kapasitas_awal)

    # O(1) amortized: masukkan elemen ke puncak tumpukan
    def push(self, x):
        self._arr.append(x)

    # O(1): ambil dan buang elemen di puncak tumpukan
    def pop(self):
        if self._arr.ukuran == 0:
            return None
        return self._arr.pop_belakang()

    # O(1): intip elemen di puncak tanpa membuang
    def peek(self):
        if self._arr.ukuran == 0:
            return None
        return self._arr.get(self._arr.ukuran - 1)

    # O(1): periksa apakah tumpukan kosong
    def kosong(self):
        return self._arr.ukuran == 0

    # O(1): kembalikan jumlah elemen dalam tumpukan
    def panjang(self):
        return self._arr.ukuran

    def to_string(self):
        """Format string isi tumpukan dari dasar ke puncak."""
        if self._arr.ukuran == 0:
            return "[]"
        hasil = "["
        for i in range(self._arr.ukuran):
            if i > 0:
                hasil += ", "
            hasil += str(self._arr.get(i))
        hasil += "]"
        return hasil


# --- 2B: KASIR POSTFIX (INFIX -> POSTFIX -> EVALUASI) ---

class LangkahProses:
    """
    Menyimpan catatan satu baris langkah konversi atau evaluasi postfix
    untuk ditampilkan pada tabel log UI.
    """
    __slots__ = ('langkah', 'token', 'tindakan', 'stack_str', 'output_str')

    def __init__(self, langkah, token, tindakan, stack_str, output_str):
        self.langkah = str(langkah)
        self.token = str(token)
        self.tindakan = str(tindakan)
        self.stack_str = str(stack_str)
        self.output_str = str(output_str)

    def __repr__(self):
        return f"{self.langkah:<6} | {self.token:<8} | {self.tindakan:<45} | {self.stack_str:<25} | {self.output_str}"


def prioritas_operator(op):
    """Mengembalikan tingkat prioritas operator matematika (tanpa dict)."""
    if op == '+' or op == '-':
        return 1
    elif op == '*' or op == '/':
        return 2
    return 0


def tokenize_ekspresi(ekspresi):
    """
    Tokenizer matematika kasir:
    Memisahkan angka multi-digit, operator (+, -, *, /), dan tanda kurung.
    Abaikan spasi. Mengembalikan Array token.
    """
    tokens = Array(kapasitas_awal=16)
    n = len(ekspresi)
    i = 0
    while i < n:
        c = ekspresi[i]
        if c.isspace():
            i += 1
            continue

        if c.isdigit():
            j = i
            while j < n and ekspresi[j].isdigit():
                j += 1
            tokens.append(ekspresi[i:j])
            i = j
        elif c == '+' or c == '-' or c == '*' or c == '/' or c == '(' or c == ')':
            tokens.append(c)
            i += 1
        else:
            # Karakter tidak dikenal dilewati atau dianggap galat
            i += 1
    return tokens


def format_array_ke_string(arr):
    """Menggabungkan elemen Array token menjadi string dengan spasi pemisah."""
    hasil = ""
    for i in range(arr.ukuran):
        if i > 0:
            hasil += " "
        hasil += str(arr.get(i))
    return hasil


def ke_postfix(ekspresi):
    """
    Mengonversi ekspresi infix ke postfix menggunakan tumpukan operator.
    Mengembalikan tuple: (array_postfix_tokens, string_postfix, array_tabel_langkah)
    """
    tokens = tokenize_ekspresi(ekspresi)
    output_tokens = Array(kapasitas_awal=tokens.ukuran)
    stack_op = Tumpukan(kapasitas_awal=8)
    tabel_langkah = Array(kapasitas_awal=32)

    nomor_langkah = 1

    for idx in range(tokens.ukuran):
        tok = tokens.get(idx)
        langkah_id = f"1.{nomor_langkah}"
        nomor_langkah += 1

        if tok.isdigit():
            # Angka langsung ke keluaran
            output_tokens.append(tok)
            tindakan = f"Angka {tok} -> langsung ke keluaran"
            tabel_langkah.append(
                LangkahProses(langkah_id, tok, tindakan, stack_op.to_string(), format_array_ke_string(output_tokens))
            )
        elif tok == '(':
            # Kurung buka -> push ke stack
            stack_op.push(tok)
            tindakan = "Kurung buka '(' -> push ke stack operator"
            tabel_langkah.append(
                LangkahProses(langkah_id, tok, tindakan, stack_op.to_string(), format_array_ke_string(output_tokens))
            )
        elif tok == ')':
            # Kurung tutup -> pop sampai '('
            tindakan_detail = "Kurung tutup ')' -> pop operator hingga '('"
            ketemu_buka = False
            while not stack_op.kosong():
                top = stack_op.pop()
                if top == '(':
                    ketemu_buka = True
                    break
                else:
                    output_tokens.append(top)

            if not ketemu_buka:
                raise ValueError("Galat: Tanda kurung tutup ')' tidak memiliki kurung buka yang sesuai")

            tabel_langkah.append(
                LangkahProses(langkah_id, tok, tindakan_detail, stack_op.to_string(), format_array_ke_string(output_tokens))
            )
        elif tok == '+' or tok == '-' or tok == '*' or tok == '/':
            # Operator: pop operator yang lebih kuat atau sama kuat
            prio_tok = prioritas_operator(tok)
            while not stack_op.kosong():
                top = stack_op.peek()
                if top == '(' or prioritas_operator(top) < prio_tok:
                    break
                op_keluar = stack_op.pop()
                output_tokens.append(op_keluar)

            stack_op.push(tok)
            tindakan = f"Operator '{tok}' -> pop operator >= kuat, lalu push"
            tabel_langkah.append(
                LangkahProses(langkah_id, tok, tindakan, stack_op.to_string(), format_array_ke_string(output_tokens))
            )

    # Pop seluruh sisa stack operator
    while not stack_op.kosong():
        top = stack_op.pop()
        if top == '(' or top == ')':
            raise ValueError("Galat: Tanda kurung buka '(' tidak memiliki pasangan tutup")
        output_tokens.append(top)
        langkah_id = f"1.{nomor_langkah}"
        nomor_langkah += 1
        tabel_langkah.append(
            LangkahProses(langkah_id, top, f"Pop sisa operator '{top}' ke keluaran", stack_op.to_string(), format_array_ke_string(output_tokens))
        )

    str_postfix = format_array_ke_string(output_tokens)
    return (output_tokens, str_postfix, tabel_langkah)


def hitung(postfix_tokens_atau_str, tabel_langkah_awal=None):
    """
    Mengevaluasi ekspresi postfix menggunakan stack angka.
    Kritis: urutan pop b = pop() dulu, lalu a = pop(), hitung a op b.
    Mengembalikan tuple: (total_nilai, format_rupiah, array_tabel_langkah)
    """
    if isinstance(postfix_tokens_atau_str, str):
        tokens = tokenize_ekspresi(postfix_tokens_atau_str)
    else:
        tokens = postfix_tokens_atau_str

    if tabel_langkah_awal is not None:
        tabel_langkah = tabel_langkah_awal
    else:
        tabel_langkah = Array(kapasitas_awal=32)

    stack_angka = Tumpukan(kapasitas_awal=8)
    nomor_langkah = 1

    for idx in range(tokens.ukuran):
        tok = tokens.get(idx)
        langkah_id = f"2.{nomor_langkah}"
        nomor_langkah += 1

        if tok.isdigit():
            nilai = int(tok)
            stack_angka.push(nilai)
            tindakan = f"Operand {nilai} -> push ke stack angka"
            tabel_langkah.append(
                LangkahProses(langkah_id, tok, tindakan, stack_angka.to_string(), "")
            )
        elif tok == '+' or tok == '-' or tok == '*' or tok == '/':
            if stack_angka.panjang() < 2:
                raise ValueError("Galat: Ekspresi postfix tidak valid (operand tidak mencukupi)")

            # Kritis: b pop pertama, a pop kedua
            b = stack_angka.pop()
            a = stack_angka.pop()

            if tok == '+':
                hasil = a + b
            elif tok == '-':
                hasil = a - b
            elif tok == '*':
                hasil = a * b
            elif tok == '/':
                if b == 0:
                    raise ZeroDivisionError("Galat: Pembagian dengan nol tidak diizinkan")
                hasil = a // b  # Pembagian bulat untuk satuan rupiah / acuan pengujian

            stack_angka.push(hasil)
            tindakan = f"Pop {b} dan {a} -> hitung {a} {tok} {b} = {hasil} -> push"
            tabel_langkah.append(
                LangkahProses(langkah_id, tok, tindakan, stack_angka.to_string(), f"Hasil sementara: {hasil}")
            )

    if stack_angka.panjang() != 1:
        raise ValueError("Galat: Ekspresi tidak valid (terlalu banyak operand tersisa)")

    total = stack_angka.pop()
    langkah_id = f"2.{nomor_langkah}"
    tindakan = f"Hasil akhir kasir: Rp {total:,}"
    format_rp = f"Rp {total:,}".replace(",", ".")
    tabel_langkah.append(
        LangkahProses(langkah_id, "TOTAL", tindakan, f"[{total}]", format_rp)
    )

    return (total, format_rp, tabel_langkah)


def proses_kasir(ekspresi):
    """
    Pintu masuk lengkap untuk mesin kasir:
    Infix -> Postfix -> Evaluasi Total.
    Mengembalikan tuple: (str_postfix, total_int, str_rupiah, tabel_langkah)
    """
    postfix_tokens, str_postfix, tabel_langkah = ke_postfix(ekspresi)
    total, str_rp, tabel_langkah_lengkap = hitung(postfix_tokens, tabel_langkah)
    return (str_postfix, total, str_rp, tabel_langkah_lengkap)


# --- 2C: ANTREAN (NAIF VS MELINGKAR) ---

class AntreanNaif:
    """
    Antrean Naif dibangun di atas buffer array primitif.
    - Enqueue di belakang: O(1) amortized.
    - Dequeue di depan: O(n) menggeser seluruh elemen tersisa ke kiri dengan perulangan eksplisit.
    Mencatat jumlah total geseran elemen.
    """
    def __init__(self, kapasitas_awal=256):
        if kapasitas_awal < 4:
            kapasitas_awal = 4
        self.kapasitas = kapasitas_awal
        self.ukuran = 0
        self.data = [None] * self.kapasitas
        self.total_geseran = 0
        self.geseran_terakhir = 0
        self.waktu_operasi = 0.0

    # O(1): baca ukuran antrean
    def panjang(self):
        return self.ukuran

    # O(1): periksa apakah antrean kosong
    def is_empty(self):
        return self.ukuran == 0

    # O(n): pertumbuhan kapasitas 2x bila penuh
    def _tumbuh(self):
        kapasitas_baru = self.kapasitas * 2
        buffer_baru = [None] * kapasitas_baru
        for i in range(self.ukuran):
            buffer_baru[i] = self.data[i]
        self.data = buffer_baru
        self.kapasitas = kapasitas_baru

    # O(1) amortized: enqueue di paling belakang
    def enqueue(self, x):
        t_awal = time.perf_counter()
        if self.ukuran == self.kapasitas:
            self._tumbuh()
        self.data[self.ukuran] = x
        self.ukuran += 1
        self.geseran_terakhir = 0
        self.waktu_operasi = time.perf_counter() - t_awal

    # O(n): dequeue satu elemen dari depan (indeks 0) dan geser seluruh sisa ke kiri
    def dequeue_satu(self):
        if self.ukuran == 0:
            self.geseran_terakhir = 0
            self.waktu_operasi = 0.0
            return None

        t_awal = time.perf_counter()
        x = self.data[0]
        jumlah_geser = self.ukuran - 1

        for j in range(self.ukuran - 1):
            self.data[j] = self.data[j + 1]

        self.data[self.ukuran - 1] = None
        self.ukuran -= 1
        self.geseran_terakhir = jumlah_geser
        self.total_geseran += jumlah_geser
        self.waktu_operasi = time.perf_counter() - t_awal
        return x

    # O(n * k): dequeue k elemen secara berurutan
    def dequeue(self, n=None):
        if self.is_empty():
            return None
        if n is None:
            return self.dequeue_satu()

        t_awal = time.perf_counter()
        keluar = Array(kapasitas_awal=n if n > 0 else 4)
        geser_batch = 0
        limit = n if n <= self.ukuran else self.ukuran

        for _ in range(limit):
            item = self.data[0]
            keluar.append(item)
            jumlah_geser = self.ukuran - 1
            for j in range(self.ukuran - 1):
                self.data[j] = self.data[j + 1]
            self.data[self.ukuran - 1] = None
            self.ukuran -= 1
            geser_batch += jumlah_geser

        self.geseran_terakhir = geser_batch
        self.total_geseran += geser_batch
        self.waktu_operasi = time.perf_counter() - t_awal
        return (keluar, geser_batch)

    # O(1): buang dari belakang (untuk undo aksi ENQUEUE)
    def pop_belakang(self):
        if self.ukuran == 0:
            return None
        self.ukuran -= 1
        val = self.data[self.ukuran]
        self.data[self.ukuran] = None
        return val

    # O(n): kembalikan daftar elemen ke depan (untuk undo aksi DEQUEUE)
    def kembalikan_ke_depan(self, daftar):
        k = daftar.panjang()
        if k == 0:
            return
        while self.ukuran + k > self.kapasitas:
            self._tumbuh()

        # Geser elemen lama ke kanan sejauh k posisi
        for j in range(self.ukuran - 1, -1, -1):
            self.data[j + k] = self.data[j]

        # Salin daftar pesanan ke petak depan 0 .. k-1
        for i in range(k):
            self.data[i] = daftar.get(i)

        self.ukuran += k


class AntreanMelingkar:
    """
    Antrean Melingkar (Circular Queue) berbasis buffer tetap dengan penunjuk front, rear, dan count.
    - enqueue: data[rear] = x; rear = (rear+1) % K; count += 1 (O(1))
    - dequeue: x = data[front]; front = (front+1) % K; count -= 1 (O(1))
    - is_empty: count == 0
    - Bila penuh: tumbuh 2x, salin mulai dari front, reset front = 0
    """
    def __init__(self, kapasitas=4):
        if kapasitas < 4:
            kapasitas = 4
        self.kapasitas = kapasitas
        self.data = [None] * self.kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geseran = 0
        self.geseran_terakhir = 0
        self.geseran_grow = 0
        self.waktu_operasi = 0.0

    # O(1): baca jumlah elemen
    def panjang(self):
        return self.count

    # O(1): periksa antrean kosong (menggunakan pencacah count)
    def is_empty(self):
        return self.count == 0

    # O(1): periksa apakah antrean penuh
    def is_full(self):
        return self.count == self.kapasitas

    # O(n): tumbuh 2x saat penuh, susun ulang buffer mulai dari front
    def _tumbuh(self):
        kapasitas_baru = self.kapasitas * 2
        buffer_baru = [None] * kapasitas_baru
        for i in range(self.count):
            idx_lama = (self.front + i) % self.kapasitas
            buffer_baru[i] = self.data[idx_lama]
        self.data = buffer_baru
        self.front = 0
        self.rear = self.count
        self.geseran_grow += self.count
        self.kapasitas = kapasitas_baru

    # O(1) amortized: enqueue di rear secara melingkar
    def enqueue(self, x):
        t_awal = time.perf_counter()
        if self.is_full():
            self._tumbuh()

        self.data[self.rear] = x
        self.rear = (self.rear + 1) % self.kapasitas
        self.count += 1
        self.geseran_terakhir = 0
        self.waktu_operasi = time.perf_counter() - t_awal

    # O(1): dequeue satu elemen dari front secara melingkar
    def dequeue_satu(self):
        if self.is_empty():
            self.geseran_terakhir = 0
            self.waktu_operasi = 0.0
            return None

        t_awal = time.perf_counter()
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % self.kapasitas
        self.count -= 1
        self.geseran_terakhir = 0
        self.waktu_operasi = time.perf_counter() - t_awal
        return x

    # O(k): dequeue k elemen secara berurutan
    def dequeue(self, n=None):
        if self.is_empty():
            return None
        if n is None:
            return self.dequeue_satu()

        t_awal = time.perf_counter()
        keluar = Array(kapasitas_awal=n if n > 0 else 4)
        limit = n if n <= self.count else self.count

        for _ in range(limit):
            item = self.dequeue_satu()
            keluar.append(item)

        self.geseran_terakhir = 0
        self.waktu_operasi = time.perf_counter() - t_awal
        return (keluar, 0)

    # O(1): buang dari belakang (rear) untuk undo aksi ENQUEUE
    def pop_belakang(self):
        if self.is_empty():
            return None
        self.rear = (self.rear - 1) % self.kapasitas
        val = self.data[self.rear]
        self.data[self.rear] = None
        self.count -= 1
        return val

    # O(1): masukkan ke depan (front) untuk undo aksi DEQUEUE
    def tambah_depan(self, x):
        if self.is_full():
            self._tumbuh()
        self.front = (self.front - 1) % self.kapasitas
        self.data[self.front] = x
        self.count += 1

    # O(k): kembalikan daftar elemen ke depan dalam urutan semula
    def kembalikan_ke_depan(self, daftar):
        k = daftar.panjang()
        # Sisip mundur dari k-1 ke 0 agar urutan front tetap persis sama
        for i in range(k - 1, -1, -1):
            self.tambah_depan(daftar.get(i))


# --- 2D: UNDO / REDO & LAYANAN ANTREAN TERPADU ---

class CatatanAksi:
    """
    Menyimpan catatan riwayat aksi pada antrean beserta data pembaliknya.
    - 'ENQUEUE': data berupa objek Pesanan (dikeluarkan dari belakang saat undo).
    - 'DEQUEUE': data berupa Array daftar pesanan (dikembalikan ke depan saat undo).
    """
    __slots__ = ('jenis', 'data', 'keterangan')

    def __init__(self, jenis, data, keterangan=""):
        self.jenis = jenis
        self.data = data
        self.keterangan = keterangan


class StatistikAntrean:
    """
    Objek ringkasan statistik antrean (bebas dictionary).
    """
    __slots__ = (
        'queue_len_naif', 'queue_len_circular',
        'queue_capacity_naif', 'queue_capacity_circular',
        'total_geseran_naif', 'total_geseran_circular',
        'undo_depth', 'redo_depth'
    )

    def __init__(self, ql_naif, ql_circ, cap_naif, cap_circ, geser_naif, geser_circ, undo_d, redo_d):
        self.queue_len_naif = ql_naif
        self.queue_len_circular = ql_circ
        self.queue_capacity_naif = cap_naif
        self.queue_capacity_circular = cap_circ
        self.total_geseran_naif = geser_naif
        self.total_geseran_circular = geser_circ
        self.undo_depth = undo_d
        self.redo_depth = redo_d

    def __repr__(self):
        return (
            f"StatistikAntrean(len=[naif:{self.queue_len_naif}, circ:{self.queue_len_circular}], "
            f"cap=[naif:{self.queue_capacity_naif}, circ:{self.queue_capacity_circular}], "
            f"geseran=[naif:{self.total_geseran_naif:,}, circ:{self.total_geseran_circular:,}], "
            f"undo_depth={self.undo_depth}, redo_depth={self.redo_depth})"
        )


class LayananAntrean:
    """
    Manajer terpadu yang memelihara AntreanNaif dan AntreanMelingkar
    secara tersinkronisasi, lengkap dengan tumpukan Undo dan Redo.
    """
    def __init__(self, kapasitas_awal=256):
        self.antrean_naif = AntreanNaif(kapasitas_awal=kapasitas_awal)
        self.antrean_circular = AntreanMelingkar(kapasitas=kapasitas_awal)
        self.tumpukan_undo = Tumpukan(kapasitas_awal=16)
        self.tumpukan_redo = Tumpukan(kapasitas_awal=16)
        self.riwayat_teks = Array(kapasitas_awal=32)

    def _kosongkan_redo(self):
        """Aksi baru apa pun wajib mengosongkan tumpukan redo."""
        while not self.tumpukan_redo.kosong():
            self.tumpukan_redo.pop()

    def _catat_riwayat(self, pesan):
        self.riwayat_teks.append(pesan)

    def muat_dari_array(self, arr_pesanan):
        """Mengisi kedua antrean secara identik dari pesanan berstatus ANTRE."""
        total = arr_pesanan.panjang()
        dimuat = 0
        for i in range(total):
            p = arr_pesanan.get(i)
            if p is not None and p.status == "ANTRE":
                self.antrean_naif.enqueue(p)
                self.antrean_circular.enqueue(p)
                dimuat += 1
        return dimuat

    def enqueue(self, pesanan):
        """Memasukkan pesanan ke kedua antrean sekaligus, mencatat ke undo, dan mengosongkan redo."""
        t_awal = time.perf_counter()
        self.antrean_naif.enqueue(pesanan)
        self.antrean_circular.enqueue(pesanan)
        durasi = time.perf_counter() - t_awal

        aksi = CatatanAksi('ENQUEUE', pesanan, f"ENQUEUE {pesanan.oid} - {pesanan.pelanggan}")
        self.tumpukan_undo.push(aksi)
        self._kosongkan_redo()
        self._catat_riwayat(aksi.keterangan)
        return (pesanan, durasi)

    def dequeue_naif(self, n=1):
        """
        Menjalankan dequeue pada AntreanNaif (mengukur waktu & geseran naif)
        dan menyinkronkan AntreanMelingkar agar isi kedua struktur tetap identik.
        """
        if self.antrean_naif.is_empty():
            return (None, 0.0, 0)

        t_awal = time.perf_counter()
        daftar_keluar, geser = self.antrean_naif.dequeue(n)
        durasi = time.perf_counter() - t_awal

        # Sinkronkan antrean circular
        self.antrean_circular.dequeue(n)

        aksi = CatatanAksi('DEQUEUE', daftar_keluar, f"DEQUEUE NAIF ({daftar_keluar.panjang()} pesanan)")
        self.tumpukan_undo.push(aksi)
        self._kosongkan_redo()
        self._catat_riwayat(aksi.keterangan)
        return (daftar_keluar, durasi, geser)

    def dequeue_circular(self, n=1):
        """
        Menjalankan dequeue pada AntreanMelingkar (mengukur waktu & geseran circular)
        dan menyinkronkan AntreanNaif agar isi kedua struktur tetap identik.
        """
        if self.antrean_circular.is_empty():
            return (None, 0.0, 0)

        t_awal = time.perf_counter()
        daftar_keluar, geser = self.antrean_circular.dequeue(n)
        durasi = time.perf_counter() - t_awal

        # Sinkronkan antrean naif
        self.antrean_naif.dequeue(n)

        aksi = CatatanAksi('DEQUEUE', daftar_keluar, f"DEQUEUE CIRCULAR ({daftar_keluar.panjang()} pesanan)")
        self.tumpukan_undo.push(aksi)
        self._kosongkan_redo()
        self._catat_riwayat(aksi.keterangan)
        return (daftar_keluar, durasi, geser)

    def undo_last(self):
        """Membatalkan aksi terakhir dari tumpukan undo dan memindahkannya ke redo."""
        if self.tumpukan_undo.kosong():
            return (False, "Tumpukan undo kosong. Tidak ada aksi yang dapat dibatalkan.", 0.0)

        t_awal = time.perf_counter()
        aksi = self.tumpukan_undo.pop()

        if aksi.jenis == 'ENQUEUE':
            # Kebalikan: keluarkan lagi oid dari belakang
            self.antrean_naif.pop_belakang()
            self.antrean_circular.pop_belakang()
            pesan = f"UNDO berhasil: Pesanan {aksi.data.oid} dikeluarkan kembali dari belakang antrean."
        elif aksi.jenis == 'DEQUEUE':
            # Kebalikan: kembalikan seluruh daftar pesanan ke depan antrean (urutan semula)
            self.antrean_naif.kembalikan_ke_depan(aksi.data)
            self.antrean_circular.kembalikan_ke_depan(aksi.data)
            pesan = f"UNDO berhasil: {aksi.data.panjang()} pesanan dikembalikan ke depan antrean dalam urutan semula."
        else:
            pesan = "UNDO berhasil."

        self.tumpukan_redo.push(aksi)
        self._catat_riwayat(pesan)
        durasi = time.perf_counter() - t_awal
        return (True, pesan, durasi)

    def redo_last(self):
        """Mengulang aksi yang baru dibatalkan dari tumpukan redo dan memindahkannya ke undo."""
        if self.tumpukan_redo.kosong():
            return (False, "Tumpukan redo kosong. Tidak ada aksi yang dapat diulang.", 0.0)

        t_awal = time.perf_counter()
        aksi = self.tumpukan_redo.pop()

        if aksi.jenis == 'ENQUEUE':
            # Kerjakan aksi aslinya: masukkan lagi ke belakang
            pesanan = aksi.data
            self.antrean_naif.enqueue(pesanan)
            self.antrean_circular.enqueue(pesanan)
            pesan = f"REDO berhasil: Pesanan {pesanan.oid} dimasukkan kembali ke antrean."
        elif aksi.jenis == 'DEQUEUE':
            # Kerjakan aksi aslinya: keluarkan lagi dari depan
            k = aksi.data.panjang()
            self.antrean_naif.dequeue(k)
            self.antrean_circular.dequeue(k)
            pesan = f"REDO berhasil: {k} pesanan dikeluarkan kembali dari depan antrean."
        else:
            pesan = "REDO berhasil."

        self.tumpukan_undo.push(aksi)
        self._catat_riwayat(pesan)
        durasi = time.perf_counter() - t_awal
        return (True, pesan, durasi)

    # 2E: stats()
    def stats(self):
        """
        Mengembalikan statistik antrean:
        queue_len (naif & circular), queue_capacity, total geseran, undo_depth, redo_depth.
        """
        return StatistikAntrean(
            ql_naif=self.antrean_naif.panjang(),
            ql_circ=self.antrean_circular.panjang(),
            cap_naif=self.antrean_naif.kapasitas,
            cap_circ=self.antrean_circular.kapasitas,
            geser_naif=self.antrean_naif.total_geseran,
            geser_circ=self.antrean_circular.total_geseran,
            undo_d=self.tumpukan_undo.panjang(),
            redo_d=self.tumpukan_redo.panjang()
        )

    def history(self):
        """Mengembalikan array riwayat aksi."""
        return self.riwayat_teks
