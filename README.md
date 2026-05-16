<div align="center">

# 🤖 Rams VIP Bot

**Telegram userbot berbasis VIP — download media view-once, bypass no-forward, dan copy konten channel private langsung ke Saved Messages.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Telethon](https://img.shields.io/badge/Telethon-1.x-blue?style=flat-square)](https://docs.telethon.dev)
[![Deploy on Railway](https://img.shields.io/badge/Deploy-Railway-0B0D0E?style=flat-square&logo=railway)](https://railway.app)

</div>

---

## ✨ Fitur

### 📥 `.dl` — Download Media View-Once & Restricted
Reply ke pesan media lalu ketik `.dl` untuk menyimpannya ke Saved Messages. Caption hasil download menampilkan:
```
📥 Dari: [Nama Pengirim] (mention)
🔖 Username: @username
🆔 ID: 1234567890
```

### 📣 `.copy` — Copy Konten dari Channel/Grup Private
Kirim `.copy <link>` untuk menyalin foto, video, dokumen, atau teks dari channel/grup yang tidak mengizinkan forward.

**Format link yang didukung:**
- Public: `https://t.me/namaChannel/123`
- Private: `https://t.me/c/1234567890/123`

### ⏱️ Auto DL View-Once & No-Forward
Aktifkan fitur auto download di menu **Fitur VIP** — setiap media view-once atau no-forward yang masuk ke chat akan otomatis disimpan ke Saved Messages tanpa perlu reply manual. Caption sama dengan fitur `.dl`.

### 🛡️ Manajemen VIP
- Admin dapat memberikan atau mencabut akses VIP via bot
- Session Telethon per-user, disimpan di database SQLite
- Auto-stop client saat VIP expired atau dicabut

---

## 🧱 Teknologi

| Komponen | Library |
|----------|---------|
| Bot interface | `python-telegram-bot` v20+ |
| Userbot (session) | `Telethon` |
| Database | SQLite (via `database.py`) |
| Runtime | Python 3.10+ |
| Deployment | Railway |

---

## 🗂️ Struktur Proyek

```
rams-2/
├── main.py          # Entry point utama — semua handler bot & userbot
├── database.py      # Fungsi DB: user, session, subscription
├── requirements.txt # Dependency Python
├── Procfile         # Perintah start untuk Railway/Heroku
└── README.md
```

---

## ⚙️ Environment Variables

Buat file `.env` (lokal) atau set di Railway Dashboard:

| Variable | Keterangan |
|----------|------------|
| `BOT_TOKEN` | Token bot dari [@BotFather](https://t.me/BotFather) |
| `ADMIN_ID` | Telegram user ID kamu (angka) |

---

## 🚀 Deploy di Railway

### Prasyarat
- Akun [Railway](https://railway.app) (bisa daftar dengan GitHub)
- Repository ini sudah ada di GitHub kamu

### Langkah Deploy

**1. Buat project baru di Railway**

Buka [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → pilih repo `rams-2`.

**2. Set Environment Variables**

Di halaman project Railway, buka tab **Variables** → tambahkan:

```
BOT_TOKEN   = token_dari_botfather
ADMIN_ID    = user_id_kamu
```

> Cara cek user ID: forward pesan kamu ke [@getidsbot](https://t.me/getidsbot) atau [@userinfobot](https://t.me/userinfobot).

**3. Pastikan `Procfile` ada di root repo**

```
worker: python main.py
```

> Gunakan tipe `worker` bukan `web` karena bot tidak expose HTTP port.

**4. Pastikan `requirements.txt` lengkap**

```
python-telegram-bot>=20.0
telethon
```

**5. Deploy**

Railway akan otomatis build dan menjalankan bot. Pantau log di tab **Deployments** → klik deployment terbaru → lihat **Build Logs** dan **Deploy Logs**.

Jika berhasil, kamu akan melihat log:
```
✅ Database siap.
🔄 Memuat N session tersimpan...
🚀 Rams VIP Bot berjalan...
```

**6. Pastikan service type = Worker**

Di Railway → tab **Settings** → pastikan tidak ada **Start Command** yang memaksa expose port. Kalau ada warning soal port, abaikan — bot berjalan sebagai worker.

---

## 📱 Cara Penggunaan

### Setup Awal (untuk user VIP)

1. Start bot → `/start`
2. Pastikan status langganan **Aktif**
3. Jalankan `/setup` dan ikuti langkah-langkah:
   - Masukkan **API ID** dari [my.telegram.org](https://my.telegram.org)
   - Masukkan **API Hash**
   - Masukkan nomor HP (format: `+6281xxxxxxx`)
   - Masukkan kode OTP yang dikirim ke Telegram
   - Jika aktif 2FA, masukkan password

> ⚠️ **Jangan logout dari sesi yang digunakan untuk setup!** Jika sesi dihapus, kamu perlu `/setup` ulang.

### Perintah Tersedia

| Perintah | Fungsi |
|----------|--------|
| `/start` | Tampilkan menu utama & status |
| `/setup` | Setup session Telegram |
| `/cancel` | Batalkan proses yang sedang berjalan |

### Perintah Userbot (di Telegram langsung)

| Perintah | Fungsi |
|----------|--------|
| `.dl` | Reply ke media → download ke Saved Messages |
| `.copy <link>` | Copy konten dari channel/grup via link |

### Menu Auto DL

Di menu **✨ Fitur VIP** → toggle **⏱️ Auto DL Timer/View-Once** untuk mengaktifkan/menonaktifkan auto download.

---

## 👤 Fitur Admin

Admin (user dengan ID = `ADMIN_ID`) mendapat akses menu tambahan:

| Aksi | Cara |
|------|------|
| Gift VIP | `/gift <user_id> [hari]` atau via menu Admin |
| Revoke VIP | `/revoke <user_id>` atau via menu Admin |
| Backup DB | Menu Admin → 📦 Backup DB |
| Restore DB | Menu Admin → ♻️ Restore DB → kirim file `.sql` |

---

## 🔒 Catatan Keamanan

- **API ID & API Hash bersifat rahasia** — jangan di-commit ke repo publik, selalu gunakan environment variable.
- **String session tersimpan di database** — pastikan file `db.sqlite` tidak diakses publik.
- Bot menggunakan sesi akun Telegram asli (userbot) — gunakan dengan bijak sesuai [Terms of Service Telegram](https://telegram.org/tos).

---

## 🐛 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Bot tidak merespons | Cek log Railway, pastikan `BOT_TOKEN` benar |
| `.dl` tidak bekerja | Pastikan sudah `/setup` dan reply ke pesan media |
| Session expired | Jalankan `/setup` ulang |
| Auto DL tidak aktif | Cek toggle di menu Fitur VIP |
| Error `FloodWait` | Tunggu beberapa menit, Telegram membatasi request |
| VIP expired otomatis | Bot akan stop client dan kirim notifikasi ke user |

---

<div align="center">

Made with ❤️ &nbsp;·&nbsp; [Report Issue](../../issues)

</div>
