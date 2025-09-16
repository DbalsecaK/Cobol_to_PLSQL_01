      **************************
       IDENTIFICATION DIVISION.
      **************************
       PROGRAM-ID. CTB0010.
       AUTHOR. WALTER MARTINEZ.
       INSTALLATION.
      ***************************************************************
      *     ------- DATOS IDENTIFICACION DEL PROGRAMA   --------    *
      *                                                   BATCH     *
      *                                                             *
      * PROGRAMA        :  CTB0010.                                 *
      * FEC.CODIFICAC.  :  06-05-2004.                              *
      ***************************************************************

      **********************
       ENVIRONMENT DIVISION.
      **********************
       CONFIGURATION SECTION.
       SPECIAL-NAMES.
           DECIMAL-POINT IS COMMA.
       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT IMPRES01
               ASSIGN TO IMPRES01
               ORGANIZATION IS SEQUENTIAL.

      ****************************************************
       DATA DIVISION.
      ****************************************************

       FILE SECTION.

        FD  IMPRES01
            RECORDING  MODE     IS         F
            LABEL      RECORDS  STANDARD.
        01  R-IMPRES01                     PIC X(133).

      ****************************************************
       WORKING-STORAGE SECTION.
      ****************************************************
      *--------------------------------------------------*
      *       CAMPOS NUMERICOS                           *
      *--------------------------------------------------*

       01 FS-FILE-STATUS.
         05  FS-FCUENTAI               PIC XX.
             88  FS-FCUENTAI-CORRECTO  VALUE '00'.

       01  WS-NUMERICOS.
           05 CTRL-CUENTA            PIC 9(8) VALUE 1.
           05 WS-IMPORTE             PIC S9(12)V9(2) VALUE ZEROS.
           05 WS-VALOR-ANT           PIC S9(12)V9(2) VALUE ZEROS.
           05 WS-VALOR-C1            PIC S9(12)V9(2) VALUE ZEROS.
           05 WS-VALOR-C2            PIC S9(12)V9(2) VALUE ZEROS.
           05 WS-PREGUNTA            PIC 9(5).
           05 WS-SUC-ALTA            PIC 9(4).
           05 WS-NUM-ERROR           PIC 9(02) VALUE ZEROS.
           
       01  WS-NUM-CUENTA             PIC 9(10).
       01  WS-NUM-CUENTA-REDE REDEFINES WS-NUM-CUENTA.
           05  WS-CUENTA             PIC 9(8).
           05  WS-EXPEDIENTE         PIC X(2).

       01  WS-CONTADORES.
           05  WS-CONT-LEIDOS        PIC 9(06) VALUE ZEROS.
           05  WS-CONT-GRABADOS      PIC 9(06) VALUE ZEROS.
           05  WN-CONT-PAG1          PIC 9(07) VALUE ZEROS.
           05  WN-CONT-LIN1          PIC 9(02) VALUE ZEROS.
           
       01  WS-ALFANUMERICAS.
           05 WS-FILE-STATUS         PIC X(02) VALUE SPACES.
           05 WS-FEC-VALOR           PIC X(10) VALUE SPACES.
           05 WS-FEM-OPERACION       PIC X(10) VALUE SPACES.

       01  WS-HORA-SISTEMA.
           05 WS-HORAS              PIC X(2).
           05 FILLER                PIC X(1) VALUE ':'.
           05 WS-MINUTOS            PIC X(2).
           05 FILLER                PIC X(1) VALUE ':'.
           05 WS-SEGUNDOS           PIC X(2).

       01  AREA-INFORMACION.
           05  WS-PARRAFO            PIC X(30)  VALUE SPACES.
           05  WS-TEXTO              PIC X(50)  VALUE SPACES.

       01  WS-TIMESTAMP.
           05 WS-TIMES-INICIO       PIC X(26) VALUE SPACES.
           05 FILLER                PIC X.
           05 WS-TIMES-FIN          PIC X(26) VALUE SPACES.

       01  LT-N-0                   PIC 9(1)  VALUE   0.
       01  LT-N-1                   PIC 9(1)  VALUE   1.
       01  LT-N-7                   PIC 9(1)  VALUE   7.
       01  LT-N-16                  PIC 9(2)  VALUE  16.       
       01  LT-N-60                  PIC 9(2)  VALUE  60.       
       01  LT-N-ZEROS               PIC S9(13)V9(2) USAGE COMP-3
                                              VALUE ZEROS.
      *--------------------------------------------------*
      * AREA DE CABECERA Y DETALLE DEL REPORTE           *
      *--------------------------------------------------*
       01 CABE00.
          05 CABE00-NOMBRE-EMP  PIC X(40).
          05 FILLER             PIC X(92)       VALUE SPACES.

       01 CABE01.
          05 FILLER             PIC X(7)        VALUE 'CTB0010'.
          05 FILLER             PIC X(21)       VALUE SPACES.
          05 WX-LITERAL-CABE01  PIC X(69)       VALUE
        'Reporte del Control de cupos de sobregiros virtuales       '.
          05 FILLER             PIC X(16)       VALUE SPACES.
          05 FILLER             PIC X(9)        VALUE 'FECHA  = '.
          05 WX-FECHA-CABE01    PIC X(10)       VALUE SPACES.

       01 CABE02.
          05 WX-LISTADO-CABE02  PIC X(8)        VALUE SPACES.
          05 FILLER             PIC X(105)      VALUE SPACES.
          05 FILLER             PIC X(11)       VALUE 'HORA   =   '.
          05 WN-HORA-CABE02     PIC 99.99.99    VALUE ZEROS.

       01 CABE03.
          05 FILLER             PIC X(4)        VALUE SPACES.
          05 FILLER             PIC X(35)       VALUE SPACES.
          05 WX-OFICINA-CABE03  PIC X(45)       VALUE SPACES.
          05 FILLER             PIC X(29)       VALUE SPACES.
          05 FILLER             PIC X(12)       VALUE 'PAGINA =    '.
          05 WN-PAG-CABE03      PIC ZZZ.ZZ9.

       01 GUION                 PIC X(132)      VALUE ALL '='.
       01 BLANCO                PIC X(132)      VALUE ALL ' '.

        
       01 GUION2.
          05 FILLER             PIC X(25)  VALUE SPACES.
          05 FILLER             PIC X(107) VALUE ALL '='.
          
       01 CABE04.
          05 FILLER         PIC X(11) VALUE 'Cuenta     '.
          05 FILLER         PIC X(04) VALUE SPACES.
          05 FILLER         PIC X(20) VALUE '   Cupo Disponible  '.
          05 FILLER         PIC X(04) VALUE SPACES.
          05 FILLER         PIC X(60) VALUE 'Nombre  del Titular'.
          05 FILLER         PIC X(33) VALUE SPACES.

       01 CABE05.
          05 FILLER         PIC X(25) VALUE SPACES.
          05 FILLER         PIC X(10) VALUE 'Fecha'.
          05 FILLER         PIC X(02) VALUE SPACES.
          05 FILLER         PIC X(20) VALUE '   Valor Sobregirado'.
          05 FILLER         PIC X(02) VALUE SPACES.
          05 FILLER         PIC X(20) VALUE '      Cupo Utilizado'.
          05 FILLER         PIC X(53) VALUE SPACES.


       01 WX-DETALLE.
          05 DET-CTA        PIC 9(08)       VALUE ZEROS.
          05 FILLER         PIC X(01)       VALUE '-'.
          05 DET-EXP        PIC X(02)       VALUE ZEROS.
          05 FILLER         PIC X(04)       VALUE SPACES.
          05 DET-MONTO      PIC -ZZZZZZZZ.ZZZ.ZZ9,99.
          05 FILLER         PIC X(04)       VALUE SPACES.
          05 DET-NOMBRE     PIC X(60)       VALUE SPACES.


       01 WX-DETALLE1.
          05 FILLER         PIC X(25)       VALUE SPACES.       
          05 DET1-FECHA     PIC X(10)       VALUE SPACES.
          05 FILLER         PIC X(02)       VALUE SPACES.
          05 DET1-MONTO1    PIC -ZZZZZZZZ.ZZZ.ZZ9,99.
          05 FILLER         PIC X(02)       VALUE SPACES.
          05 DET1-MONTO2    PIC -ZZZZZZZZ.ZZZ.ZZ9,99.
          05 FILLER         PIC X(53)       VALUE SPACES. 


      *-----> SWITCH PARA CONOCER SI DEBEMOS IMPRIMIR LAS ESTADSTICAS
      *              DEL IMPRESO O NO.
       01 SWITCH-IMP               PIC X(1) VALUE SPACES.
          88 SW-CABECERA-SI        VALUE 'S'.
          88 SW-CABECERA-NO        VALUE 'N'.

      *--------------------------------------------------*
      *   AREA INCLUDE DE SQL Y DE ESTRUCTURAS DE TABLAS *
      *--------------------------------------------------*

           EXEC SQL
                INCLUDE T03LOG47
           END-EXEC.

           EXEC SQL
                INCLUDE T06TC002
           END-EXEC.
           
           EXEC SQL
                INCLUDE T08CT141
           END-EXEC.

           EXEC SQL
                INCLUDE T17SOB84 
           END-EXEC.

           EXEC SQL
                INCLUDE T17RET85
           END-EXEC.

                      
      *--------------------------------------------------*
      *      AREA DE DEFINICION DE LITERALES             *
      *--------------------------------------------------*

       01  LT-A-0                   PIC X(01) VALUE '0'.
       01  LT-A-1                   PIC X(01) VALUE '1'.
       01  LT-A-2                   PIC X(01) VALUE '2'.
       
       01  LT-A-PARRAFO1000         PIC X(27) VALUE
           '1000-INICIO'.
           
       01  LT-A-PARRAFO1240         PIC X(27) VALUE
           'A1240-BUSCA-DESCRIP'.
           
       01  LT-A-PARRAFO1300         PIC X(27) VALUE
           'A1110-OPEN-CURLOG'.
           
       01  LT-A-PARRAFO2000         PIC X(21) VALUE
           '2000-PROCESO'.
           
       01  LT-A-PARRAFO3000         PIC X(27) VALUE
           'A3100-FETCH-CUENTAS'.
           
       01  LT-A-ERROR-GXINIBAT      PIC X(35)  VALUE
           'ERROR EN MACRO GXINIBAT'.
           
       01  LT-A-PARRAFO8000         PIC X(21) VALUE
           '8000-FINAL'.
           
       01  LT-A-ERROR-AQININOD      PIC X(35)  VALUE
           'ERROR EN MACRO AQININOD'.
           
       01  LT-A-E-OPEN-CURSOR       PIC X(41)  VALUE
           'ERROR ABRIENDO CURSOR DE T03LOG47'.
           
       01  LT-A-ERRORFE-CUENTAS     PIC X(34)  VALUE
           'ERROR EN FETCH CURSOR DE T03LOG47'.
           
       01  LT-A-ERROR-CLOSE-CURSOR  PIC X(41)  VALUE
           'ERROR CERRANDO CURSOR DE T03LOG47'.
           
       01  LT-A-COMMIT              PIC X(12)  VALUE
           'ERROR COMMIT'.
           
       01  LT-A-ROLLBACK            PIC X(20)  VALUE
           'ERROR ROLLBACK'.

       01  LT-A-CTB0010             PIC X(07)  VALUE 'CTB0010'.


      *--------------------------------------------------*
      *             AREA DE SWITCHES                     *
      *--------------------------------------------------*
       01  SW-ERROR                 PIC X(2) VALUE 'NO'.
           88  SI-ERROR             VALUE 'SI'.
           88  NO-ERROR             VALUE 'NO'.

      *-----> SWITCH PARA CONOCER FIN DE CURSOR
       01  SW-CURSOR-GENERAL        PIC X(1) VALUE '0'.
               88 FIN-CURSOR-SI              VALUE '1'.
               88 FIN-CURSOR-NO              VALUE '0'.


      *********************************************
      *-- DECLARAR CURSORES DE TABLA DE LOG
      *********************************************

           EXEC SQL
              DECLARE CURSOR-SOP  CURSOR FOR
                 SELECT A.NUM_CTA_INT      , 
                        A.COD_TIP_EXPE     ,
                        A.COD_EMPRESA      ,
                        A.IMP_AUTORIZACION ,
                        A.IMP_UTILIZADO    ,
                        C.IMP_CONC_CAL     ,
                        B.FECHA_INICIO     ,
                        C.IMP_SOBREGIRO    ,
                        C.COD_CONC_LIQ     ,
                        C.FEC_SOBREGIRO    
                 FROM T08CT141 A,
                      T17SOB84 B, 
                      T17RET85 C
                 WHERE A.COD_TIP_EXPE   = B.COD_TIP_EXPE
                 AND   A.NUM_CTA_INT    = B.NUM_CTA_INT
                 AND   A.COD_EMPRESA    = B.COD_EMPRESA
                 AND   A.IND_STATUS     = 'A'
                 AND   B.FEC_FIN        = '31.12.9999'
                 AND   B.IND_ESTADO     = 'N'
                 AND   B.FECHA_INICIO  >= '03.05.2004'
                 AND   C.FEC_SOBREGIRO >= B.FECHA_INICIO
                 AND   A.COD_TIP_EXPE   = C.COD_TIP_EXPE
                 AND   A.NUM_CTA_INT    = C.NUM_CTA_INT
                 AND   A.COD_EMPRESA    = C.COD_EMPRESA
                 AND   C.COD_CONC_LIQ   = '350'
                 ORDER BY A.COD_TIP_EXPE, 
                          A.NUM_CTA_INT, 
                          C.FEC_SOBREGIRO
           END-EXEC.


       LINKAGE SECTION.

      **********************************************
       PROCEDURE DIVISION.

      **INICIO-PROGRAMA-CTB0010
      **********************************************

           PERFORM 1000-INICIO.

          PERFORM 2000-PROCESO
            UNTIL FIN-CURSOR-SI.

           PERFORM 8000-FINAL.
      **FINAL-PROGRAMA-CTB0010


       1000-INICIO.
      *****************************************************************
      *  + EL CONTROL DE ERRORES NO LO REALIZARA LA ARQUITECTURA.     *
      *  + SE LEE LA PRIMERA FILA DEL CURSOR DE CUENTAS CON EXTRACTO  *
      *    AGRUPADO.                                                  *
      *****************************************************************
           DISPLAY 'INICIO'
           INITIALIZE RETURN-CODE

           PERFORM A1100-FORMATEO-ARQUITECTURA.

           MOVE LT-A-CTB0010  TO COD-USUARIO      OF S21-AREA-ENTORNO
           MOVE FEM-OPERACION OF S21-AREA-ENTORNO TO WS-FEM-OPERACION
                                                     WX-FECHA-CABE01
           MOVE HOR-MAQUINA   OF S21-AREA-ENTORNO TO WN-HORA-CABE02.

           OPEN OUTPUT IMPRES01.

           MOVE  FEM-CONTABLE OF S21-AREA-ENTORNO  TO  WS-FEC-VALOR
           
           INITIALIZE WS-CONTADORES.

           MOVE ZEROS              TO WN-CONT-PAG1
           MOVE 70                 TO WN-CONT-LIN1

           SET  SW-CABECERA-NO     TO TRUE
           SET FIN-CURSOR-NO TO TRUE

      *-----> RECUPERA EMPRESA TCS04002
           PERFORM A1250-RECUPERA-EMPRESA.
           
           PERFORM A1110-OPEN-CURLOG.

           PERFORM A1120-FETCH-CURLOG.

           ADD   LT-N-1            TO   WN-CONT-PAG1
           MOVE  WN-CONT-PAG1      TO   WN-PAG-CABE03
           WRITE R-IMPRES01        FROM GUION  AFTER PAGE
           WRITE R-IMPRES01        FROM CABE00 AFTER 1
           WRITE R-IMPRES01        FROM CABE01 AFTER 1
           WRITE R-IMPRES01        FROM CABE02 AFTER 1
           WRITE R-IMPRES01        FROM CABE03 AFTER 1
           MOVE  5                 TO   WN-CONT-LIN1.
                
       A1100-FORMATEO-ARQUITECTURA.
      **************************************************************
      *  INICIALIZAMOS LAS MACROS DE ARQUITECTURA.                **
      **************************************************************
           DISPLAY 'FORMATEA'
           @DEFINE(NO-ERROSQL).
           @CTRLERR(APLICACION).
           @INIBAT()

           IF TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
              SET SI-ERROR                     TO  TRUE
              MOVE LT-A-ERROR-GXINIBAT         TO  WS-TEXTO
              MOVE LT-A-PARRAFO1000            TO  WS-PARRAFO
              @ERROR(ERROR,NUM-ERROR OF S21-AREA-ERROR,AREA-INFORMACION)
           END-IF.
           MOVE '1' TO COD-IDIOMA      OF S21-AREA-ENTORNO.



       A1250-RECUPERA-EMPRESA.
      **************************************************************
      * - LLAMA AL SERVICIO TCS04002 PARA RECUPERAR EL NOMBRE DE LA
      * ENTIDAD DESDE TABLA DE ENTIDADES T06TC004.
      **************************************************************
           DISPLAY 'RECUPERA-EMPRESA'
           INITIALIZE MSG-IN-TCS04002

           MOVE 'R'
             TO ACC-SERV                   OF MSG-IN-TCS04002

           MOVE 1
             TO NUM-REGE                   OF MSG-IN-TCS04002

           MOVE '0'
             TO IND-TIPO-LIS               OF MSG-IN-TCS04002

           MOVE 1
             TO NUM-CLAVE                 OF MSG-IN-TCS04002

           MOVE ZEROS
             TO NUM-CONDICION-ADICIONAL   OF MSG-IN-TCS04002

           MOVE COD-EMPRESA               OF S21-AREA-ENTORNO
             TO COD-ENTIDAD               OF MSG-IN-TCS04002


             @INVOCAR(TCS04002,B)


           EVALUATE TRUE

              WHEN NUM-REGS     OF MSG-OUT-TCS04002 NOT = ZEROS

                   MOVE NOMBRE  OF MSG-OUT-TCS04002(1)
                     TO CABE00-NOMBRE-EMP

              WHEN OTHER
                   DISPLAY '*****************************************'
                   DISPLAY '*  ERROR AL BUSCAR NOMBRE ENTIDAD DESDE *'
                   DISPLAY '*  SERVICIO  TCS04002, PARRAFO A1250-RE *'
                   DISPLAY '*****************************************'

                   MOVE LT-N-16 TO RETURN-CODE

                   PERFORM  8000-FINAL

           END-EVALUATE.


       A1110-OPEN-CURLOG.
      **************************************************************
      *  ABRIR CURSOR   PARA PROCESAR                             **
      **************************************************************
           DISPLAY 'OPEN CURSOR'
           EXEC SQL
              OPEN CURSOR-SOP
           END-EXEC.
 
           MOVE SQLSTATE   TO SQLSTATE-SIGLO.
       
           IF NOT IND-SQL-CORRECTO
              MOVE LT-A-PARRAFO1300     TO WS-PARRAFO
              MOVE LT-A-E-OPEN-CURSOR   TO WS-TEXTO
              @ERROR(ERROR,SQLSTATE-SIGLO,AREA-INFORMACION)
           END-IF.



       2000-PROCESO.
      ***************************************************************
      ** 2000-PROCESO.
      ***************************************************************
      
           PERFORM 8300-IMPRIME-REPORTE.
           
           PERFORM A1120-FETCH-CURLOG.

       A1120-FETCH-CURLOG.
      *************************************************************
      **  LEE EL CORRESPONDIENTE CURSOR DE LA TABLA DE EXTRCTOS  **
      *************************************************************

           EXEC SQL
              FETCH CURSOR-SOP
               INTO :T08CT141.NUM-CTA-INT      , 
                    :T08CT141.COD-TIP-EXPE     ,
                    :T08CT141.COD-EMPRESA      ,
                    :T08CT141.IMP-AUTORIZACION ,
                    :T08CT141.IMP-UTILIZADO    ,
                    :T17RET85.IMP-CONC-CAL     ,
                    :T17SOB84.FECHA-INICIO     ,
                    :T17RET85.IMP-SOBREGIRO    ,
                    :T17RET85.COD-CONC-LIQ     ,
                    :T17RET85.FEC-SOBREGIRO    
           END-EXEC.
                  
           MOVE SQLSTATE    TO  SQLSTATE-SIGLO.
       
           EVALUATE TRUE
               WHEN IND-SQL-CORRECTO
                    ADD 1 TO WS-CONT-LEIDOS
               WHEN IND-NO-ENCONTRADO
                    SET FIN-CURSOR-SI TO TRUE
               WHEN OTHER
                    MOVE LT-A-ERRORFE-CUENTAS  TO WS-TEXTO
                    MOVE LT-A-PARRAFO3000      TO WS-PARRAFO
                    MOVE NUM-CTA-INT           OF T03LOG47
                    TO   WS-PARRAFO(20:8)
                    MOVE COD-TIP-EXPE          OF T03LOG47
                    TO   WS-PARRAFO(28:2)
                    @LOGERR(ERROR,SQLSTATE-SIGLO,AREA-INFORMACION)
                    @ERROR(ERROR,SQLSTATE-SIGLO,AREA-INFORMACION)
           END-EVALUATE.


      ******************************************************************
      * A2500-MUEVE-REPORTE.                                           *
      * ========================                                       *
      *        MUEVE LOS DATOS DE LA TABLA T03LOG47 PARA IMPRIMIRLO EN *
      * EN REPORTE                                                     *
      ******************************************************************
       A2500-MUEVE-REPORTE.

           PERFORM 8300-IMPRIME-REPORTE.
          
       8000-FINAL.
      *************************************************************
      *   CIERRA EL CURSOR  DE CUENTAS                           **
      *************************************************************
           DISPLAY 'FINAL'
           PERFORM A8100-CERRAR-CURSOR.

           CLOSE IMPRES01.
           
           MOVE ZEROS TO RETURN-CODE.

           GOBACK.

       A8100-CERRAR-CURSOR.
      **************************************************************
      **  A8100-CERRAR-CURSORES.                                  **
      **************************************************************
           DISPLAY 'CLOSE CURSOR'
           EXEC SQL
              CLOSE CURSOR-SOP
           END-EXEC.
           
           MOVE ZEROS TO SQLCODE   
                         SQLSTATE-SIGLO   
                         SQLSTATE
                         NUM-ERROR  OF S21-AREA-ERROR
                         TIPO-ERROR OF S21-AREA-ERROR.

       8300-IMPRIME-REPORTE.
      **************************************************************
      ** 8300-IMPRIME-REPORTE.
      **************************************************************

      *     IF WN-CONT-LIN1 > LT-N-60

      *     END-IF.
 
           IF CTRL-CUENTA NOT EQUAL NUM-CTA-INT OF T08CT141
              MOVE NUM-CTA-INT              OF T08CT141
                TO DET-CTA
              MOVE COD-TIP-EXPE             OF T08CT141
                TO DET-EXP
              MOVE IMP-AUTORIZACION         OF T08CT141
                TO WS-IMPORTE
              MOVE WS-IMPORTE
                TO DET-MONTO
              PERFORM 8400-BUSCA-NOMBRE
              WRITE R-IMPRES01        FROM BLANCO AFTER 1
              WRITE R-IMPRES01        FROM BLANCO AFTER 1
              WRITE R-IMPRES01        FROM GUION  AFTER 1
              WRITE R-IMPRES01        FROM CABE04 AFTER 1
              WRITE R-IMPRES01        FROM GUION  AFTER 1
              WRITE R-IMPRES01        FROM WX-DETALLE AFTER 1
              WRITE R-IMPRES01        FROM BLANCO AFTER 1
              WRITE R-IMPRES01        FROM CABE05 AFTER 1
      *        WRITE R-IMPRES01        FROM GUION2 AFTER 1
              ADD 7 TO WN-CONT-LIN1
              ADD 1 TO WS-CONT-GRABADOS              
              MOVE NUM-CTA-INT OF T08CT141 TO CTRL-CUENTA
              MOVE ZEROS TO WS-VALOR-ANT
           END-IF.
 
           MOVE IMP-SOBREGIRO  OF T17RET85
             TO WS-VALOR-C1
           
           IF WS-VALOR-ANT > WS-VALOR-C1
              MOVE ZEROS TO WS-VALOR-C2
           ELSE
             COMPUTE WS-VALOR-C2 = WS-VALOR-C1 - WS-VALOR-ANT
           END-IF
           
           MOVE WS-VALOR-C2
             TO DET1-MONTO2
           
           MOVE WS-VALOR-C1
             TO DET1-MONTO1
 
           MOVE FEC-SOBREGIRO  OF T17RET85
             TO DET1-FECHA
 
           ADD   LT-N-1     TO   WN-CONT-LIN1
 
           WRITE R-IMPRES01 FROM WX-DETALLE1 AFTER 1.
           
           MOVE IMP-SOBREGIRO  OF T17RET85
             TO WS-VALOR-ANT.
             
       8400-BUSCA-NOMBRE.
       
           MOVE COD-TIP-EXPE         OF T08CT141
             TO COD-TIP-EXPE         OF MSG-IN-PES11001
             
           MOVE NUM-CTA-INT          OF T08CT141
             TO NUM-CTA-INT          OF MSG-IN-PES11001
             
           MOVE COD-EMPRESA          OF T08CT141
             TO COD-EMPRESA          OF MSG-IN-PES11001
             
           MOVE '01'
             TO COD-TIPO-INTERVEN    OF MSG-IN-PES11001
             
           MOVE   1  
             TO NUM-ORDEN-INTERV     OF MSG-IN-PES11001
             
           MOVE  '1' 
             TO COD-IDIOMA           OF MSG-IN-PES11001.

           @INVOCAR(PES11001,C).

           IF NUM-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
              MOVE 'Error al buscar el nombre'  
                TO DET-NOMBRE
           ELSE
              MOVE NOM-DENOM-SOCIAL OF MSG-OUT-PES11001(1)
                TO DET-NOMBRE
           END-IF.