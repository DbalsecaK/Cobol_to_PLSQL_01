      ****************************************************************
      **                       B   G   R                            **
      ****************************************************************
      **  MODULE NAME   : CTS00063                                  **
      **  DATE GENERATED: 2022-02-16                                **
      **  TIME GENERATED: 14:00:00                                  **
      **  PROGRAMMER    : Cristian Pachacama                        **
      **  DESIGNER      : cristian Pachacama                        **
      **  DESCRIPCION   : Crea encabezado de las ordenes a procesar **
      **                  de CASH y la nueva version                **
      ****************************************************************
      *********************  MODIFICACIONES **************************
      ****************************************************************
      **  AUTOR     FECHA                 MODIFICACION              **
      **-------- ---------- --------------------------------------- **
      **                                                            **
      **                                                            **
      ****************************************************************
       IDENTIFICATION DIVISION.
       @INTERFAZ(CTS00063,A)

      *------------------------------------------------------------*
       ENVIRONMENT DIVISION.
       DATA DIVISION.
      *------------------------------------------------------------*
       WORKING-STORAGE SECTION.
      ***************************************************
      ***  CAMPOS DE TRABAJO                          ***
      ***************************************************
       01  CAMPOS-DE-TRABAJO.
      *********VARIABLES DE ENTORNNO*********
           02 PGM                   PIC X(9)         VALUE 'CTS00063 '.
           02 INDX                  PIC 9(4)         VALUE ZEROS.
           02 WS-TEXTO              PIC X(80)        VALUE SPACES.
           02 WS-ERROR              PIC X(5)         VALUE SPACES.
           02 WS-STRING25           PIC X(25)        VALUE SPACES.
           02 WS-CHAR               PIC X(1)         VALUE SPACES.
           02 WS-IDX1               PIC 9(2)         VALUE ZEROS.
           02 WS-IDX2               PIC 9(2)         VALUE ZEROS.
           02 WS-LONG-PAL           PIC 9(2)         VALUE ZEROS.
           02 WS-POSIC-CADENA       PIC 9(2)         VALUE ZEROS.
           02 WS-INIPAL             PIC 9(2)         VALUE ZEROS.
      *********VARIABLES DE PROCESAMIENTO*********
           02 WS-GUID                     PIC X(36)  VALUE SPACES.
           02 WS-SEC-PROCESO              PIC S9(10) VALUE ZEROS.
           02 WS-NUM-PRIORIDAD            PIC S9(06) VALUE ZEROS.
           02 WS-FEC-PROCESO              PIC X(10)  VALUE SPACES.
           02 WS-TIMESTAMP-ALTA           PIC X(26)  VALUE SPACES.
           02 WS-IND-ESTADO               PIC X(2)   VALUE SPACES.
           02 WS-ID-SOBRE                 PIC S9(10) VALUE ZEROS.
           02 WS-ID-SOBRE-CHAR            PIC X(10)  VALUE SPACES.
           02 WS-TIP-ORIENTACION          PIC X(2)   VALUE SPACES.
           02 WS-TIP-ID-ORDENANTE         PIC X(1)   VALUE SPACES.
           02 WS-DESCRIPCION              PIC X(40)  VALUE SPACES.
           02 WS-NRO-REGISTROS            PIC S9(10) VALUE ZEROS.
           02 WS-MNT-ORDEN                PIC S9(15)V9(2) VALUE ZEROS.
      *    02 WS-COD-EMPRESA              PIC X(4)   VALUE SPACES.
           02 WS-COD-TIP-EXPE             PIC X(2)   VALUE SPACES.
           02 WS-NUM-CTA-INT              PIC S9(8)  VALUE ZEROS.
           02 WS-COD-CONTA-SERV           PIC X(10)  VALUE SPACES.
           02 WS-COD-CENTIM-SERV          PIC X(4)   VALUE SPACES.
           02 WS-COD-CONTA-RETE           PIC X(10)  VALUE SPACES.
           02 WS-COD-CENTIM-RETE          PIC X(4)   VALUE SPACES.
           02 WS-TIP-PROCESO              PIC X(1)   VALUE SPACES.
           02 WS-POR-RETENCION            PIC S9(3)V9(2) VALUE ZEROS.
           02 WS-COD-ERROR                PIC X(5)   VALUE SPACES.
           02 WS-DESC-ERROR               PIC X(100) VALUE SPACES.
           02 WS-COD-OFI-PROPIE           PIC X(4)   VALUE SPACES.
           02 WS-IMP-PROCESADO            PIC S9(13)V9(2) VALUE ZEROS.
           02 WS-NUM-OPERACION            PIC S9(10) VALUE ZEROS.
           02 WS-COD-ERROR-RETEN          PIC X(5)   VALUE SPACES.
           02 WS-DESC-ERROR-RETEN         PIC X(100) VALUE SPACES.
           02 WS-IMP-VAL-RETENCION        PIC S9(16)V9(2) VALUE ZEROS.
           02 WS-IMP-PRO-RETENCION        PIC S9(16)V9(2) VALUE ZEROS.
           02 WS-NUM-OPER-RETEN           PIC S9(10) VALUE ZEROS.
           02 WS-IND-CONSIDERACION        PIC X(1)   VALUE SPACES.
           02 WS-COD-OPERACION-RETE       PIC X(5)   VALUE SPACES.
           02 WS-COD-REFER-RETE           PIC X(4)   VALUE SPACES.
           02 WS-DIAS-FLOAT               PIC S9(2)  VALUE ZEROS.
           02 WS-COD-ERROR-CONSID         PIC X(5)   VALUE SPACES.
           02 WS-DESC-ERROR-CONSID        PIC X(100) VALUE SPACES.
           02 WS-IMP-PROCES-CONSID        PIC S9(13)V9(2) VALUE ZEROS.
           02 WS-NUM-OPER-CONSID          PIC S9(10) VALUE ZEROS.
           02 WS-COD-ERROR-RET-CON        PIC X(5)   VALUE SPACES.
           02 WS-DESC-ERROR-RET-CON       PIC X(100) VALUE SPACES.
           02 WS-IMP-PRO-RET-CONSID       PIC S9(13)V9(2) VALUE ZEROS.
           02 WS-NUM-OPER-RC              PIC S9(10) VALUE ZEROS.
           02 WS-IMP-DEVOLUCION           PIC S9(13)V9(2) VALUE ZEROS.
           02 WS-COD-ERROR-DEVOLUCION     PIC X(5)   VALUE SPACES.
           02 WS-DESC-ERROR-DEVOLUCION    PIC X(100) VALUE SPACES.
           02 WS-NUM-OPERACION-DEVOLUCION PIC S9(10) VALUE ZEROS.
           02 WS-COD-SISTEMA              PIC X(10)  VALUE SPACES.
           02 WS-TIMESTAMP-SIGLO          PIC X(26)  VALUE SPACES.
           02 WS-ID-EMPRESA               PIC S9(10) VALUE ZEROS.
           02 WS-ID-SERVICIO              PIC S9(10) VALUE ZEROS.
           02 WS-IMP-ORIGINAL-PRO         PIC S9(13)V9(2) VALUE ZEROS.
           02 WS-COD-PERSONA              PIC S9(9) VALUE ZEROS.
           02 WS-COUNT                    PIC S9(10) VALUE ZEROS.
