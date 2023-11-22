from lexer import Lexer

class ASTNode:
    pass

class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Num(ASTNode):
    def __init__(self, value):
        self.value = value

class VarAssign(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class Var(ASTNode):
    def __init__(self, name):
        self.name = name

class Print(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class NoOp(ASTNode):
    pass

class Input(ASTNode):
    def __init__(self, solicitud):
        self.prompt = solicitud
        
class String(ASTNode):
    def __init__(self, value):
        self.value = value
        
class PrintMultiple(ASTNode):
    def __init__(self, args):
        self.args = args

class RelOp(ASTNode):  # New class for relational operators
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
        
class Conditional(ASTNode):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        
class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value
    def __repr__(self):  # Optional, for debugging and printing the node
        return f'StringLiteral({self.value})'

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.tokens = lexer.tokenize()
        self.current_token = self.tokens.pop(0)
    
    def error(self):
        raise Exception('Invalid syntax')
    
    def eat(self, token_type):
        if self.current_token[0] == token_type:
            if self.tokens: 
                self.current_token = self.tokens.pop(0)
            else:
                self.current_token = ('EOF', None) 
        else:
            self.error()
    
    # Reemplazo de nombres en inglés por nombres en español
    def factor(self):
        """ factor : NUM | ID | CADENA | sentencia_entrada """
        token = self.current_token
        if token[0] == 'NUM':
            self.eat('NUM')
            return Num(token[1])
        elif token[0] == 'ID':
            self.eat('ID')
            return Var(token[1])
        elif token[0] == 'CADENA':
            value = token[1][1:-1]
            self.eat('CADENA')
            return String(value)
        elif token[0] == 'ESCANEAR':
            return self.sentencia_entrada()
        self.error()
    
    def termino(self):
        """ termino : factor ((MULT | DIV) factor)* """
        node = self.factor()
        while self.current_token[0] in ('MULT', 'DIV'):
            op = self.current_token
            if op[0] == 'MULT':
                self.eat('MULT')
            elif op[0] == 'DIV':
                self.eat('DIV')
            else:
                self.error()
            node = BinOp(left=node, op=op, right=self.factor())
        return node
    
    def expresion(self):
        """ expresion : comparacion ((SUMA | RESTA) comparacion)* """
        node = self.comparacion()
        while self.current_token[0] in ('SUMA', 'RESTA'):
            op = self.current_token
            if op[0] == 'SUMA':
                self.eat('SUMA')
            elif op[0] == 'RESTA':
                self.eat('RESTA')
            else:
                self.error()
            node = BinOp(left=node, op=op, right=self.comparacion())
        return node
    
    def bloque(self):
        """ bloque : LLAVE_I sentencia* LLAVE_D """
        self.eat('LLAVE_I')
        sentencias = []
        while self.current_token[0] != 'LLAVE_D':
            sentencias.append(self.sentencia())
        self.eat('LLAVE_D')
        return sentencias
    
    def tipo(self):
        """ tipo : ENTERO """
        if self.current_token[0] == 'ENTERO':
            self.eat('ENTERO')
        else:
            self.error()
    
    def comparacion(self):
        """ comparacion : termino ((MAYOR | MENOR | IGUAL | MAYOR_IGUAL | MENOR_IGUAL | NO_IGUAL) termino)* """
        node = self.termino()
        while self.current_token[0] in ('MAYOR', 'MENOR', 'IGUAL', 'MAYOR_IGUAL', 'MENOR_IGUAL', 'NO_IGUAL'):
            op = self.current_token
            if op[0] == 'MAYOR':
                self.eat('MAYOR')
            elif op[0] == 'MENOR':
                self.eat('MENOR')
            elif op[0] == 'IGUAL':
                self.eat('IGUAL')
            elif op[0] == 'MAYOR_IGUAL':
                self.eat('MAYOR_IGUAL')
            elif op[0] == 'MENOR_IGUAL':
                self.eat('MENOR_IGUAL')
            elif op[0] == 'NO_IGUAL':
                self.eat('NO_IGUAL')
            # Continue parsing the right side of the comparison to form a binary operation
            right = self.termino()
            node = BinOp(left=node, op=op, right=right)
        return node
    
    def string_expression(self):
        token = self.current_token
        if token.type == 'STRING':
            self.eat('STRING')
            return StringLiteral(token.value)
        else:
            # Handle other expressions as before
            ...
    
    def sentencia_asignacion(self):
        """sentencia_asignacion : ID ASIGNACION expresion"""
        token_type, nombre_var = self.current_token  # Assuming the type is the first element.
        self.eat('ID')
        self.eat('ASIGNACION')
        if self.current_token[0] == 'STRING':  # self.current_token is a tuple, access type with [0].
            nodo_expresion = self.string_expression()
        else:
            nodo_expresion = self.expresion()
        return VarAssign(name=nombre_var, value=nodo_expresion)

    
    def sentencia_si(self):
        """ sentencia_si : si PAREN_I expresion PAREN_D bloque (sino bloque)? """
        self.eat('si')
        self.eat('PAREN_I')
        condition = self.expresion()
        self.eat('PAREN_D')
        true_block = self.bloque()
        false_block = None
        if self.current_token[0] == 'sino':
            self.eat('sino')
            false_block = self.bloque()
        return Conditional(condition=condition, true_block=true_block, false_block=false_block)
    
    def sentencia(self):
        """ sentencia : sentencia_asignacion | sentencia_imprimir | sentencia_entrada | sentencia_si | bloque | vacio """
        if self.current_token[0] == 'ID' and self.tokens[0][0] == 'ESCANEAR':  
            nodo = self.sentencia_asignacion_entrada()
        elif self.current_token[0] == 'ID':
            nodo = self.sentencia_asignacion()
        elif self.current_token[0] == 'IMPRIMIR':
            nodo = self.sentencia_imprimir()
        elif self.current_token[0] == 'ESCANEAR':
            nodo = self.sentencia_entrada()
        elif self.current_token[0] == 'si':
            nodo = self.sentencia_si()
        else:
            nodo = self.vacio()
        return nodo
    
    def sentencia_asignacion_entrada(self):
        """ sentencia_asignacion_entrada : ID 'escanear' '(' CADENA ')' """
        nombre_var = self.current_token[1]
        self.eat('ID')
        nodo_entrada = self.sentencia_entrada()
        return VarAssign(name=nombre_var, valor=nodo_entrada)
    
    def sentencia_entrada(self):
        """sentencia_entrada : 'ESCANEAR' '(' CADENA ')'"""
        self.eat('ESCANEAR')
        self.eat('PAREN_I')
        solicitud = None
        if self.current_token[0] == 'CADENA':
            solicitud = self.current_token[1][1:-1]
            self.eat('CADENA')
        self.eat('PAREN_D')
        return Input(solicitud=solicitud)
    
    def lista_argumentos(self):
        args = [self.argumento()]
        while self.current_token[0] == 'COMA':
            self.eat('COMA')
            args.append(self.argumento())
        return args
    
    def argumento(self):
        token = self.current_token
        if token[0] == 'CADENA':
            valor = token[1][1:-1]
            self.eat('CADENA')
            return String(valor)
        else:
            return self.expresion()
    
    def sentencia_imprimir(self):
        """ sentencia_imprimir : 'IMPRIMIR' '(' lista_argumentos ')' """
        self.eat('IMPRIMIR')
        self.eat('PAREN_I')
        args = self.lista_argumentos()
        self.eat('PAREN_D')
        if len(args) == 1:
            return Print(args[0])
        else:
            return PrintMultiple(args)
   
    def vacio(self):
        return NoOp()
    
    def parse(self):
        """ parse : sentencia+ """
        sentencias = []
        while self.current_token[0] != 'EOF':
            sentencias.append(self.sentencia())
            while self.current_token[0] == 'NUEVAL':
                self.eat('NUEVAL')
        return sentencias