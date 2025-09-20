#!/usr/bin/env python3
"""
COBOL FILE OPERATIONS CONVERTER - Conversor de operaciones de archivos COBOL a PL/SQL

Basado en el archivo de migración de operaciones de archivos y el programa manual C1040_A_MANO.pck
Implementa conversión de operaciones de archivos COBOL a UTL_FILE de PL/SQL siguiendo principios SOLID.

PRINCIPIOS SOLID APLICADOS:
- S: Single Responsibility - Cada clase maneja un aspecto específico de operaciones de archivos
- O: Open/Closed - Extensible para nuevas operaciones sin modificar código existente  
- L: Liskov Substitution - Operaciones intercambiables
- I: Interface Segregation - Interfaces específicas por tipo de operación
- D: Dependency Inversion - Abstracción de operaciones de archivos

OPERACIONES IMPLEMENTADAS:
1. SELECT/FD → UTL_FILE.FILE_TYPE declarations
2. OPEN INPUT/OUTPUT/I-O → UTL_FILE.FOPEN/FOPEN_NCHAR 
3. CLOSE → UTL_FILE.FCLOSE
4. READ → UTL_FILE.GET_LINE/GET_LINE_NCHAR
5. WRITE → UTL_FILE.PUT_LINE/PUT_LINE_NCHAR
6. FILE STATUS → Exception handling

PATRONES DEL ARCHIVO MANUAL C1040_A_MANO.pck:
- IMPRES01 UTL_FILE.FILE_TYPE;
- FICCON01 := UTL_FILE.FOPEN_NCHAR('NEXTI_DIR','FICCON01.TXT','R');
- UTL_FILE.PUT_LINE_NCHAR(IMPRES01, REG_IMPRES01);
- UTL_FILE.FCLOSE(IMPRES01);
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from abc import ABC, abstractmethod
from enum import Enum

class FileOperation(Enum):
    """Tipos de operaciones de archivos"""
    SELECT = "select"
    OPEN = "open"
    CLOSE = "close"
    READ = "read"
    WRITE = "write"
    REWRITE = "rewrite"
    DELETE = "delete"
    START = "start"

class FileMode(Enum):
    """Modos de apertura de archivos"""
    INPUT = "R"     # Read
    OUTPUT = "W"    # Write
    IO = "A"        # Append (simula I-O)
    EXTEND = "A"    # Append

class IFileOperationConverter(ABC):
    """Interface para conversores de operaciones de archivos - Interface Segregation Principle"""
    
    @abstractmethod
    def convert(self, operation_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir operación de archivo COBOL a PL/SQL"""
        pass
    
    @abstractmethod
    def can_handle(self, operation_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        pass
    
    @abstractmethod
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        pass

class IFileOperationParser(ABC):
    """Interface para parseadores de operaciones de archivos"""
    
    @abstractmethod
    def parse_file_operation(self, statement: str) -> Dict[str, Any]:
        """Parsear operación de archivo COBOL"""
        pass

class CobolFileOperationParser(IFileOperationParser):
    """Parser de operaciones de archivos COBOL basado en el documento de migración"""
    
    def __init__(self):
        # Patrones para diferentes operaciones de archivos
        self.operation_patterns = {
            'select': r'SELECT\s+([A-Z][\w\-]*)\s+ASSIGN\s+TO\s+[\'"]([^\'\"]+)[\'"]',
            'fd': r'FD\s+([A-Z][\w\-]*)',
            'open_input': r'OPEN\s+INPUT\s+([A-Z][\w\-]*)',
            'open_output': r'OPEN\s+OUTPUT\s+([A-Z][\w\-]*)',
            'open_io': r'OPEN\s+I\-O\s+([A-Z][\w\-]*)',
            'open_extend': r'OPEN\s+EXTEND\s+([A-Z][\w\-]*)',
            'close': r'CLOSE\s+([A-Z][\w\-]*)',
            'read_simple': r'READ\s+([A-Z][\w\-]*)',
            'read_into': r'READ\s+([A-Z][\w\-]*)\s+INTO\s+([A-Z][\w\-]*)',
            'read_key': r'READ\s+([A-Z][\w\-]*)\s+KEY\s+IS\s+([A-Z][\w\-]*)',
            'read_next': r'READ\s+([A-Z][\w\-]*)\s+NEXT\s+RECORD',
            'write_simple': r'WRITE\s+([A-Z][\w\-]*)',
            'write_from': r'WRITE\s+([A-Z][\w\-]*)\s+FROM\s+([A-Z][\w\-]*)',
            'rewrite': r'REWRITE\s+([A-Z][\w\-]*)',
            'delete': r'DELETE\s+([A-Z][\w\-]*)',
            'start': r'START\s+([A-Z][\w\-]*)'
        }
    
    def parse_file_operation(self, statement: str) -> Dict[str, Any]:
        """Parsear operación de archivo COBOL"""
        statement = statement.strip()
        
        # Buscar patrón que coincida
        for operation_type, pattern in self.operation_patterns.items():
            match = re.search(pattern, statement, re.IGNORECASE)
            if match:
                return self._build_operation_info(operation_type, match, statement)
        
        # No reconocida
        return {
            'type': 'unknown',
            'raw': statement,
            'is_file_operation': False
        }
    
    def _build_operation_info(self, operation_type: str, match, statement: str) -> Dict[str, Any]:
        """Construir información de operación de archivo"""
        base_info = {
            'type': operation_type,
            'raw': statement,
            'is_file_operation': True
        }
        
        if operation_type == 'select':
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'physical_name': match.group(2),
                'operation': FileOperation.SELECT
            })
        elif operation_type == 'fd':
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.SELECT  # FD es parte de la declaración
            })
        elif operation_type.startswith('open_'):
            mode = operation_type.split('_')[1]
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'mode': mode,
                'operation': FileOperation.OPEN
            })
        elif operation_type == 'close':
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.CLOSE
            })
        elif operation_type.startswith('read_'):
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.READ,
                'read_type': operation_type
            })
            
            if operation_type == 'read_into':
                base_info['target_record'] = self._clean_identifier(match.group(2))
            elif operation_type == 'read_key':
                base_info['key_field'] = self._clean_identifier(match.group(2))
        elif operation_type.startswith('write_'):
            base_info.update({
                'record_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.WRITE,
                'write_type': operation_type
            })
            
            if operation_type == 'write_from':
                base_info['source_record'] = self._clean_identifier(match.group(2))
        elif operation_type == 'rewrite':
            base_info.update({
                'record_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.REWRITE
            })
        elif operation_type == 'delete':
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.DELETE
            })
        elif operation_type == 'start':
            base_info.update({
                'file_name': self._clean_identifier(match.group(1)),
                'operation': FileOperation.START
            })
        
        return base_info
    
    def _clean_identifier(self, identifier: str) -> str:
        """Limpiar identificador COBOL para PL/SQL"""
        if not identifier:
            return identifier
        return identifier.strip().lower().replace('-', '_')

