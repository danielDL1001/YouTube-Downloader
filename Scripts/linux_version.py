import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from threading import Thread
from yt_dlp import YoutubeDL
from mutagen.easyid3 import EasyID3
import shutil
import sys
import os

# Temas
tema_claro = {
    "bg": "#f2f2f2",
    "fg": "#000000",
    "entry_bg": "#ffffff",
    "button_bg": "#e0e0e0",
    "highlight": "#0078D7"
}

tema_escuro = {
    "bg": "#1e1e1e",
    "fg": "#ffffff",
    "entry_bg": "#2d2d2d",
    "button_bg": "#3a3a3a",
    "highlight": "#0a84ff"
}

tema_atual = tema_escuro

# Fontes
FONTE_PADRAO = ("Segoe UI", 10)
FONTE_TITULO = ("Segoe UI", 14, "bold")

# Caminhos para cookies e arquivos de histórico
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_PATH = os.path.join(BASE_DIR, 'cookies.txt')

# Pastas de download
HOME = os.path.expanduser("~")
pasta_mp3 = os.path.join(HOME, "Downloads", "Audios_YouTube")
pasta_mp4 = os.path.join(HOME, "Downloads", "Videos_YouTube")
os.makedirs(pasta_mp3, exist_ok=True)
os.makedirs(pasta_mp4, exist_ok=True)

def baixar(url, opcao, organizar_musica, status):
    try:
        # Opções inválidas
        if not url:
            status("❌ Nenhum link informado.")
            return

        # Reconhecer quantidade de itens (vídeo ou playlist)
        try:
            info_opts = {
                'quiet': True,
                'ignoreerrors': True,
                'raise_if_error': False,
                'extract_flat': 'in_playlist'
            }
            with YoutubeDL(info_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            status(f"❌ Erro ao acessar vídeo/playlist:")
            status(str(e))
            return

        total = len(info['entries']) if 'entries' in info else 1
        concluidos = 0

        def progresso_hook(d):
            nonlocal concluidos
            if d['status'] == 'finished':
                concluidos += 1
                pct = int((concluidos / total) * 100)
                janela.after(0, lambda: (
                    progress.config(value=pct),
                    label_status.config(
                        text=f"Baixando... {concluidos} de {total} ({pct}%)"
                    )
                ))

        # Configurações download
        ydl_opts = {
            'progress_hooks': [progresso_hook],

            # logs
            'quiet': False,
            'verbose': True,
            'no_warnings': False,

            # rede / estabilidade
            'force_ipv4': True,
            'retries': 10,
            'fragment_retries': 10,
            'skip_unavailable_fragments': True,
            'nocheckcertificate': True,

            # opções avançadas do nodeJS (para vídeos com player complexo)
            'js_runtimes': {
                'node': {
                    'cmd': 'node'
                }
            },

            # headers
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            },

            # extratores
            'extractor_args': {
                'youtube': {
                    'player_client': [
                        'android',
                        'tv'
                    ]
                }
            }
        }

        if os.path.exists(COOKIE_PATH):
            ydl_opts['cookiefile'] = COOKIE_PATH
            status("🍪 cookies.txt carregado...")
        else:
            status("❌ cookies.txt não encontrado (modo público).")

        # Vídeo MP4:
        if opcao == "1":
            ydl_opts.update({
                # Historico de downloads mp4
                'download_archive': 'downloaded_video.txt',
                # Forçar vídeo MP4 + áudio M4A (100% compatíveis)
                'format': '(bv*[ext=mp4]/bv*)+(ba[ext=m4a]/ba)/b',
                # Garante merge final em MP4
                'merge_output_format': 'mp4',
                # Não extrair áudio
                'outtmpl': (
                    os.path.join(pasta_mp4, '%(playlist_title|single)s',
                                '%(title)s[%(channel)s].%(ext)s')
                ),
            })

        # Áudio MP3
        else:
            ydl_opts.update({
                # Historico de downloads mp3
                'download_archive': 'downloaded_audio.txt',
                'format': 'bestaudio/best',
                'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }
                ],
                'final_ext': 'mp3',
                'outtmpl': (
                    os.path.join(pasta_mp3, '%(playlist_title|single)s',
                                '%(channel)s - %(title)s.%(ext)s')
                ),
            })

        # Download
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            status("✅ Download finalizado.")
        except Exception as e:
            status("❌ Erro durante o download:")
            status(str(e))

        # 🎵 Organização automática
        if opcao == "2" and organizar_musica:
            organizar_mp3(status)
        pass
    finally:
        botao_baixar.config(state="normal")