CJP01      02 WS-COUNT1                   PIC S9(10) VALUE ZEROS.
           02 WS-IMP-MOVIMIENTO           PIC S9(15)V9(2) VALUE ZEROS.
           02 WS-COD-OPERACION            PIC X(5) VALUE SPACES.
           02 WS-COD-REFER                PIC X(4) VALUE SPACES.
           02 WS-IND-TIP-CONTA            PIC X(2) VALUE SPACES.
           02 WS-COD-CENTIM-EMP           PIC X(4) VALUE SPACES.
           02 WS-COD-CONTA-EMP            PIC X(6) VALUE SPACES.
           02 WS-COD-TAB-PARM             PIC X(8) VALUE 'TC63CASH'.
CJP01      02 WS-COD-TAB-PARM1            PIC X(8) VALUE 'T63CASH1'.
           02 WS-COD-TIP-ORIENTACION      PIC X(2) VALUE SPACES.
           02 WS-NUM-CUENTA               PIC X(10) VALUE SPACES.
CJP01      02 WS-NUM-CUENTA1              PIC X(8) VALUE SPACES.
           02 WS-NRO-ID-ORDENANTE         PIC X(14) VALUE SPACES.
CJP01      02 WS-NRO-ID-ORDENANTE1        PIC X(13) VALUE SPACES.
           02 WS-FOR-PAGO                 PIC X(3) VALUE SPACES.

      ********************************
      ***  DEFINICION DE SWITCHES  ***
      ********************************
       01  SW-ENCAB-CASC               PIC 9        VALUE 0.
           88 ENCAB-CASC-ENCONTRADO                 VALUE 1.
           88 ENCAB-CASC-NO-ENCONTRADO              VALUE 0.
       01  SW-SALIR-CADENA             PIC X(1)     VALUE 'N'.
           88 NO-SALIR-CADENA                       VALUE 'N'.
           88 SI-SALIR-CADENA                       VALUE 'S'.

      ***************************************************
      ***  AREAS VARIAS                               ***
      ***************************************************
       01  AREAS-DE-TRABAJO.
      *
           02  WK-FECHA-ACTUAL.
               03 DIA                 PIC X(2)      VALUE SPACES.
               03 FILLER              PIC X(1)      VALUE '.'.
               03 MES                 PIC X(2)      VALUE SPACES.
               03 FILLER              PIC X(1)      VALUE '.'.
               03 ANYO                PIC X(4)      VALUE SPACES.
       
           02  WK-FECHA-P.
               03 DIA-P               PIC X(2)      VALUE '01'.
               03 FILLER              PIC X(1)      VALUE '.'.
               03 MES-P               PIC X(2)      VALUE '01'.
               03 FILLER              PIC X(1)      VALUE '.'.
               03 ANYO-P              PIC X(4)      VALUE '0001'.

           02  WK-HORA-ACTUAL.
               03 HORA                PIC X(2)      VALUE SPACES.
               03 MINUTOS             PIC X(2)      VALUE SPACES.
               03 SEGUNDOS            PIC X(2)      VALUE SPACES.
           02  WK-HORA-ACTUAL-NUM REDEFINES WK-HORA-ACTUAL PIC 9(6).
       
           02  WK-TIMESTAMP           PIC X(26)     VALUE SPACES.
           02  WK-TIMES-R REDEFINES WK-TIMESTAMP.
               03 ANYO                PIC X(4).
               03 FILLER              PIC X(1).
               03 MES                 PIC X(2).
               03 FILLER              PIC X(1).
               03 DIA                 PIC X(2).
               03 FILLER              PIC X(1).
               03 HORA                PIC X(2).
               03 FILLER              PIC X(1).
               03 MINUTOS             PIC X(2).
               03 FILLER              PIC X(1).
               03 SEGUNDOS            PIC X(2).
               03 FILLER              PIC X(7).
           
           02  WK-COD-DOC-OFICIAL-IN  PIC X(14)     VALUE SPACES.
           02  WK-COD-DOC-OFICIAL-IN-R REDEFINES WK-COD-DOC-OFICIAL-IN.
               03 COD-DOC-IN-10       PIC X(10).
               03 COD-DOC-IN-4        PIC X(4).
               
           02  WK-COD-DOC-OFICIAL-OU  PIC X(14)     VALUE SPACES.
           02  WK-COD-DOC-OFICIAL-OU-R REDEFINES WK-COD-DOC-OFICIAL-OU.
               03 COD-DOC-OU-4       PIC X(4).
               03 COD-DOC-OU-10      PIC X(10).
  
      ********************
      ***  CONSTANTES  ***
      ********************
       01  DEFINICION-DE-CONSTANTES.
           02 WS-COD-EMPRESA   PIC X(4)   VALUE '0042'.
       01  WS-IND-NATURALEZA   PIC X(1)   VALUE 'D'.
      *******************************
      ***  COPYS VARIOS           ***
      *******************************
      ** AREA DE DESCRIPCION ERRORES SQUL
           COPY OBERROR.
      ***********************************
      ***  DESCRIPCION DE TABLAS DB2  ***
      ***********************************
           EXEC SQL
              INCLUDE T08CT176
           END-EXEC.
      
           EXEC SQL
              INCLUDE T06TC002
           END-EXEC.

           EXEC SQL
              INCLUDE T06TC007
           END-EXEC.

           EXEC SQL
              INCLUDE T50ATC35
           END-EXEC.

           EXEC SQL
              INCLUDE T08CT175
           END-EXEC.

           EXEC SQL
              INCLUDE T08CT006
           END-EXEC.

      ******************************************************
      *              CURSORES                              *
      ******************************************************
      *------------------------------------------------------------*
       LINKAGE SECTION.
      *------------------------------------------------------------*
       PROCEDURE DIVISION USING  MSG-IN
                                 MSG-OUT
                                 S21-AREA-ERROR
                                 S21-AREA-ENTORNO.
      **INICIO-PROGRAMA-CTS00063
       0000-CONTROLA-PROGRAMA.
      *-----------------------
           PERFORM 1000-INICIALIZA  THRU 1000-FINALIZA.
           PERFORM 2000-PROCESA     THRU 2000-FINALIZA.
           PERFORM 8000-FINALIZA    THRU 8000-FIN.
      **FINAL-PROGRAMA-CTS00063
      ******************************************************************
      ***  RUTINAS DE INICIALIZACION                                 ***
      ******************************************************************
       1000-INICIALIZA.
      *---------------- 
           @DEFINE(NO-ERROSQL).
      *
           @CTRLERR(APLICACION).
           DISPLAY 'CTS00063 1000-INICIALIZA '.
      *
      ******************************************************************
      * Verifico si aun no esta grabado el encabezado del sobre.
      * Si no esta, armo el registro de encabezado para t08ct176, 
      * y grabo.
      ******************************************************************
      *--  - Obtencion fecha y hora actual y movida a auxiliares.
           EXEC SQL
                SELECT CURRENT-TIMESTAMP
                INTO :WK-TIMESTAMP
                FROM DUAL
           END-EXEC.
           
           MOVE ANYO         OF      WK-TIMES-R
             TO ANYO         OF      WK-FECHA-ACTUAL.
           MOVE MES          OF      WK-TIMES-R
             TO MES          OF      WK-FECHA-ACTUAL.
           MOVE DIA          OF      WK-TIMES-R
             TO DIA          OF      WK-FECHA-ACTUAL.
           MOVE HORA         OF      WK-TIMES-R
             TO HORA         OF      WK-HORA-ACTUAL.
           MOVE MINUTOS      OF      WK-TIMES-R
             TO MINUTOS      OF      WK-HORA-ACTUAL.
           MOVE SEGUNDOS     OF      WK-TIMES-R
             TO SEGUNDOS     OF      WK-HORA-ACTUAL.
           MOVE ID-SOBRE     OF MSG-IN
             TO ID-SOBRE     OF T08CT176.
             
      *--  - Obtencion codigo gerente
           
           MOVE COD-EMPRESA      OF S21-AREA-ENTORNO TO COD-EMPRESA 
                                 OF T06TC007.
           SET  ENCAB-CASC-NO-ENCONTRADO   TO TRUE.
           MOVE ID-SOBRE         OF MSG-IN
             TO ID-SOBRE         OF T08CT176.
           PERFORM  1100-BUSCA-ORDEN-T08CT176.
           IF  ENCAB-CASC-NO-ENCONTRADO
               PERFORM 1400-ARMA-REC-T08CT176
               PERFORM 1300-INSERTA-REC-T08CT176
           END-IF.
           DISPLAY 'CTS00063 TERMINO 1000-INICIALIZA '.
           
      *
       1000-FINALIZA.
      *-------------- 
           EXIT.
      *
       1100-BUSCA-ORDEN-T08CT176.
      *--------------------------
      * Accesa a T08CT176 para saber si esta grabado o no el encabezado.
           DISPLAY 'CTS00063 - ENTRO A 1100-BUSCA-ORDEN-T08CT176 '.
           EXEC SQL
                SELECT ID_SOBRE
                  INTO :WS-ID-SOBRE
                  FROM M2D.T08CT176
                 WHERE ID_SOBRE = :T08CT176.ID-SOBRE
           END-EXEC.
           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY 'CTS00063 1100-BUSCA-ORDEN-T08CT176: '
                     SQLSTATE  '     ' SQLCODE
                     'ID-SOBRE: ' WS-ID-SOBRE.
           IF  IND-SQL-CORRECTO 
           OR  IND-NO-ENCONTRADO
               CONTINUE
           ELSE
              
              
               MOVE '21016'         TO WS-ERROR
               MOVE '21016'         TO COD-ERROR      OF MSG-OUT
               MOVE 'CTS00063'      TO NOM-PROGRAMA   OF OBERROR
               MOVE '1100-BUSCA'    TO NOM-RUTINA     OF OBERROR
               MOVE 'T08CT176'      TO NOM-TABLA      OF OBERROR
               MOVE  SQLSTATE       TO COD-SQLSTATE   OF OBERROR
                          
               MOVE 'ERROR ACCESO T08CT176'
                                   TO DEL-INCID      OF OBERROR
                                   WS-TEXTO
                                   DESC-ERROR OF MSG-OUT
               @ERROR(ERROR, 21016, OBERROR)
           END-IF.


             IF NOT IND-SQL-CORRECTO
                DISPLAY 'CTS00063 1100-BUSCA-ORDEN-T08CT176: '
                        'ENCABEZADO DE SOBRE ' WS-ID-SOBRE
                        ' A CREARSE'
                SET  ENCAB-CASC-NO-ENCONTRADO   TO TRUE          
             ELSE
                DISPLAY 'CTS00063 1100-BUSCA-ORDEN-T08CT176: '
                        'ENCABEZADO DE SOBRE ' WS-ID-SOBRE
                        ' CREADO EN CARGA PREVIA'
                SET  ENCAB-CASC-ENCONTRADO TO TRUE
             END-IF.
      *
       1300-INSERTA-REC-T08CT176.
      *--------------------------
           DISPLAY 'CTS00063 1300-INSERTA-REC-T08CT176'.
           DISPLAY 'Fecha proceso: ' 
                        FEC-PROCESO       OF T08CT176
                   'Timestamp: '
                        TIMESTAMP-ALTA    OF T08CT176.
       DISPLAY '****************************************************'
       DISPLAY PGM 'GUID:           '     GUID OF T08CT176
       DISPLAY PGM 'SEC-PROCESO:    '     SEC-PROCESO OF T08CT176
       DISPLAY PGM 'NUM-PRIORIDAD:  '     NUM-PRIORIDAD OF T08CT176
       DISPLAY PGM 'FEC-PROCESO:    '     FEC-PROCESO OF T08CT176
       DISPLAY PGM 'TIMESTAMP-ALTA: '     TIMESTAMP-ALTA OF T08CT176
       DISPLAY PGM 'IND-ESTADO:     '     IND-ESTADO OF T08CT176
       DISPLAY PGM 'ID-SOBRE:       '     ID-SOBRE OF T08CT176
       DISPLAY PGM 'TIP-ORIENTACION: '    TIP-ORIENTACION OF T08CT176
       DISPLAY PGM 'TIP-ID-ORDENANTE: '   TIP-ID-ORDENANTE OF T08CT176
       DISPLAY PGM 'NRO-ID-ORDENANTE: '   NRO-ID-ORDENANTE OF T08CT176
       DISPLAY PGM 'COD-MONEDA:     '     COD-MONEDA OF T08CT176
       DISPLAY PGM 'DESCRIPCION:     '    DESCRIPCION OF T08CT176
       DISPLAY PGM 'NRO-REGISTROS:   '    NRO-REGISTROS OF T08CT176
       DISPLAY PGM 'MNT-ORDEN:      '     MNT-ORDEN OF T08CT176
       DISPLAY PGM 'FOR-PAGO:       '     FOR-PAGO OF T08CT176
       DISPLAY PGM 'COD-EMPRESA:    '     COD-EMPRESA OF T08CT176
       DISPLAY PGM 'COD-TIP-EXPE:   '     COD-TIP-EXPE OF T08CT176
       DISPLAY PGM 'NUM-CTA-INT:    '     NUM-CTA-INT OF T08CT176
       DISPLAY PGM 'IND-TIP-CONTA:  '     IND-TIP-CONTA OF T08CT176
       DISPLAY PGM 'COD-CONTA-EMP:  '     COD-CONTA-EMP OF T08CT176
       DISPLAY PGM 'COD-CENTIM-EMP: '     COD-CENTIM-EMP OF T08CT176
       DISPLAY PGM 'COD-CONTA-SERV: '     COD-CONTA-SERV OF T08CT176
       DISPLAY PGM 'COD-CENTIM-SERV: '    COD-CENTIM-SERV OF T08CT176
       DISPLAY PGM 'COD-CONTA-RETE: '     COD-CONTA-RETE OF T08CT176
       DISPLAY PGM 'COD-CENTIM-RETE: '    COD-CENTIM-RETE OF T08CT176
       DISPLAY PGM 'COD-OPERACION:  '     COD-OPERACION OF T08CT176
       DISPLAY PGM 'COD-REFER:      '     COD-REFER OF T08CT176
       DISPLAY PGM 'TIP-PROCESO:    '     TIP-PROCESO OF T08CT176
       DISPLAY PGM 'POR-RETENCION:  '     POR-RETENCION OF T08CT176
       DISPLAY PGM 'IND-CONSIDERACION: '  IND-CONSIDERACION OF T08CT176
       DISPLAY PGM 'COD-OPERACION-RETE: ' COD-OPERACION-RETE OF T08CT176
       DISPLAY PGM 'COD-REFER-RETE:   '   COD-REFER-RETE OF T08CT176
       DISPLAY PGM 'DIAS-FLOAT: '         DIAS-FLOAT OF T08CT176
       DISPLAY PGM 'ID-EMPRESA:     '     ID-EMPRESA OF T08CT176
       DISPLAY PGM 'ID-SERVICIO:    '     ID-SERVICIO OF T08CT176
       DISPLAY PGM 'IMP-ORIGINAL-PRO: '   IMP-ORIGINAL-PRO OF T08CT176
       DISPLAY PGM 'APLICA-PARCIAL: '     TIP-PROCESO OF T08CT176
       DISPLAY PGM 'VALOR-MINIMO: '       VALOR-MINIMO OF T08CT176

              
           EXEC SQL INSERT INTO T08CT176
               ( 
                GUID            ,
                SEC_PROCESO     ,
                NUM_PRIORIDAD   ,
                FEC_PROCESO     ,
                TIMESTAMP_ALTA  ,
                IND_ESTADO      ,
                ID_SOBRE        ,
                TIP_ORIENTACION ,
                TIP_ID_ORDENANTE,
                NRO_ID_ORDENANTE,
                COD_MONEDA      ,
                DESCRIPCION     ,
                NRO_REGISTROS   ,
                MNT_ORDEN       ,
                FOR_PAGO        ,
                COD_EMPRESA     ,
                COD_TIP_EXPE    ,
                NUM_CTA_INT     ,
                IND_TIP_CONTA   ,
                COD_CONTA_EMP   ,
                COD_CENTIM_EMP  ,
                COD_CONTA_SERV  ,
                COD_CENTIM_SERV ,
                COD_CONTA_RETE  ,
                COD_CENTIM_RETE ,
                COD_OPERACION   ,
                COD_REFER       ,
                TIP_PROCESO     ,
                POR_RETENCION   ,
                IND_CONSIDERACION ,
                COD_OPERACION_RETE,
                COD_REFER_RETE    ,
                DIAS_FLOAT      ,
                ID_EMPRESA      ,
                ID_SERVICIO     ,
                IMP_ORIGINAL_PRO,
                VALOR_MINIMO,
                COD_ERROR,
                DESC_ERROR
                )
           VALUES
               (:T08CT176.GUID            ,
                :T08CT176.SEC-PROCESO     ,
                :T08CT176.NUM-PRIORIDAD   ,
                :T08CT176.FEC-PROCESO     ,
                :T08CT176.TIMESTAMP-ALTA  ,
                :T08CT176.IND-ESTADO      ,
                :T08CT176.ID-SOBRE        ,
                :T08CT176.TIP-ORIENTACION ,
                :T08CT176.TIP-ID-ORDENANTE,
                :T08CT176.NRO-ID-ORDENANTE,
                :T08CT176.COD-MONEDA      ,
                :T08CT176.DESCRIPCION     ,
                :T08CT176.NRO-REGISTROS   ,
                :T08CT176.MNT-ORDEN       ,
                :T08CT176.FOR-PAGO        ,
                :T08CT176.COD-EMPRESA     ,
                :T08CT176.COD-TIP-EXPE    ,
                :T08CT176.NUM-CTA-INT     ,
                :T08CT176.IND-TIP-CONTA   ,
                :T08CT176.COD-CONTA-EMP   ,
                :T08CT176.COD-CENTIM-EMP  ,
                :T08CT176.COD-CONTA-SERV  ,
                :T08CT176.COD-CENTIM-SERV ,
                :T08CT176.COD-CONTA-RETE  ,
                :T08CT176.COD-CENTIM-RETE ,
                :T08CT176.COD-OPERACION   ,
                :T08CT176.COD-REFER       ,
                :T08CT176.TIP-PROCESO     ,
                :T08CT176.POR-RETENCION   ,
                :T08CT176.IND-CONSIDERACION ,
                :T08CT176.COD-OPERACION-RETE,
                :T08CT176.COD-REFER-RETE  ,
                :T08CT176.DIAS-FLOAT      ,
                :T08CT176.ID-EMPRESA      ,
                :T08CT176.ID-SERVICIO     ,
                :T08CT176.IMP-ORIGINAL-PRO,
                :T08CT176.VALOR-MINIMO,
                :T08CT176.COD-ERROR       ,
                :T08CT176.DESC-ERROR
               )
           END-EXEC.
           
           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           DISPLAY 'CTS00063 1300-... '
                   'SQLCODE: '    SQLCODE
                   'SQLSTATE: '   SQLSTATE. 
           IF NOT IND-SQL-CORRECTO
              MOVE '05606'         TO WS-ERROR
              MOVE '05606'         TO COD-ERROR      OF MSG-OUT
              MOVE 'CTS00063'      TO NOM-PROGRAMA   OF OBERROR
              MOVE '1300-INSER'    TO NOM-RUTINA     OF OBERROR
              MOVE 'T08CT176'      TO NOM-TABLA      OF OBERROR
              MOVE  SQLSTATE       TO COD-SQLSTATE   OF OBERROR
                          
              MOVE 'ERROR INSERTAR T08CT176'
                                   TO DEL-INCID      OF OBERROR
                                   WS-TEXTO
                                   DESC-ERROR OF MSG-OUT
              @ERROR(ERROR, 05606, OBERROR)
           END-IF.


       1400-ARMA-REC-T08CT176.
      *-----------------------
      *-- Arma la informacion que se grabara como encabezado en T08CT176
           DISPLAY PGM ' 1400-ARMA-REC-T08CT176'
           MOVE  COD-GUID           OF MSG-IN
             TO  GUID               OF T08CT176.

           EXEC SQL
                SELECT M2D.S08CT176_SEC_PROCESO.NEXTVAL
                  INTO WS-SEC-PROCESO
                  FROM DUAL
           END-EXEC

           MOVE  WS-SEC-PROCESO
             TO  SEC-PROCESO        OF T08CT176.
           MOVE  1
             TO  NUM-PRIORIDAD      OF T08CT176.
           MOVE  FEM-OPERACION      OF S21-AREA-ENTORNO
             TO  FEC-PROCESO        OF T08CT176.
           MOVE WK-TIMESTAMP
             TO TIMESTAMP-ALTA      OF T08CT176.
           MOVE COD-TIP-ORIENTACION OF MSG-IN
             TO TIP-ORIENTACION     OF T08CT176.
           MOVE COD-EMPRESA        OF MSG-IN
             TO COD-EMPRESA        OF T08CT176.
           MOVE ID-SOBRE            OF MSG-IN
             TO ID-SOBRE            OF T08CT176.

           EXEC SQL
                SELECT ESTADO
                  INTO WS-IND-ESTADO
                  FROM M2D.T08CT175
                 WHERE COD_EMPRESA = :T08CT176.COD-EMPRESA
                   AND TIPO_PROCESO = :T08CT176.TIP-ORIENTACION
                   AND ID_SOBRE = :T08CT176.ID-SOBRE
      *            AND FEC_PROCESO = :T08CT176.FEC-PROCESO
           END-EXEC

          DISPLAY PGM 'COD-EMPRESA: ' COD-EMPRESA OF T08CT176
          DISPLAY PGM 'TIP-ORIENTACION: ' TIP-ORIENTACION OF T08CT176
          DISPLAY PGM 'ID-SOBRE: ' ID-SOBRE OF T08CT176
          DISPLAY PGM 'FEC-PROCESO: ' FEC-PROCESO OF T08CT176
          DISPLAY PGM 'WS-IND-ESTADO: ' WS-IND-ESTADO

           MOVE WS-IND-ESTADO
             TO IND-ESTADO          OF T08CT176.

           MOVE COD-DOC-ORDENANTE   OF MSG-IN
             TO TIP-ID-ORDENANTE    OF T08CT176.
           MOVE NUM-DOC-ORDENANTE   OF MSG-IN
             TO NRO-ID-ORDENANTE    OF T08CT176.
           MOVE COD-MONEDA          OF MSG-IN
             TO COD-MONEDA          OF T08CT176.
           MOVE TXT-DESCRIPCION     OF MSG-IN
             TO DESCRIPCION         OF T08CT176.
           MOVE NUM-REGISTROS       OF MSG-IN
             TO NRO-REGISTROS       OF T08CT176.
           MOVE MNT-ORDEN           OF MSG-IN
             TO MNT-ORDEN           OF T08CT176.

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
           
           END-IF.

           MOVE NUM-CUENTA         OF MSG-IN(9:2)
             TO COD-TIP-EXPE       OF T08CT176.
           MOVE NUM-CUENTA         OF MSG-IN(1:8)
             TO NUM-CTA-INT        OF T08CT176.
           MOVE 'CC'
             TO IND-TIP-CONTA      OF T08CT176.
           MOVE '006414'
             TO COD-CONTA-EMP      OF T08CT176.
           MOVE '0186'
             TO COD-CENTIM-EMP     OF T08CT176.
           MOVE '006414'
             TO COD-CONTA-SERV     OF T08CT176.
           MOVE '0186'
             TO COD-CENTIM-SERV    OF T08CT176.
           MOVE '006454'
             TO COD-CONTA-RETE     OF T08CT176.
           MOVE '0186'
             TO COD-CENTIM-RETE    OF T08CT176.
           MOVE '40399'
             TO COD-OPERACION      OF T08CT176.

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
           END-IF.

           MOVE NUM-CUENTA         OF MSG-IN
             TO WS-NUM-CUENTA
           MOVE ZEROS
             TO WS-COUNT
           MOVE COD-TIP-ORIENTACION OF MSG-IN 
             TO WS-COD-TIP-ORIENTACION
           MOVE NUM-DOC-ORDENANTE   OF MSG-IN (2:14)
             TO WS-NRO-ID-ORDENANTE