class OpenFileConverter(IFileOperationConverter):
    """Conversor para operaciones OPEN - Single Responsibility Principle"""
    
    def __init__(self):
        self.parser = CobolFileOperationParser()
    
    def can_handle(self, operation_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return operation_type.startswith('open_')
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "OPEN"
    
    def convert(self, operation_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir OPEN a UTL_FILE.FOPEN/FOPEN_NCHAR"""
        file_name = operation_info.get('file_name', 'unknown_file')
        mode = operation_info.get('mode', 'input')
        raw_content = operation_info.get('raw', '')
        
        # Mapear modo COBOL a PL/SQL
        plsql_mode = self._map_file_mode(mode)
        
        # Generar nombre de archivo físico (basado en patrones del archivo manual)
        physical_name = f"{file_name.upper()}.TXT"
        
        # Usar patrón del archivo manual: UTL_FILE.FOPEN_NCHAR
        return f"""
    BEGIN 
        {file_name.upper()}   :=  UTL_FILE.FOPEN_NCHAR('NEXTI_DIR','{physical_name}','{plsql_mode}');
        DBMS_OUTPUT.PUT_LINE('Archivo {physical_name} abierto correctamente.');
    EXCEPTION
        WHEN UTL_FILE.INVALID_PATH THEN
            DBMS_OUTPUT.PUT_LINE('Directorio NEXTI_DIR inválido');
            RAISE_APPLICATION_ERROR(-20001, 'Error al abrir archivo {physical_name}');
        WHEN UTL_FILE.INVALID_FILENAME THEN
            DBMS_OUTPUT.PUT_LINE('Nombre de archivo {physical_name} inválido');
            RAISE_APPLICATION_ERROR(-20002, 'Error al abrir archivo {physical_name}');
        WHEN UTL_FILE.INVALID_MODE THEN
            DBMS_OUTPUT.PUT_LINE('Modo de apertura {plsql_mode} inválido');
            RAISE_APPLICATION_ERROR(-20003, 'Error al abrir archivo {physical_name}');
        WHEN OTHERS THEN
            DBMS_OUTPUT.PUT_LINE('Error al abrir archivo: ' || SQLERRM);
            RAISE_APPLICATION_ERROR(-20004, 'Error al abrir archivo {physical_name}');
    END;"""
    
    def _map_file_mode(self, cobol_mode: str) -> str:
        """Mapear modo COBOL a modo PL/SQL UTL_FILE"""
        mode_mapping = {
            'input': 'R',
            'output': 'W',
            'io': 'A',
            'extend': 'A'
        }
        return mode_mapping.get(cobol_mode.lower(), 'R')

class CloseFileConverter(IFileOperationConverter):
    """Conversor para operaciones CLOSE - Single Responsibility Principle"""
    
    def can_handle(self, operation_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return operation_type == 'close'
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "CLOSE"
    
    def convert(self, operation_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir CLOSE a UTL_FILE.FCLOSE"""
        file_name = operation_info.get('file_name', 'unknown_file')
        
        # Patrón del archivo manual: simple FCLOSE
        return f"""
    UTL_FILE.FCLOSE({file_name.upper()});"""

class ReadFileConverter(IFileOperationConverter):
    """Conversor para operaciones READ - Single Responsibility Principle"""
    
    def can_handle(self, operation_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return operation_type.startswith('read_')
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "READ"
    
    def convert(self, operation_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir READ a UTL_FILE.GET_LINE/GET_LINE_NCHAR"""
        file_name = operation_info.get('file_name', 'unknown_file')
        read_type = operation_info.get('read_type', 'read_simple')
        target_record = operation_info.get('target_record', f'reg_{file_name}')
        
        if read_type == 'read_into':
            # READ file INTO record
            return f"""
    BEGIN
        UTL_FILE.GET_LINE_NCHAR({file_name.upper()}, {target_record.upper()});
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            -- Equivalent to AT END in COBOL
            v_eof_flag := TRUE;
            DBMS_OUTPUT.PUT_LINE('Fin de archivo {file_name.upper()} alcanzado');
        WHEN UTL_FILE.READ_ERROR THEN
            DBMS_OUTPUT.PUT_LINE('Error de lectura en archivo {file_name.upper()}');
            RAISE_APPLICATION_ERROR(-20005, 'Error de lectura en {file_name.upper()}');
    END;"""
        elif read_type == 'read_key':
            # READ file KEY IS key-field → Convert to database query
            key_field = operation_info.get('key_field', 'key_field')
            return f"""
    -- GAP -- {operation_info.get('raw', '')} -- (READ with KEY requires database table)
    -- TODO: Convert to SELECT * FROM table WHERE {key_field} = ?"""
        elif read_type == 'read_next':
            # READ file NEXT RECORD
            return f"""
    BEGIN
        UTL_FILE.GET_LINE_NCHAR({file_name.upper()}, {target_record.upper()});
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            v_eof_flag := TRUE;
    END;"""
        else:
            # Simple READ
            return f"""
    BEGIN
        UTL_FILE.GET_LINE_NCHAR({file_name.upper()}, {target_record.upper()});
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            v_eof_flag := TRUE;
    END;"""

class WriteFileConverter(IFileOperationConverter):
    """Conversor para operaciones WRITE - Single Responsibility Principle"""
    
    def can_handle(self, operation_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return operation_type.startswith('write_')
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "WRITE"
    
    def convert(self, operation_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir WRITE a UTL_FILE.PUT_LINE/PUT_LINE_NCHAR"""
        record_name = operation_info.get('record_name', 'unknown_record')
        write_type = operation_info.get('write_type', 'write_simple')
        source_record = operation_info.get('source_record', record_name)
        
        # Inferir nombre de archivo desde record name (convención común)
        # Si el record es REG_IMPRES01, el archivo sería IMPRES01
        file_name = record_name.replace('reg_', '').replace('record_', '')
        if file_name.startswith('r_'):
            file_name = file_name[2:]
        
        # Patrón del archivo manual: UTL_FILE.PUT_LINE_NCHAR
        if write_type == 'write_from':
            # WRITE record FROM source
            return f"""
    UTL_FILE.PUT_LINE_NCHAR({file_name.upper()}, {source_record.upper()});"""
        else:
            # Simple WRITE record
            return f"""
    UTL_FILE.PUT_LINE_NCHAR({file_name.upper()}, {record_name.upper()});"""

class FileDeclarationConverter(IFileOperationConverter):
    """Conversor para declaraciones SELECT/FD - Single Responsibility Principle"""
    
    def can_handle(self, operation_type: str) -> bool:
        """Verificar si puede manejar esta operación"""
        return operation_type in ['select', 'fd']
    
    def get_operation_name(self) -> str:
        """Obtener nombre de la operación"""
        return "DECLARATION"
    
    def convert(self, operation_info: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Convertir SELECT/FD a declaración UTL_FILE.FILE_TYPE"""
        file_name = operation_info.get('file_name', 'unknown_file')
        
        # Patrón del archivo manual: IMPRES01 UTL_FILE.FILE_TYPE;
        return f"""
   {file_name.upper()} UTL_FILE.FILE_TYPE;"""

class FileOperationConverterFactory:
    """Factory para crear conversores de operaciones de archivos - Dependency Inversion Principle"""
    
    def __init__(self):
        self.converters = [
            OpenFileConverter(),
            CloseFileConverter(),
            ReadFileConverter(),
            WriteFileConverter(),
            FileDeclarationConverter()
        ]
        self.parser = CobolFileOperationParser()
    
    def get_converter(self, operation_type: str) -> Optional[IFileOperationConverter]:
        """Obtener conversor apropiado para la operación"""
        for converter in self.converters:
            if converter.can_handle(operation_type):
                return converter
        return None
    
    def convert_file_operation(self, statement: str, context: Dict[str, Any] = None) -> str:
        """Convertir operación de archivo completa"""
        # Parsear la operación
        operation_info = self.parser.parse_file_operation(statement)
        
        if not operation_info.get('is_file_operation', False):
            return f"  -- GAP -- {statement} -- (Unknown file operation)"
        
        # Obtener conversor apropiado
        operation_type = operation_info.get('type', 'unknown')
        converter = self.get_converter(operation_type)
        
        if not converter:
            return f"  -- GAP -- {statement} -- (File operation not supported: {operation_type})"
        
        try:
            return converter.convert(operation_info, context)
        except Exception as e:
            return f"  -- GAP -- {statement} -- (File operation conversion error: {e})"
    
    def detect_file_operations(self, cobol_code: str) -> List[Dict[str, Any]]:
        """Detectar todas las operaciones de archivos en código COBOL"""
        lines = cobol_code.split('\n')
        file_operations = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            operation_info = self.parser.parse_file_operation(line)
            if operation_info.get('is_file_operation', False):
                operation_info['line_number'] = i + 1
                file_operations.append(operation_info)
        
        return file_operations
    
    def generate_file_declarations_section(self, file_operations: List[Dict[str, Any]]) -> str:
        """Generar sección de declaraciones de archivos para el package"""
        declarations = []
        declared_files = set()
        
        for operation in file_operations:
            if operation.get('operation') == FileOperation.SELECT:
                file_name = operation.get('file_name', '').upper()
                if file_name and file_name not in declared_files:
                    declarations.append(f"   {file_name} UTL_FILE.FILE_TYPE;")
                    declared_files.add(file_name)
        
        if declarations:
            return """
  --INPUT-OUTPUT SECTION.
""" + '\n'.join(declarations)
        else:
            return ""
    
    def generate_file_records_section(self, file_operations: List[Dict[str, Any]]) -> str:
        """Generar sección de records de archivos basada en las operaciones detectadas"""
        records = []
        declared_records = set()
        
        for operation in file_operations:
            if operation.get('operation') in [FileOperation.READ, FileOperation.WRITE]:
                file_name = operation.get('file_name', '')
                record_name = operation.get('record_name', f'reg_{file_name}')
                
                if file_name and record_name.upper() not in declared_records:
                    # Usar CHAR en lugar de VARCHAR2 (patrón del archivo manual)
                    records.append(f"   {record_name.upper()} CHAR(133);")  # Longitud estándar
                    declared_records.add(record_name.upper())
        
        if records:
            return """
  --WORKING-STORAGE SECTION.
""" + '\n'.join(records)
        else:
            return ""

# Utilidades de migración de archivos
class CobolFileSystemMigrator:
    """Migrador del sistema de archivos COBOL completo"""
    
    def __init__(self):
        self.factory = FileOperationConverterFactory()
    
    def migrate_file_control_section(self, file_control_section: str) -> str:
        """Migrar sección FILE-CONTROL completa"""
        operations = self.factory.detect_file_operations(file_control_section)
        
        # Generar declaraciones
        declarations = self.factory.generate_file_declarations_section(operations)
        records = self.factory.generate_file_records_section(operations)
        
        return declarations + records
    
    def migrate_file_operations_in_procedure(self, procedure_code: str) -> str:
        """Migrar operaciones de archivos en PROCEDURE DIVISION"""
        lines = procedure_code.split('\n')
        converted_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                converted_lines.append(line)
                continue
            
            # Intentar convertir como operación de archivo
            operation_info = self.factory.parser.parse_file_operation(line_stripped)
            
            if operation_info.get('is_file_operation', False):
                converted = self.factory.convert_file_operation(line_stripped)
                converted_lines.append(converted)
            else:
                converted_lines.append(line)
        
        return '\n'.join(converted_lines)

# Función de prueba
def main():
    """Función de prueba del conversor de operaciones de archivos"""
    factory = FileOperationConverterFactory()
    
    # Casos de prueba basados en el archivo de migración y manual
    test_cases = [
        # Declaraciones (del archivo manual)
        "SELECT IMPRES01 ASSIGN TO 'IMPRES01.TXT'",
        "SELECT FICCON01 ASSIGN TO 'FICCON01.TXT'",
        "FD IMPRES01",
        
        # Operaciones OPEN
        "OPEN INPUT FICCON01",
        "OPEN OUTPUT IMPRES01", 
        "OPEN I-O ARCHIVO-MAESTRO",
        
        # Operaciones READ
        "READ FICCON01 INTO REG-FICCON",
        "READ ARCHIVO-ENTRADA AT END SET EOF-FLAG TO TRUE",
        "READ ARCHIVO-INDEXADO KEY IS WS-CLAVE",
        
        # Operaciones WRITE
        "WRITE REG-IMPRES01",
        "WRITE REGISTRO-SALIDA FROM WS-BUFFER",
        
        # Operaciones CLOSE
        "CLOSE IMPRES01",
        "CLOSE FICCON01",
        
        # Casos del archivo manual
        "IMPRES01 UTL_FILE.FILE_TYPE;",  # Ya en PL/SQL
        "UTL_FILE.PUT_LINE_NCHAR(IMPRES01, REG_IMPRES01);"  # Ya en PL/SQL
    ]
    
    print("🧪 PRUEBAS DEL CONVERSOR DE OPERACIONES DE ARCHIVOS")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Caso {i}: {test_case}")
        print("-" * 50)
        
        try:
            result = factory.convert_file_operation(test_case)
            print(f"Resultado:\n{result}")
        except Exception as e:
            print(f"ERROR: {e}")
    
    # Prueba de detección de operaciones
    sample_cobol = """
FILE-CONTROL.
    SELECT ARCHIVO-ENTRADA ASSIGN TO "entrada.dat"
    SELECT ARCHIVO-SALIDA ASSIGN TO "salida.dat"

PROCEDURE DIVISION.
    OPEN INPUT ARCHIVO-ENTRADA
    OPEN OUTPUT ARCHIVO-SALIDA
    READ ARCHIVO-ENTRADA INTO REG-ENTRADA
    WRITE REG-SALIDA FROM WS-BUFFER
    CLOSE ARCHIVO-ENTRADA
    CLOSE ARCHIVO-SALIDA
    """
    
    print(f"\n\n🔍 DETECCIÓN DE OPERACIONES EN CÓDIGO COBOL:")
    print("-" * 50)
    
    operations = factory.detect_file_operations(sample_cobol)
    for op in operations:
        print(f"Línea {op['line_number']}: {op['type']} - {op['raw']}")

if __name__ == "__main__":
    main()

