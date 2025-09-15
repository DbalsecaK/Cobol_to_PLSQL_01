#!/usr/bin/env python3
"""
Conversion Utils - Módulo de utilidades comunes
Funciones compartidas para el pipeline de conversión COBOL → IR → PL/SQL

Incluye:
- Utilidades de timing
- Funciones de limpieza de expresiones
- Utilidades de archivos
- Configuraciones comunes
"""

import os
import hashlib
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ===== TIMING UTILITIES =====

def get_timestamp() -> str:
    """Obtener timestamp detallado con milisegundos"""
    now = datetime.now()
    return now.strftime("%H:%M:%S.%f")[:-3]

def format_duration(start_time: float, end_time: float) -> str:
    """Formatear duración en segundos y milisegundos"""
    duration = end_time - start_time
    if duration < 1:
        return f"{duration*1000:.1f} ms"
    elif duration < 60:
        return f"{duration:.3f} segundos"
    else:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.3f}s"

# ===== FILE UTILITIES =====

def get_file_hash(file_path: str) -> str:
    """Generar hash MD5 del archivo para caché"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return ""

def ensure_output_directory(output_dir: str = "out") -> str:
    """Asegurar que existe el directorio de salida"""
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def get_base_name(file_path: str, remove_suffix: str = None) -> str:
    """Obtener nombre base del archivo, opcionalmente removiendo sufijo"""
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    if remove_suffix and base_name.endswith(remove_suffix):
        base_name = base_name[:-len(remove_suffix)]
    return base_name.upper()

# ===== EXPRESSION CLEANING =====

def clean_expression(expr: str) -> str:
    """Limpiar expresiones para PL/SQL"""
    if not expr:
        return ""
    
    # Remover puntos finales
    expr = expr.rstrip('.')
    
    # Limpiar espacios extra
    expr = ' '.join(expr.split())
    
    # Convertir comillas COBOL a PL/SQL si es necesario
    if expr.startswith("'") and expr.endswith("'"):
        return expr
    elif expr.startswith('"') and expr.endswith('"'):
        return "'" + expr[1:-1] + "'"
    
    return expr

def normalize_cobol_value(value: str) -> str:
    """Normalizar valores especiales de COBOL"""
    value_upper = value.upper()
    
    if value_upper in ['ZERO', 'ZEROS', 'ZEROES']:
        return '0'
    elif value_upper in ['SPACE', 'SPACES']:
        return "' '"
    elif value_upper == 'HIGH-VALUE':
        return 'CHR(255)'
    elif value_upper == 'LOW-VALUE':
        return 'CHR(0)'
    elif value_upper == 'TRUE':
        return '1'
    elif value_upper == 'FALSE':
        return '0'
    
    return value

def clean_cobol_condition(condition: str) -> str:
    """Limpiar y convertir condiciones COBOL a PL/SQL"""
    if not condition:
        return ""
    
    # Convertir operadores COBOL a PL/SQL
    condition = condition.replace(' NOT = ', ' <> ')
    condition = condition.replace(' NOT EQUAL ', ' <> ')
    condition = condition.replace(' EQUAL ', ' = ')
    condition = condition.replace(' GREATER THAN ', ' > ')
    condition = condition.replace(' LESS THAN ', ' < ')
    condition = condition.replace(' AND ', ' AND ')
    condition = condition.replace(' OR ', ' OR ')
    
    return condition.strip()

# ===== REGEX PATTERNS =====

# Regex compilados para mejor rendimiento
COMPILED_REGEXES = {
    'comment_col7': re.compile(r'^.{6}\*'),
    'comment_asterisks': re.compile(r'^\s*\*\*'),
    'move_pattern': re.compile(r'MOVE\s+(.+?)\s+TO\s+(.+)', re.IGNORECASE),
    'display_pattern': re.compile(r'^DISPLAY\s+(.+?)\\.?$', re.IGNORECASE),
    'if_pattern': re.compile(r'^IF\s+(.+)', re.IGNORECASE),
    'exec_sql': re.compile(r'EXEC\s+SQL', re.IGNORECASE),
    'end_exec': re.compile(r'END-EXEC', re.IGNORECASE),
    'perform_pattern': re.compile(r'^PERFORM\s+(.+)', re.IGNORECASE),
    'qualified_field': re.compile(r'^([A-Z0-9_-]+)\s+OF\s+([A-Z0-9_-]+)', re.IGNORECASE),
    'set_pattern': re.compile(r'^SET\s+(.+?)\s+TO\s+(.+)', re.IGNORECASE),
    'program_id': re.compile(r'PROGRAM-ID\.\s*([A-Z0-9]+)', re.IGNORECASE),
    'variable_definition': re.compile(r'^\s*(\d+)\s+([A-Z0-9_-]+)', re.IGNORECASE)
}

def get_regex(pattern_name: str) -> re.Pattern:
    """Obtener regex compilado por nombre"""
    return COMPILED_REGEXES.get(pattern_name)

# ===== VALIDATION UTILITIES =====

def validate_ir_structure(ir: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validar estructura básica de IR"""
    errors = []
    
    # Validar campos requeridos
    required_fields = ['program_name', 'variables', 'procedures']
    for field in required_fields:
        if field not in ir:
            errors.append(f"Campo requerido faltante: {field}")
    
    # Validar procedures
    if 'procedures' in ir:
        if not isinstance(ir['procedures'], list):
            errors.append("'procedures' debe ser una lista")
        else:
            for i, proc in enumerate(ir['procedures']):
                if not isinstance(proc, dict):
                    errors.append(f"Procedure {i} debe ser un diccionario")
                elif 'statements' not in proc:
                    errors.append(f"Procedure {i} debe tener 'statements'")
    
    # Validar variables
    if 'variables' in ir:
        if not isinstance(ir['variables'], list):
            errors.append("'variables' debe ser una lista")
    
    return len(errors) == 0, errors

