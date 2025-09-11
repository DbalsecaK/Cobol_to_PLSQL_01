       IDENTIFICATION DIVISION.
       PROGRAM-ID. DEMO1.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  NOMBRE          PIC X(20).
       01  CONT            PIC 9(4).
       01  X               PIC 9(4).
       PROCEDURE DIVISION.
           MOVE 'ABACAXI' TO NOMBRE.
           MOVE 5 TO X.
           ADD 3 TO X.
           IF X > 7 DISPLAY 'OK'.
           DISPLAY 'FIN'.
           STOP RUN.
