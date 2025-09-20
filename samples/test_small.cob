       IDENTIFICATION DIVISION.
       PROGRAM-ID. TEST-SMALL.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-CUENTA-INI    PIC X(10).
       01 WS-CUENTA-FIN    PIC X(10).
       01 WS-NUM-CHEQUE    PIC 9(8).
       
       PROCEDURE DIVISION.
       A1000-MAIN.
           DISPLAY 'Cuenta Inicial: ' WS-CUENTA-INI.
           DISPLAY 'Cuenta Final  : ' WS-CUENTA-FIN.
           DISPLAY WS-NUM-CHEQUE ' - '.
           STOP RUN.











