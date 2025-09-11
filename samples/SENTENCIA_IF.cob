       IDENTIFICATION DIVISION.
       PROGRAM-ID. PROGRAMADEMO.

       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.

       DATA DIVISION.
       WORKING-STORAGE SECTION.

       PROCEDURE DIVISION.

       1400-ARMA-REC-T08CT176.
           IF SQLCODE NOT EQUAL 000000000 THEN
             DISPLAY PGM 'VOY POR IF'
 
           IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'CC' OR
              COD-TIP-ORIENTACION OF MSG-IN EQUAL 'RT'
            THEN
                   MOVE 'CTB' TO FOR-PAGO    OF T08CT176
             DISPLAY PGM 'FOR-PAGO CC o RT:' COD-TIP-ORIENTACION
                                             OF MSG-IN
           ELSE
 
              IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'C ' THEN
                   MOVE 'CTA' TO FOR-PAGO    OF T08CT176
                 DISPLAY PGM 'FOR-PAGO C:' COD-TIP-ORIENTACION
                                             OF MSG-IN
              ELSE
                 IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'P ' THEN
                   MOVE 'CTA' TO FOR-PAGO    OF T08CT176
                   DISPLAY PGM 'FOR-PAGO: P'
                 END-IF
              END-IF
           
           END-IF
 
           MOVE NUM-CUENTA         OF MSG-IN(9:2)
             TO COD-TIP-EXPE       OF T08CT176
           MOVE NUM-CUENTA         OF MSG-IN(1:8)
             TO NUM-CTA-INT        OF T08CT176
           MOVE 'CC'
             TO IND-TIP-CONTA      OF T08CT176
           MOVE '006414'
             TO COD-CONTA-EMP      OF T08CT176
           MOVE '0186'
             TO COD-CENTIM-EMP     OF T08CT176
           MOVE '006414'
             TO COD-CONTA-SERV     OF T08CT176
           MOVE '0186'
             TO COD-CENTIM-SERV    OF T08CT176
           MOVE '006454'
             TO COD-CONTA-RETE     OF T08CT176
           MOVE '0186'
             TO COD-CENTIM-RETE    OF T08CT176
           MOVE '40399'
             TO COD-OPERACION      OF T08CT176
 
           IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'CC'
              THEN
                   MOVE '2006' TO COD-REFER   OF T08CT176
                 DISPLAY PGM 'COD-REFER CC:' COD-TIP-ORIENTACION
                                             OF MSG-IN
           ELSE
           
              IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'C ' THEN
                   MOVE '0006' TO COD-REFER   OF T08CT176
                 DISPLAY PGM 'COD-REFER C:' COD-TIP-ORIENTACION
                                             OF MSG-IN
              ELSE
                 IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'P ' THEN
                    MOVE '2902' TO COD-REFER    OF T08CT176
                    DISPLAY PGM 'COD-REFER P: ' COD-REFER OF T08CT176
                 ELSE
                   IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'RT' THEN
                     MOVE '4470' TO COD-REFER    OF T08CT176
                     DISPLAY PGM 'COD-REFER RT: ' COD-REFER OF T08CT176
                   END-IF
                 END-IF
              END-IF
           END-IF
 
           END-IF
      ***    FIN CONTROL
      ***    IF WS-COUNT EQUAL ZEROS THEN
           IF WS-COUNT EQUAL ZEROS AND WS-COUNT1 EQUAL ZEROS THEN
             DISPLAY PGM 'IF 1'
              CONTINUE
           ELSE
      ***       IF WS-COUNT > 1 THEN
              IF WS-COUNT > 1 THEN
             DISPLAY PGM 'IF 2'
                 MOVE '21015'
                   TO COD-ERROR          OF T08CT176
                 MOVE 'ERROR DE ACCESO AL DB2.'
                   TO DESC-ERROR         OF T08CT176
                 PERFORM 8000-FINALIZA
                 EXIT
              ELSE
      ***       IF WS-COUNT EQUAL 1 THEN
              IF WS-COUNT EQUAL 1 OR WS-COUNT1 >= 1 THEN
             DISPLAY PGM 'IF 3'
      *******************************************************************
      **********************VOY POR COBRO COMISION***********************
      *******************************************************************
             IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'CC'
                AND WS-COUNT NOT EQUAL ZEROS THEN
                  DISPLAY PGM 'VOY POR CC'
                   MOVE COD-TIP-ORIENTACION OF MSG-IN
                     TO WS-COD-TIP-ORIENTACION
 
           EXEC SQL
             SELECT SUBSTR(DEL_REGISTRO,3,5),
                    SUBSTR(DEL_REGISTRO,8,4),
                    SUBSTR(DEL_REGISTRO,12,2),
                    SUBSTR(DEL_REGISTRO,14,4),
                    SUBSTR(DEL_REGISTRO,18,6),
                    SUBSTR(DEL_REGISTRO,24,3)
               INTO WS-COD-OPERACION,
                    WS-COD-REFER,
                    WS-IND-TIP-CONTA,
                    WS-COD-CENTIM-EMP,
                    WS-COD-CONTA-EMP,
                    WS-FOR-PAGO
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM
                AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
           END-EXEC
 
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
 
      ***  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
           IF SQLCODE NOT EQUAL 000000000 THEN
             DISPLAY PGM 'VOY POR IF'
             CONTINUE
           ELSE
                     MOVE WS-IND-TIP-CONTA
                       TO IND-TIP-CONTA      OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-EMP      OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-EMP     OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-SERV     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-SERV    OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-RETE     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-RETE    OF T08CT176
                     MOVE WS-COD-OPERACION
                       TO COD-OPERACION      OF T08CT176
                     MOVE WS-COD-REFER
                       TO COD-REFER          OF T08CT176
                     MOVE WS-FOR-PAGO
                       TO FOR-PAGO           OF T08CT176
               DISPLAY PGM 'COD-REFER CC:' COD-REFER OF T08CT176
             END-IF
             ELSE
      *******************************************************************
      *****************VOY POR COBRO COMISION ESPECIALES*****************
      *******************************************************************
             IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'CC'
                 AND WS-COUNT1 NOT EQUAL ZEROS THEN
                  DISPLAY PGM 'VOY POR CC1'
                   MOVE COD-TIP-ORIENTACION OF MSG-IN
                     TO WS-COD-TIP-ORIENTACION
 
           EXEC SQL
             SELECT SUBSTR(DEL_REGISTRO,3,5),
                    SUBSTR(DEL_REGISTRO,8,4),
                    SUBSTR(DEL_REGISTRO,12,2),
                    SUBSTR(DEL_REGISTRO,14,4),
                    SUBSTR(DEL_REGISTRO,18,6),
                    SUBSTR(DEL_REGISTRO,24,3)
               INTO WS-COD-OPERACION,
                    WS-COD-REFER,
                    WS-IND-TIP-CONTA,
                    WS-COD-CENTIM-EMP,
                    WS-COD-CONTA-EMP,
                    WS-FOR-PAGO
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM1
      ***         AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
                AND SUBSTR(CODIGO_REGISTRO,3,13) = :WS-NRO-ID-ORDENANTE1
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
                AND SUBSTR(DEL_REGISTRO,27,8) = :T08CT176.NUM-CTA-INT
           END-EXEC
 
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
 
      ***  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
           IF SQLCODE NOT EQUAL 000000000 THEN
             DISPLAY PGM 'VOY POR IF'
             CONTINUE
           ELSE
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'VOY POR COMISIONES'
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
           DISPLAY PGM 'WS-COD-OPERACION: '  WS-COD-OPERACION
           DISPLAY PGM 'WS-COD-REFER: '      WS-COD-REFER
           DISPLAY PGM 'WS-IND-TIP-CONTA: '  WS-IND-TIP-CONTA
           DISPLAY PGM 'WS-COD-CENTIM-EMP: ' WS-COD-CENTIM-EMP
           DISPLAY PGM 'WS-COD-CONTA-EMP: '  WS-COD-CONTA-EMP
           DISPLAY PGM 'WS-FOR-PAGO: '       WS-FOR-PAGO
 
                     MOVE WS-IND-TIP-CONTA
                       TO IND-TIP-CONTA      OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-EMP      OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-EMP     OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-SERV     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-SERV    OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-RETE     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-RETE    OF T08CT176
                     MOVE WS-COD-OPERACION
                       TO COD-OPERACION      OF T08CT176
                     MOVE WS-COD-REFER
                       TO COD-REFER          OF T08CT176
                     MOVE WS-FOR-PAGO
                       TO FOR-PAGO           OF T08CT176
               DISPLAY PGM 'COD-REFER CC:' COD-REFER OF T08CT176
             END-IF
             ELSE
      *******************************************************************
      ************************VOY POR COBRO NORMAL***********************
      *******************************************************************
               IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'C ' THEN
                  DISPLAY PGM 'VOY POR C'
                    MOVE COD-TIP-ORIENTACION OF MSG-IN
                      TO WS-COD-TIP-ORIENTACION
 
           EXEC SQL
             SELECT SUBSTR(DEL_REGISTRO,3,5),
                    SUBSTR(DEL_REGISTRO,8,4),
                    SUBSTR(DEL_REGISTRO,12,2),
                    SUBSTR(DEL_REGISTRO,14,4),
                    SUBSTR(DEL_REGISTRO,18,6),
                    SUBSTR(DEL_REGISTRO,24,3)
               INTO WS-COD-OPERACION,
                    WS-COD-REFER,
                    WS-IND-TIP-CONTA,
                    WS-COD-CENTIM-EMP,
                    WS-COD-CONTA-EMP,
                    WS-FOR-PAGO
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM
                AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
           END-EXEC
 
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
 
      ***  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
           IF SQLCODE NOT EQUAL 000000000 THEN
             DISPLAY PGM 'VOY POR IF'
             CONTINUE
           ELSE
                     MOVE WS-IND-TIP-CONTA
                       TO IND-TIP-CONTA      OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-EMP      OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-EMP     OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-SERV     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-SERV    OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-RETE     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-RETE    OF T08CT176
                     MOVE WS-COD-OPERACION
                       TO COD-OPERACION      OF T08CT176
                     MOVE WS-COD-REFER
                       TO COD-REFER          OF T08CT176
                     MOVE WS-FOR-PAGO
                       TO FOR-PAGO           OF T08CT176
                     DISPLAY PGM 'COD-REFER C:' COD-REFER OF T08CT176
              
               ELSE
      *******************************************************************
      ************************VOY POR PAGO NORMAL************************
      *******************************************************************
               IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'P ' THEN
                      DISPLAY PGM 'VOY POR P'
                      MOVE COD-TIP-ORIENTACION OF MSG-IN
                        TO WS-COD-TIP-ORIENTACION
 
           EXEC SQL
             SELECT SUBSTR(DEL_REGISTRO,3,5),
                    SUBSTR(DEL_REGISTRO,8,4),
                    SUBSTR(DEL_REGISTRO,12,2),
                    SUBSTR(DEL_REGISTRO,14,4),
                    SUBSTR(DEL_REGISTRO,18,6),
                    SUBSTR(DEL_REGISTRO,24,3)
               INTO WS-COD-OPERACION,
                    WS-COD-REFER,
                    WS-IND-TIP-CONTA,
                    WS-COD-CENTIM-EMP,
                    WS-COD-CONTA-EMP,
                    WS-FOR-PAGO
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM
                AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
           END-EXEC
 
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
 
      ***  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
           IF SQLCODE NOT EQUAL 000000000 THEN
             DISPLAY PGM 'VOY POR IF'
             CONTINUE
           ELSE
                     MOVE WS-IND-TIP-CONTA
                       TO IND-TIP-CONTA      OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-EMP      OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-EMP     OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-SERV     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-SERV    OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-RETE     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-RETE    OF T08CT176
                     MOVE WS-COD-OPERACION
                       TO COD-OPERACION      OF T08CT176
                     MOVE WS-COD-REFER
                       TO COD-REFER          OF T08CT176
                     MOVE WS-FOR-PAGO
                       TO FOR-PAGO           OF T08CT176
                     DISPLAY PGM 'COD-REFER C:' COD-REFER OF T08CT176
                    END-IF
                    ELSE
                     IF COD-TIP-ORIENTACION OF MSG-IN EQUAL 'RT' THEN
                      DISPLAY PGM 'VOY POR RT'
                      MOVE COD-TIP-ORIENTACION OF MSG-IN
                        TO WS-COD-TIP-ORIENTACION
 
           EXEC SQL
             SELECT SUBSTR(DEL_REGISTRO,3,5),
                    SUBSTR(DEL_REGISTRO,8,4),
                    SUBSTR(DEL_REGISTRO,12,2),
                    SUBSTR(DEL_REGISTRO,14,4),
                    SUBSTR(DEL_REGISTRO,18,6),
                    SUBSTR(DEL_REGISTRO,24,3)
               INTO WS-COD-OPERACION,
                    WS-COD-REFER,
                    WS-IND-TIP-CONTA,
                    WS-COD-CENTIM-EMP,
                    WS-COD-CONTA-EMP,
                    WS-FOR-PAGO
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM
                AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
           END-EXEC
 
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
 
      ***  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
           IF SQLCODE NOT EQUAL 000000000 THEN
             DISPLAY PGM 'VOY POR IF'
             CONTINUE
           ELSE
 
                     MOVE WS-IND-TIP-CONTA
                       TO IND-TIP-CONTA      OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-EMP      OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-EMP     OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-SERV     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-SERV    OF T08CT176
                     MOVE WS-COD-CONTA-EMP
                       TO COD-CONTA-RETE     OF T08CT176
                     MOVE WS-COD-CENTIM-EMP
                       TO COD-CENTIM-RETE    OF T08CT176
                     MOVE WS-COD-OPERACION
                       TO COD-OPERACION      OF T08CT176
                     MOVE WS-COD-REFER
                       TO COD-REFER          OF T08CT176
                     MOVE WS-FOR-PAGO
                       TO FOR-PAGO           OF T08CT176
                     DISPLAY PGM 'COD-REFER RT:' COD-REFER OF T08CT176
                 END-IF
                     END-IF
                    END-IF
                END-IF
               END-IF
              END-IF
             END-IF 
            END-IF
           END-IF.