      *************************
       IDENTIFICATION DIVISION.
      *************************
       PROGRAM-ID. CTB0001.
       AUTHOR. TITO CORONEL.
       INSTALLATION. BANCO PICHINCHA C.A.

      ****************************************************************
      **                                                            **
      **                INTERFACES - SIGLO21                        **
      **                                                            **
      ****************************************************************
      ****************************************************************
      **                                                            **
      **  MODULE NAME...: CTB0001                                   **
      **  APLICATION....: CUENTAS                                   **
      **  DATE GENERATED: 22,ENE,2003                               **
      **  TIME GENERATED: 08:35:49                                  **
      **  BY USER.......: TITO CORONEL SOLIS                        **
      **                                                            **
      ****************************************************************
      ** DESCRIPCION: CREA ARCHIVO CON INFORMACION CORRESPONDIENTE  **
      **              A CANJES Y CREACION DE CERTIFICADOS DE SEGU-  **
      **              ROS DE CUENTAS SIGLO 21 GANADOLAR Y GANADIA-  **
      **              RIO POR OFICINA Y PRODUCTO.                   **
      **===================  MODIFICACIONES ========================**
      **  AUTOR     FECHA  CAUSA DE LA MODIFICACION                 **
      **--------- -------- ---------------------------------------  **
      **......... DD-MM-AA .......................................  **
      **......... DD-MM-AA .......................................  **
      ****************************************************************
      /
      **********************
       ENVIRONMENT DIVISION.
      **********************
       CONFIGURATION SECTION.
       SPECIAL-NAMES.
           DECIMAL-POINT IS COMMA.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT ESTADIS ASSIGN TO ESTADIS
                  FILE STATUS IS FS-ESTA.
       DATA DIVISION.
       FILE SECTION.
       FD ESTADIS.
       01 REG-ESTADIS                PIC X(87).

      ****************************************************************
      ****************************************************************
      *  W O R K I N G   S T O R A G E                               *
      ****************************************************************
      ****************************************************************
       WORKING-STORAGE SECTION.
      ****************************************************************
      ** VARIABLES Y CONSTANTES                                     **
      ****************************************************************
       01 REG-GRABAR.
          05 EST-FEC-CORTE           PIC X(10).
          05 FILLER                  PIC X     VALUE ';'.
          05 EST-COD-OF-PRO          PIC 9(04).
          05 FILLER                  PIC X     VALUE ';'.
          05 EST-NOM-OFIPRO          PIC X(40).
          05 FILLER                  PIC X     VALUE ';'.
          05 EST-PRODUCTO            PIC X(10).
          05 FILLER                  PIC X     VALUE ';'.
          05 EST-COD-OF-MOD          PIC 9(04).
          05 FILLER                  PIC X     VALUE ';'.
          05 EST-CERTIF-CAN          PIC 9(06).
          05 FILLER                  PIC X     VALUE ';'.
          05 EST-CERTIF-APE          PIC 9(06).
          05 FILLER                  PIC X     VALUE ';'.
       01 AREA-VARIABLES.
          05 WS-COD-EMPRESA                PIC X(04) VALUE SPACES.
          05 WS-NOMBRE-OFICINA             PIC X(40) VALUE SPACES.
          05 WS-COD-CENT-CUENTA            PIC X(04) VALUE SPACES.
          05 WS-COD-CENT-ANTE              PIC X(04) VALUE SPACES.
          05 WS-TOT-LEIDOS                 PIC 9(06) VALUE ZEROS.
          05 WS-REG-GRABADOS               PIC 9(06) VALUE ZEROS.
          05 WS-ACUM-GANDIA-CAN            PIC 9(06) VALUE ZEROS.
          05 WS-ACUM-GANDIA-APE            PIC 9(06) VALUE ZEROS.
          05 WS-ACUM-GANDOL-CAN            PIC 9(06) VALUE ZEROS.
          05 WS-ACUM-GANDOL-APE            PIC 9(06) VALUE ZEROS.
          05 WS-ACUM-OTROS-CAN             PIC 9(06) VALUE ZEROS.
          05 WS-ACUM-OTROS-APE             PIC 9(06) VALUE ZEROS.
          05 FS-ESTA                       PIC 9(02) VALUE ZEROS.

      *--------------------------------------------------------------*
      * VARIABLES PARA INFORMACION DE ERRORES                        *
      *--------------------------------------------------------------*
       01  AREA-DE-ERRORES.
           05 LINEA-ERRORES.
              10 DESC-ERROR              PIC  X(60).
              10 ERROR-NUM               PIC  ZZZZ999999.

       01  LT-N-4                  PIC 9(2) VALUE 4.
      ***************************************************************
      *   SWITCH'S
      ***************************************************************
       01 SW-FIN-CURSOR                PIC  X(01)      VALUE 'N'.
          88 SI-FIN-CURSOR                             VALUE 'S'.
          88 NO-FIN-CURSOR                             VALUE 'N'.

      *--------------------------------------------------------------*
      * TABLAS                                                       *
      *--------------------------------------------------------------*

      ****************************************
      *                                      *
      *  INCLUDE DE LA TABLA                 *
      *                                      *
      ****************************************
           EXEC SQL
              INCLUDE T10PSE65
           END-EXEC.

           EXEC SQL
              INCLUDE T06TC006
           END-EXEC.

           EXEC SQL
              INCLUDE T08CT005
           END-EXEC.

      ****************************************************************
      * DECLARACION DE CURSORES.                                     *
      ****************************************************************
            EXEC SQL
             DECLARE CUR_CANJES CURSOR WITH HOLD FOR
              SELECT A.COD_CENTRO,
                     A.CODIGO_CENTRO_MO,
                     A.COD_TIPO_SEGURO,
                     B.COD_PROD
              FROM T10PSE65 A, T08CT005 B
              WHERE A.NUM_CTA_INT = B.NUM_CTA_INT
              AND   A.FEC_PROPU >= '13.01.2003'
              ORDER BY A.COD_CENTRO, A.CODIGO_CENTRO_MO
            END-EXEC.

      ****************************************************************
      ****************************************************************
       LINKAGE SECTION.

      *-- -Area de comunicacion.
      ****************************************************************
      ****************************************************************
      ** P R O C E D U R E   D I V I S I O N                        **
      ****************************************************************
      ****************************************************************
       PROCEDURE DIVISION.

      **INICIO-PROGRAMA-CTB0001
           PERFORM 1000-INICIO.

           PERFORM 2000-PROCESO.

           PERFORM 8000-FINAL.

      **FINAL-PROGRAMA-CTB0001

      ****************************************************************
      ** 1000-INICIO                                                **
      **------------------------------------------------------------**
      ** - Tomar el control de errores...                           **
      ** - Inicializacion de variables...                           **
      ****************************************************************
       1000-INICIO.

           INITIALIZE RETURN-CODE
      *--  Toma del control de errores DB2 y de Servicios invocados.
           @DEFINE(NO-ERROSQL).
           @CTRLERR(APLICACION).
           @INIBAT().
           IF TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
              MOVE '1000-INICIO, ERROR EN MACRO INIBAT' TO DESC-ERROR
              MOVE NUM-ERROR OF S21-AREA-ERROR   TO ERROR-NUM
              @ERROR(ERROR, ERROR-NUM, LINEA-ERRORES)
           END-IF.
           MOVE COD-EMPRESA OF S21-AREA-ENTORNO TO WS-COD-EMPRESA.

      ****************************************************************
      ** 2000-PROCESO.                                              **
      **------- ----------------------------------------------------**
      ** - SE PROCEDE A ABRIR EL CURSOR, LUEGO SE LO PROCESA Y      **
      ** - FINALMENTE SE LO CIERRA.                                 **
      ****************************************************************
       2000-PROCESO.
            PERFORM A2005-OPEN-ESTADIS.
            PERFORM A2010-OPEN-CURSOR.
            PERFORM A2020-PROCESA-CURSOR.
            EXEC SQL
               CLOSE CUR_CANJES
            END-EXEC.

       A2005-OPEN-ESTADIS.
            OPEN OUTPUT ESTADIS.
            IF FS-ESTA NOT EQUAL ZEROS
              MOVE 'ERROR EN OPEN ARCHIVO DE ESTADISTICAS'
                TO DESC-ERROR
              MOVE FS-ESTA TO ERROR-NUM
              MOVE 8           TO RETURN-CODE
              @ERROR(ERROR, ERROR-NUM, LINEA-ERRORES)
            END-IF.

       A2010-OPEN-CURSOR.
           EXEC SQL
                OPEN CUR_CANJES
           END-EXEC.
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           IF NOT IND-SQL-CORRECTO
              MOVE 'ERROR EN OPEN DEL CURSOR DE CANJES   '
                TO DESC-ERROR
              MOVE SQLSTATE TO ERROR-NUM
              MOVE 8        TO RETURN-CODE
              @ERROR(ERROR, ERROR-NUM, LINEA-ERRORES)
           END-IF.

       A2020-PROCESA-CURSOR.
      *  SE LEE EL PRIMER REGISTRO DEL CURSOR.
           SET NO-FIN-CURSOR TO TRUE.
           PERFORM A2030-LEER-CURSOR.
           PERFORM UNTIL SI-FIN-CURSOR
      *  SE PROCESA HASTA FIN DE CURSOR.
              PERFORM A2040-PROCESA-REGISTRO
              PERFORM A2030-LEER-CURSOR
              IF SI-FIN-CURSOR
                 PERFORM A2050-MUEVE-DATOS
              END-IF
           END-PERFORM.

       A2030-LEER-CURSOR.
           EXEC SQL
              FETCH CUR_CANJES
               INTO :T10PSE65.COD-CENTRO,
                    :T10PSE65.CODIGO-CENTRO-MO,
                    :T10PSE65.COD-TIPO-SEGURO,
                    :T08CT005.COD-PROD
           END-EXEC.
           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           IF IND-SQL-CORRECTO
              ADD 1 TO WS-TOT-LEIDOS
           ELSE
              IF IND-NO-ENCONTRADO
                 SET SI-FIN-CURSOR  TO TRUE
              ELSE
                 MOVE 'ERROR AL REALIZAR EL FETCH EN CANJES'
                   TO DESC-ERROR
                 MOVE SQLSTATE TO ERROR-NUM
                 MOVE 8        TO RETURN-CODE
                 @ERROR(ERROR, ERROR-NUM, LINEA-ERRORES)
              END-IF
           END-IF.

       A2040-PROCESA-REGISTRO.
           IF COD-CENTRO OF T10PSE65 NOT EQUAL WS-COD-CENT-CUENTA
              IF WS-COD-CENT-CUENTA NOT EQUAL SPACES
                 PERFORM A2050-MUEVE-DATOS
                 PERFORM A2070-ENCERA-VARIABLES
              END-IF
              MOVE COD-CENTRO       OF T10PSE65 TO WS-COD-CENT-CUENTA
              MOVE CODIGO-CENTRO-MO OF T10PSE65 TO WS-COD-CENT-ANTE
              PERFORM A2260-LEER-OFICINA
           END-IF.
           IF CODIGO-CENTRO-MO OF T10PSE65 NOT EQUAL WS-COD-CENT-ANTE
              PERFORM A2050-MUEVE-DATOS
              PERFORM A2070-ENCERA-VARIABLES
              MOVE CODIGO-CENTRO-MO OF T10PSE65 TO WS-COD-CENT-ANTE
           END-IF.
           PERFORM A2080-ACUMULA-VARIABLES.

       A2050-MUEVE-DATOS.
           MOVE FEM-OPERACION OF S21-AREA-ENTORNO
             TO EST-FEC-CORTE.
           MOVE WS-COD-CENT-CUENTA
             TO EST-COD-OF-PRO.
           MOVE WS-NOMBRE-OFICINA
             TO EST-NOM-OFIPRO.
           MOVE WS-COD-CENT-ANTE
             TO EST-COD-OF-MOD.
           IF WS-ACUM-GANDIA-CAN GREATER 0 OR
              WS-ACUM-GANDIA-APE GREATER 0
              MOVE WS-ACUM-GANDIA-CAN TO EST-CERTIF-CAN
              MOVE WS-ACUM-GANDIA-APE TO EST-CERTIF-APE
              MOVE 'GANADIARIO'       TO EST-PRODUCTO
              PERFORM A2060-GRABA-REGISTRO
           END-IF.
           IF WS-ACUM-GANDOL-CAN GREATER 0 OR
              WS-ACUM-GANDOL-APE GREATER 0
              MOVE WS-ACUM-GANDOL-CAN TO EST-CERTIF-CAN
              MOVE WS-ACUM-GANDOL-APE TO EST-CERTIF-APE
              MOVE 'GANADOLAR '       TO EST-PRODUCTO
              PERFORM A2060-GRABA-REGISTRO
           END-IF.
           IF WS-ACUM-OTROS-CAN GREATER 0 OR
              WS-ACUM-OTROS-APE GREATER 0
              MOVE WS-ACUM-OTROS-CAN TO EST-CERTIF-CAN
              MOVE WS-ACUM-OTROS-APE TO EST-CERTIF-APE
              MOVE 'OTROS     '       TO EST-PRODUCTO
              PERFORM A2060-GRABA-REGISTRO
           END-IF.

       A2060-GRABA-REGISTRO.
           WRITE REG-ESTADIS FROM REG-GRABAR.
           IF FS-ESTA NOT EQUAL 0
              MOVE 'ERROR AL GRABAR ARCHIVO DE ESTADISTICAS'
                TO DESC-ERROR
              MOVE FS-ESTA TO ERROR-NUM
              MOVE 8           TO RETURN-CODE
              @ERROR(ERROR, ERROR-NUM, LINEA-ERRORES)
           ELSE
              ADD 1 TO WS-REG-GRABADOS
           END-IF.

       A2070-ENCERA-VARIABLES.
           MOVE ZEROS TO WS-ACUM-GANDIA-CAN
                         WS-ACUM-GANDIA-APE
                         WS-ACUM-GANDOL-CAN
                         WS-ACUM-GANDOL-APE
                         WS-ACUM-OTROS-CAN
                         WS-ACUM-OTROS-APE.

       A2080-ACUMULA-VARIABLES.
           EVALUATE COD-PROD OF T08CT005
              WHEN 4052
              WHEN 4552
                 IF COD-TIPO-SEGURO OF T10PSE65 EQUAL 'C' OR 'D' OR
                                                      'F' OR 'G'
                    ADD 1 TO WS-ACUM-GANDIA-CAN
                 ELSE
                    ADD 1 TO WS-ACUM-GANDIA-APE
                 END-IF
              WHEN 4053
              WHEN 4553
              WHEN 4063
              WHEN 4563
              WHEN 4054
              WHEN 4554
                 IF COD-TIPO-SEGURO OF T10PSE65 EQUAL 'C' OR 'D' OR
                                                      'F' OR 'G'
                    ADD 1 TO WS-ACUM-GANDOL-CAN
                 ELSE
                    ADD 1 TO WS-ACUM-GANDOL-APE
                 END-IF
              WHEN OTHER
                 IF COD-TIPO-SEGURO OF T10PSE65 EQUAL 'C' OR 'D' OR
                                                      'F' OR 'G'
                    ADD 1 TO WS-ACUM-OTROS-CAN
                 ELSE
                    ADD 1 TO WS-ACUM-OTROS-APE
                 END-IF
           END-EVALUATE.

       A2260-LEER-OFICINA.
           EXEC SQL
              SELECT NOMBRE
              INTO   :T06TC006.NOMBRE
              FROM   T06TC006
              WHERE  COD_ENTIDAD     = :WS-COD-EMPRESA
              AND    COD_CENTRO      = :WS-COD-CENT-CUENTA
           END-EXEC.
           MOVE SQLSTATE         TO SQLSTATE-SIGLO
           IF IND-SQL-CORRECTO
              MOVE NOMBRE OF T06TC006
                TO WS-NOMBRE-OFICINA
           ELSE
              MOVE SPACES
                TO WS-NOMBRE-OFICINA
           END-IF.

      ****************************************************************
      ** 8000-FINAL.                                                **
      **------------------------------------------------------------**
      ****************************************************************
       8000-FINAL.
           PERFORM A8100-DISPLAY-TOTALES.
           CLOSE ESTADIS.
           IF  RETURN-CODE   <=  LT-N-4
	       EXEC SQL COMMIT END-EXEC
	   END-IF.
           STOP RUN.

       A8100-DISPLAY-TOTALES.
           DISPLAY 'REGISTROS LEIDOS      = ' WS-TOT-LEIDOS.
           DISPLAY 'REGISTROS GRABADOS    = ' WS-REG-GRABADOS.
