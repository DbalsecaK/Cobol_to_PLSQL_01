#!/usr/bin/env python3
"""
Script para corregir específicamente la función main en ir_to_sql_converter.py
"""

def fix_main_function():
    """Corregir la función main para que termine correctamente"""
    
    # Leer el archivo
    with open('ir_to_sql_converter.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    corrected_lines = []
    inside_main = False
    main_start_line = -1
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Detectar el inicio de la función main
        if line_stripped == 'def main():':
            inside_main = True
            main_start_line = i
            corrected_lines.append(line.rstrip())
            continue
        
        # Si estamos dentro de la función main
        if inside_main:
            # Si encontramos if __name__ == "__main__":
            if line_stripped == 'if __name__ == "__main__":':
                # Terminar la función main aquí
                inside_main = False
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
    
    print('✅ Función main corregida exitosamente')

if __name__ == "__main__":
    fix_main_function()