def validate_statement(stmt: Dict[str, Any]) -> Tuple[bool, str]:
    """Validar estructura de un statement"""
    if not isinstance(stmt, dict):
        return False, "Statement debe ser un diccionario"
    
    if 'op' not in stmt:
        return False, "Statement debe tener campo 'op'"
    
    if 'raw' not in stmt:
        return False, "Statement debe tener campo 'raw'"
    
    return True, ""

# ===== STATISTICS UTILITIES =====

class ConversionStats:
    """Clase para manejar estadísticas de conversión"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reiniciar estadísticas"""
        self.total_processed = 0
        self.successful = 0
        self.gaps = 0
        self.operation_counts = {}
        self.error_counts = {}
    
    def record_success(self, operation: str):
        """Registrar conversión exitosa"""
        self.total_processed += 1
        self.successful += 1
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1
    
    def record_gap(self, operation: str, error: str = None):
        """Registrar GAP (conversión fallida)"""
        self.total_processed += 1
        self.gaps += 1
        self.operation_counts[operation] = self.operation_counts.get(operation, 0) + 1
        if error:
            self.error_counts[error] = self.error_counts.get(error, 0) + 1
    
    def get_success_rate(self) -> float:
        """Obtener tasa de éxito como porcentaje"""
        if self.total_processed == 0:
            return 0.0
        return (self.successful / self.total_processed) * 100
    
    def get_most_common_operations(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Obtener operaciones más comunes"""
        return sorted(self.operation_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de estadísticas"""
        return {
            'total_processed': self.total_processed,
            'successful': self.successful,
            'gaps': self.gaps,
            'success_rate': round(self.get_success_rate(), 2),
            'most_common_operations': self.get_most_common_operations(),
            'error_summary': dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True))
        }

# ===== LOGGING UTILITIES =====

def print_header(title: str, width: int = 70):
    """Imprimir encabezado formateado"""
    print("=" * width)
    print(f"{title:^{width}}")
    print("=" * width)

def print_section(title: str, items: Dict[str, Any], width: int = 70):
    """Imprimir sección formateada con elementos"""
    print(f"{title}:")
    for key, value in items.items():
        print(f"   {key}: {value}")

def print_performance_summary(times: Dict[str, float], stats: ConversionStats = None):
    """Imprimir resumen de rendimiento"""
    print("⏰ MÉTRICAS DE RENDIMIENTO:")
    
    total_time = times.get('total', 0)
    print(f"   ⏱️  Tiempo total: {format_duration(0, total_time)}")
    
    for phase, duration in times.items():
        if phase != 'total':
            print(f"   ⏱️  {phase.capitalize()}: {format_duration(0, duration)}")
    
    if stats:
        if total_time > 0:
            rate = stats.total_processed / total_time
            print(f"   ⚡ Velocidad: {rate:.1f} items/segundo")

# ===== CONFIGURATION =====

class Config:
    """Configuración del sistema de conversión"""
    
    # Directorios
    OUTPUT_DIR = "out"
    CACHE_DIR = ".cache"
    
    # Archivos
    IR_SUFFIX = "_ir.json"
    PARSING_REPORT_SUFFIX = "_parsing_report.json"
    CONVERSION_REPORT_SUFFIX = "_conversion_report.json"
    PLSQL_SUFFIX = "_generated.sql"
    
    # Límites
    MAX_CACHE_ENTRIES = 100
    MAX_VARIABLES_IN_HEADER = 20
    MAX_ERROR_DISPLAY = 10
    
    # Formatos
    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
    JSON_INDENT = 2
    
    @classmethod
    def get_output_path(cls, base_name: str, suffix: str) -> str:
        """Obtener ruta completa de archivo de salida"""
        return os.path.join(cls.OUTPUT_DIR, f"{base_name}{suffix}")

# ===== COMPATIBILITY HELPERS =====

def ensure_python_compatibility():
    """Verificar compatibilidad de Python"""
    import sys
    if sys.version_info < (3, 6):
        raise RuntimeError("Se requiere Python 3.6 o superior")

def check_dependencies():
    """Verificar dependencias requeridas"""
    try:
        import antlr4
        return True, "ANTLR4 disponible"
    except ImportError:
        return False, "ANTLR4 no encontrado. Instalar con: pip install antlr4-python3-runtime"

# ===== EXPORTS =====

__all__ = [
    # Timing
    'get_timestamp', 'format_duration',
    
    # Files
    'get_file_hash', 'ensure_output_directory', 'get_base_name',
    
    # Expression cleaning
    'clean_expression', 'normalize_cobol_value', 'clean_cobol_condition',
    
    # Regex
    'get_regex', 'COMPILED_REGEXES',
    
    # Validation
    'validate_ir_structure', 'validate_statement',
    
    # Statistics
    'ConversionStats',
    
    # Logging
    'print_header', 'print_section', 'print_performance_summary',
    
    # Configuration
    'Config',
    
    # Compatibility
    'ensure_python_compatibility', 'check_dependencies'
]
