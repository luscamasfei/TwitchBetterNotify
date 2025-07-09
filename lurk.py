import requests
import time
import threading
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
from win10toast_click import ToastNotifier
import os
from PIL import Image
import pystray
import sys
from dotenv import load_dotenv

load_dotenv()

client_id = os.getenv("TWITCH_CLIENT_ID")
client_secret = os.getenv("TWITCH_CLIENT_SECRET")
verificacao_intervalo = 60
arquivo_canais = "canais_twitch.txt"
icone_caminho = "gwen.ico"
canais_monitorados = []
notificados = set()
canal_selecionado = [None]
mostrar_notificacao = [True]
abrir_live = [False]
bandeja = [None]

toaster = ToastNotifier()
monitor_thread = None
monitor_stop_event = threading.Event()
botoes_canais = {}

def obter_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials'}
    resp = requests.post(url, params=params)
    return resp.json()['access_token']

def checar_online(token, canal):
    headers = {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}
    resp = requests.get(f'https://api.twitch.tv/helix/streams?user_login={canal}', headers=headers)
    data = resp.json()
    return len(data['data']) > 0

def notificar(canal):
    url_live = f'https://www.twitch.tv/{canal}'
    try:
        if mostrar_notificacao[0]:
            toaster.show_toast(
                "🔴 Stream ao vivo!",
                f"{canal} está AO VIVO!",
                icon_path=icone_caminho if os.path.exists(icone_caminho) else None,
                duration=10,
                threaded=True,
                callback_on_click=lambda: webbrowser.open(url_live)
            )
        if abrir_live[0]:
            webbrowser.open(url_live)
    except Exception as e:
        print(f"[Erro notificar] {e}")

def adicionar_canal():
    canal = entrada.get().strip()
    if canal and canal not in canais_monitorados:
        canais_monitorados.append(canal)
        entrada.delete(0, "end")
        salvar_lista()
        atualizar_lista_canais()
    elif canal in canais_monitorados:
        messagebox.showinfo("Aviso", "Este canal já está na sua lista.")
    else:
        messagebox.showwarning("Erro", "Por favor, insira um nome válido.")

def remover_canal():
    if canal_selecionado[0] and canal_selecionado[0] in canais_monitorados:
        canais_monitorados.remove(canal_selecionado[0])
        notificados.discard(canal_selecionado[0])
        canal_selecionado[0] = None
        salvar_lista()
        atualizar_lista_canais()
    else:
        messagebox.showwarning("Erro", "Nenhum canal foi selecionado.")

def salvar_lista():
    with open(arquivo_canais, "w") as f:
        for canal in canais_monitorados:
            f.write(canal + "\n")

def carregar_lista():
    if os.path.exists(arquivo_canais):
        with open(arquivo_canais, "r") as f:
            for linha in f:
                canal = linha.strip()
                if canal:
                    canais_monitorados.append(canal)

def atualizar_lista_canais():
    botoes_canais.clear()
    for widget in frame_lista_canais.winfo_children():
        widget.destroy()
    for canal in canais_monitorados:
        btn = ctk.CTkButton(
            frame_lista_canais, text=canal, width=230, height=30,
            fg_color="#7c3aed", hover_color="#5b21b6",
            text_color="white", font=("Segoe UI", 13),
            command=lambda c=canal: selecionar_canal(c)
        )
        btn.pack(pady=3)
        botoes_canais[canal] = btn
    canal_selecionado[0] = None
    texto_selecionado.configure(text="Nenhum canal selecionado")

def selecionar_canal(canal):
    canal_selecionado[0] = canal
    texto_selecionado.configure(text=f"Selecionado: {canal}")

def atualizar_botao_status(canal, online):
    def update():
        btn = botoes_canais.get(canal)
        if not btn:
            return
        if online:
            btn.configure(fg_color="#22c55e", hover_color="#16a34a")  # verde
            if "(ONLINE)" not in btn.cget("text"):
                btn.configure(text=f"{canal} (ONLINE)")
        else:
            btn.configure(fg_color="#dc2626", hover_color="#b91c1c")  # vermelho
            if "(OFFLINE)" not in btn.cget("text"):
                btn.configure(text=f"{canal} (OFFLINE)")
    janela.after(0, update)


