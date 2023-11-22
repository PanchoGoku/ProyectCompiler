import re

# Especificaciones de los tokens
token_specs = [
    ('NUM',          r'\d+(\.\d*)?'),                  # Número entero o decimal
    ('SUMA',         r'\+'),                           # Símbolo de suma
    ('RESTA',        r'-'),                            # Símbolo de resta
    ('MULT',         r'\*'),                           # Símbolo de multiplicación
    ('DIV',          r'\/'),                           # Símbolo de división
    ('IGUAL',        r'=='),                           # Igual a
    ('NO_IGUAL',     r'!='),                           # No igual a
    ('MAYOR',        r'>'),                            # Mayor que
    ('MENOR',        r'<'),                            # Menor que
    ('MAYOR_IGUAL',  r'>='),                           # Mayor o igual a
    ('MENOR_IGUAL',  r'<='),                           # Menor o igual a
    ('ASIGNACION',   r'='),                            # Operador de asignación
    ('PAREN_I',      r'\('),                           # Paréntesis izquierdo
    ('PAREN_D',      r'\)'),                           # Paréntesis derecho
    ('LLAVE_I',      r'\{'),                           # Llave izquierda
    ('LLAVE_D',      r'\}'),                           # Llave derecha
    ('COMA',         r','),                            # Coma
    ('CADENA',       r'"(?:\\.|[^"\\])*"'),            # Cadena de caracteres
    ('ID',           r'[a-zA-Z_]\w*'),                 # Identificadores
    ('NUEVAL',       r'\n'),                           # Fin de línea
    ('OMITIR',       r'[ \t]+'),                       # Espacios y tabs a ignorar
    ('entero',       r'entero'),                       # Declaración de tipo entero
    ('si',           r'si'),                           # Condicional Si
    ('sino',         r'sino'),                         # Condicional SiNo
    ('ERROR',        r'.'),                            # Cualquier otro carácter
]

tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specs)

class Lexer:
    def __init__(self, code):
        self.tokens = []
        self.code = code
    
    def tokenize(self):
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind == 'NUM':
                value = float(value) if '.' in value else int(value)
            elif kind == 'NUEVAL':
                # Se manejarán los fin de línea en el analizador sintáctico
                continue
            elif kind == 'OMITIR':
                continue
            elif kind == 'ID':
                if value == 'imprimir':
                    kind = 'IMPRIMIR'  # Caso especial para la palabra clave 'imprimir'
                elif value == 'escanear':
                    kind = 'ESCANEAR'  # Caso especial para la palabra clave 'escanear'
                elif value in ['entero', 'Si', 'sino']:  # Palabras reservadas para tipos y condicionales
                    kind = value.lower()  # Convertir en mayúsculas para el tipo de token
            elif kind == 'ERROR':
                raise RuntimeError(f'Carácter inesperado: {value}')
            self.tokens.append((kind, value))
        self.tokens.append(('EOF', 'EOF'))  # Fin de archivo
        return self.tokens