"""
tests/test_m2.py
Pengujian Unit untuk Milestone 2 (M2):
- Tumpukan (Stack)
- Mesin Kasir Postfix (Infix -> Postfix -> Evaluasi)
- Antrean Naif vs Melingkar (Wrap-around, Kapasitas)
- Undo dan Redo
- Uji Skala Geseran Dequeue (~19.850 elemen)
"""

import unittest
import os
from backend.m1_pesanan import Pesanan, muat_pesanan
from backend.m2_antrean import (
    Tumpukan, ke_postfix, hitung, proses_kasir,
    AntreanNaif, AntreanMelingkar, LayananAntrean
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestM2Antrean(unittest.TestCase):

    def test_tumpukan_dasar(self):
        """Uji dasar operasi stack: push, pop, peek, kosong, panjang."""
        s = Tumpukan()
        self.assertTrue(s.kosong())
        self.assertEqual(s.panjang(), 0)
        self.assertIsNone(s.pop())
        self.assertIsNone(s.peek())

        s.push(10)
        s.push(20)
        s.push(30)
        self.assertFalse(s.kosong())
        self.assertEqual(s.panjang(), 3)
        self.assertEqual(s.peek(), 30)

        self.assertEqual(s.pop(), 30)
        self.assertEqual(s.pop(), 20)
        self.assertEqual(s.panjang(), 1)
        self.assertEqual(s.pop(), 10)
        self.assertTrue(s.kosong())
        self.assertIsNone(s.pop())

    def test_postfix_dan_hitung_ekspresi(self):
        """
        Uji postfix + hitung untuk 4 ekspresi wajib + uji pembagian dan campuran:
        1. Tanpa kurung
        2. Berkurung (contoh wajib Rp 48.000)
        3. '-' beruntun (10 - 3 - 2 = 5)
        4. Kurung bersarang
        5. '/' beruntun (100 / 5 / 2 = 10)
        6. Campuran '-' dan '/'
        """
        # 1. Tanpa kurung: 3 * 10000 + 5000 = 35000
        str_post1, total1, rp1, _ = proses_kasir("3 * 10000 + 5000")
        self.assertEqual(str_post1, "3 10000 * 5000 +")
        self.assertEqual(total1, 35000)

        # 2. Contoh wajib spesifikasi: ( 3 * 12000 ) + ( 2 * 8500 ) - 5000 = 48000
        str_post2, total2, rp2, _ = proses_kasir("( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        self.assertEqual(str_post2, "3 12000 * 2 8500 * + 5000 -")
        self.assertEqual(total2, 48000)
        self.assertIn("48.000", rp2)

        # 3. '-' beruntun: 10 - 3 - 2 = 5
        str_post3, total3, _, _ = proses_kasir("10 - 3 - 2")
        self.assertEqual(str_post3, "10 3 - 2 -")
        self.assertEqual(total3, 5)

        # 4. Kurung bersarang: ( 50 - ( 10 + 5 ) ) * 2 = 70
        str_post4, total4, _, _ = proses_kasir("( 50 - ( 10 + 5 ) ) * 2")
        self.assertEqual(str_post4, "50 10 5 + - 2 *")
        self.assertEqual(total4, 70)

        # 5. '/' beruntun: 100 / 5 / 2 = 10
        str_post5, total5, _, _ = proses_kasir("100 / 5 / 2")
        self.assertEqual(str_post5, "100 5 / 2 /")
        self.assertEqual(total5, 10)

        # 6. Campuran '-' dan '/': 100 - 20 / 2 - 5 = 85
        str_post6, total6, _, _ = proses_kasir("100 - 20 / 2 - 5")
        self.assertEqual(str_post6, "100 20 2 / - 5 -")
        self.assertEqual(total6, 85)

    def test_postfix_kasus_batas_dan_galat(self):
        """Penanganan galat kurung tidak seimbang dan pembagian nol tanpa crash."""
        with self.assertRaises(ValueError):
            ke_postfix("( 3 * 5")

        with self.assertRaises(ValueError):
            ke_postfix("3 * 5 )")

        with self.assertRaises(ZeroDivisionError):
            proses_kasir("100 / 0")

    def test_antrean_melingkar_wrap_around_k4(self):
        """
        UJI TERPENTING: Wrap-around AntreanMelingkar K=4:
        masukkan 3, keluarkan 2, masukkan 3 lagi, pastikan penunjuk berputar dan data tetap benar.
        """
        q = AntreanMelingkar(kapasitas=4)
        self.assertEqual(q.kapasitas, 4)

        # 1. Masukkan 3 elemen (A, B, C)
        q.enqueue("A")
        q.enqueue("B")
        q.enqueue("C")
        self.assertEqual(q.panjang(), 3)
        self.assertEqual(q.front, 0)
        self.assertEqual(q.rear, 3)

        # 2. Keluarkan 2 elemen (A, B)
        keluar1 = q.dequeue_satu()
        keluar2 = q.dequeue_satu()
        self.assertEqual(keluar1, "A")
        self.assertEqual(keluar2, "B")
        self.assertEqual(q.panjang(), 1)
        self.assertEqual(q.front, 2)
        self.assertEqual(q.rear, 3)

        # 3. Masukkan 3 elemen lagi (D, E, F) -> terjadi wrap-around ke indeks 0 dan 1!
        q.enqueue("D")  # rear jadi 0 (3 + 1 % 4)
        self.assertEqual(q.rear, 0)
        q.enqueue("E")  # rear jadi 1 (0 + 1 % 4)
        self.assertEqual(q.rear, 1)
        q.enqueue("F")  # rear jadi 2 (1 + 1 % 4)
        self.assertEqual(q.rear, 2)

        self.assertEqual(q.panjang(), 4)
        self.assertTrue(q.is_full())

        # 4. Verifikasi FIFO: sisa elemen harus keluar berurutan: C, D, E, F
        self.assertEqual(q.dequeue_satu(), "C")
        self.assertEqual(q.dequeue_satu(), "D")
        self.assertEqual(q.dequeue_satu(), "E")
        self.assertEqual(q.dequeue_satu(), "F")
        self.assertTrue(q.is_empty())
        self.assertEqual(q.panjang(), 0)

    def test_antrean_naif_dan_melingkar_keluaran_identik(self):
        """Antrean naif dan circular menghasilkan keluaran identik pada urutan operasi yang sama."""
        q_naif = AntreanNaif(kapasitas_awal=4)
        q_circ = AntreanMelingkar(kapasitas=4)

        for i in range(20):
            p = Pesanan(f"ORD-{i}", f"Cust-{i}", "Resto", "Menu", 15000, 3, 100, None, "ANTRE")
            q_naif.enqueue(p)
            q_circ.enqueue(p)

        self.assertEqual(q_naif.panjang(), 20)
        self.assertEqual(q_circ.panjang(), 20)

        # Dequeue batch 8 pesanan
        out_naif, geser_n = q_naif.dequeue(8)
        out_circ, geser_c = q_circ.dequeue(8)

        self.assertEqual(out_naif.panjang(), 8)
        self.assertEqual(out_circ.panjang(), 8)
        self.assertEqual(geser_c, 0)
        self.assertGreater(geser_n, 0)

        for i in range(8):
            self.assertEqual(out_naif.get(i).oid, out_circ.get(i).oid)
            self.assertEqual(out_naif.get(i).oid, f"ORD-{i}")

        self.assertEqual(q_naif.panjang(), 12)
        self.assertEqual(q_circ.panjang(), 12)

    def test_kasus_batas_antrean(self):
        """Dequeue saat kosong mengembalikan None; enqueue saat penuh tumbuh 2x."""
        q_circ = AntreanMelingkar(kapasitas=4)
        self.assertIsNone(q_circ.dequeue())
        self.assertIsNone(q_circ.dequeue_satu())

        q_naif = AntreanNaif(kapasitas_awal=4)
        self.assertIsNone(q_naif.dequeue())
        self.assertIsNone(q_naif.dequeue_satu())

        # Enqueue melebihi kapasitas awal 4 -> tumbuh ke 8
        for i in range(5):
            q_circ.enqueue(f"X-{i}")
        self.assertEqual(q_circ.kapasitas, 8)
        self.assertEqual(q_circ.panjang(), 5)

        for i in range(5):
            self.assertEqual(q_circ.dequeue_satu(), f"X-{i}")

    def test_undo_redo_konsistensi(self):
        """
        Uji Undo dan Redo:
        1. enqueue -> undo -> redo mengembalikan keadaan identik
        2. dequeue 100 -> undo mengembalikan 100 ke depan dengan urutan semula
        3. aksi baru setelah undo mengosongkan redo
        """
        layanan = LayananAntrean(kapasitas_awal=16)

        # 1. Enqueue 5 pesanan
        for i in range(5):
            p = Pesanan(f"A-{i}", f"User-{i}", "R", "M", 10000, 3, 10, None, "ANTRE")
            layanan.enqueue(p)

        self.assertEqual(layanan.antrean_circular.panjang(), 5)
        self.assertEqual(layanan.antrean_naif.panjang(), 5)

        # Enqueue pesanan ke-6
        p6 = Pesanan("A-5", "User-5", "R", "M", 10000, 3, 10, None, "ANTRE")
        layanan.enqueue(p6)
        self.assertEqual(layanan.antrean_circular.panjang(), 6)

        # Undo enqueue p6 -> panjang kembali 5, p6 terbuang dari belakang
        sukses_undo, _, _ = layanan.undo_last()
        self.assertTrue(sukses_undo)
        self.assertEqual(layanan.antrean_circular.panjang(), 5)
        self.assertEqual(layanan.antrean_naif.panjang(), 5)
        self.assertEqual(layanan.tumpukan_redo.panjang(), 1)

        # Redo enqueue p6 -> panjang kembali 6
        sukses_redo, _, _ = layanan.redo_last()
        self.assertTrue(sukses_redo)
        self.assertEqual(layanan.antrean_circular.panjang(), 6)
        self.assertEqual(layanan.antrean_naif.panjang(), 6)

        # 2. Dequeue 3 pesanan
        keluar, _, _ = layanan.dequeue_circular(3)
        self.assertEqual(keluar.panjang(), 3)
        self.assertEqual(layanan.antrean_circular.panjang(), 3)
        self.assertEqual(layanan.antrean_naif.panjang(), 3)

        # Elemen di depan sekarang harus A-3
        self.assertEqual(layanan.antrean_circular.dequeue_satu().oid, "A-3")
        # Masukkan lagi A-3 sementara agar pengujian undo bersih
        layanan.antrean_circular.tambah_depan(Pesanan("A-3", "User-3", "R", "M", 10000, 3, 10, None, "ANTRE"))

        # Undo dequeue -> 3 pesanan (A-0, A-1, A-2) kembali ke depan dalam urutan semula!
        layanan.undo_last()
        self.assertEqual(layanan.antrean_circular.panjang(), 6)
        self.assertEqual(layanan.antrean_naif.panjang(), 6)
        # Verifikasi urutan depan: A-0, A-1, A-2
        self.assertEqual(layanan.antrean_circular.data[layanan.antrean_circular.front].oid, "A-0")
        self.assertEqual(layanan.antrean_naif.data[0].oid, "A-0")

        # 3. Aksi baru setelah undo mengosongkan redo
        layanan.undo_last()  # Undo lagi satu kali
        self.assertGreater(layanan.tumpukan_redo.panjang(), 0)

        # Lakukan aksi baru (enqueue baru)
        p_baru = Pesanan("NEW-99", "Baru", "R", "M", 20000, 3, 10, None, "ANTRE")
        layanan.enqueue(p_baru)

        # Redo harus kosong sekarang
        self.assertEqual(layanan.tumpukan_redo.panjang(), 0)
        sukses, pesan, _ = layanan.redo_last()
        self.assertFalse(sukses)
        self.assertIn("kosong", pesan.lower())

    def test_skala_dequeue_100_dan_geseran(self):
        """
        Uji Skala: dequeue 100 pada ~19.850 elemen ANTRE.
        Naif harus melakukan ~1.979.950 geseran, sedangkan Circular 0 geseran.
        """
        csv_path = os.path.join(BASE_DIR, "data", "pesanan.csv")
        if not os.path.exists(csv_path):
            self.skipTest("Berkas data/pesanan.csv tidak ditemukan.")

        arr_pesanan, _ = muat_pesanan(csv_path)
        layanan = LayananAntrean(kapasitas_awal=262144)
        dimuat = layanan.muat_dari_array(arr_pesanan)
        self.assertEqual(dimuat, 19850)

        stats_awal = layanan.stats()
        self.assertEqual(stats_awal.queue_len_naif, 19850)
        self.assertEqual(stats_awal.queue_len_circular, 19850)

        # Uji dequeue 100 pesanan
        keluar, durasi_circ, geser_circ = layanan.dequeue_circular(100)
        self.assertEqual(keluar.panjang(), 100)
        self.assertEqual(geser_circ, 0)

        # Cek geseran pada antrean naif:
        # Sum of (19849 down to 19750) = 1.979.950 geseran!
        stats_akhir = layanan.stats()
        self.assertEqual(stats_akhir.queue_len_circular, 19750)
        self.assertEqual(stats_akhir.queue_len_naif, 19750)
        self.assertEqual(stats_akhir.total_geseran_circular, 0)
        self.assertEqual(stats_akhir.total_geseran_naif, 1979950)

        print(
            f"\n[Uji Skala M2 Dequeue 100 / 19.850]"
            f"\n  Geseran Naif    : {stats_akhir.total_geseran_naif:,}"
            f"\n  Geseran Circular: {stats_akhir.total_geseran_circular}"
            f"\n  Waktu Circular  : {durasi_circ * 1000:.4f} ms"
        )
        self.assertEqual(stats_akhir.total_geseran_naif, 1979950)


if __name__ == "__main__":
    unittest.main()