def organizar_mp3(status):
    status("🎶 Organizando músicas...")

    for raiz, _, arquivos in os.walk(pasta_mp3):
        for arquivo in arquivos:
            if not arquivo.lower().endswith(".mp3"):
                continue

            caminho = os.path.join(raiz, arquivo)

            try:
                audio = EasyID3(caminho)
                artista = audio.get("artist", ["Desconhecido"])[0]
                titulo = audio.get("title", ["Sem título"])[0]

                if artista.lower() in titulo.lower():
                    novo_nome = f"{titulo}.mp3"
                else:
                    novo_nome = f"{artista} - {titulo}.mp3"

                novo_caminho = os.path.join(raiz, novo_nome)

                if not os.path.exists(novo_caminho):
                    os.rename(caminho, novo_caminho)
                    status(f"✅ {novo_nome}")
                else:
                    status(f"⚠️ Já existe: {novo_nome}")

            except Exception as e:
                status(f"❌ Erro em {arquivo}: {e}")

def diagnostico():
    print("🔎 Diagnóstico do ambiente:")

    print(f"• Python: {sys.version.split()[0]}")

    if shutil.which("ffmpeg"):
        print("• FFmpeg: OK")
    else:
        print("❌ FFmpeg: NÃO encontrado")

    if shutil.which("node"):
        print("• Node.js: OK")
    else:
        print("❌ Node.js: NÃO encontrado")

    try:
        import yt_dlp
        print(f"• yt-dlp: OK ({yt_dlp.version.__version__})")
    except Exception as e:
        print(f"❌ yt-dlp: erro ({e})")

def iniciar_download():
    progress["value"] = 0
    label_status.config(text="Iniciando...")

    url = entry_url.get().strip()
    if not url:
        messagebox.showerror("Erro", "Cole um link do YouTube")
        return

    Thread(
        target=lambda: (
            diagnostico(),
            baixar(
                entry_url.get().strip(),
                formato.get(),
                var_organizar.get(),
                log
            )
        ),
        daemon=True
    ).start()


def log(msg):
    janela.after(0, lambda: (
        status_text.insert("end", msg + "\n"),
        status_text.see("end")
    ))


def atualizar_progresso(valor, texto):
    progress["value"] = valor
    label_status.config(text=texto)


def atualizar_opcoes():
    if formato.get() == "1":  # MP4
        var_organizar.set(False)
        check_organizar.config(state="disabled")
    else:  # MP3
        check_organizar.config(state="normal")


def aplicar_tema_recursivo(widget):
    # Frames, Labels, Buttons, etc.
    try:
        widget.configure(
            bg=tema_atual["bg"],
            fg=tema_atual["fg"]
        )
    except tk.TclError:
        pass

    # Entry
    if isinstance(widget, tk.Entry):
        widget.configure(
            bg=tema_atual["entry_bg"],
            fg=tema_atual["fg"],
            insertbackground=tema_atual["fg"],
            highlightbackground=tema_atual["highlight"],
            highlightcolor=tema_atual["highlight"]
        )

    # Text (status_text)
    if isinstance(widget, tk.Text):
        widget.configure(
            bg=tema_atual["entry_bg"],
            fg=tema_atual["fg"],
            insertbackground=tema_atual["fg"]
        )

    # Percorrer filhos
    for filho in widget.winfo_children():
        aplicar_tema_recursivo(filho)


