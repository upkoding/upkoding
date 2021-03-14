# upkoding

![Screenshot Awal](https://raw.githubusercontent.com/upkoding/upkoding/main/screenshot.png)


🔥🔥🔥  WORK IN PROGRESS 🔥🔥🔥

## Development

Untuk pengembangan di local maka pengetahuan Django sangat diperlukan paling tidak sudah bisa menjalankan sampai di `./manage.py runserver`.

Proyek ini memiliki fitur pencarian menggunakan fitur Full Text Search yg dimiliki PostgreSQL, jadi untuk di local juga harus menggunakan Postgres sebagai databasenya. Cara yang paling gampang yaitu menggunakan Docker imagenya postgres.

**Caranya, download dulu Docker imagenya Postgres:**

```
$ docker pull postgres
```

**Start Postgres:**

```
docker run -it --rm --name dev-postgres \
-e POSTGRES_PASSWORD=password \
-v /Users/eka/Documents/postgres-data/:/var/lib/postgresql/data \
-p 5432:5432 postgres
```
Perhatikan kita menaruh datanya di hardisknya kita (`/Users/eka/Documents/postgres-data/`) bukan didalam imagenya, jadi ketika server DB kita matikan maka data tetap ada, dan kalau di start lagi maka akan me-load data yang sama.

**Setup database proyek:**

Langkah ini cukup sekali. Pertama pastikan DB server jalan dengan command docker diatas, setelah itu kita login ke Postgres.
```
# Masuk kedalam server
$ docker exec -it dev-postgres bash

# Login ke Postgres (dari dalam server)
$ psql -h localhost -U postgres

# Buat database dan user (disini nama DB nya `upkoding` dan usernya juga `upkoding` sesuai dengan settings.py)
CREATE DATABASE upkoding;
CREATE USER upkoding WITH PASSWORD 'upkoding';
ALTER ROLE upkoding SET client_encoding TO 'utf8';
ALTER ROLE upkoding SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE upkoding TO upkoding;
```
Setelah itu bisa keluar dari Postgres dengan `\q`+ Enter. Dan `CTRL+C` untuk keluar dari server.

**Django DB migration:**

Masih dengan server yang masih berjalan, jalankan perintah berikut di terminal lainnya.
```
# migrate
$ ./manage.py migrate

# buat super user
$ ./manage.py createsuperuser

# jalankan server
$ ./manage.py runserver
```

**Start developing & login ke admin:**

Kalau semua lancar maka, kita akan melihat websitenya jalan di `http://localhost:8000`. Untuk login ke admin tinggal buka `http://localhost:8000/admin` dan login dengan username dan password yang sama pada saat kita bikin superuser.

> Apabila ada yang kurang jelas, ketemu bug, feature request bisa kita diskusikan lewat github **Issue** atau **Discussion**.

## Latar Belakang

Saya banyak mendengar keluh-kesah teman-teman kita yang belajar pemrograman baik itu dari komentar2 di [Youtube Channel UpKoding](https://youtube.com/c/UpKoding) ataupun dari [Group Telegram UpKoding](https://t.me/upkoding). Salah satu yang saya tangkap adalah banyak yang menemui kendala ketika belajar baik itu karena hilangnya motivasi, kurangnya dukungan ataupun tidak ada sistem support yang memotivasi mereka untuk tetap belajar.

Dan yang saya selalu tekankan kepada mereka adalah, cara terbaik belajar pemrograman adalah dengan membuat proyek nyata. Mengaplikasikan teori yang dipelajari dengan proyek nyata. Akhirnya tercetuslah ide bagaimana caranya supaya terdapat sebuah platform yang bisa jadi tempat nongkrong, tempat mencari support, tempat belajar dan tempat meningkatkan skill pemrograman yang aktif dan interaktif.

Akhirnya saya mulailah proyek ini, berikut fitur utama yang ada di pikiran saya saat ini:

- **Proyek**, tempat teman-teman memilih proyek yang akan dikerjakan ataupun mensubmit ide proyek buat dikerjakan sama teman-teman pengguna lainnya.
- **Coders**, disini kita bisa melihat profile para coders (pengguna), proyek yang dikerjakan, proyek yang disubmit dan diskusi yang diikuti.
- **Diskusi**, disinilah tempat mereka berdiskusi, sharing, bertanya dan berinteraksi dengan pengguna lainnya. Saya ingin forum ini bisa menjadi Stack Overflow nya Indonesia :)

*Nanti setiap interaksi (menyelesaikan proyek, mensubmit proyek, bertanya dan menjawab pertanyaan di forum) yang dilakukkan akan mendapatkan poin.*

## Sumbangan Ide

Saya juga sadar alasan saya menginisiasi proyek ini adalah karena melihat situasi diatas dan pastinya merupakan asumsi pribadi. Apabila ada masukan, saran dan ide menarik lainnya yang sepertinya akan membuat platform ini berguna maka dengan senang hati saya akan mendengarkannya. Silahkan buat issue baru dan kita bisa diskusikan disana.

## Ingin berkontribusi?

Karena ini masih tahap awal sekali, saya belum menentukan struktur dan fitur yang pasti di proyek ini jadi sepertinya teman-teman mohon maaf belum bisa berkontribusi untuk saat ini. Nanti setelah diluncurkan ke public maka saat itu juga akan saya buka dan dengan senang hati menerima setiap kontribusi dari kalian.

**Tapi sumbangan ide selalu saya nantikan setiap saat.** Ini yang paling saya butuhkan saat ini.

## Teknologi

Proyek ini dibuat dengan [Framework Django](https://www.djangoproject.com), database menggunakan [PostgreSQL](https://www.postgresql.org) dan dideploy di Google Appengine.

## Lisensi

```
MIT License

Copyright (c) 2021 UpKoding

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
