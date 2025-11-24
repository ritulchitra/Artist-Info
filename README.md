# 🎵 Spotify Artist Explorer

🔥 Live Website: **https://artist-info-two.vercel.app/**  

A fast and beautiful web app to instantly explore any Spotify artist.  
Search artists, view followers, genres, top tracks, albums, and full album tracklists — all with a stunning UI and dynamic colors.

---

## 📁 Project Structure

```
Artist-Info/
│
├── backend/
│   ├── app.py
│   ├── spotify_client.py
│   ├── requirements.txt
│   └── __init__.py
│
├── frontend/
│   └── index.html
│
└── README.md
```

---

## 🚀 Features

- 🔍 Real-time search with autocomplete  
- 👤 Artist profile (image, genres, followers)  
- 🔥 Top 3 tracks  
- 💿 Album list with cover images  
- 🎧 Modal view for full album tracklist  
- 🎨 Dynamic background color based on artist image  
- ⚡ Super fast API responses  

---

## 🧠 How It Works

### Frontend (Vercel)
- HTML + CSS + JavaScript  
- Deployed on **Vercel**

### Backend (Render)
- Flask REST API  
- Communicates with Spotify Web API  
- Endpoints for search, artist info, albums, tracks  
- Deployed on **Render**

---

## 🔌 API Endpoints (Backend)

```
GET /search?name={artist_name}&limit=8
GET /artist?id={artist_id}
GET /artist_top_tracks?id={artist_id}&limit=3
GET /album_tracks?id={album_id}
```

---

## 🛠️ Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/ritulchitra/Artist-Info.git
cd Artist-Info
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs at:  
`http://127.0.0.1:5000`

### 3. Frontend
Open:
```
frontend/index.html
```

---

## 🌍 Deployment Guide

### Backend on Render

**Build Command:**
```
pip install -r backend/requirements.txt
```

**Start Command:**
```
gunicorn backend.app:app
```

Add environment variables:
```
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

---

### Frontend on Vercel

- Deploy the `frontend` folder  
- Update API URL in `index.html`:
```js
const API_BASE = "https://<your-render-url>";
```

---

## 🔐 Environment Variables (.env)

```
SPOTIFY_CLIENT_ID=your_id
SPOTIFY_CLIENT_SECRET=your_secret
```

---

## ⭐ Credits

Built by **Ritul Chitra**  
Powered by Spotify Web API  

If you like this project, please ⭐ star the repository!
