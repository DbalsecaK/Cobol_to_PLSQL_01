grammar Cobol85;

// Keywords
PROGRAM_ID: 'PROGRAM-ID';
IDENTIFICATION: 'IDENTIFICATION';
DIVISION: 'DIVISION';
DATA: 'DATA';
WORKING_STORAGE: 'WORKING-STORAGE';
SECTION: 'SECTION';
PROCEDURE: 'PROCEDURE';
MOVE: 'MOVE';
TO: 'TO';
ADD: 'ADD';
IF: 'IF';
THEN: 'THEN';
ELSE: 'ELSE';
END_IF: 'END-IF';
DISPLAY: 'DISPLAY';
STOP: 'STOP';
RUN: 'RUN';
GIVING: 'GIVING';

// Data types
PIC: 'PIC';

// Operators
GREATER_THAN: '>';
EQUAL: 'EQUAL';
NOT_EQUAL: 'NOT EQUAL';
AND: 'AND';
OR: 'OR';
DOT: '.';
COMMA: ',';
SEMICOLON: ';';
LPAREN: '(';
RPAREN: ')';
COLON: ':';
OF: 'OF';

// Literals
STRING_LITERAL: '\'' ~'\''* '\'';
NUMBER: [0-9]+;
IDENTIFIER: [A-Z0-9_-]+;

// Whitespace
WS: [ \t\r\n]+ -> skip;

// Parser rules
program: identification_division data_division procedure_division;

identification_division: IDENTIFICATION DIVISION DOT PROGRAM_ID DOT IDENTIFIER DOT;

data_division: DATA DIVISION DOT working_storage_section;

working_storage_section: WORKING_STORAGE SECTION DOT variable_declaration*;

variable_declaration: NUMBER IDENTIFIER PIC data_type DOT;

data_type: X_TYPE | NINE_TYPE;
X_TYPE: 'X' '(' NUMBER ')';
NINE_TYPE: '9' '(' NUMBER ')';

procedure_division: PROCEDURE DIVISION DOT statement* STOP RUN DOT;

statement: move_statement | add_statement | if_statement | display_statement;

move_statement: MOVE (literal | identifier_expression) TO identifier_expression DOT;

add_statement: ADD literal TO IDENTIFIER (GIVING IDENTIFIER)? DOT;

if_statement: IF condition THEN? statement* (ELSE statement*)? END_IF DOT;

display_statement: DISPLAY (literal | IDENTIFIER) (literal | IDENTIFIER)* DOT;

condition: identifier_expression (GREATER_THAN | EQUAL | NOT_EQUAL) literal
         | identifier_expression EQUAL literal AND identifier_expression EQUAL literal
         | identifier_expression GREATER_THAN literal AND identifier_expression NOT_EQUAL literal;

identifier_expression: IDENTIFIER (OF IDENTIFIER)? (LPAREN NUMBER COLON NUMBER RPAREN)?;

literal: STRING_LITERAL | NUMBER;
