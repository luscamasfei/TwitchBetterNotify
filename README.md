# 🎮 Twitch Better Notify

**Um aplicativo desktop leve para receber notificações e acompanhar seus streamers favoritos na Twitch!**

---

## 🚀 Sobre o Aplicativo

O **Twitch Better Notify** foi desenvolvido para melhorar sua experiência de acompanhar lives na Twitch, permitindo que você:

- Receba **notificações instantâneas** quando seus canais favoritos ficarem ao vivo.
- Veja o status online/offline dos canais diretamente no app, com botões coloridos intuitivos.
- Abra automaticamente a live ao clicar na notificação ou ativar a opção no app.
- Aplicativo discretamente em segundo plano, minimizado na bandeja do sistema.
- Gerencie facilmente sua lista de canais: adicionar, remover e acompanhar.

---

## 🛠 Como Usar

1. **Configurar o `.env`**

   Crie um arquivo `.env` na mesma pasta do executável com suas credenciais da Twitch:

TWITCH_CLIENT_ID=seu_client_id_aqui
TWITCH_CLIENT_SECRET=seu_secret_aqui

2. **Adicionar canais**

- Digite o nome do canal Twitch no campo.
- Clique em "Adicionar canal".
- O canal aparecerá na lista para monitoramento.

3. **Iniciar monitoramento**

- Clique em "Iniciar Monitoramento".
- O app começará a checar os canais a cada minuto.
- Notificações serão exibidas quando um canal ficar ao vivo.

4. **Opções**

- **Receber notificação**: habilite ou desabilite alertas.
- **Abrir live automaticamente**: ao receber notificação, abrirá a live no navegador.

5. **Minimizar para bandeja**

- Feche a janela com o "X" para minimizar para a bandeja do Windows.
- Clique no ícone na bandeja para reabrir ou sair do app.

---

## 🖼 Twitch Better Notify

![Tela principal do app mostrando lista de canais](https://i.postimg.cc/63PK7LCp/Captura-de-tela-2025-07-09-152840.png)

---

## ⚙️ Requisitos

- Windows 10/11
- Python 3.8+ (para rodar código fonte)
- Bibliotecas Python: `requests`, `customtkinter`, `win10toast_click`, `pystray`, `python-dotenv`, `Pillow`

---

Este programa é gratuito e não deve ser comercializado.
Bug? Sugestão? Abra uma issue ou envie mensagem.
