import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
from lexer import Lexer
from parser1 import Parser
from interpreter import Interpreter
from parser1 import ASTNode
import subprocess
import os
import re

class ResultsWindow(tk.Toplevel):
    def __init__(self, parent, results):
        super().__init__(parent)
        self.title('Analysis Results')
        self.geometry('400x300')

        style = ttk.Style(self)
        style.configure('TLabel', foreground='green', background='black')
        style.configure('TText', foreground='green', background='black')

        results_label = ttk.Label(self, text='Analysis Results', style='TLabel')
        results_label.pack(pady=5)

        results_text = scrolledtext.ScrolledText(self, wrap='word', font=('Courier', 10))
        results_text.insert('1.0', results)
        results_text.pack(expand=True, fill='both', padx=10, pady=5)
        
class PyCompilerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Capa Code')
        self.configure(bg='white')

        style = ttk.Style(self)
        style.theme_use('alt')

        # Create menu
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        self.config(menu=menu_bar)

        # Text Area Frame
        text_frame = ttk.Frame(self)
        text_frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Line numbers for text_area
        self.line_numbers = tk.Text(text_frame, width=2, padx=3, takefocus=0, border=0,
                                    background='lightgrey', state='disabled', wrap='none')
        self.line_numbers.pack(side='left', fill='y')

        self.text_area = scrolledtext.ScrolledText(text_frame, height=5, undo=True)
        self.text_area.pack(expand=True, fill='both', padx=(0, 10))
        self.text_area.bind('<KeyRelease>', self.on_key_release)

        self.translated_code_label = ttk.Label(self, text='Translated Python Code:')
        self.translated_code_label.pack(fill='x', padx=10, pady=(5, 0))

        self.translated_code_area = scrolledtext.ScrolledText(self, height=10, state='disabled')
        self.translated_code_area.pack(expand=True, fill='both', side='right', padx=10, pady=5)

        # Output Area Frame
        output_frame = ttk.Frame(self)
        output_frame.pack(expand=True, fill='both', padx=2, pady=2)

        self.output_area = scrolledtext.ScrolledText(output_frame, height=10, background='black', foreground='yellow')
        self.output_area.pack(expand=True, fill='both')

        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        self.run_btn = ttk.Button(btn_frame, text='Run', command=self.run_code)
        self.run_btn.pack(side='left', padx=2)

        self.analysis_btn = ttk.Button(btn_frame, text='Analyze', command=self.analyze_code)
        self.analysis_btn.pack(side='left', padx=2)

        self.compile_btn = ttk.Button(btn_frame, text='Compile', command=self.create_executable)
        self.compile_btn.pack(side='right', anchor='e', padx=2)

        self.current_open_file = None
        self.update_line_numbers()


    def update_line_numbers(self):
        '''Update the line numbers in the line_numbers Text widget.'''
        line_numbers = ''
        if self.text_area.index('end-1c') != "1.0":
            line_numbers += '\n'.join(str(i) for i in range(1, int(self.text_area.index('end-1c').split('.')[0])))
        self.line_numbers.configure(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers)
        self.line_numbers.configure(state='disabled')

    def on_key_release(self, event=None):
        self.update_line_numbers()

    def open_file(self):
        file = filedialog.askopenfile(mode='r')
        if file:
            code = file.read()
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', code)
            self.current_open_file = file.name
            self.highlight_syntax()
            file.close()
            self.update_line_numbers()

    # Other class methods remain unchanged, except for the addition of
    # update_line_numbers within methods that modify the text_area content.
    
    def highlight_syntax(self):
        '''Apply syntax highlighting to the text in the text_area.'''
        self.text_area.tag_remove("Token.Keyword", "1.0", tk.END)
        self.text_area.tag_remove("Token.Number", "1.0", tk.END)
        # Define tags for syntax highlighting
        self.text_area.tag_configure("Token.Keyword", foreground="blue")
        self.text_area.tag_configure("Token.Number", foreground="red")
        code = self.text_area.get("1.0", tk.END)
        lexer = Lexer(code)
        for token_type, token_value in lexer.tokenize():
            # Esta es una simplificación, necesitas las posiciones exactas del texto para aplicar correctamente los tags.
            if token_type == 'PRINT':
                self.text_area.tag_add("Token.Keyword", "1.0", "end")
            elif token_type == 'NUM':
                self.text_area.tag_add("Token.Number", "1.0", "end")
                
    def translate_source_code(self, source_code):
        python_code = source_code

        # Traducir imprimir() con texto dentro

        # Resto de las traducciones
        if 'Si' in python_code:
            python_code = python_code.replace('Si', 'if')
            python_code = python_code.replace('{', ':')
            python_code = python_code.replace('}', '')

        if 'sino' in python_code:
            python_code = python_code.replace('sino', 'else')
            
        if 'escanear()' in python_code:
            python_code = python_code.replace('escanear()', 'input()')
        match = re.search(r'imprimir\((.*?)\)', python_code)
        while match:
            content_inside_parentheses = match.group(1)
            translated_line = f'print({content_inside_parentheses})'
            python_code = python_code.replace(f'imprimir({content_inside_parentheses})', translated_line, 1)
            match = re.search(r'imprimir\((.*?)\)', python_code)

    # Traducir escanear() con texto dentro
        match = re.search(r'escanear\("(.*?)"\)', python_code)
        while match:
            text_to_scan = match.group(1)
            translated_line = f'input("{text_to_scan}")'
            python_code = python_code.replace(f'escanear("{text_to_scan}")', translated_line, 1)
            match = re.search(r'escanear\("(.*?)"\)', python_code)
        return python_code
    
    def run_code(self):
        self.output_area.configure(state='normal')
        self.output_area.delete('1.0', tk.END)
        code = self.text_area.get('1.0', tk.END)
        lexer = Lexer(code)
        parser = Parser(lexer)
        tree = parser.parse()
        interpreter = Interpreter(tree, self.output_area)
        interpreter.interpret()
        self.highlight_syntax()
        self.output_area.insert(tk.END, "\n")  # Esto agregará el salto de línea después de la ejecución del código.
        self.output_area.configure(state='disabled')
        
        translated_code = self.translate_source_code(self.text_area.get('1.0', tk.END))
        # Actualiza el área de texto del código traducido
        self.translated_code_area.configure(state='normal')
        self.translated_code_area.delete('1.0', tk.END)
        self.translated_code_area.insert('1.0', translated_code)
        self.translated_code_area.configure(state='disabled')
        exec(translated_code)
        
    def analyze_code(self):
        code = self.text_area.get('1.0', tk.END)
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(Lexer(code))

        analysis_results = f"Tokens:\n{tokens}\n\nAbstract Syntax Tree:\n"
        try:
            tree = parser.parse()
            analysis_results += self.tree_to_string(tree)
        except Exception as e:
            analysis_results += str(e)

        # Abre la nueva ventana con los resultados del análisis
        ResultsWindow(self, analysis_results)
    
    def tree_to_string(self, nodes, level=0):
        tree_str = ""
        if not isinstance(nodes, list):
            nodes = [nodes]
        for node in nodes:
            tree_str += "  " * level + repr(node) + "\n"
            for attr in node.__dict__.values():
                if isinstance(attr, ASTNode) or isinstance(attr, list):
                    tree_str += self.tree_to_string(attr, level + 1)
        return tree_str
    
    
    def save_file(self):

            translated_file = filedialog.asksaveasfile(defaultextension='.mylang',
                                                       filetypes=[("MyLang Files", "*.capa"), ("All Files", "*.*")])
            if translated_file:
                translated_text_to_save = self.translated_code_area.get('1.0', tk.END)
                translated_file.write(translated_text_to_save)
                self.current_open_file = translated_file.name
                translated_file.close()
            
    def create_executable(self):
        if not self.current_open_file:
            self.save_file()
        
        # Guardamos el contenido de `text_area` en el archivo actual abierto.
        if self.current_open_file:
            with open(self.current_open_file, 'w') as file:
                code_to_save = self.translated_code_area.get('1.0', tk.END)
                file.write(code_to_save)
            
            # Obtenemos la ruta de la carpeta del archivo actual
            file_folder = os.path.dirname(self.current_open_file)
            
            # Compilamos con pyinstaller
            dist_path = os.path.join(file_folder, 'dist')
            build_path = os.path.join(file_folder, 'build')
            
            # Creamos las carpetas si no existen
            if not os.path.exists(dist_path):
                os.makedirs(dist_path)
            if not os.path.exists(build_path):
                os.makedirs(build_path)
            
            # Llamada a pyinstaller con las rutas personalizadas para 'dist' y 'build'
            subprocess.call([
                "pyinstaller",
                "--noconfirm",  # Sobrescribir sin preguntar
                "--onefile",  # Un solo archivo
                "--distpath", dist_path,  # Ruta de la carpeta de distribución
                "--workpath", build_path,  # Ruta de la carpeta de trabajo/build
                self.current_open_file  # Archivo a compilar
            ])

if __name__ == '__main__':
    app = PyCompilerApp()
    app.mainloop()