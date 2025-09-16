      ******************************************************************
      *       I D E N T I F I C A T I O N      D I V I S I O N         *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID.         CTB0012.
       AUTHOR.             ALBERTO.
       INSTALLATION.       CAJAESPA#A.

      ******************************************************************
      *  ------------ DATOS DE IDENTIFICACION DEL PROGRAMA ---------   *
      *                                                                *
      * PROGRAMA       : CTB0012.                                      *
      * APLICACION     : CUENTAS.                                      *
      * FEC.CODIFICAC. : 25-11-94.                                     *
      *                                                                *
      * FUNCIONES: ESTE PROGRAMA REALIZARA LA GENERACION DE LOS DATOS  *
      *    A IMPRIMIR EN EL LISTADO DE CORRETAJES.                     *
      *                                                                *
      * TABLAS DB2: - T04RPC11 => PERSONAS.                            *
      *             - T04DBA01 => PERSONAS.                            *
      *             - T08CT005 => CUENTAS.                             *
      *             - T08CT006 => MOVIMIENTOS.                         *
      *                                                                *
      * FICHEROS: - FICCON01 => FICHA JCL CON LOS DATOS DE ENTRADA QUE *
      *                         DETERMINAN LA FECHA DE INICIO Y FINAL  *
      *                         PARA ELEGIR LOS MVTOS. DE CORRETAJE.   *
      *           - FCTCORSD => FICHERO DE SALIDA CON LOS REGISTROS A  *
      *                         IMPRIMIR EN EL LISTADO DE CORRETAJES.  *
      *                                                                *
      * ================  MODIFICACIONES ========================      *
      *                                                                *
      *   AUTOR     FECHA     CAUSA DE LA MODIFICACION                 *
      * --------- -------- ------------------------------------------- *
      * ALBERTO   22-12-94 CONTROLAR EL VCTO. DE LA CUENTA             *
      * GMG0902.. 13-11-97 ANIO 2000 Y EFECTO BISAGRA................. *
      * ......... DD-MM-AA ........................................... *
      *                                                                *
      ******************************************************************

      ******************************************************************
      *         E N V I R O N M E N T      D I V I S I O N             *
      ******************************************************************
       ENVIRONMENT DIVISION.

      *****************************************************************
      *                 CONFIGURATION  SECTION                        *
      *****************************************************************
       CONFIGURATION SECTION.

       SPECIAL-NAMES. DECIMAL-POINT IS COMMA.

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT TABLASKD COPY TABCSEL.

           SELECT FICCON01 ASSIGN TO FICCON01
                  FILE STATUS IS WS-STATUS.

           SELECT FCTCORSD ASSIGN TO FCTCORSD
                  FILE STATUS IS WS-STATUS-1.


       DATA DIVISION.
      *****************************************************************
      *                  D A T A      D I V I S I O N                 *
      *****************************************************************

       FILE SECTION.

       FD  TABLASKD.
           COPY TABCFIC.

       FD  FICCON01
           BLOCK CONTAINS 0 RECORDS
           RECORDING MODE IS F.
       01  R-FICCON01                      PIC X(80).

       FD  FCTCORSD
           BLOCK CONTAINS 0 RECORDS
           RECORDING MODE IS F.
       01  R-FCTCORSD                      PIC X(104).


       WORKING-STORAGE SECTION.
      *****************************************************************
      *                WORKING-STORAGE  SECTION                       *
      *****************************************************************

      ********************  VARIABLES AUXILIARES  **********************
       01  WS-AUXILIARES.
           05  WS-STATUS                   PIC X(2).
           05  WS-STATUS-1                 PIC X(2).
           05  WS-BLANCOS                  PIC X(2)       VALUE SPACES.

      ********************  CLAVES ACCESO A TABLA T08CT006  ************
       01  WS-CLAVES-T08CT006.
           05  WS-TIP-EXPE                 PIC X(2)       VALUE '30'.
           05  WS-REFER-2900               PIC X(4)       VALUE '2900'.
           05  WS-REFER-2901               PIC X(4)       VALUE '2901'.
           05  WS-FEC-INICIO               PIC X(10)      VALUE SPACE.
           05  WS-FEC-FINAL                PIC X(10)      VALUE SPACE.

      ****  CONVERSION A FORMATO DATE DE LAS FECHAS RECIBIDA EN FICCON
       01  DDMMAAAA.
           05  DIA                         PIC 9(2).
           05  FILLER                      PIC X          VALUE '.'.
           05  MES                         PIC 9(2).
           05  FILLER                      PIC X          VALUE '.'.
           05  ANYO                        PIC 9(4).

      ****  TRATAMIENTO DE LA CLAVE DE ACCESO A TABLASKD
       01  CLAVE-TABLASKD.
           05  FILLER                      PIC X(3)       VALUE '003'.
           05  OFIC-TABLASKD               PIC X(4)       VALUE ZERO.
           05  FILLER                      PIC X(6)       VALUE SPACE.

      ****  TRATAMIENTO DE LOS DATOS RECIBIDOS DE TABLASKD
       01  DATOS-TABLASKD.
           05  FILLER                      PIC X(10)      VALUE SPACE.
           05  ZONA-TABLASKD               PIC X(2)       VALUE ZERO.
           05  FILLER                      PIC X(5)       VALUE SPACE.

       01  WS-CONT-DIAS-VCTO               PIC S9(7) COMP-3 VALUE ZERO.
      *************************************************************
      *         PARAMETROS PARA LA RUTINA DE ERROR DB2            *
      *************************************************************
       01  LITERALES.
           05  LT-A-TABLA                  PIC X(9)  VALUE 'TABLA    '.
           05  LT-A-FICHERO                PIC X(9)  VALUE 'FICHERO  '.
           05  LT-A-CURSOR                 PIC X(9)  VALUE 'CURSOR A '.

           05  LT-A-T08CT005               PIC X(8)  VALUE 'T08CT005'.
           05  LT-A-T08CT006               PIC X(8)  VALUE 'T08CT006'.
           05  LT-A-T04RPC11               PIC X(8)  VALUE 'T04RPC11'.
           05  LT-A-T04DBA01               PIC X(8)  VALUE 'T04DBA01'.
           05  LT-A-FICCON01               PIC X(8)  VALUE 'FICCON01'.
           05  LT-A-FCTCORSD               PIC X(8)  VALUE 'FCTCORSD'.
           05  LT-A-TABLASKD               PIC X(8)  VALUE 'TABLASKD'.

           05  LT-A-OPEN                   PIC X(6)  VALUE 'OPEN  '.
           05  LT-A-FETCH                  PIC X(6)  VALUE 'FETCH '.
           05  LT-A-SELECT                 PIC X(6)  VALUE 'SELECT'.
           05  LT-A-READ                   PIC X(6)  VALUE 'READ  '.
           05  LT-A-WRITE                  PIC X(6)  VALUE 'WRITE '.
           05  LT-A-CLOSE                  PIC X(6)  VALUE 'CLOSE '.

           05  LT-1                        PIC X     VALUE '1'.
           05  LT-N-4                      PIC 9(2) VALUE 4.


      ********************        SWITCHES        **********************
       01  SW-FIN-CUENTAS                  PIC 9     VALUE ZERO.
           88 FIN-CUENTAS-SI                         VALUE 1.


      ************       REGISTROS DE FICHEROS       ******************

      *----------------------------------------------------------------*
      *   REGISTRO DEL FICHERO FICCON01 (FICHA CON LOS DATOS QUE       *
      *   DETERMINAN LOS REGISTROS A INCLUIR EN EL FICHERO).           *
      *----------------------------------------------------------------*
       01  FICCON.
           05  FC-FEC-INICIO.
               10  DIA                      PIC X(02).
               10  MES                      PIC X(02).
               10  ANYO                     PIC X(04).
           05  FC-FEC-FINAL.
               10  DIA                      PIC X(02).
               10  MES                      PIC X(02).
               10  ANYO                     PIC X(04).
           05  FILLER                       PIC X(64).


      *----------------------------------------------------------------*
      *   COPY DE LOS CAMPOS DE TRABAJO PARA ACCDEDER A TABLASKD       *
      *----------------------------------------------------------------*
       01  TABCWKG.
           02       TABCPSW   PIC X(8)  VALUE 'TABLASVS'.
           02       TABCFST   PIC X(2).


      *----------------------------------------------------------------*
      *   REGISTRO DEL FICHERO FCTCORSD (CONTIENE LOS CAMPOS QUE SE    *
      *   USARAN PARA IMPRIMIR EL INFORME).                            *
      *----------------------------------------------------------------*
       01  SALIDA.
           05  COD-EMPRESA                  PIC X(04).
           05  COD-ZONA                     PIC X(02).
           05  COD-SUC-ALTA                 PIC X(04).
           05  COD-TIP-EXPE                 PIC X(02).
           05  NUM-CTA-INT                  PIC S9(08) COMP-3.
           05  NOM-DENOM-SOCIAL             PIC X(60).
           05  FEC-OPERACION                PIC X(10).
           05  IMP-LIM-DISPOCTA             PIC S9(13)V9(2) COMP-3.
           05  IMP-MOVIMIENTO               PIC S9(13)V9(2) COMP-3.
           05  IND-VCTO                     PIC X.


      ************      MENSAJES DE ERROR            ******************
       01  MENSAJES-ERROR.
           05  MENSAJE-ERROR.
               10  FILLER                  PIC X(9)
                                   VALUE 'ERROR EN '.
               10  ERR-RECURSO             PIC X(9).
               10  ERR-NOMBRE              PIC X(8).
               10  FILLER                  PIC X(6)
                                   VALUE ' AL-> '.
               10  ERR-ACCION              PIC X(6).

           05  MENSAJE-ERROR1.
               10  FILLER                  PIC X(8)
                                   VALUE 'LA CTA. '.
               10  ERR-CUENTA              PIC 9(8).
               10  FILLER                  PIC X(22)
                                   VALUE ' NO EXISTE EN T08CT005'.

           05  MENSAJE-ERROR-3.
               10  FILLER                  PIC X(9)
                                   VALUE 'ERROR EN '.
               10  ERR-RECURSO3            PIC X(9).
               10  ERR-NOMBRE3             PIC X(8).
               10  FILLER                  PIC X(6)
                                   VALUE ' AL-> '.
               10  ERR-ACCION3             PIC X(6).
               10  FILLER                  PIC X(9)
                                   VALUE ' CUENTA: '.
               10  ERR-EMPRESA3            PIC X(4).
               10  FILLER                  PIC X(3)
                                   VALUE ' - '.
               10  ERR-TIPEXPE             PIC X(2).
               10  FILLER                  PIC X(3)
                                   VALUE ' - '.
               10  ERR-NUMCTA              PIC 9(8).

           05  MENSAJE-ERROR-4.
               10  FILLER                  PIC X(9)
                                   VALUE 'ERROR EN '.
               10  ERR-RECURSO4            PIC X(9).
               10  ERR-NOMBRE4             PIC X(8).
               10  FILLER                  PIC X(6)
                                   VALUE ' AL-> '.
               10  ERR-ACCION4             PIC X(6).
               10  FILLER                  PIC X(10)
                                   VALUE ' EMPRESA: '.
               10  ERR-EMPRESA4            PIC X(4).
               10  FILLER                  PIC X(10)
                                   VALUE ' PERSONA: '.
               10  ERR-PERSONA             PIC 9(9).

           05  ERROR-PERSONA.
               10  FILLER                  PIC X(33)   VALUE
                   'NO HAY TITULAR DE LA CUENTA.     '.

      *****************************************************************
      *               INCLUDE DE LAS TABLAS DB2                       *
      *****************************************************************
      *----------------------------------------------------------------*
      * REGISTRO DE LA TABLA T08CT005 (CUENTAS)                        *
      *----------------------------------------------------------------*
           EXEC SQL INCLUDE T08CT005 END-EXEC.

      *----------------------------------------------------------------*
      * REGISTRO DE LA TABLA T04RPC11 (PERSONAS)                       *
      *----------------------------------------------------------------*
           EXEC SQL INCLUDE T04RPC11 END-EXEC.

      *----------------------------------------------------------------*
      * REGISTRO DE LA TABLA T04DBA01 (PERSONAS)                       *
      *----------------------------------------------------------------*
           EXEC SQL INCLUDE T04DBA01 END-EXEC.

      *----------------------------------------------------------------*
      * REGISTRO DE LA TABLA T08CT006 (MOVIMIENTOS)                    *
      *----------------------------------------------------------------*
           EXEC SQL INCLUDE T08CT006 END-EXEC.


      *****************************************************************
      *               DECLARE DE LOS CURSORES DB2                     *
      *****************************************************************
      *----------------------------------------------------------------*
      * DECLARE DE LA TABLA T08CT006 (MOVIMIENTOS)                     *
      *----------------------------------------------------------------*
           EXEC SQL
             DECLARE CSR1 CURSOR FOR
               SELECT  COD_EMPRESA,  COD_TIP_EXPE,
                       NUM_CTA_INT,  IMP_MOVIMIENTO,
                       FEC_OPERACION
                 FROM  T08CT006
                 WHERE COD_TIP_EXPE     =   :WS-TIP-EXPE
                   AND COD_REFER        IN (:WS-REFER-2900,
                                            :WS-REFER-2901)
                   AND FEC_CONTABLE BETWEEN :WS-FEC-INICIO
                                        AND :WS-FEC-FINAL
                ORDER BY COD_EMPRESA,COD_TIP_EXPE,
                         NUM_CTA_INT
           END-EXEC.

      *----------------------------------------------------------------*
      * DECLARE DE LA TABLA T04RPC11 (PERSONAS)                        *
      *----------------------------------------------------------------*
           EXEC SQL
               DECLARE CSR2 CURSOR FOR
                SELECT COD_PERSONA     ,
                       NUM_ORDEN_INTERV
                 FROM  T04RPC11
                 WHERE COD_TIP_EXPE = :WS-TIP-EXPE
                   AND NUM_CTA_INT  = :T08CT006.NUM-CTA-INT
                   AND COD_EMPRESA  = :T08CT006.COD-EMPRESA
                   AND COD_TIPO_INTERVEN  = '01'
                   AND FEC_BAJA IS NULL
                ORDER BY NUM_ORDEN_INTERV
           END-EXEC.

      *****************************************************************
      *                        LINKAGE SECTION                        *
      *****************************************************************
       LINKAGE SECTION.

      *****************************************************************
      *           P R O C E D U R E      D I V I S I O N              *
      *****************************************************************
       PROCEDURE DIVISION.

      **INICIO-PROGRAMA-CTB0012

           PERFORM 1000-INICIO.
           PERFORM 2000-PROCESO UNTIL FIN-CUENTAS-SI.
            PERFORM 8000-FINAL.
      **FINAL-PROGRAMA-CTB0012


       1000-INICIO.
      *****************************************************************
      * EN ESTE PROCESO SE PROCEDERA A ABRIR LOS FICHEROS QUE SE VAN  *
      * A UTILIZAR EN EL PROGRAMA Y, A TRATAR LA FICHA DE CONTROL QUE *
      * RECIBE LAS FECHAS ENTRE LAS QUE SE VAN A SELECCIONAR FILAS DE *
      * LA TABLA T08CT006.                                            *
      * POSTERIORMENTE SE ABRIRA EL CURSOR A LA TABLA T08CT006 Y SE   *
      * REALIZARA LA PRIMERA LECTURA.                                 *
      *****************************************************************

      *---------------------------------------------------------------*
      * SE TOMA EL CONTROL DE ERRORES                                 *
      *---------------------------------------------------------------*

           INITIALIZE RETURN-CODE
           @DEFINE(NO-ERROSQL).
           @CTRLERR(APLICACION).

      *---------------------------------------------------------------*
      * SE INICIALIZAN VARIABLES                                      *
      *---------------------------------------------------------------*
           INITIALIZE WS-AUXILIARES
                      T08CT005
                      T08CT006
                      T04RPC11
                      T04DBA01.

      *---------------------------------------------------------------*
      * SE TRATA LA FICHA DE CONTROL                                  *
      *---------------------------------------------------------------*
           OPEN INPUT FICCON01.

           IF WS-STATUS NOT = ZERO
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-FICCON01 TO ERR-NOMBRE
               MOVE LT-A-OPEN     TO ERR-ACCION
               @ERROR(FATAL,WS-STATUS,MENSAJE-ERROR)
           END-IF.

           READ      FICCON01    INTO FICCON
             AT END
               MOVE  LT-A-FICHERO  TO ERR-RECURSO
               MOVE  LT-A-FICCON01 TO ERR-NOMBRE
               MOVE  LT-A-READ     TO ERR-ACCION
               @ERROR(FATAL,WS-BLANCOS,MENSAJE-ERROR)
           END-READ.

           MOVE CORR FC-FEC-INICIO TO DDMMAAAA.
           MOVE      DDMMAAAA      TO WS-FEC-INICIO.

           MOVE CORR FC-FEC-FINAL  TO DDMMAAAA.
           MOVE      DDMMAAAA      TO WS-FEC-FINAL.

           CLOSE     FICCON01.

      *---------------------------------------------------------------*
      * SE ABRE EL FICHERO DE SALIDA Y TABLASKD                       *
      *---------------------------------------------------------------*
           OPEN INPUT  TABLASKD
                OUTPUT FCTCORSD.

           IF TABCFST NOT = ZERO AND '97'
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-TABLASKD TO ERR-NOMBRE
               MOVE LT-A-OPEN     TO ERR-ACCION
               @ERROR(FATAL,TABCFST,MENSAJE-ERROR)
           END-IF.

           IF WS-STATUS-1 NOT = ZERO
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-FCTCORSD TO ERR-NOMBRE
               MOVE LT-A-OPEN     TO ERR-ACCION
               @ERROR(FATAL,WS-STATUS-1,MENSAJE-ERROR)
           END-IF.


      *---------------------------------------------------------------*
      * SE ABRE EL CURSOR A T08CT006                                  *
      *---------------------------------------------------------------*

           EXEC SQL OPEN CSR1 END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
               MOVE LT-A-CURSOR   TO ERR-RECURSO
               MOVE LT-A-T08CT006 TO ERR-NOMBRE
               MOVE LT-A-OPEN     TO ERR-ACCION
               @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR)
           END-IF.

      *---------------------------------------------------------------*
      * SE REALIZA LA PRIMERA LECTURA DEL CURSOR                      *
      *---------------------------------------------------------------*
           PERFORM IO1100-FETCH-CSR1.


       2000-PROCESO.
      *****************************************************************
      * EN ESTE PROCESO SE CONTROLARA EL FLUJO DEL PROGRAMA. LO QUE   *
      * SE REALIZARA SERA LO SIGUIENTE:                               *
      * - SE SELECCIONAN DATOS DE LAS TABLAS.                         *
      * - SE MUEVEN LOS DATOS LEIDOS A LOS CAMPOS DEL REGISTRO DEL    *
      *   FICHERO DE SALIDA.                                          *
      * - SE GRABA EL FICHERO DE SALIDA.                              *
      * - SE REALIZA LA SIGUIENTE LECTURA, PROCESANDO PARA UN NUEVO   *
      *   REGISTRO, HASTA FINALIZAR LAS CUENTAS.                      *
      *****************************************************************

      *---------------------------------------------------------------*
      * SE MUEVEN LOS CAMPOS LEIDOS A SALIDA                          *
      *---------------------------------------------------------------*
           MOVE COD-EMPRESA    OF T08CT006 TO COD-EMPRESA    OF SALIDA.
           MOVE COD-TIP-EXPE   OF T08CT006 TO COD-TIP-EXPE   OF SALIDA.
           MOVE NUM-CTA-INT    OF T08CT006 TO NUM-CTA-INT    OF SALIDA.
           MOVE IMP-MOVIMIENTO OF T08CT006 TO IMP-MOVIMIENTO OF SALIDA.
           MOVE FEC-OPERACION  OF T08CT006 TO FEC-OPERACION  OF SALIDA.

      *---------------------------------------------------------------*
      * SE OBTIENE LA SUCURSAL PROPIETARIA DE LA CUENTA               *
      *---------------------------------------------------------------*
           PERFORM A2100-ACCEDER-T08CT005.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
                IF IND-NO-ENCONTRADO
                     MOVE NUM-CTA-INT OF T08CT006 TO ERR-CUENTA
                     @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR1)
                ELSE
                     MOVE LT-A-TABLA    TO ERR-RECURSO
                     MOVE LT-A-T08CT005 TO ERR-NOMBRE
                     MOVE LT-A-SELECT   TO ERR-ACCION
                     @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR)
                END-IF
           END-IF.

           MOVE IMP-LIM-DISPOCTA OF T08CT005
                                    TO IMP-LIM-DISPOCTA    OF SALIDA.
           MOVE COD-SUC-ALTA  OF T08CT005 TO COD-SUC-ALTA  OF SALIDA.

           IF WS-CONT-DIAS-VCTO < 184
                MOVE LT-1 TO IND-VCTO OF SALIDA
           ELSE
                MOVE ZERO TO IND-VCTO OF SALIDA
           END-IF.

      *---------------------------------------------------------------*
      * SE OBTIENE LA ZONA DEL FICHERO TABLASKD ACCEDIENDO POR        *
      * COD-SUC-ALTA                                                  *
      *---------------------------------------------------------------*

           MOVE COD-SUC-ALTA  OF T08CT005 TO  OFIC-TABLASKD.
           MOVE CLAVE-TABLASKD            TO TABCCLA.

           READ TABLASKD INVALID KEY
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-TABLASKD TO ERR-NOMBRE
               MOVE LT-A-READ     TO ERR-ACCION
               @ERROR(FATAL,TABCFST,MENSAJE-ERROR)
           END-READ.

           MOVE TABCDAT            TO DATOS-TABLASKD.
           MOVE ZONA-TABLASKD      TO COD-ZONA OF SALIDA.

      *---------------------------------------------------------------*
      * SE OBTIENEN DATOS DEL CLIENTE                                 *
      *---------------------------------------------------------------*
           PERFORM A2200-ACCEDER-T04RPC11
           IF COD-PERSONA OF T04RPC11 = ZERO
               MOVE SPACE    TO  NOM-DENOM-SOCIAL OF SALIDA
           ELSE
               PERFORM A2300-ACCEDER-T04DBA01
           END-IF.

      *---------------------------------------------------------------*
      * SE GRABA EL REGISTRO                                          *
      *---------------------------------------------------------------*
           PERFORM IO1100-GRABAR-FCTCORSD.

      *---------------------------------------------------------------*
      * SE REALIZA LA SIGUIENTE LECTURA                               *
      *---------------------------------------------------------------*
           PERFORM IO1100-FETCH-CSR1.


       A2100-ACCEDER-T08CT005.
      *****************************************************************
      * SE OBTIENE LA SUCURSAL PROPIETARIA DE LA CUENTA ACCEDIENDO A  *
      * LA TABLA T08CT005 (CUENTAS)                                   *
      *****************************************************************

           EXEC SQL SELECT IMP_LIM_DISPOCTA,
                           COD_SUC_ALTA,
                           DAYS(FEC_VENCIMIENTO) - DAYS(FEC_VALOR2)
                 INTO  :T08CT005.IMP-LIM-DISPOCTA,
                       :T08CT005.COD-SUC-ALTA,
                       :WS-CONT-DIAS-VCTO
                 FROM  T08CT005
                 WHERE NUM_CTA_INT  = :T08CT006.NUM-CTA-INT
                   AND COD_TIP_EXPE = :WS-TIP-EXPE
                   AND COD_EMPRESA  = :T08CT006.COD-EMPRESA
           END-EXEC.


       A2200-ACCEDER-T04RPC11.
      *****************************************************************
      * EN ESTE PROCESO SE SELECCIONA EL CODIGO DE PERSONA.           *
      *****************************************************************

           INITIALIZE T04RPC11.
           EXEC SQL
               SELECT COD_PERSONA
                INTO  :T04RPC11.COD-PERSONA
                FROM  T04RPC11
                WHERE COD_EMPRESA        = :T08CT006.COD-EMPRESA
                  AND COD_TIP_EXPE       = :WS-TIP-EXPE
                  AND NUM_CTA_INT        = :T08CT006.NUM-CTA-INT
                  AND IND_CLIENTE_INDIV IN ('1', '3')
                  AND FEC_BAJA          IS NULL
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF IND-NO-ENCONTRADO
               PERFORM A2210-ACCEDER-CURSOR-T04RPC11
           ELSE
               IF NOT IND-SQL-CORRECTO
                   MOVE LT-A-TABLA               TO ERR-RECURSO3
                   MOVE LT-A-T04RPC11            TO ERR-NOMBRE3
                   MOVE LT-A-SELECT              TO ERR-ACCION3
                   MOVE COD-EMPRESA  OF T08CT006 TO ERR-EMPRESA3
                   MOVE WS-TIP-EXPE              TO ERR-TIPEXPE
                   MOVE NUM-CTA-INT  OF T08CT006 TO ERR-NUMCTA
                   @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR-3)
               END-IF
           END-IF.


       A2210-ACCEDER-CURSOR-T04RPC11.
      *****************************************************************
      * EN ESTE PROCESO SE SELECCIONA EL CODIGO DE PERSONA.           *
      *****************************************************************

           EXEC SQL OPEN CSR2 END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
               MOVE LT-A-CURSOR   TO ERR-RECURSO
               MOVE LT-A-T04RPC11 TO ERR-NOMBRE
               MOVE LT-A-OPEN     TO ERR-ACCION
               @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR)
           END-IF.

           INITIALIZE T04RPC11.
           EXEC SQL
               FETCH CSR2
                INTO :T04RPC11.COD-PERSONA     ,
                     :T04RPC11.NUM-ORDEN-INTERV
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO AND NOT IND-NO-ENCONTRADO
               @ERROR(FATAL,SQLSTATE-SIGLO,ERROR-PERSONA)
           END-IF.

           EXEC SQL CLOSE CSR2 END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
               MOVE LT-A-CURSOR   TO ERR-RECURSO
               MOVE LT-A-T04RPC11 TO ERR-NOMBRE
               MOVE LT-A-CLOSE    TO ERR-ACCION
               @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR)
           END-IF.


       A2300-ACCEDER-T04DBA01.
      *****************************************************************
      * EN ESTE PROCESO SE SELECCIONAN EL NOMBRE Y EL DOCUMENTO.      *
      *****************************************************************

           EXEC SQL
               SELECT NOM_DENOM_SOCIAL,
                      COD_NUM_DOC_OFICIA
                INTO :T04DBA01.NOM-DENOM-SOCIAL,
                     :T04DBA01.COD-NUM-DOC-OFICIA
                FROM  T04DBA01
                WHERE COD_EMPRESA = :T08CT006.COD-EMPRESA
                  AND COD_PERSONA = :T04RPC11.COD-PERSONA
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF IND-SQL-CORRECTO
               MOVE NOM-DENOM-SOCIAL   OF T04DBA01
                 TO NOM-DENOM-SOCIAL               OF SALIDA
           ELSE
               MOVE LT-A-TABLA              TO ERR-RECURSO4
               MOVE LT-A-T04DBA01           TO ERR-NOMBRE4
               MOVE LT-A-SELECT             TO ERR-ACCION4
               MOVE COD-EMPRESA OF T08CT006 TO ERR-EMPRESA4
               MOVE COD-PERSONA OF T04RPC11 TO ERR-PERSONA
               @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR-4)
           END-IF.


       8000-FINAL.
      *****************************************************************
      * EN ESTE PROCESO SE CIERRAN EL CURSOR Y LOS FICHEROS.          *
      *****************************************************************

           EXEC SQL CLOSE CSR1 END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
               MOVE LT-A-CURSOR   TO ERR-RECURSO
               MOVE LT-A-T08CT006 TO ERR-NOMBRE
               MOVE LT-A-CLOSE    TO ERR-ACCION
               @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR)
           END-IF.

           CLOSE FCTCORSD.

           IF WS-STATUS NOT = ZERO
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-FCTCORSD TO ERR-NOMBRE
               MOVE LT-A-CLOSE    TO ERR-ACCION
               @ERROR(FATAL,WS-STATUS,MENSAJE-ERROR)
           END-IF.

           IF  RETURN-CODE   <=  LT-N-4
	       EXEC SQL COMMIT END-EXEC
	   END-IF.
           STOP RUN.


       IO1100-FETCH-CSR1.
      *****************************************************************
      * EN ESTE PROCESO SE HACE UN FETCH DEL CURSOR A LA TABLA        *
      * T08CT006 (MOVIEMIENTOS)                                       *
      *****************************************************************

           INITIALIZE T08CT006.

      *---------------------------------------------------------------*
      * FETCH DE LA TABLA T08CT006 (MOVIMIENTOS)                      *
      *---------------------------------------------------------------*
           EXEC SQL
               FETCH CSR1
                INTO :T08CT006.COD-EMPRESA      ,
                     :T08CT006.COD-TIP-EXPE     ,
                     :T08CT006.NUM-CTA-INT      ,
                     :T08CT006.IMP-MOVIMIENTO   ,
                     :T08CT006.FEC-OPERACION
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
                IF IND-NO-ENCONTRADO
                     SET FIN-CUENTAS-SI TO TRUE
                ELSE
                     MOVE LT-A-CURSOR   TO ERR-RECURSO
                     MOVE LT-A-T08CT006 TO ERR-NOMBRE
                     MOVE LT-A-FETCH    TO ERR-ACCION
                     @ERROR(FATAL,SQLSTATE-SIGLO,MENSAJE-ERROR)
                END-IF
           END-IF.


       IO1100-GRABAR-FCTCORSD.
      *****************************************************************
      * EN ESTE PROCESO SE GRABA EL REGISTRO DE SALIDA.               *
      *****************************************************************

           WRITE R-FCTCORSD FROM SALIDA.

           IF WS-STATUS-1 NOT = ZERO
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-FCTCORSD TO ERR-NOMBRE
               MOVE LT-A-WRITE    TO ERR-ACCION
               @ERROR(FATAL,WS-STATUS-1,MENSAJE-ERROR)
           END-IF.