CJP01      MOVE NUM-DOC-ORDENANTE   OF MSG-IN (3:13)
CJP01        TO WS-NRO-ID-ORDENANTE1


         DISPLAY PGM 'WS-COD-TIP-ORIENTACION: ' WS-COD-TIP-ORIENTACION
         DISPLAY PGM 'WS-NRO-ID-ORDENANTE: ' WS-NRO-ID-ORDENANTE
         DISPLAY PGM 'WS-NRO-ID-ORDENANTE1: ' WS-NRO-ID-ORDENANTE1

           EXEC SQL
             SELECT COUNT(1)
               INTO WS-COUNT
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM
                AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
           END-EXEC

           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
           DISPLAY PGM 'WS-COUNT: ' WS-COUNT

           MOVE NUM-CUENTA         OF MSG-IN(1:8)
             TO NUM-CTA-INT        OF T08CT176
CJP01
           EXEC SQL
             SELECT COUNT(1)
               INTO WS-COUNT1
               FROM M2D.T06TC002
              WHERE COD_TABLA_ID = :WS-COD-TAB-PARM1
               AND SUBSTR(CODIGO_REGISTRO,3,13) = :WS-NRO-ID-ORDENANTE1
               AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
                AND SUBSTR(DEL_REGISTRO,27,8) = :T08CT176.NUM-CTA-INT
           END-EXEC
