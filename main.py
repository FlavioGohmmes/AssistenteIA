import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import google.generativeai as genai
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import json
from datetime import datetime
import os
import threading

# Configuração da API do Gemini
api_key = "AIzaSyDiiyWBmj6kDxSaQrWKQPZhk7di36y6Xz4"
genai.configure(api_key=api_key)

# Função para carregar o histórico de conversas
def carregar_historico():
    try:
        with open("historico_conversas.json", "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []

# Função para salvar o histórico de conversas
def salvar_historico(historico):
    with open("historico_conversas.json", "w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=4)

# Função para salvar o histórico em um arquivo .txt
def salvar_historico_txt():
    historico = carregar_historico()
    if not historico:
        messagebox.showinfo("Histórico", "Nenhuma conversa salva ainda.")
        return

    nome_arquivo = f"historico_conversas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Arquivos de Texto", "*.txt")],
        initialfile=nome_arquivo
    )

    if caminho_arquivo:
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                for conversa in historico:
                    arquivo.write(f"Data: {conversa['data']}\n")
                    arquivo.write(f"Você: {conversa['usuario']}\n")
                    arquivo.write(f"Assistente: {conversa['assistente']}\n")
                    arquivo.write("-" * 50 + "\n")
            messagebox.showinfo("Sucesso", f"Histórico salvo em {caminho_arquivo}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o arquivo: {e}")

# Função para exibir o histórico de conversas
def exibir_historico():
    historico = carregar_historico()
    if not historico:
        messagebox.showinfo("Histórico", "Nenhuma conversa salva ainda.")
        return

    janela_historico = ttk.Toplevel(janela)
    janela_historico.title("Histórico de Conversas")
    janela_historico.geometry("600x400")

    area_historico = scrolledtext.ScrolledText(
        janela_historico, wrap=tk.WORD, state=tk.NORMAL, font=("Arial", 12))
    area_historico.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    for conversa in historico:
        area_historico.insert(tk.END, f"Data: {conversa['data']}\n")
        area_historico.insert(tk.END, f"Você: {conversa['usuario']}\n")
        area_historico.insert(tk.END, f"Assistente: {conversa['assistente']}\n")
        area_historico.insert(tk.END, "-" * 50 + "\n")

    area_historico.config(state=tk.DISABLED)

# Função para animação de carregamento
def animacao_carregamento():
    texto_carregamento = "Estou pensando"
    while carregando:
        for i in range(4):
            if not carregando:
                break
            label_carregamento.config(text=texto_carregamento + "." * i)
            janela.update()
            janela.after(500)  # Atualiza a cada 500ms
    label_carregamento.config(text="")

# Função para enviar mensagem e obter resposta
def enviar_mensagem():
    global carregando
    user_input = entrada.get()
    if user_input.strip() == "":
        return  # Ignora mensagens vazias

    entrada.delete(0, tk.END)

    # Exibe a mensagem do usuário alinhada à direita
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "Você\n", "user_bold")
    chat_area.insert(tk.END, f"{user_input}\n\n", "user_tag")
    chat_area.config(state=tk.DISABLED)

    # Inicia a animação de carregamento
    carregando = True
    threading.Thread(target=animacao_carregamento).start()

    # Obtém a resposta do Gemini em uma thread separada
    def obter_resposta():
        global carregando
        resposta = model.generate_content(user_input)
        responder = resposta.text

        # Exibe a resposta do assistente alinhada à esquerda
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, "Assistente\n", "assistant_bold")
        chat_area.insert(tk.END, f"{responder}\n\n", "assistant_tag")
        chat_area.config(state=tk.DISABLED)

        # Scrolla para o final
        chat_area.see(tk.END)

        # Salva a conversa no histórico
        historico = carregar_historico()
        historico.append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "usuario": user_input,
            "assistente": responder
        })
        salvar_historico(historico)

        # Finaliza a animação de carregamento
        carregando = False

    # Executa a obtenção da resposta em uma thread separada
    threading.Thread(target=obter_resposta).start()

