# parser/antlr_driver.py
from antlr4 import FileStream, CommonTokenStream
from Cobol85Lexer import Cobol85Lexer
from Cobol85Parser import Cobol85Parser
from .ir_visitor import IRBuildingVisitor

def parse_cobol_to_ir(file_path: str):
    input_stream = FileStream(file_path, encoding='utf-8')
    lexer = Cobol85Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Cobol85Parser(stream)
    
    # Usar la regla 'program' como entry point
    tree = parser.program()
    
    visitor = IRBuildingVisitor(token_stream=stream, full_text=input_stream.strdata)
    return visitor.build_ir(tree)
