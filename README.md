<div align="center">

# 🤖 Rams VIP Bot

**Telegram userbot berbasis VIP — download media view-once, bypass no-forward, dan copy konten channel private langsung ke Saved Messages.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-blue?style=flat-square)](https://docs.telethon.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Railway-336791?style=flat-square&logo=postgresql&logoColor=white)](https://railway.app)
[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=flat-square&logo=railway)](https://railway.app)

</div>

---

## ✨ Fitur

### 📥 `.dl` — Download Media View-Once & Restricted

Reply ke pesan berisi foto, video, atau file apapun — termasuk yang **view-once** atau **no-forward** — lalu ketik `.dl`. Media akan langsung dikirim ke Saved Messages kamu dengan caption:

```
📥 Dari: Nama Pengirim  ← bisa diklik (mention)
🔖 Username: @username  ← atau — jika tidak punya username
🆔 ID: 1234567890
```

**Yang didukung:**
- Foto (JPEG, PNG, WebP)
- Video & GIF
- Dokumen / File
- Audio & Voice Note
- Stiker (termasuk animasi)
- Media view-once (foto & video timer)
- Pesan dengan proteksi no-forward

---

### 📣 `.copy` — Copy dari Channel/Grup Private

Kirim `.copy <link_pesan>` untuk menyalin konten dari channel atau grup yang membatasi forward. Bot mengambil medianya lalu mengirim ulang ke Saved Messages.

**Format link yang didukung:**

| Tipe | Contoh Link |
|------|-------------|
| Channel/grup publik | `https://t.me/namaChannel/123` |
| Channel/grup privat | `https://t.me/c/1234567890/123` |

**Yang bisa dicopy:**
- Foto, video, dokumen
- Teks / caption pesan
- Media dengan proteksi no-forward

---

### ⏱️ Auto DL View-Once & No-Forward

Aktifkan toggle di menu **✨ Fitur VIP** → **⏱️ Auto DL**. Setelah aktif, **setiap** pesan view-once dan media no-forward yang masuk ke chat manapun akan **otomatis disimpan** ke Saved Messages tanpa perlu reply atau ketik apapun.

Caption otomatis sama persis dengan fitur `.dl` manual:
```
📥 Dari: ...
🔖 Username: ...
🆔 ID: ...
```

> **Catatan:** Auto DL berjalan selama userbot client aktif. Jika bot restart, fitur ini tetap aktif selama setting tersimpan di database.

---

### 🛡️ Sistem VIP & Subscription

- Setiap user harus memiliki langganan VIP aktif untuk menggunakan fitur userbot
- Admin dapat memberikan VIP secara manual dengan durasi tertentu (default 30 hari)
- Bot otomatis menghentikan client userbot jika VIP expired atau dicabut
- Status dan sisa waktu VIP bisa dicek kapanpun via menu `/start`

---

## 🧱 Teknologi

| Komponen | Detail |
|----------|---------|
| Bot interface | `python-telegram-bot` v20+ (async) |
| Userbot / session | `Telethon` — satu client per user VIP |
| Database | **PostgreSQL** via Railway Add-on (`psycopg2`) |
| Runtime | Python 3.10+ |
| Deployment | Railway (Worker service) |

---

## 🗂️ Struktur Proyek

```
rams-2/
├── main.py          # Entry point — semua handler bot & userbot
├── database.py      # Semua operasi DB: users, sessions, subscriptions, settings
├── requirements.txt # Dependency Python
├── Procfile         # Perintah start untuk Railway
└── README.md
```

---

## 🗄️ Database (PostgreSQL)

Bot menggunakan **PostgreSQL** (bukan SQLite) yang dihosting sebagai Railway Add-on. Koneksi diambil dari environment variable `DATABASE_URL` yang otomatis di-inject oleh Railway.

### Skema Tabel

#### `users`
Menyimpan data dasar setiap pengguna yang pernah berinteraksi dengan bot.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `user_id` | BIGINT (PK) | Telegram user ID |
| `username` | TEXT | Username Telegram (tanpa @) |
| `full_name` | TEXT | Nama lengkap user |
| `created_at` | TEXT | Waktu pertama kali start bot |

#### `sessions`
Menyimpan kredensial dan session Telethon per-user. **Data sensitif** — jangan diekspos.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `user_id` | BIGINT (PK) | Referensi ke `users.user_id` |
| `api_id` | BIGINT | API ID dari my.telegram.org |
| `api_hash` | TEXT | API Hash dari my.telegram.org |
| `string_session` | TEXT | Telethon string session (terenkripsi base64) |

#### `subscriptions`
Melacak status VIP setiap user.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `user_id` | BIGINT (PK) | Referensi ke `users.user_id` |
| `plan` | TEXT | Tipe plan (default: `'vip'`) |
| `paid_at` | TEXT | Waktu VIP diaktifkan (ISO 8601) |
| `expired_at` | TEXT | Waktu VIP berakhir (ISO 8601) |
| `is_active` | INTEGER | `1` = aktif, `0` = dicabut/expired |

#### `user_settings`
Menyimpan preferensi fitur per-user.

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `user_id` | BIGINT (PK) | Referensi ke `users.user_id` |
| `auto_dl_view_once` | INTEGER | `1` = Auto DL aktif, `0` = nonaktif |

---

## ⚙️ Environment Variables

Set di Railway Dashboard → tab **Variables**:

| Variable | Wajib | Keterangan |
|----------|-------|------------|
| `BOT_TOKEN` | ✅ | Token bot dari [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | ✅ | Telegram user ID admin (angka, bukan username) |
| `DATABASE_URL` | ✅ | Otomatis di-inject Railway setelah add PostgreSQL |

---

## 🚀 Deploy di Railway

### Prasyarat

- Akun [Railway](https://railway.app) (daftar via GitHub)
- Repo `rams-2` sudah ada di GitHub kamu
- Token bot dari [@BotFather](https://t.me/BotFather)

---

### Langkah Deploy

#### 1. Buat Project Baru

Buka [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → pilih repo `rams-2`.

#### 2. Tambahkan PostgreSQL Add-on

Di halaman project → **+ New** → **Database** → **Add PostgreSQL**.

Railway akan otomatis membuat database dan mengisi variable `DATABASE_URL` ke semua service dalam project yang sama.

#### 3. Set Environment Variables

Di service bot → tab **Variables** → tambahkan:

```
BOT_TOKEN  = token_dari_botfather
ADMIN_ID   = user_id_kamu_dalam_angka
```

> 💡 Cara cek user ID kamu: kirim pesan ke [@userinfobot](https://t.me/userinfobot) atau [@getidsbot](https://t.me/getidsbot).

#### 4. Pastikan `Procfile` Ada di Root

```
worker: python main.py
```

> ⚠️ Gunakan `worker:` bukan `web:` — bot tidak butuh HTTP port. Pakai `web:` akan menyebabkan Railway terus restart karena menunggu port yang tidak pernah dibuka.

#### 5. Pastikan `requirements.txt` Lengkap

```
python-telegram-bot>=20.0
telethon
psycopg2-binary
```

#### 6. Deploy & Cek Log

Railway otomatis build dan deploy setiap push ke branch `main`. Pantau di tab **Deployments** → klik deployment terbaru → **Deploy Logs**.

Log sukses akan terlihat seperti:
```
✅ Database siap.
🔄 Memuat N session tersimpan...
🚀 Rams VIP Bot berjalan...
```

---

## 📱 Cara Penggunaan

### Setup Awal (User VIP)

1. Start bot → `/start`
2. Pastikan status langganan menampilkan **✅ Aktif**
3. Ketik `/setup` dan ikuti langkah berikut:

| Langkah | Input |
|---------|-------|
| 1 | **API ID** — ambil dari [my.telegram.org](https://my.telegram.org) → App configuration |
| 2 | **API Hash** — ambil dari halaman yang sama |
| 3 | **Nomor HP** — format internasional: `+6281xxxxxxx` |
| 4 | **Kode OTP** — dikirim Telegram ke akun kamu |
| 5 | **Password 2FA** — hanya jika kamu aktifkan Two-Step Verification |

> ⚠️ Jangan logout dari akun Telegram yang dipakai setup! String session akan invalid dan kamu perlu `/setup` ulang.

---

### Daftar Perintah Bot

| Perintah | Fungsi |
|----------|--------|
| `/start` | Menu utama, status VIP, dan navigasi fitur |
| `/setup` | Mulai proses setup session Telethon |
| `/cancel` | Batalkan proses setup yang sedang berjalan |

### Perintah Userbot (langsung di Telegram)

| Perintah | Cara Pakai | Fungsi |
|----------|------------|--------|
| `.dl` | Reply ke pesan media | Download media ke Saved Messages |
| `.copy <link>` | Kirim di chat manapun | Copy pesan dari channel/grup via link |

---

## 👤 Fitur Admin

Admin (user dengan `user_id` = nilai `ADMIN_ID`) mendapat akses menu khusus di bot:

| Aksi | Cara |
|------|------|
| Gift VIP ke user | Menu Admin → 🎁 Gift VIP → masukkan user ID & durasi (hari) |
| Cabut VIP user | Menu Admin → ❌ Revoke VIP → masukkan user ID |
| Lihat semua user | Menu Admin → 👥 Daftar User |
| Backup database | Menu Admin → 📦 Backup DB → bot kirim file `.sql` |
| Restore database | Menu Admin → ♻️ Restore DB → kirim file `.sql` ke bot |

---

## 🔒 Catatan Keamanan

- **API ID & API Hash** bersifat rahasia — jangan pernah hardcode di kode atau commit ke repo publik. Selalu gunakan environment variable.
- **String session** (`sessions.string_session`) setara dengan password akun Telegram. Pastikan database PostgreSQL tidak diekspos ke publik.
- Bot menggunakan akun Telegram asli (userbot) — gunakan sesuai [Terms of Service Telegram](https://telegram.org/tos). Jangan gunakan untuk spam atau aktivitas yang melanggar ToS.

---

## 🐛 Troubleshooting

| Masalah | Kemungkinan Penyebab | Solusi |
|---------|---------------------|--------|
| Bot tidak merespons sama sekali | `BOT_TOKEN` salah atau service tidak jalan | Cek Variables & Deploy Logs di Railway |
| `.dl` tidak bekerja | Session belum di-setup atau expired | Jalankan `/setup` ulang |
| Auto DL tidak aktif setelah restart | Normal — client di-reload dari DB | Pastikan toggle masih ON di menu Fitur VIP |
| Error `FloodWaitError` | Terlalu banyak request ke Telegram API | Tunggu beberapa menit |
| `DATABASE_URL not found` | PostgreSQL add-on belum ditambahkan | Tambahkan PostgreSQL di Railway project |
| VIP expired, bot tidak bisa dipakai | Subscription habis | Minta admin untuk gift VIP ulang |
| Session invalid / `AuthKeyError` | Akun logout atau 2FA berubah | Jalankan `/setup` ulang dengan kredensial baru |

---

<div align="center">

Made with ❤️ &nbsp;·&nbsp; [Report Issue](../../issues)

</div>