# Função para perguntar ao usuário se deseja salvar o histórico antes de sair
def sair_programa():
    resposta = messagebox.askyesno("Sair", "Deseja salvar o histórico de conversas antes de sair?")

    if resposta:  # Se o usuário quiser salvar
        salvar_historico_txt()
    else:  # Se o usuário não quiser salvar
        try:
            if os.path.exists("historico_conversas.json"):
                os.remove("historico_conversas.json")
                print("Histórico anterior apagado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao apagar o histórico: {e}")

    # Fecha a janela e encerra o programa
    janela.quit()

# Configuração da janela principal com ttkbootstrap
janela = ttk.Window(themename="minty")
janela.title("Assistente AB Areias")
janela.geometry("800x900")  # Tamanho ajustado para 800x900

# Adiciona o ícone da janela
try:
    # Caminho do ícone
    janela.iconbitmap(r"C:\Users\PC\assistente\ab.ico")
except Exception as e:
    print(f"Erro ao carregar o ícone: {e}")

# Configuração do modelo Gemini
model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

# Área de chat (ScrolledText)
chat_area = scrolledtext.ScrolledText(
    janela, wrap=tk.WORD, state=tk.DISABLED, font=("Arial", 14), bg="#ffffff")
chat_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Configuração de tags para cores, estilos e alinhamento
chat_area.tag_configure("user_tag", background="#cefcef", font=("Arial", 14), spacing3=10, justify="right")
chat_area.tag_configure("assistant_tag", background="#e8f5e9", font=("Arial", 14), spacing3=10, justify="left")

# Tags para texto em negrito
bold_font = ("Arial", 14, "bold")
chat_area.tag_configure("user_bold", font=bold_font, justify="right")
chat_area.tag_configure("assistant_bold", font=bold_font, justify="left")

# Frame para o campo de entrada e botões
frame_entrada = ttk.Frame(janela)
frame_entrada.pack(padx=10, pady=10, fill=tk.X)

# Campo de entrada de texto
entrada = ttk.Entry(frame_entrada, font=("Arial", 14))
entrada.pack(side=tk.LEFT, fill=tk.X, expand=True)

# Botão de enviar
botao_enviar = ttk.Button(frame_entrada, text="Enviar", bootstyle=PRIMARY, command=enviar_mensagem)
botao_enviar.pack(side=tk.LEFT, padx=5)

# Botão de histórico
botao_historico = ttk.Button(frame_entrada, text="Histórico", bootstyle=INFO, command=exibir_historico)
botao_historico.pack(side=tk.LEFT, padx=5)

# Botão para salvar histórico em .txt
botao_salvar_txt = ttk.Button(frame_entrada, text="Salvar Histórico (.txt)", bootstyle=SUCCESS, command=salvar_historico_txt)
botao_salvar_txt.pack(side=tk.LEFT, padx=5)

# Botão de sair
botao_sair = ttk.Button(frame_entrada, text="Sair", bootstyle=DANGER, command=sair_programa)
botao_sair.pack(side=tk.LEFT)

# Label para a animação de carregamento
label_carregamento = ttk.Label(janela, text="", font=("Arial", 12))
label_carregamento.pack(pady=5)

# Mensagem inicial do assistente
chat_area.config(state=tk.NORMAL)
chat_area.insert(tk.END, "Assistente\n", "assistant_bold")
chat_area.insert(tk.END, "Bem-vindo ao Assistente AB Areias! Em que posso ajudar?\n\n", "assistant_tag")
chat_area.config(state=tk.DISABLED)

# Configuração de redimensionamento da janela
janela.grid_rowconfigure(0, weight=1)
janela.grid_columnconfigure(0, weight=1)

# Vincular o evento de pressionar Enter ao campo de entrada
janela.bind("<Return>", lambda event: enviar_mensagem())

# Variável global para controlar a animação de carregamento
carregando = False

# Inicia a aplicação
janela.mainloop()