# YouTube Downloader (Python + Tkinter)

Aplicação gráfica em Python para baixar vídeos (MP4) ou áudios (MP3) do YouTube,
com suporte a playlists e organização automática de músicas.

Este é meu primeiro projeto em Python com interface gráfica usando Tkinter.

---

## 🚀 Funcionalidades
- Download de vídeos em MP4
- Extração de áudio em MP3
- Suporte a playlists
- Interface gráfica simples e intuitiva
- Organização automática de arquivos
- Suporte a cookies (opcional)
- Compatível com vídeos privados (se o usuário tiver acesso)

---

## 📦 Requisitos
- Python 3.10+
- FFmpeg (no PATH)
- **Node.js (LTS recomendado)**

> ⚠️ O Node.js é usado internamente pelo yt-dlp para lidar com mudanças recentes do YouTube.
> Sem ele, alguns vídeos ou formatos podem não funcionar corretamente.

---

## 🔧 Instalação

```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
python -m venv .venv