       IDENTIFICATION DIVISION.
       PROGRAM-ID. VALIDACION.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  EDAD           PIC 9(3).
       01  NOMBRE         PIC X(20).
       01  ES_MAYOR       PIC X(1).
       01  MENSAJE        PIC X(50).
       PROCEDURE DIVISION.
           MOVE 'JUAN PEREZ' TO NOMBRE.
           MOVE 25 TO EDAD.
           IF EDAD > 18
               MOVE 'S' TO ES_MAYOR
               MOVE 'ES MAYOR DE EDAD' TO MENSAJE
           ELSE
               MOVE 'N' TO ES_MAYOR
               MOVE 'ES MENOR DE EDAD' TO MENSAJE
           END-IF.
           DISPLAY NOMBRE.
           DISPLAY MENSAJE.
           STOP RUN.
