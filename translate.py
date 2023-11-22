# custom_compiler.py

# custom_compiler.py

def translate_keywords(custom_code):
    translation_map = {
        'entero': 'int',
        'escanear': 'input',
        'Si': 'if',
        'SiNo': 'else',
        'imprimir': 'print',
    }

    # Utiliza la función replace con el diccionario de traducción
    for keyword, translation in translation_map.items():
        custom_code = custom_code.replace(keyword, translation)

    # Elimina los puntos y coma, paréntesis de la condicional y llaves de la condicional
    custom_code = custom_code.replace(';', '')
    custom_code = custom_code.replace('(', '')
    custom_code = custom_code.replace(')', '')
    custom_code = custom_code.replace('{', '')
    custom_code = custom_code.replace('}', '')

    # Utiliza la función replace con el diccionario de traducción
    for keyword, translation in translation_map.items():
        custom_code = custom_code.replace(keyword, translation)

    return custom_code
