       IDENTIFICATION DIVISION.
       PROGRAM-ID. TIMINGTEST.
       
       ENVIRONMENT DIVISION.
       
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-COUNTER   PIC 9(3) VALUE 0.
       01  WS-MESSAGE   PIC X(20) VALUE 'HELLO WORLD'.
       
       PROCEDURE DIVISION.
      * Test timing functionality
           INITIALIZE WS-COUNTER.
           MOVE 'TEST' TO WS-MESSAGE.
           DISPLAY WS-MESSAGE.
           ADD 1 TO WS-COUNTER.
           STOP RUN.
