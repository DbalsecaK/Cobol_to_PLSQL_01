       IDENTIFICATION DIVISION.
       PROGRAM-ID. TESTERROR.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  VARIABLE1    PIC X(10).

       PROCEDURE DIVISION.
           MOVE 'TEST' TO VARIABLE1.
           IF VARIABLE1 = 'TEST' THEN
              DISPLAY 'OK'
           ELSE
              DISPLAY 'NOT OK'
           END-IF.
           
           -- Esta línea causará un error de parsing
           INVALID-STATEMENT WITH SYNTAX ERROR.
           
           STOP RUN.