CJP01

           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
           DISPLAY PGM 'WS-COUNT1: ' WS-COUNT

         DISPLAY PGM 'WS-NUM-CUENTA: ' WS-NUM-CUENTA
         DISPLAY PGM 'WS-COD-TIP-ORIENTACION: ' WS-COD-TIP-ORIENTACION

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

CJP01 *  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
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

CJP01      END-IF
CJP01 *    FIN CONTROL
CJP01 *    IF WS-COUNT EQUAL ZEROS THEN
CJP01      IF WS-COUNT EQUAL ZEROS AND WS-COUNT1 EQUAL ZEROS THEN
             DISPLAY PGM 'IF 1'
              CONTINUE
           ELSE
CJP01 *       IF WS-COUNT > 1 THEN
CJP01         IF WS-COUNT > 1 THEN
             DISPLAY PGM 'IF 2'
                 MOVE '21015'
                   TO COD-ERROR          OF T08CT176
                 MOVE 'ERROR DE ACCESO AL DB2.'
                   TO DESC-ERROR         OF T08CT176
                 PERFORM 8000-FINALIZA
                 EXIT
              ELSE
CJP01 *       IF WS-COUNT EQUAL 1 THEN
CJP01         IF WS-COUNT EQUAL 1 OR WS-COUNT1 >= 1 THEN
             DISPLAY PGM 'IF 3'
      *****************************************************************
      ********************VOY POR COBRO COMISION***********************
      *****************************************************************
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