def monitorar(stop_event):
    token = obter_token()
    while not stop_event.is_set():
        try:
            for canal in canais_monitorados:
                if stop_event.is_set():
                    break
                online = checar_online(token, canal)
                if online:
                    if canal not in notificados:
                        notificar(canal)
                        notificados.add(canal)
                else:
                    notificados.discard(canal)
                atualizar_botao_status(canal, online)
        except Exception as e:
            print(f"[Erro] {e}")
        for _ in range(verificacao_intervalo):
            if stop_event.is_set():
                break
            time.sleep(1)

def iniciar_monitoramento():
    global monitor_thread, monitor_stop_event
    notificados.clear()  # <- Aqui reenviará notificações dos canais ao vivo

    if monitor_thread and monitor_thread.is_alive():
        monitor_stop_event.set()
        monitor_thread.join(timeout=5)

    monitor_stop_event = threading.Event()
    monitor_thread = threading.Thread(target=monitorar, args=(monitor_stop_event,), daemon=True, name="MonitorThread")
    monitor_thread.start()

    messagebox.showinfo("Monitoramento", "Monitoramento iniciado.")

def sair_app(icon, item):
    icon.stop()
    bandeja[0] = None
    janela.destroy()
    sys.exit()

def mostrar_janela(icon, item):
    janela.after(0, janela.deiconify)

def esconder_para_bandeja():
    if bandeja[0] is None:
        janela.withdraw()
        image = Image.open(icone_caminho)
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar", mostrar_janela),
            pystray.MenuItem("Sair", sair_app)
        )
        bandeja[0] = pystray.Icon("TwitchNotify", image, "Twitch Better Notify", menu)
        threading.Thread(target=bandeja[0].run, daemon=True).start()
    else:
        janela.withdraw()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

janela = ctk.CTk()
janela.title("TWITCH BETTER NOTIFY")
janela.geometry("380x640")
janela.resizable(False, False)
janela.protocol("WM_DELETE_WINDOW", esconder_para_bandeja)

try:
    janela.iconbitmap(icone_caminho)
except Exception as e:
    print(f"Erro ao definir ícone da janela: {e}")

titulo = ctk.CTkLabel(janela, text="Digite o nome do canal da Twitch:", font=("Segoe UI", 16))
titulo.pack(pady=10)

entrada = ctk.CTkEntry(janela, width=250, corner_radius=10)
entrada.pack(pady=5)

btn_adicionar = ctk.CTkButton(janela, text="Adicionar canal", command=adicionar_canal,
                               width=200, corner_radius=10, fg_color="#7c3aed", hover_color="#5b21b6")
btn_adicionar.pack(pady=5)

btn_remover = ctk.CTkButton(janela, text="Remover canal selecionado", command=remover_canal,
                             width=200, corner_radius=10, fg_color="#7c3aed", hover_color="#5b21b6")
btn_remover.pack(pady=5)

texto_selecionado = ctk.CTkLabel(janela, text="Nenhum canal selecionado", font=("Segoe UI", 13))
texto_selecionado.pack(pady=(15, 3))

scroll_frame = ctk.CTkScrollableFrame(janela, width=280, height=200, corner_radius=10)
scroll_frame.pack(pady=10)
frame_lista_canais = scroll_frame

frame_check = ctk.CTkFrame(janela, fg_color="transparent")
frame_check.pack(pady=10)

check1 = ctk.CTkCheckBox(frame_check, text="Receber notificação",
                         command=lambda: mostrar_notificacao.__setitem__(0, not mostrar_notificacao[0]))
check1.pack(side="left", padx=10)
check1.select()

check2 = ctk.CTkCheckBox(frame_check, text="Abrir live automaticamente",
                         command=lambda: abrir_live.__setitem__(0, not abrir_live[0]))
check2.pack(side="left", padx=10)

btn_monitorar = ctk.CTkButton(janela, text="Iniciar Monitoramento", command=iniciar_monitoramento,
                               width=240, corner_radius=10, fg_color="#7c3aed", hover_color="#5b21b6")
btn_monitorar.pack(pady=20)

creditos = ctk.CTkLabel(
    janela,
    text="Este é um programa totalmente gratuito.\nQualquer comercialização do mesmo é proibida.\nFeito por @luscamasfei",
    font=("Segoe UI", 10),
    text_color="gray"
)
creditos.pack(pady=(10, 5))

carregar_lista()
atualizar_lista_canais()
janela.mainloop()
