import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
import sqlite3
from tkcalendar import DateEntry


def criar_tabelas():
    conn = sqlite3.connect('frequencia.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        data_matricula DATE,
        certificado BOOLEAN DEFAULT 0
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Aulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        assunto TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Presencas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_aluno INTEGER,
        id_aula INTEGER,
        presente BOOLEAN,
        FOREIGN KEY(id_aluno) REFERENCES Alunos(id),
        FOREIGN KEY(id_aula) REFERENCES Aulas(id)
    )
    ''')

    conn.commit()
    conn.close()

# Funções do banco
def conectar_db():
    return sqlite3.connect('frequencia.db')

def cadastrar_aluno(nome, telefone, data_matricula):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Alunos (nome, telefone, data_matricula) VALUES (?, ?, ?)',
                   (nome, telefone, data_matricula))
    conn.commit()
    conn.close()

def cadastrar_aula(data, assunto):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Aulas (data, assunto) VALUES (?, ?)', (data, assunto))
    conn.commit()
    conn.close()




def criar_interface():
        
    #Colocar mascara de telefone "(00) 00000-0000"
    def aplicar_mascara_telefone(event):
        texto = entry_telefone.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        novo_texto = ""

        if len(texto) >= 2:
            novo_texto += "(" + texto[:2] + ") "
        if len(texto) >= 7:
            novo_texto += texto[2:7] + "-"
        if len(texto) > 7:
            novo_texto += texto[7:11]
        else:
            novo_texto += texto[7:]

        entry_telefone.delete(0, tk.END)
        entry_telefone.insert(0, novo_texto)

    #Deixa as letras maiusculas
    def aplicar_mascara_nome(event):
        texto = entry_nome.get()
        novo_texto = texto.upper()
        entry_nome.delete(0, tk.END)
        entry_nome.insert(0, novo_texto)

    # Coloca a mascara de data "00/00/0000" 
    def aplicar_mascara_data(event):
        widget = event.widget if event else entry_data_aula  # padrão para aula se não tiver evento
        texto = widget.get().replace("/", "")
        novo_texto = ""

        if len(texto) >= 2:
            novo_texto += texto[:2] + "/"
        if len(texto) >= 4:
            novo_texto += texto[2:4] + "/"
        if len(texto) > 4:
            novo_texto += texto[4:8]
        else:
            novo_texto += texto[4:]

        widget.delete(0, tk.END)
        widget.insert(0, novo_texto)


    def formatar_para_iso(data_br):
        return datetime.strptime(data_br, "%d/%m/%Y").date().isoformat()
        
        
    root = tk.Tk()
    root.title("Sistema de Frequência de Alunos EDUCAR- Versão 1.0")
    root.geometry('700x500')
    root.resizable(False, False)
    #root.iconbitmap('imagens/icone.ico')  # Coloca o icone do programa

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)
    
    
    # Aba 1 - Aluno
    frame_aluno = ttk.Frame(notebook)
    notebook.add(frame_aluno, text="Cadastrar Aluno")
    
    tk.Label(frame_aluno, text="Nome:").grid(row=0, column=0,sticky='e', pady=5)
    
    entry_nome = tk.Entry(frame_aluno, relief="groove", width=80)
    entry_nome.grid(row=0, column=1, pady=5)
    entry_nome.bind("<KeyRelease>", aplicar_mascara_nome)


    tk.Label(frame_aluno, text="Telefone:").grid(row=1, column=0,sticky='e', pady=5)
    
    entry_telefone = tk.Entry(frame_aluno, relief="groove", width=25)
    entry_telefone.grid(row=1, column=1,sticky='w', pady=5)
    entry_telefone.bind("<FocusOut>", aplicar_mascara_telefone)

    
    tk.Label(frame_aluno, text="Data de Cadastro:").grid(row=2, column=0, pady=2,sticky='e')

    
    entry_data_cadastro = tk.Entry(frame_aluno, relief="groove")
    entry_data_cadastro.grid(row=2, column=1,sticky='w', pady=5)
    
    entry_data_cadastro.insert(0, date.today().strftime("%d/%m/%Y"))  # Preenche com a data atual
    entry_data_cadastro.bind("<FocusOut>", aplicar_mascara_data)


    def salvar_aluno():
        nome = entry_nome.get().strip()
        telefone = entry_telefone.get().strip()
        data = entry_data_cadastro.get().strip()
        
        try:
            data_iso = formatar_para_iso(data)
            cadastrar_aluno(nome, telefone, data_iso)
            messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso!")
            entry_nome.delete(0, tk.END)
            entry_telefone.delete(0, tk.END)
            entry_data_cadastro.delete(0, tk.END)
            entry_data_cadastro.insert(0, date.today().strftime("%d/%m/%Y"))
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA")

    btn_salvar_aluno = tk.Button(frame_aluno, text="Salvar", width=15, command=salvar_aluno)
    btn_salvar_aluno.grid(row=4, column=0, columnspan=2, pady=40)


    # Aba 2 - Aula
    frame_aula = ttk.Frame(notebook)
    notebook.add(frame_aula, text="Cadastrar Aula", padding=10)

    tk.Label(frame_aula, text="Assunto:").grid(row=0, column=0, pady=5, sticky='e')
    
    entry_assunto = tk.Entry(frame_aula, relief="groove", width=40)
    entry_assunto.grid(row=0, column=1, sticky='w', pady=5) 
    entry_assunto.bind("<KeyRelease>", aplicar_mascara_nome)


    tk.Label(frame_aula, text="Data:").grid(row=1, column=0, pady=5, sticky='e')
    entry_data_aula = tk.Entry(frame_aula, relief="groove", width=20)
    entry_data_aula.grid(row=1, column=1, sticky='w', pady=5)
    entry_data_aula.bind("<FocusOut>", aplicar_mascara_data)
  
  
    def salvar_aula():

        assunto = entry_assunto.get().strip()
        data = entry_data_aula.get().strip()

        if not assunto:
            messagebox.showwarning("Atenção", "O campo 'Assunto' não pode estar vazio.")
            return

        try:
            data_iso = formatar_para_iso(data)
            cadastrar_aula(data_iso, assunto)
            messagebox.showinfo("Sucesso", "Aula cadastrada com sucesso!")
            entry_assunto.delete(0, tk.END)
            entry_data_aula.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Data inválida. Use o formato DD/MM/AAAA.")

  
    btn_salvar_aula=tk.Button(frame_aula, text="Salvar", width=15, command=salvar_aula)
    btn_salvar_aula.grid(row=4, column=0, columnspan=2, pady=40)
    
    
    
    # Aba 3 - Presença
    frame_presenca = ttk.Frame(notebook)
    notebook.add(frame_presenca, text="Registrar Presença")
    tk.Label(frame_presenca, text="Selecione a data da aula:").pack(pady=5)

    date_entry = DateEntry(frame_presenca, width=12, background='darkblue',
                           foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
    date_entry.pack(pady=5)

    frame_lista_presenca = tk.Frame(frame_presenca)
    frame_lista_presenca.pack(fill='both', expand=True)



    root.mainloop()








criar_tabelas()

criar_interface()
