import tkinter as tk

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("App com Múltiplas Telas")
        self.frames = {}

        for F in (TelaInicial, TelaSecundaria):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.mostrar_tela(TelaInicial)

    def mostrar_tela(self, tela):
        frame = self.frames[tela]
        frame.tkraise()

class TelaInicial(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Tela Inicial").pack()
        tk.Button(self, text="Ir para Tela Secundária",
                  command=lambda: master.mostrar_tela(TelaSecundaria)).pack()

class TelaSecundaria(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Tela Secundária").pack()
        tk.Button(self, text="Voltar", 
                  command=lambda: master.mostrar_tela(TelaInicial)).pack()

App().mainloop()