CJP01 *  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
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
      *****************************************************************
CJP01 ***************VOY POR COBRO COMISION ESPECIALES*****************
      *****************************************************************
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
      *         AND SUBSTR(CODIGO_REGISTRO,2,14) = :WS-NRO-ID-ORDENANTE
CJP02           AND SUBSTR(CODIGO_REGISTRO,3,13) = :WS-NRO-ID-ORDENANTE1
                AND SUBSTR(DEL_REGISTRO,1,2) = :WS-COD-TIP-ORIENTACION
                AND SUBSTR(DEL_REGISTRO,27,8) = :T08CT176.NUM-CTA-INT
           END-EXEC

           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE

CJP01 *  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
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
      *****************************************************************
      **********************VOY POR COBRO NORMAL***********************
      *****************************************************************
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

CJP01 *  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
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
      *****************************************************************
      **********************VOY POR PAGO NORMAL************************
      *****************************************************************
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

CJP01 *  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
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

CJP01 *  INI - SE INGRESA CONTROL PARA RELLENAR CON DATOS POR DEFAULT *
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
           END-IF

           DISPLAY PGM 'APLICA-PARCIAL: ' APLICA-PARCIAL OF MSG-IN

           EVALUATE APLICA-PARCIAL OF MSG-IN
               WHEN '0'
                   MOVE 'T' TO TIP-PROCESO OF T08CT176
               WHEN '1'
                   MOVE 'P' TO TIP-PROCESO OF T08CT176
           END-EVALUATE

           MOVE 0
             TO POR-RETENCION      OF T08CT176.
           MOVE 'N'
             TO IND-CONSIDERACION  OF T08CT176.
           MOVE '     '
             TO COD-OPERACION-RETE OF T08CT176.
           MOVE '    '
             TO COD-REFER-RETE.
           MOVE 0
             TO DIAS-FLOAT.
           MOVE 0
             TO ID-EMPRESA         OF T08CT176.
           MOVE 0
             TO ID-SERVICIO        OF T08CT176.
           MOVE 0
             TO IMP-ORIGINAL-PRO   OF T08CT176.
           MOVE VALOR-MINIMO       OF MSG-IN
             TO VALOR-MINIMO       OF T08CT176.
           MOVE '03152'
             TO COD-ERROR          OF T08CT176.
           MOVE 'ZNo procesado'
             TO DESC-ERROR         OF T08CT176.

           IF COD-EMPRESA OF MSG-IN EQUAL '0042' AND
              FOR-PAGO EQUAL 'CTA' AND
              WS-NUM-CUENTA NOT EQUAL '9999999999' THEN
              PERFORM 1500-VALIDA-CUENTA
           END-IF.

           IF COD-ERROR OF T08CT176 EQUAL '00000' OR '03152' THEN
             DISPLAY PGM 'COD-ERROR: ' COD-ERROR OF T08CT176
             IF COD-EMPRESA OF MSG-IN EQUAL '0042' AND
                COD-TIP-ORIENTACION OF MSG-IN EQUAL 'P ' AND
                WS-NUM-CUENTA NOT EQUAL '9999999999' THEN
                PERFORM 1600-VALIDA-FONDEO
             END-IF
           END-IF.

      ******************************************************************
       1500-VALIDA-CUENTA.
      *-------------
      ***************************************************************
           DISPLAY PGM '1500-VALIDA-CUENTA'.

           MOVE NUM-CUENTA         OF MSG-IN(9:2)
             TO COD-TIP-EXPE       OF T08CT176.
           MOVE NUM-CUENTA         OF MSG-IN(1:8)
             TO NUM-CTA-INT        OF T08CT176.
           MOVE NUM-DOC-ORDENANTE  OF MSG-IN(2:14)
             TO WS-NRO-ID-ORDENANTE.
           MOVE ID-SOBRE           OF MSG-IN
             TO ID-SOBRE           OF T08CT176.

          DISPLAY PGM 'COD-TIP-EXPE: ' COD-TIP-EXPE OF T08CT176
          DISPLAY PGM 'NUM-CTA-INT: ' NUM-CTA-INT OF T08CT176
          DISPLAY PGM 'NRO-ID-ORDENANTE: ' WS-NRO-ID-ORDENANTE
          DISPLAY PGM 'ID-SOBRE: ' ID-SOBRE OF T08CT176

              MOVE ZEROS TO WS-COUNT

              EXEC SQL
                SELECT COUNT(1)
                  INTO WS-COUNT
                  FROM M2D.T08CT005
                 WHERE COD_TIP_EXPE = :T08CT176.COD-TIP-EXPE
                   AND NUM_CTA_INT = :T08CT176.NUM-CTA-INT
                   AND IND_EST_CUENTA = 'A'
              END-EXEC.

          DISPLAY PGM 'WS-COUNT: ' WS-COUNT


          IF WS-COUNT > 0 THEN
             DISPLAY PGM 'VOY POR IF1 '


                 EXEC SQL
                  SELECT COUNT(1)
                    INTO WS-COD-PERSONA
                    FROM M2D.T04RPC11 A, M2D.T04DBA01 B
                   WHERE A.COD_TIP_EXPE       = :T08CT176.COD-TIP-EXPE
                     AND A.NUM_CTA_INT        = :T08CT176.NUM-CTA-INT
                     AND A.COD_PERSONA        = B.COD_PERSONA
                     AND A.COD_TIPO_INTERVEN  = '01'
                     AND A.NUM_ORDEN_INTERV   = 1
                     AND A.FEC_BAJA           IS NULL
                     AND B.FEC_BAJA           IS NULL
                     AND B.COD_NUM_DOC_OFICIA = :WS-NRO-ID-ORDENANTE
                 END-EXEC

             DISPLAY PGM 'WS-COD-PERSONA: ' WS-COD-PERSONA

             IF WS-COD-PERSONA > 0 THEN
                DISPLAY PGM 'VOY POR IF '
                CONTINUE
             ELSE
                DISPLAY PGM 'VOY POR ELSE '
                MOVE '88020'
                  TO COD-ERROR          OF T08CT176
                MOVE 'ERROR NO ES EL PROPIETARIO DE LA CUENTA'
                  TO DESC-ERROR         OF T08CT176

               EXEC SQL
                    SELECT CURRENT_TIMESTAMP INTO :WK-TIMESTAMP
                       FROM DUAL
               END-EXEC

              EXEC SQL
                   UPDATE M2D.T08CT175
                      SET ESTADO = 'R',
                          FEC_FIN = :WK-TIMESTAMP
                    WHERE COD_EMPRESA = :T08CT176.COD-EMPRESA
                      AND TIPO_PROCESO = :T08CT176.TIP-ORIENTACION
      *               AND FEC_PROCESO = :T08CT176.FEC-PROCESO
                      AND ID_SOBRE = :T08CT176.ID-SOBRE
              END-EXEC

              MOVE 'R'
                TO IND-ESTADO          OF T08CT176

             END-IF

          ELSE
             DISPLAY PGM 'VOY POR ELSE1 '
             MOVE '03022'
               TO COD-ERROR          OF T08CT176
             MOVE 'ZCuenta inexistente.'
               TO DESC-ERROR         OF T08CT176

            EXEC SQL
                 SELECT CURRENT_TIMESTAMP INTO :WK-TIMESTAMP
                    FROM DUAL
            END-EXEC

          END-IF.

      ******************************************************************
       1600-VALIDA-FONDEO.
      *-------------
      ***************************************************************
        DISPLAY PGM '1600-VALIDA-FONDEO'

           MOVE COD-EMPRESA        OF MSG-IN
             TO COD-EMPRESA        OF T08CT006.
           MOVE NUM-CUENTA         OF MSG-IN(9:2)
             TO COD-TIP-EXPE       OF T08CT006.
           MOVE NUM-CUENTA         OF MSG-IN(1:8)
             TO NUM-CTA-INT        OF T08CT006.
           MOVE ID-SOBRE           OF MSG-IN
             TO WS-ID-SOBRE
           MOVE ID-SOBRE           OF MSG-IN
             TO WS-ID-SOBRE-CHAR.

           DISPLAY PGM 'COD-EMPRESA: ' COD-EMPRESA OF T08CT006
           DISPLAY PGM 'COD-TIP-EXPE: ' COD-TIP-EXPE OF T08CT006
           DISPLAY PGM 'NUM-CTA-INT: ' NUM-CTA-INT OF T08CT006
           DISPLAY PGM 'WS-ID-SOBRE: ' WS-ID-SOBRE
           DISPLAY PGM 'WS-IND-NATURALEZA: ' WS-IND-NATURALEZA
           DISPLAY PGM 'WS-ID-SOBRE-CHAR: ' WS-ID-SOBRE-CHAR

           EXEC SQL
                SELECT IMP_MOVIMIENTO
                  INTO WS-IMP-MOVIMIENTO
                  FROM M2D.T08CT006
                 WHERE COD_EMPRESA = :T08CT006.COD-EMPRESA
                   AND COD_TIP_EXPE = :T08CT006.COD-TIP-EXPE
                   AND NUM_CTA_INT = :T08CT006.NUM-CTA-INT
                   AND SUBSTR(TXT_MOVIMIENTO,1,10) = :WS-ID-SOBRE-CHAR
                   AND IND_NATURALEZA = :WS-IND-NATURALEZA
           END-EXEC

           MOVE SQLSTATE TO SQLSTATE-SIGLO
           DISPLAY PGM 'SQLSTATE: ' SQLSTATE ' SQLCODE: ' SQLCODE
           DISPLAY PGM 'WS-IMP-MOVIMIENTO: ' WS-IMP-MOVIMIENTO
           DISPLAY PGM 'MNT-ORDEN: ' MNT-ORDEN OF MSG-IN
           DISPLAY PGM 'MNT-ORDEN1: ' MNT-ORDEN OF T08CT176

           IF WS-IMP-MOVIMIENTO EQUAL MNT-ORDEN OF T08CT176 THEN
               CONTINUE
           ELSE
             DISPLAY PGM 'VOY POR ELSE1 '
             MOVE '03153'
               TO COD-ERROR          OF T08CT176
             MOVE 'IMPORTE DIFIERE AL VALOR FONDEADO'
               TO DESC-ERROR         OF T08CT176

               EXEC SQL
                    SELECT CURRENT_TIMESTAMP INTO :WK-TIMESTAMP
                       FROM DUAL
               END-EXEC

              EXEC SQL
                   UPDATE M2D.T08CT175
                      SET ESTADO = 'R',
                          FEC_FIN = :WK-TIMESTAMP
                    WHERE COD_EMPRESA = :T08CT176.COD-EMPRESA
                      AND TIPO_PROCESO = :T08CT176.TIP-ORIENTACION
      *               AND FEC_PROCESO = :T08CT176.FEC-PROCESO
                      AND ID_SOBRE = :T08CT176.ID-SOBRE
              END-EXEC

              MOVE 'R'
                TO IND-ESTADO          OF T08CT176

           END-IF.

      ******************************************************************
       2000-PROCESA.
      *-------------
      ***************************************************************
           DISPLAY 'CTS00063 2000-PROCESA FIN EJECUCION MODULO'.
                   
       2000-FINALIZA.
      *------------- 
           EXIT.
           
       8000-FINALIZA.
      *--------------
           MOVE '00000'       TO COD-ERROR     OF MSG-OUT.
           MOVE 'PROCESO OK' TO DESC-ERROR    OF MSG-OUT.
           DISPLAY 'CTS00063 8000-FINALIZA '
                    'COD-ERROR ' COD-ERROR     OF MSG-OUT
                    'DESC-ERROR ' DESC-ERROR    OF MSG-OUT.
           GOBACK.
       8000-FIN.
      *---------
           EXIT.
      
