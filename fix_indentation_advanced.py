#!/usr/bin/env python3
"""
Script avanzado para corregir el error de indentación en ir_to_sql_converter.py
"""

def fix_indentation_advanced():
    """Corregir la indentación del archivo ir_to_sql_converter.py"""
    
    # Leer el archivo
    with open('ir_to_sql_converter.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    corrected_lines = []
    inside_main_function = False
    main_function_indent = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        line_indent = len(line) - len(line.lstrip())
        
        # Detectar el inicio de la función main
        if line_stripped.startswith('def main():'):
            inside_main_function = True
            main_function_indent = line_indent
            corrected_lines.append(line.rstrip())
            continue
        
        # Si estamos dentro de la función main
        if inside_main_function:
            # Si encontramos if __name__ == "__main__":
            if line_stripped == 'if __name__ == "__main__":':
                # Terminar la función main aquí y mover el if fuera
                inside_main_function = False
                corrected_lines.append('')  # Línea vacía
                corrected_lines.append('if __name__ == "__main__":')
                continue
            
            # Si encontramos main() después del if
            if line_stripped == 'main()':
                corrected_lines.append('    main()')
                continue
        
        # Para todas las demás líneas, mantenerlas como están
        corrected_lines.append(line.rstrip())
    
    # Escribir el archivo corregido
    with open('ir_to_sql_converter.py', 'w', encoding='utf-8') as f:
        for line in corrected_lines:
            f.write(line + '\n')
    
    print('✅ Archivo corregido exitosamente')

if __name__ == "__main__":
    fix_indentation_advanced()
