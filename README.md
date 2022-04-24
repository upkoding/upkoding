# upkoding

![Screenshot Awal](https://raw.githubusercontent.com/upkoding/upkoding/main/screenshot.png)

UpKoding ingin membuat belajar pemrograman menyenangkan dengan format bite-sized learning, belajar materi secukupnya, langsung uji dan praktekkan dengan proyek atau problem solving.
## Development

Cara yang paling mudah yaitu dengan menggunakan Docker dan Docker compose, beberapa perintah penting sudah disediakan melalui `Makefile`.

Kemudian jalankan perintah berikut secara berurutan:
```bash
# 1. buat file env baru bernama .env dan copy isi dari .env.example
# dan ubah parameter kalau diperlukan.
cp .env.example .env

# 2. jalankan DB migration
make migrate

# 3. buat admin / superuser, masukkan informasi yang diminta
make createsuperuser

# 4. build theme static files
make buildstatic

# 4. build Svelte static files (new)
make buildsvelte

# 5. jalankan proyek
make runserver
```

**Start developing & login ke admin:**

Kalau semua lancar maka, kita akan melihat websitenya jalan di `http://localhost:8000`. Untuk login ke admin tinggal buka `http://localhost:8000/admin` (gunakan username dan password yang sama pada saat kita buat superuser).

> Apabila ada yang kurang jelas, ketemu bug, feature request bisa kita diskusikan lewat github **Issue** atau **Discussion**.
## Teknologi

Platform ini dibuat dengan [Framework Django](https://www.djangoproject.com), database [PostgreSQL](https://www.postgresql.org) dan hosting di [Digital Ocean](https://m.do.co/c/71f884aaaabb) (link afiliasi).

## Beri Dukungan

Kode proyek selalu terbuka dan siapa saja bisa bergabung dan memanfaatkannya secara gratis, tapi untuk menjaga platform tetap berjalan dan mendukung pengembangannya pastinya perlu tenaga dan biaya (infrastruktur/maintenance/support).

Untuk itu bagi siapapun yang berkenan bisa mendukung dengan cara berikut ini:

- Bantu mengembangkan
- Bagikan ke media sosial, referensikan ke teman
- Jadi sponsor (perusahaan atau perorangan)
- Jadi member Pro Access di [upkoding.com](https://www.upkoding.com/)
- Sponsor perorangan via [Saweria](https://saweria.co/upkoding) atau [Paypal](https://www.paypal.com/paypalme/UpKoding)


## Lisensi

Proyek ini berlisensi **AGPL-3.0 License**.
```
Permissions of this strongest copyleft license are conditioned on making available complete source code of licensed works and modifications, which include larger works using a licensed work, under the same license. Copyright and license notices must be preserved. Contributors provide an express grant of patent rights. When a modified version is used to provide a service over a network, the complete source code of the modified version must be made available.
```

Yang artinya:
```
Siapa saja boleh mempergunakan, memodifikasi dan mendistribusikan proyek ini tetapi harus tetap menggunakan lisensi yang sama dan kode sumber harus selalu dibuka secara penuh seperti yang dilakukkan pengembang dengan upkoding.com.
```

Lebih detail mengenai lisensi ini bisa dibaca [disini](https://github.com/upkoding/upkoding/blob/main/LICENSE).
