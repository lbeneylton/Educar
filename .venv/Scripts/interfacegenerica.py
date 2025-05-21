import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import date, datetime
import sqlite3

# ------------------- Utilitários de Data -------------------

def br_to_iso(data_str):
    try:
        return datetime.strptime(data_str, '%d-%m-%Y').date()
    except ValueError:
        messagebox.showerror("Erro", "Formato de data inválido. Use DD-MM-YYYY.")
        return None

def iso_to_br(data_str):
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        return data.strftime('%d-%m-%Y')
    except ValueError:
        messagebox.showerror("Erro", "Formato de data inválido. Use YYYY-MM-DD.")
        return None

# ------------------- Banco de Dados -------------------

def conectar_db():
    return sqlite3.connect('frequencia.db')

def criar_tabelas():
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        telefone TEXT,
        data_matricula DATE,
        certificado BOOLEAN DEFAULT 0
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Aulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE,
        assunto TEXT
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Presencas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_aluno INTEGER,
        id_aula INTEGER,
        presente BOOLEAN,
        FOREIGN KEY(id_aluno) REFERENCES Alunos(id),
        FOREIGN KEY(id_aula) REFERENCES Aulas(id)
    )''')

    conn.commit()
    conn.close()

# ------------------- Operações de Aluno -------------------

def aluno_existe(nome):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Alunos WHERE nome = ?', (nome,))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def cadastrar_aluno(nome, telefone, data_matricula):
    if not nome or not telefone or not data_matricula:
        messagebox.showerror("Erro", "Nome, telefone e data de matrícula são obrigatórios.")
        return

    nome = nome.upper()
    if aluno_existe(nome):
        messagebox.showerror("Erro", "Aluno já cadastrado.")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Alunos (nome, telefone, data_matricula) VALUES (?, ?, ?)',
                   (nome, telefone, data_matricula))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Aluno cadastrado com sucesso.")

def aulas_restantes(id_aluno):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute('SELECT certificado FROM Alunos WHERE id = ?', (id_aluno,))
    resultado = cursor.fetchone()
    if not resultado:
        conn.close()
        messagebox.showerror("Erro", f"Aluno com ID {id_aluno} não encontrado.")
        return []

    if resultado[0]:
        conn.close()
        return []

    cursor.execute('''
        SELECT Aulas.data, Aulas.assunto
        FROM Aulas
        WHERE Aulas.id NOT IN (
            SELECT id_aula FROM Presencas
            WHERE id_aluno = ? AND presente = 1
        )
        ORDER BY Aulas.data
    ''', (id_aluno,))
    
    aulas = cursor.fetchall()
    conn.close()
    return aulas

# ------------------- Operações de Aula -------------------

def aula_existe(data, assunto):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM Aulas WHERE data = ? AND assunto = ?', (data, assunto))
    existe = cursor.fetchone() is not None
    conn.close()
    return existe

def cadastrar_aula(data, assunto):
    if not data or not assunto:
        messagebox.showerror("Erro", "Data e assunto são obrigatórios.")
        return

    assunto = assunto.upper()
    if aula_existe(data, assunto):
        messagebox.showerror("Erro", "Aula já cadastrada.")
        return

    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Aulas (data, assunto) VALUES (?, ?)', (data, assunto))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sucesso", "Aula cadastrada com sucesso.")

def buscar_frequencia(data):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Aulas WHERE data = ?', (data,))
    aula = cursor.fetchone()
    if not aula:
        conn.close()
        messagebox.showerror("Erro", "Aula não encontrada.")
        return None

    assunto = aula[2]
    cursor.execute('''
        SELECT Alunos.id, Alunos.nome, Alunos.telefone
        FROM Alunos
        LEFT JOIN Presencas ON Alunos.id = Presencas.id_aluno AND Presencas.id_aula = ?
        WHERE Presencas.id IS NULL AND Alunos.certificado = 0
    ''', (aula[0],))

    alunos = cursor.fetchall()
    conn.close()
    return aula[0], assunto, alunos

def presenca_aluno(id_aluno, id_aula, presente):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Presencas (id_aluno, id_aula, presente) VALUES (?, ?, ?)',
                   (id_aluno, id_aula, presente))
    conn.commit()
    conn.close()

# ------------------- Interface Gráfica -------------------

def criar_interface():
    def mascarar_telefone(event):
        texto = telefone_entry.get().replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
        novo = ""
        if len(texto) >= 2:
            novo += f"({texto[:2]}) "
        if len(texto) >= 7:
            novo += texto[2:7] + "-"
        novo += texto[7:]
        telefone_entry.delete(0, tk.END)
        telefone_entry.insert(0, novo)

    def upper_case_entry(event):
        widget = event.widget
        texto = widget.get()
        widget.delete(0, tk.END)
        widget.insert(0, texto.upper())


    def gerar_grade_presenca():
        data = data_presenca.get()
        resultado = buscar_frequencia(data)
        if not resultado:
            return

        id_aula, assunto, alunos = resultado
        if not alunos:
            messagebox.showinfo("Aviso", "Nenhum aluno pendente de presença.")
            return

        janela = tk.Toplevel()
        janela.title(f"Registrar Presença - {data} - {assunto}")

        checkboxes = {}
        for i, (id_aluno, nome, _) in enumerate(alunos):
            ttk.Label(janela, text=nome).grid(row=i, column=0, sticky='w', padx=5)
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(janela, text="Presente", variable=var)
            chk.grid(row=i, column=1, sticky='w')
            checkboxes[id_aluno] = var

        def salvar():
            for id_aluno, var in checkboxes.items():
                presenca_aluno(id_aluno, id_aula, var.get())
            messagebox.showinfo("Sucesso", "Presenças registradas com sucesso.")
            janela.destroy()

        ttk.Button(janela, text="Salvar Presenças", command=salvar).grid(row=len(alunos)+1, columnspan=2, pady=10)

    # --- Janela Principal ---
    root = tk.Tk()
    root.title("Sistema de Frequência EDUCAR - v1.0")
    root.geometry('700x500')
    root.resizable(False, False)

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    # --- Aba Aluno ---
    frame_aluno = ttk.Frame(notebook)
    notebook.add(frame_aluno, text="Cadastrar Aluno")

    ttk.Label(frame_aluno, text="Nome:").grid(row=0, column=0, sticky='e', pady=5)
    nome_entry = ttk.Entry(frame_aluno, width=80)
    nome_entry.grid(row=0, column=1, pady=5)
    nome_entry.bind("<KeyRelease>", upper_case_entry)

    ttk.Label(frame_aluno, text="Telefone:").grid(row=1, column=0, sticky='e', pady=5)
    telefone_entry = ttk.Entry(frame_aluno, width=25)
    telefone_entry.grid(row=1, column=1, sticky='w', pady=5)
    telefone_entry.bind("<FocusOut>", mascarar_telefone)

    ttk.Label(frame_aluno, text="Data de Matrícula:").grid(row=2, column=0, sticky='e')
    data_matricula = DateEntry(frame_aluno, date_pattern='dd/mm/yyyy')
    data_matricula.grid(row=2, column=1, sticky='w', pady=5)
    data_matricula.set_date(date.today())

    ttk.Button(frame_aluno, text="Cadastrar Aluno",
               command=lambda: cadastrar_aluno(nome_entry.get(), telefone_entry.get(), data_matricula.get())
               ).grid(row=3, columnspan=2)

    # --- Aba Aula ---
    frame_aula = ttk.Frame(notebook)
    notebook.add(frame_aula, text="Cadastrar Aula")

    ttk.Label(frame_aula, text="Assunto:").grid(row=0, column=0, sticky='e', pady=5)
    assunto_entry = ttk.Entry(frame_aula, width=60)
    assunto_entry.grid(row=0, column=1, pady=5)
    assunto_entry.bind("<KeyRelease>", upper_case_entry)

    ttk.Label(frame_aula, text="Data:").grid(row=1, column=0, sticky='e', pady=5)
    data_aula = DateEntry(frame_aula, date_pattern='dd/mm/yyyy')
    data_aula.grid(row=1, column=1, sticky='w', pady=5)
    data_aula.set_date(date.today())

    ttk.Button(frame_aula, text="Cadastrar Aula",
               command=lambda: cadastrar_aula(data_aula.get(), assunto_entry.get())
               ).grid(row=2, columnspan=2)

    # --- Aba Presença ---
    frame_presenca = ttk.Frame(notebook)
    notebook.add(frame_presenca, text="Registrar Presença")

    ttk.Label(frame_presenca, text="Data:").grid(row=0, column=0, sticky='e', pady=5)
    data_presenca = DateEntry(frame_presenca, date_pattern='dd/mm/yyyy')
    data_presenca.grid(row=0, column=1, sticky='w', pady=5)
    data_presenca.set_date(date.today())

    ttk.Button(frame_presenca, text="Gerar grade", command=gerar_grade_presenca).grid(row=1, columnspan=2, pady=10)

    root.mainloop()

# ------------------- Execução -------------------

if __name__ == "__main__":
    criar_tabelas()
    criar_interface()
