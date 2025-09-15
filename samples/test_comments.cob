       IDENTIFICATION DIVISION.
       PROGRAM-ID. TESTCOMMENTS.
       
      ****************************************************************
      **  Programa de prueba para comentarios COBOL               **
      ****************************************************************
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-VARIABLE  PIC X(10) VALUE 'TEST'.
      * Este es un comentario con asterisco en columna 7
       01  WS-COUNTER   PIC 9(3) VALUE 0.
      ** Este es un comentario con doble asterisco
       
       PROCEDURE DIVISION.
      * Comentario de procedimiento
           MOVE 'HOLA' TO WS-VARIABLE.
      ** Otro comentario con doble asterisco  
           DISPLAY WS-VARIABLE.
      ***  Comentario tradicional con triple asterisco
           STOP RUN.
