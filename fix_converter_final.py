#!/usr/bin/env python3
"""
Script final para corregir ir_to_sql_converter.py
"""

def fix_converter_final():
    """Corregir definitivamente el conversor"""
    
    # Leer el archivo
    with open('ir_to_sql_converter.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir en líneas
    lines = content.split('\n')
    new_lines = []
    inside_main = False
    
    for line in lines:
        if line.strip() == 'def main():':
            inside_main = True
            new_lines.append(line)
        elif inside_main and line.strip() == 'if __name__ == "__main__":':
            # Terminar la función main aquí
            inside_main = False
            new_lines.append('')  # Línea vacía
            new_lines.append('if __name__ == "__main__":')
        elif inside_main and line.strip() == 'main()':
            new_lines.append('    main()')
        else:
            new_lines.append(line)
    
    # Escribir el archivo corregido
    with open('ir_to_sql_converter.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print('✅ Conversor corregido definitivamente')

if __name__ == "__main__":
    fix_converter_final()