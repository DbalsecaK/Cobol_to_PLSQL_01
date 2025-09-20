#!/usr/bin/env python3
"""
Script para corregir el error de indentación en ir_to_sql_converter.py
"""

def fix_indentation():
    """Corregir la indentación del archivo ir_to_sql_converter.py"""
    
    # Leer el archivo
    with open('ir_to_sql_converter.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Dividir en líneas
    lines = content.split('\n')
    corrected_lines = []
    
    # Procesar línea por línea
    for i, line in enumerate(lines):
        # Si encontramos el if __name__ == "__main__": que está mal indentado
        if line.strip() == 'if __name__ == "__main__":' and line.startswith('        '):
            # Corregir la indentación - debe estar al nivel de función (sin indentación)
            corrected_lines.append('if __name__ == "__main__":')
        elif line.strip() == 'main()' and line.startswith('        '):
            # Corregir la indentación del main()
            corrected_lines.append('    main()')
        else:
            corrected_lines.append(line)
    
    # Escribir el archivo corregido
    with open('ir_to_sql_converter.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(corrected_lines))
    
    print('✅ Archivo corregido exitosamente')

if __name__ == "__main__":
    fix_indentation()
