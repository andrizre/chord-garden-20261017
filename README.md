# Chord Garden

Chord Garden adalah pembuat seni string-art geometris berbasis CLI. Dari seed, ia memilih aturan sambungan antartitik di keliling lingkaran dan menumpuk beberapa lapisan tali menjadi pola SVG yang konsisten dan dapat dibuat ulang.

## Fitur

- Menghasilkan pola geometri string-art dalam SVG mandiri.
- Mengatur seed, jumlah pin, lapisan tali, nama karya, dan palet warna.
- Empat palet bawaan: `aurora`, `ember`, `tideline`, dan `moss`.
- Seed yang sama menghasilkan karya yang sama; file dapat dibuka di browser atau editor vektor.
- Menyertakan contoh hasil di [examples/aurora-garden.svg](examples/aurora-garden.svg).
- Hanya menggunakan Python standard library.

## Persyaratan

Python 3.11 atau lebih baru. Tidak ada dependensi runtime eksternal.

## Instalasi

```bash
git clone https://github.com/andrizre/chord-garden-20261017.git
cd chord-garden-20261017
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Di Windows PowerShell, aktifkan virtualenv dengan `.venv\Scripts\Activate.ps1`.

## Cara menjalankan

Lihat palet yang tersedia:

```bash
chord-garden palettes
```

Buat karya yang dapat dibuat ulang:

```bash
chord-garden generate --seed 20261017 --pins 80 --layers 4 --palette aurora --title "Aurora Garden" --output aurora.svg
```

Opsi `--pins` menerima 16–192 dan `--layers` menerima 1–8. Jika seed tidak diberikan, program memilih seed acak dan mencetaknya agar karya dapat dibuat ulang. Jika `--output` tidak diberikan, SVG disimpan dengan nama otomatis di folder aktif.

Jalankan pengujian:

```bash
python -m unittest discover -s tests -v
```

Tes memeriksa determinisme seed, batas parameter, koordinat titik, keunikan sambungan tiap lapisan, XML SVG, serta alur CLI penulisan file.

## Lisensi

MIT. Lihat [LICENSE](LICENSE).
