"""
tests/test_m1.py
Pengujian Unit untuk Milestone 1 (M1): Array vs LinkList.
"""

import unittest
import os
import time
from backend.m1_pesanan import Pesanan, Array, LinkList, tambah, muat_pesanan, muat_pesanan_ke_dua_struktur

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cek_struktur_identik(arr, ll):
    """Fungsi pembantu untuk memverifikasi kesamaan isi Array dan LinkList."""
    if arr.panjang() != ll.panjang():
        return False
    curr = ll.head
    for i in range(arr.panjang()):
        if arr.get(i) != curr.nilai:
            return False
        curr = curr.next
    return True


class TestM1Pesanan(unittest.TestCase):

    def test_append_1000_dan_kapasitas(self):
        """Append 1.000 elemen: kapasitas tumbuh benar dan urutan elemen tepat."""
        arr = Array(kapasitas_awal=4)
        ll = LinkList()

        for i in range(1000):
            p = Pesanan(f"O-{i:06d}", f"Pelanggan-{i}", "resto-a", "menu-a", 10000, 3, 100, None, "ANTRE")
            arr.append(p)
            ll.append(p)

        self.assertEqual(arr.panjang(), 1000)
        self.assertEqual(ll.panjang(), 1000)
        # Kapasitas array awal 4 -> 8 -> 16 -> ... -> 1024
        self.assertGreaterEqual(arr.kapasitas, 1000)
        self.assertEqual(arr.kapasitas, 1024)

        # Cek urutan elemen
        for i in range(1000):
            p_arr = arr.get(i)
            self.assertEqual(p_arr.oid, f"O-{i:06d}")

        self.assertTrue(cek_struktur_identik(arr, ll))

    def test_posisi_prioritas_dan_identitas(self):
        """Uji VIP (depan), PRIORITAS (tengah n//2), REGULER (belakang) identik di kedua struktur."""
        arr = Array()
        ll = LinkList()

        # Mulai dengan 4 pesanan reguler
        for i in range(4):
            p = Pesanan(f"R-{i}", f"User-R{i}", "resto", "m", 15000, 3, 10, None, "ANTRE")
            tambah(arr, p)
            tambah(ll, p)

        self.assertTrue(cek_struktur_identik(arr, ll))

        # 1. Tambah VIP (prioritas 1) -> harus di indeks 0
        p_vip1 = Pesanan("VIP-1", "Sultan", "resto", "m", 50000, 1, 15, None, "ANTRE")
        tambah(arr, p_vip1)
        tambah(ll, p_vip1)

        self.assertEqual(arr.get(0).oid, "VIP-1")
        self.assertEqual(ll.head.nilai.oid, "VIP-1")
        self.assertTrue(cek_struktur_identik(arr, ll))

        # 2. Tambah PRIORITAS (prioritas 2) -> ukuran saat ini 5, n//2 = 2
        p_prio1 = Pesanan("PRIO-1", "Pejabat", "resto", "m", 30000, 2, 20, None, "ANTRE")
        tambah(arr, p_prio1)
        tambah(ll, p_prio1)

        self.assertEqual(arr.get(2).oid, "PRIO-1")
        self.assertEqual(ll.get(2).oid, "PRIO-1")
        self.assertTrue(cek_struktur_identik(arr, ll))

        # 3. Tambah REGULER (prioritas 3) -> paling belakang
        p_reg5 = Pesanan("REG-5", "Rakyat", "resto", "m", 10000, 3, 25, None, "ANTRE")
        tambah(arr, p_reg5)
        tambah(ll, p_reg5)

        self.assertEqual(arr.get(arr.panjang() - 1).oid, "REG-5")
        self.assertEqual(ll.tail.nilai.oid, "REG-5")
        self.assertTrue(cek_struktur_identik(arr, ll))

        # 4. Tambah VIP lagi
        p_vip2 = Pesanan("VIP-2", "Raja", "resto", "m", 90000, 1, 30, None, "ANTRE")
        tambah(arr, p_vip2)
        tambah(ll, p_vip2)

        self.assertEqual(arr.get(0).oid, "VIP-2")
        self.assertEqual(ll.head.nilai.oid, "VIP-2")
        self.assertTrue(cek_struktur_identik(arr, ll))

    def test_hapus_depan_tengah_belakang_dan_tail(self):
        """Hapus di depan (0), tengah, belakang (tail), dan periksa keterjagaan head/tail."""
        arr = Array()
        ll = LinkList()

        for i in range(5):
            p = Pesanan(f"ID-{i}", f"User-{i}", "resto", "m", 10000 + i, 3, 10, None, "ANTRE")
            arr.append(p)
            ll.append(p)

        self.assertEqual(arr.panjang(), 5)
        self.assertEqual(ll.panjang(), 5)

        # 1. Hapus tengah (indeks 2: ID-2)
        del_arr = arr.hapus(2)
        del_ll = ll.hapus(2)
        self.assertEqual(del_arr.oid, "ID-2")
        self.assertEqual(del_ll.oid, "ID-2")
        self.assertEqual(arr.panjang(), 4)
        self.assertEqual(ll.panjang(), 4)
        self.assertTrue(cek_struktur_identik(arr, ll))

        # 2. Hapus depan (indeks 0: ID-0)
        del_arr0 = arr.hapus(0)
        del_ll0 = ll.hapus(0)
        self.assertEqual(del_arr0.oid, "ID-0")
        self.assertEqual(del_ll0.oid, "ID-0")
        self.assertEqual(ll.head.nilai.oid, "ID-1")
        self.assertTrue(cek_struktur_identik(arr, ll))

        # Isi tersisa: ID-1, ID-3, ID-4
        # 3. Hapus belakang / tail (indeks 2: ID-4)
        del_arr_tail = arr.hapus(arr.panjang() - 1)
        del_ll_tail = ll.hapus(ll.panjang() - 1)
        self.assertEqual(del_arr_tail.oid, "ID-4")
        self.assertEqual(del_ll_tail.oid, "ID-4")
        self.assertEqual(ll.tail.nilai.oid, "ID-3")
        self.assertIsNone(ll.tail.next)
        self.assertTrue(cek_struktur_identik(arr, ll))

        # 4. Hapus sampai habis dan periksa tail/head menjadi None
        arr.hapus(0)
        ll.hapus(0)
        self.assertEqual(ll.head, ll.tail)

        arr.hapus(0)
        ll.hapus(0)
        self.assertEqual(arr.panjang(), 0)
        self.assertEqual(ll.panjang(), 0)
        self.assertIsNone(ll.head)
        self.assertIsNone(ll.tail)

        # 5. Append setelah dikosongkan
        p_baru = Pesanan("NEW-1", "User-New", "resto", "m", 20000, 3, 10, None, "ANTRE")
        arr.append(p_baru)
        ll.append(p_baru)
        self.assertEqual(ll.head.nilai.oid, "NEW-1")
        self.assertEqual(ll.tail.nilai.oid, "NEW-1")
        self.assertEqual(arr.panjang(), 1)
        self.assertEqual(ll.panjang(), 1)
        self.assertTrue(cek_struktur_identik(arr, ll))

    def test_kasus_batas_kosong_dan_di_luar_jangkauan(self):
        """Struktur kosong dan indeks di luar jangkauan mengembalikan None tanpa crash."""
        arr = Array()
        ll = LinkList()

        # Akses pada struktur kosong
        self.assertIsNone(arr.get(0))
        self.assertIsNone(ll.get(0))
        self.assertIsNone(arr.hapus(0))
        self.assertIsNone(ll.hapus(0))
        self.assertIsNone(arr.get(-1))
        self.assertIsNone(ll.get(-1))
        self.assertIsNone(arr.get(100))
        self.assertIsNone(ll.get(100))

        # Isi 1 elemen
        p = Pesanan("O-1", "A", "R", "M", 1000, 3, 1, None, "ANTRE")
        arr.append(p)
        ll.append(p)

        self.assertIsNone(arr.get(-5))
        self.assertIsNone(ll.get(-5))
        self.assertIsNone(arr.get(1))
        self.assertIsNone(ll.get(1))
        self.assertIsNone(arr.hapus(5))
        self.assertIsNone(ll.hapus(5))
        self.assertIsNone(arr.hapus(-1))
        self.assertIsNone(ll.hapus(-1))

    def test_skala_muat_200000_baris(self):
        """Uji skala muat 200.000 baris ke Array harus cepat (target < 2 detik)."""
        csv_path = os.path.join(BASE_DIR, "data", "pesanan.csv")
        if not os.path.exists(csv_path):
            self.skipTest("Berkas data/pesanan.csv tidak ditemukan.")

        arr, durasi = muat_pesanan(csv_path)
        self.assertEqual(arr.panjang(), 200000)
        print(f"\n[Uji Skala M1] Waktu muat 200.000 baris ke Array: {durasi:.4f} detik (Kapasitas: {arr.kapasitas})")
        self.assertLess(durasi, 2.0, "Pemuatan 200.000 baris harus di bawah 2 detik")


if __name__ == "__main__":
    unittest.main()
