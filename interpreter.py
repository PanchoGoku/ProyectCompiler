from parser1 import Parser
import tkinter as tk
from parser1 import ASTNode
from tkinter import simpledialog

class Input(ASTNode):
    def __init__(self, var_name):
        self.var_name = var_name

class PrintMultiple(ASTNode):
    def __init__(self, args):
        self.args = args
        
class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements
        
class Conditional(ASTNode):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
        
class VarDecl(ASTNode):
    def __init__(self, var_type, var_name, var_value=None):
        self.var_type = var_type
        self.var_name = var_name
        self.var_value = var_value
        
class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Interpreter:
    def __init__(self, tree, output_area):
        self.tree = tree
        self.variables = {}
        self.output_area = output_area  # Agrega esta línea para asignar output_area
    
    def visit_Print(self, node):
        # El método ahora sólo maneja un único argumento
        value = self.visit(node.expr)
        self.output_to_area(str(value))
    
    def visit_PrintMultiple(self, node):
        # Nuevo método para manejar múltiples argumentos en el print
        values = [self.visit(arg) for arg in node.args]
        self.output_to_area(' '.join(map(str, values)) + '\n')
        
    def visit_Input(self, node):

        #Se espera que el nodo ya contenga el nombre de la variable como self.var_name
        #Deberíamos también tomar el prompt del nodo
        value = simpledialog.askstring("Input", node.prompt)
        if value is None: # Manejamos la acción de cancelar en el diálogo
            raise Exception("Input was cancelled by the user.")

        #Convertimos el valor a int si es posible
        try:
            value = int(value)
        except ValueError:
            pass
        return value # Retornamos el valor para que visit_VarAssign lo maneje

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.no_visit_method)
        if isinstance(node, PrintMultiple):
            return self.visit_PrintMultiple(node)
        else:
            # Original visit method processing
            method_name = 'visit_' + type(node).__name__
            visitor = getattr(self, method_name, self.no_visit_method)
            return visitor(node)
        
    def visit_Block(self, node):
        for statement in node.statements:
            self.visit(statement)
        
    def visit_Conditional(self, node):
        """ Visit a Conditional node and execute the true_block or false_block based on the condition evaluation. """
        condition_value = self.visit(node.condition)
        if condition_value:
            for statement in node.true_block:
                self.visit(statement)
        elif node.false_block:  # Check if there is an 'else' block
            for statement in node.false_block:
                self.visit(statement)
                
    def visit_VarDecl(self, node):
        """ Visits a variable declaration node, which might specify a type. """
        # In this simple language, we don't enforce types, but this would be the place to do so
        var_name = node.var_name
        var_value = None if node.var_value is None else self.visit(node.var_value)
        self.variables[var_name] = var_value
    
    def no_visit_method(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')
    
    def visit_BinOp(self, node):
        # Updated operator names to match those from parser1.py
        if node.op[0] == 'SUMA':
            return self.visit(node.left) + self.visit(node.right)
        elif node.op[0] == 'RESTA':
            return self.visit(node.left) - self.visit(node.right)
        elif node.op[0] == 'MULT':
            return self.visit(node.left) * self.visit(node.right)
        elif node.op[0] == 'DIV':
            return self.visit(node.left) / self.visit(node.right)
        elif node.op[0] == 'MAYOR':
            return self.visit(node.left) > self.visit(node.right)
        elif node.op[0] == 'MENOR':
            return self.visit(node.left) < self.visit(node.right)
        elif node.op[0] == 'IGUAL':
            return self.visit(node.left) == self.visit(node.right)
        elif node.op[0] == 'MAYOR_IGUAL':
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op[0] == 'MENOR_IGUAL':
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op[0] == 'NO_IGUAL':
            return self.visit(node.left) != self.visit(node.right)
        else:
            self.no_visit_method(node)
    
    def visit_Num(self, node):
        return node.value
    
    def visit_String(self, node):
        return node.value  # node.value should hold the string value
    
    def visit_VarAssign(self, node):
        # Este método asigna el valor a la variable
        var_name = node.name
        value = self.visit(node.value)  # Podría ser un nodo Input, Expr, Num, etc.
        self.variables[var_name] = value
    
    def visit_Var(self, node):
        value = self.variables.get(node.name)
        if value is None:
            raise NameError(repr(node.name))
        else:
            return value
    def output_to_area(self, text):
        self.output_area.configure(state='normal')
        self.output_area.insert(tk.END, text)
        self.output_area.configure(state='disabled')
    
    def interpret(self):
        for node in self.tree:
            self.visit(node)
        return self.variables