def aplicar_tema():
    janela.configure(bg=tema_atual["bg"])
    aplicar_tema_recursivo(janela)

    # Estilo da Progressbar
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "Custom.Horizontal.TProgressbar",
        troughcolor=tema_atual["bg"],
        background=tema_atual["highlight"]
    )

    # Estilo do ttk
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "TProgressbar",
        troughcolor=tema_atual["bg"],
        background=tema_atual["highlight"],
        bordercolor=tema_atual["bg"],
        lightcolor=tema_atual["highlight"],
        darkcolor=tema_atual["highlight"]
    )

def alternar_tema():
    global tema_atual
    tema_atual = tema_claro if tema_atual == tema_escuro else tema_escuro
    aplicar_tema()


# Janela
janela = tk.Tk()
janela.title("YouTube Downloader")
janela.geometry("800x600")
janela.configure(bg="#1e1e1e")
janela.resizable(False, False)

# Frames
frame_titulo = tk.Frame(janela, bg="#1e1e1e")
frame_link = tk.Frame(janela, bg="#1e1e1e")
frame_opcoes = tk.Frame(janela, bg="#1e1e1e")
frame_progresso = tk.Frame(janela, bg="#1e1e1e")
frame_botao = tk.Frame(janela, bg="#1e1e1e")
frame_log = tk.Frame(janela, bg="#1e1e1e")

frame_titulo.pack(pady=10)
frame_link.pack(pady=5)
frame_opcoes.pack(pady=5)
frame_progresso.pack(pady=10)
frame_botao.pack(pady=10)
frame_log.pack(fill="both", expand=True, pady=5)


# Mensagem do link
label_titulo = tk.Label(
    frame_titulo,
    text="Cole o link do vídeo ou da playlist do YouTube abaixo 🎬",
    font=FONTE_TITULO
)
label_titulo.pack()

# Campo de link
entry_url = tk.Entry(
    frame_link,
    font=FONTE_PADRAO,
    width=70,
    relief="flat",
    highlightthickness=1,
    highlightbackground=tema_atual["highlight"],
    highlightcolor=tema_atual["highlight"]
)
entry_url.pack(pady=5, padx=20, fill="x")

# Formato
formato = tk.StringVar(value="1")  # mp4
rb_mp4 = tk.Radiobutton(
    frame_opcoes,
    text="Vídeo (MP4)",
    variable=formato,
    value="1",
    command=atualizar_opcoes,
    font=FONTE_PADRAO
)
rb_mp4.grid(row=0, column=0, padx=20, sticky="w")

rb_mp3 = tk.Radiobutton(
    frame_opcoes,
    text="Áudio (MP3)",
    variable=formato,
    value="2",
    command=atualizar_opcoes,
    font=FONTE_PADRAO
)
rb_mp3.grid(row=1, column=0, padx=20, sticky="w")


# Organizar MP3
var_organizar = tk.BooleanVar()
check_organizar = tk.Checkbutton(
    frame_opcoes,
    text="Organizar músicas por Artista - Música",
    variable=var_organizar
)
check_organizar.grid(row=2, column=0, padx=20, sticky="w")
check_organizar.config(state="disabled")


# Barra de progresso
progress = ttk.Progressbar(
    frame_progresso,
    style="Custom.Horizontal.TProgressbar",
    orient="horizontal",
    length=500,
    mode="determinate"
)
progress.pack(pady=5, padx=40)

# Label de porcentagem
label_status = tk.Label(
    frame_progresso,
    text="Aguardando...",
    font=FONTE_PADRAO
)
label_status.pack(pady=(0, 5))

# Botão
botao_baixar = tk.Button(
    frame_botao,
    text="⬇ Baixar",
    command=iniciar_download,
    font=FONTE_PADRAO,
    height=2,
    width=20
)
botao_baixar.pack()

# Botão tema
botao_tema = tk.Button(
    frame_botao,
    text="🌗 Trocar Tema",
    command=alternar_tema,
    height=2,
    width=20
)
botao_tema.pack(pady=5)

# Status
status_text = tk.Text(
    frame_log,
    font=FONTE_PADRAO,
    height=8
)
status_text.pack(fill="both", padx=10, pady=5)


aplicar_tema()
atualizar_opcoes()
try:
    janela.mainloop()
except KeyboardInterrupt:
    pass
