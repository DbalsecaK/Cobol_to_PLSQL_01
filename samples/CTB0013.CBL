      ******************************************************************
      *       I D E N T I F I C A T I O N      D I V I S I O N         *
      ******************************************************************
       IDENTIFICATION DIVISION.

       PROGRAM-ID.         CTB0013.
       AUTHOR.             ALBERTO.
       INSTALLATION.       CAJAESPA#A.
       DATE-WRITTEN.       28-11-1994.
       DATE-COMPILED.

      ******************************************************************
      *  ------------ DATOS DE IDENTIFICACION DEL PROGRAMA ---------   *
      *                                                                *
      * PROGRAMA       : CTB0013.                                      *
      * APLICACION     : CUENTAS.                                      *
      * FEC.CODIFICAC. : 28-11-94.                                     *
      *                                                                *
      * FUNCIONES: ESTE PROGRAMA IMPRIME EL LISTADO DE CORRETAJES      *
      *    OBTENIENDO LOS DATOS DEL FICHERO DE SALIDA DEL  PROGRAMA    *
      *    CTB0012 LLAMADO FCTCORSD.                                   *
      *                                                                *
      *                                                                *
      * FICHEROS: - FCTCORSD => FICHERO DE ENTRADA CON LOS REGISTROS A *
      *                         IMPRIMIR EN EL INFORME.                *
      *                                                                *
      * ================  MODIFICACIONES ========================      *
      *                                                                *
      *   AUTOR     FECHA     CAUSA DE LA MODIFICACION                 *
      * --------- -------- ------------------------------------------- *
      * FERNANDO  11-05-95 AMPLIAR LAS ZONAS DE CORRETAJE EN LA TABLA  *

      * ALBERTO   14-03-96 AMPLIAR ZONAS DE CORRETAJE EN TABLA ZONAS   *
      * CHARO     15-05-96 CAMBIAR OCCURS DE LA TABLA DE ZONAS A 33    *
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

       SPECIAL-NAMES.
           DECIMAL-POINT IS COMMA.

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

           SELECT FCTCORSD ASSIGN TO FCTCORSD
                  FILE STATUS IS WS-STATUS.

           SELECT IMPRES01 ASSIGN TO IMPRES01.

      *****************************************************************
      *                  D A T A      D I V I S I O N                 *
      *****************************************************************
       DATA DIVISION.

       FILE SECTION.

       FD  FCTCORSD
           BLOCK CONTAINS 0 RECORDS
           RECORDING MODE IS F.
       01  R-FCTCORSD                      PIC X(104).

       FD  IMPRES01
           BLOCK CONTAINS 0 RECORDS
           RECORDING MODE IS F.
       01  R-IMPRES01                      PIC X(132).

      *****************************************************************
      *                WORKING-STORAGE  SECTION                       *
      *****************************************************************
       WORKING-STORAGE SECTION.

      ********************  CONSTANTES NUMERICAS  **********************
       01  LT-NUMERICAS.
           05  LT-N-1                      PIC 9(1)    VALUE 1.
           05  LT-N-2                      PIC 9(1)    VALUE 2.
           05  LT-N-3                      PIC 9(1)    VALUE 3.
           05  LT-N-4                      PIC 9(1)    VALUE 4.
           05  LT-N-5                      PIC 9(1)    VALUE 5.
           05  LT-N-6                      PIC 9(1)    VALUE 6.
           05  LT-N-7                      PIC 9(1)    VALUE 7.
           05  LT-N-8                      PIC 9(1)    VALUE 8.
           05  LT-N-9                      PIC 9(1)    VALUE 9.
           05  LT-N-10                     PIC 9(2)    VALUE 10.
           05  LT-N-11                     PIC 9(2)    VALUE 11.
           05  LT-N-12                     PIC 9(2)    VALUE 12.
           05  MAX-INDICE                  PIC 9(2)    VALUE 39.
           05  LT-N-50                     PIC 9(2)    VALUE 54.
           05  LT-N-99                     PIC 9(2)    VALUE 99.

      ******************* CONSTANTES ALFANUMERICAS *********************
       01  LT-ALFANUMERICAS.
           05  LT-ZONA-NO-EXISTENTE        PIC X(20)   VALUE
              'ZONA SIN IDENTIFICAR'.
           05  WS-BLANCOS                  PIC XX      VALUE SPACES.
           05  LT-ASTERISCOS               PIC X(2)    VALUE '**'.

      ********************  VARIABLES AUXILIARES  **********************
       01  WS-AUXILIARES.
           05  WS-STATUS                   PIC X(2).
           05  WS-ZONA-PROCESO             PIC 9(2).
           05  WS-T-LIMITE                 PIC S9(15) COMP-3 VALUE +0.
           05  WS-T-CORRETAJE              PIC S9(13) COMP-3 VALUE +0.

      **************** DAR FORMATO A LAS FECHAS DEL LISTADO ************
       01  DD-MM-AAAA.
           05 DIA                          PIC XX      VALUE ZEROS.
           05 FILLER                       PIC X.
           05 MES                          PIC XX      VALUE ZEROS.
           05 FILLER                       PIC X(3).
           05 ANYO                         PIC XX      VALUE ZEROS.
       01  DD-MM-AA.
           05 DIA1                         PIC XX      VALUE ZEROS.
           05 FILLER                       PIC X       VALUE '-'.
           05 MES1                         PIC XX      VALUE ZEROS.
           05 FILLER                       PIC X       VALUE '-'.
           05 ANYO1                        PIC XX      VALUE ZEROS.

      ******************** NUMERO CUENTA CLIENTE  **********************

       01  WS-CUENTA-CLIENTE.
           05 ENTIDAD.
              10 E1                         PIC 9(01).
              10 E2                         PIC 9(01).
              10 E3                         PIC 9(01).
              10 E4                         PIC 9(01).
           05 FILLER                        PIC X(1)    VALUE '-'.
           05 SUCURSAL                      PIC 9(04).
           05 FILLER             REDEFINES  SUCURSAL.
              10 O1                         PIC 9(01).
              10 O2                         PIC 9(01).
              10 O3                         PIC 9(01).
              10 O4                         PIC 9(01).
           05 FILLER                        PIC X(1)    VALUE '-'.
           05 DIGITOS-CONTROL.
              10 I                          PIC 9(01).
              10 D                          PIC 9(01).
           05 FILLER                        PIC X(1)    VALUE '-'.
           05 CUENTA.
              10 N0                         PIC 9(01).
              10 N1                         PIC 9(01).
              10 N2                         PIC 9(01).
              10 N3                         PIC 9(01).
              10 N4                         PIC 9(01).
              10 N5                         PIC 9(01).
              10 N6                         PIC 9(01).
              10 D7                         PIC 9(01).
              10 G8                         PIC 9(01).
              10 G9                         PIC 9(01).
           05 CUENTA-NUEVA REDEFINES CUENTA.
              10 CTA-CUENTA-N               PIC 9(08).
              10 EXPEDIENTE-N               PIC 9(02).
           05 CUENTA-VIEJA REDEFINES CUENTA.
              10 CTA-AHORRO-V               PIC 9(02).
              10 CERO-V                     PIC X(01).
              10 CTA-CUENTA-V               PIC 9(07).

       01  DIGITO-I                         PIC 9(03).
       01  DIGITO-D                         PIC 9(03).
       01  COCIENTE                         PIC 9(03).
       01  RESTO-I                          PIC 9(02).
       01  RESTO-D                          PIC 9(02).


      ********************      CONTADORES        **********************
       01  CONTADORES.
           05  WS-CONT-PAGINAS             PIC 9(5).
           05  WS-CONT-LINEAS              PIC 9(2).

      *************************************************************
      *         PARAMETROS PARA LA RUTINA DE ERROR DB2            *
      *************************************************************
       01  LITERALES.
           05  LT-A-FICHERO                PIC X(9)  VALUE 'FICHERO  '.
           05  LT-A-CURSOR                 PIC X(9)  VALUE 'CURSOR A '.
           05  LT-A-TABLA                  PIC X(9)  VALUE 'TABLA    '.

           05  LT-A-FCTCORSD               PIC X(8)  VALUE 'FCTCORSD'.

           05  LT-A-OPEN                   PIC X(8)  VALUE 'OPEN    '.

      ********************        SWITCHES        **********************
       01  SWITCHES.
           05  SW-FIN-FICHERO              PIC 9     VALUE 0.
               88 FIN-FICHERO                        VALUE 1.

           05  SW-ENCONTRADO               PIC 9     VALUE 0.
               88 NO-ENCONTRADO                      VALUE 0.
               88 ENCONTRADO                         VALUE 1.

      *----------------------------------------------------------------*
      *   TABLAS CON LAS DESCRIPCION DE LAS DISTINTAS ZONAS DE COBRO   *
      *   DE CORRETAJES (COPIADA DEL PROG. AHOBC045)                   *
      *----------------------------------------------------------------*
       01  TABLITE.
           03  FILLER PIC X(23) VALUE '209601LEON             '.
           03  FILLER PIC X(23) VALUE '209602PONFERRADA       '.
           03  FILLER PIC X(23) VALUE '209603ASTORGA          '.
           03  FILLER PIC X(23) VALUE '209604CORU#A           '.
           03  FILLER PIC X(23) VALUE '209605LUGO             '.
           03  FILLER PIC X(23) VALUE '209606ORENSE           '.
           03  FILLER PIC X(23) VALUE '209607VIGO             '.
           03  FILLER PIC X(23) VALUE '209608ASTURIAS         '.
           03  FILLER PIC X(23) VALUE '209609SANTANDER        '.
           03  FILLER PIC X(23) VALUE '209611VALLADOLID       '.
           03  FILLER PIC X(23) VALUE '209612MEDINA DEL CAMPO '.
           03  FILLER PIC X(23) VALUE '209613MEDINA DE RIOSECO'.
           03  FILLER PIC X(23) VALUE '209614TUDELA DE DUERO  '.
           03  FILLER PIC X(23) VALUE '209615TORDESILLAS      '.
           03  FILLER PIC X(23) VALUE '209616PE#AFIEL         '.
           03  FILLER PIC X(23) VALUE '209617LAGUNA DE DUERO  '.
           03  FILLER PIC X(23) VALUE '209618ISCAR            '.
           03  FILLER PIC X(23) VALUE '209621PALENCIA         '.
           03  FILLER PIC X(23) VALUE '209631ZAMORA           '.
           03  FILLER PIC X(23) VALUE '209641AVILA            '.
           03  FILLER PIC X(23) VALUE '209649BEJAR            '.
           03  FILLER PIC X(23) VALUE '209650SALAMANCA        '.
           03  FILLER PIC X(23) VALUE '209651ARANDA DE DUERO  '.
           03  FILLER PIC X(23) VALUE '209652CUELLAR          '.
           03  FILLER PIC X(23) VALUE '209653SORIA            '.
           03  FILLER PIC X(23) VALUE '209654BURGOS           '.
           03  FILLER PIC X(23) VALUE '209660MADRID           '.
           03  FILLER PIC X(23) VALUE '209670HUESCA           '.
           03  FILLER PIC X(23) VALUE '209671TERUEL           '.
           03  FILLER PIC X(23) VALUE '209672ZARAGOZA         '.
           03  FILLER PIC X(23) VALUE '209673ALBACETE         '.
           03  FILLER PIC X(23) VALUE '209674CIUDAD REAL      '.
           03  FILLER PIC X(23) VALUE '209675GUADALAJARA      '.
           03  FILLER PIC X(23) VALUE '209676TOLEDO           '.
           03  FILLER PIC X(23) VALUE '209677PAMPLONA         '.
           03  FILLER PIC X(23) VALUE '209680DPTO. PRESTAMO   '.
           03  FILLER PIC X(23) VALUE '209690LOGRO#O          '.
           03  FILLER PIC X(23) VALUE '209698CTRAL. DEL RIESGO'.
           03  FILLER PIC X(23) VALUE '209699PTMOS EMPLEADOS  '.
       01  RTABLIT REDEFINES TABLITE.
           03 ELETAB OCCURS 39.
               05  CLATA.
                   07 ENTTA PIC X(4).
                   07 ZONTA PIC 99.
               05  LITTA    PIC X(17).
       01  INDICE                           PIC 99     VALUE 0.

      *----------------------------------------------------------------*
      *   REGISTRO DEL FICHERO FCTCORSD (CONTIENE LOS CAMPOS QUE SE    *
      *   USARAN PARA IMPRIMIR EL INFORME).                            *
      *----------------------------------------------------------------*
       01  ENTRADA.
           05  COD-EMPRESA                  PIC X(04).
           05  COD-ZONA                     PIC 9(02).
           05  COD-SUC-ALTA                 PIC X(04).
           05  COD-TIP-EXPE                 PIC X(02).
           05  NUM-CTA-INT                  PIC S9(08) COMP-3.
           05  NOM-DENOM-SOCIAL             PIC X(60).
           05  FEC-OPERACION                PIC X(10).
           05  IMP-LIM-DISPOCTA             PIC S9(13)V9(2) COMP-3.
           05  IMP-MOVIMIENTO               PIC S9(13)V9(2) COMP-3.
           05  IND-VCTO                     PIC X.

      *----------------------------------------------------------------
      *  CABECERAS Y LINEAS DEL LISTADO DE SALIDA
      *----------------------------------------------------------------
       01  CABE-1.
           05  ENTIDAD-N                   PIC X(4).
           05  FILLER                      PIC X(3)    VALUE ' -'.
           05  FILLER                      PIC X(124)  VALUE
               'CAJA ESPA#A'.

       01  CABE-2.
           05 FILLER                       PIC X(34)   VALUE 'CTB0013 '.
           05 FILLER                       PIC X(35)   VALUE
              'RELACION DE CORRETAJES COBRADOS DE'.
           05 ZONA                         PIC X(17)   VALUE SPACE.
           05 FILLER                       PIC X(26).
           05 FILLER                       PIC X(09)   VALUE 'FECHA :'.
           05 DATUM                        PIC X(10).

       01  CABE-3.
           05 FILLER                       PIC X(03)   VALUE 'LCT'.
           05 FILLER                       PIC X(109)  VALUE '001301'.
           05 FILLER                       PIC X(11)   VALUE 'HORA  :'.
           05 HORA-PROCESO                 PIC Z9.99.99.

       01  CABE-4.
           05 FILLER                       PIC X(4)    VALUE '0840'.
           05 FILLER                       PIC X(3)    VALUE ' - '.
           05 FILLER                       PIC X(30)   VALUE
                'OPERACIONES DE ACTIVO'.
           05 FILLER                       PIC X(75)   VALUE SPACES.
           05 FILLER                       PIC X(7)    VALUE 'PAGINA:'.
           05 FILLER                       PIC X(5)    VALUE SPACES.
           05 PAGINA                       PIC ZZZ.ZZ9.

       01  CABE-5.
           05 FILLER                       PIC X(131)  VALUE ALL '-'.

       01  CABE-6.
           05 FILLER                       PIC X(23)
                                   VALUE '   NUMERO DE CUENTA    '.
           05 FILLER                       PIC X(25)   VALUE SPACES.
           05 FILLER                       PIC X(7)
                                   VALUE 'TITULAR'.
           05 FILLER                       PIC X(26)   VALUE SPACES.
           05 FILLER                       PIC X(8)
                                   VALUE 'F.OPERA.'.
           05 FILLER                       PIC X(3)    VALUE SPACES.
           05 FILLER                       PIC X(20)
                                   VALUE ' CONCEDIDO O LIMITE'.
           05 FILLER                       PIC X(03)   VALUE SPACES.
           05 FILLER                       PIC X(16)
                                   VALUE '   CORRETAJE'.

       01  CABE-7.
           05 FILLER                       PIC X(23)
                                   VALUE '-----------------------'.
           05 FILLER                       PIC X(4)    VALUE SPACES.
           05 FILLER                       PIC X(50)
                                   VALUE ALL '-'.
           05 FILLER                       PIC X(4)    VALUE SPACES.
           05 FILLER                       PIC X(8)
                                   VALUE '--------'.
           05 FILLER                       PIC X(3)    VALUE SPACES.
           05 FILLER                       PIC X(20)
                                   VALUE '--------------------'.
           05 FILLER                       PIC X(03)   VALUE SPACES.
           05 FILLER                       PIC X(16)
                                   VALUE '----------------'.

       01  DETALLE.
           05 CUENTA-CLIENTE               PIC X(23).
           05 FILLER                       PIC X        VALUE SPACES.
           05 MARCA-VCTO                   PIC X(2)     VALUE SPACES.
           05 FILLER                       PIC X        VALUE SPACES.
           05 NOMBRE-TITULAR               PIC X(50).
           05 FILLER                       PIC X(4)     VALUE SPACES.
           05 FEC-OPERACION                PIC X(8).
           05 FILLER                       PIC X(5)     VALUE SPACES.
           05 LIMITE                       PIC Z.ZZZ.ZZZ.ZZZ.ZZ9.
           05 FILLER                       PIC X(05)    VALUE SPACES.
           05 CORRETAJE                    PIC Z.ZZZ.ZZZ.ZZ9-.

       01  TOTAL.
           05 FILLER                       PIC X(80)    VALUE SPACES.
           05 FILLER                       PIC X(8)    VALUE 'TOTAL...'.
           05 FILLER                       PIC X(4)     VALUE SPACES.
           05 TOTAL-LIMITE                 PIC ZZZ.ZZZ.ZZZ.ZZZ.ZZ9.
           05 FILLER                       PIC X(03)    VALUE SPACES.
           05 TOTAL-CORRETAJE              PIC ZZZ.ZZZ.ZZZ.ZZ9-.

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

           05  MENSAJE-ERROR1              PIC X(40)
                 VALUE 'NO EXISTEN REGISTROS EN FICHERO FCTCORSD'.
           05  LT-ERR-GXINIBAT             PIC X(25) VALUE
               'ERROR EN MACRO GXINIBAT.'.


      *****************************************************************
      *                        LINKAGE SECTION                        *
      *****************************************************************
       LINKAGE SECTION.

      *****************************************************************
      *           P R O C E D U R E      D I V I S I O N              *
      *****************************************************************
       PROCEDURE DIVISION.

      **INICIO-PROGRAMA-CTB0013

           PERFORM 1000-INICIO

           PERFORM 2000-PROCESO UNTIL FIN-FICHERO.

            PERFORM 8000-FINAL.
      **FINAL-PROGRAMA-CTB0013


      *****************************************************************
      *                    1000-INICIO                         *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE PROCEDERA A ABRIR LOS FICHEROS QUE SE VAN  *
      * A UTILIZAR EN EL PROGRAMA Y, A OBTENER LA FECHA Y HORA DEL    *
      * SISTEMA.                                                      *
      *****************************************************************
       1000-INICIO.

      *---------------------------------------------------------------*
      * SE INICIALIZAN VARIABLES                                      *
      *---------------------------------------------------------------*
           INITIALIZE WS-AUXILIARES
                      WS-CONT-PAGINAS
                      RETURN-CODE
                      ENTRADA.

           MOVE LT-N-99 TO WS-CONT-LINEAS

      *---------------------------------------------------------------*
      * SE CAPTURAN LA FECHA Y LA HORA DEL SISTEMA                    *
      *---------------------------------------------------------------*
      **** ANIO 2000 Y EFECTO BISAGRA. ELIMINACION DEL ACCEPT.

           @INIBAT().
           IF TIPO-ERROR OF S21-AREA-ERROR > LT-RET-AVISO
                @ERROR(,,LT-ERR-GXINIBAT)
           END-IF.

           MOVE  FEM-MAQUINA OF S21-AREA-ENTORNO
             TO DATUM.

           MOVE  HOR-MAQUINA OF S21-AREA-ENTORNO
             TO HORA-PROCESO.

      *---------------------------------------------------------------*
      * SE ABRE EL FICHERO DE ENTRADA                                 *
      *---------------------------------------------------------------*
           OPEN INPUT FCTCORSD.

           IF WS-STATUS NOT = ZERO
               MOVE LT-A-FICHERO  TO ERR-RECURSO
               MOVE LT-A-FCTCORSD TO ERR-NOMBRE
               MOVE LT-A-OPEN     TO ERR-ACCION
               @ERROR(FATAL,WS-STATUS,MENSAJE-ERROR)
           END-IF.

      *---------------------------------------------------------------*
      * SE ABRE EL FICHERO DE SALIDA                                  *
      *---------------------------------------------------------------*
           OPEN OUTPUT IMPRES01.

      *---------------------------------------------------------------*
      * SE REALIZA LA PRIMERA LECTURA DEL FICHERO                     *
      *---------------------------------------------------------------*
           PERFORM IO1100-LEER-FCTCORSD.

           IF FIN-FICHERO
              @ERROR(FATAL,WS-BLANCOS,MENSAJE-ERROR1)
           END-IF.
      *---------------------------------------------------------------*
      * SE MUEVEN VARIABLES                                           *
      *---------------------------------------------------------------*
           MOVE COD-ZONA       OF ENTRADA TO WS-ZONA-PROCESO.
           PERFORM A2600-HALLAR-NOMBRE-ZONA.

      *****************************************************************
      *                        2000-PROCESO                          *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE CONTROLARA EL FLUJO DEL PROGRAMA. LO QUE   *
      * SE REALIZARA SERA LO SIGUIENTE:                               *
      *   - SE MOVERAN LOS DATOS DEL FICHERO DE ENTRADA A LOS CAMPOS  *
      *     DEL LISTADO Y SE GRABARA EL INFORME                       *
      *   - SE ROMPERA EL INFORME POR ZONA DE PAGO DEL CORRETAJE      *
      *****************************************************************
       2000-PROCESO.

           IF COD-ZONA    OF ENTRADA  = WS-ZONA-PROCESO
      *---------------------------------------------------------------*
      * SE OBTIENE LA CUENTA EN FORMATO CODIGO DE CUENTA CLIENTE      *
      *---------------------------------------------------------------*
              PERFORM A2100-OBTENER-CUENTA
              PERFORM A2500-ESCRIBIR-DETALLE
      *---------------------------------------------------------------*
      * SE REALIZA LA SIGUIENTE LECTURA                               *
      *---------------------------------------------------------------*
              PERFORM IO1100-LEER-FCTCORSD
           ELSE
              MOVE WS-T-LIMITE          TO TOTAL-LIMITE
              MOVE WS-T-CORRETAJE       TO TOTAL-CORRETAJE
              PERFORM IO1100-GRABAR-TOTAL
              MOVE ZEROS                TO WS-T-LIMITE WS-T-CORRETAJE
              MOVE COD-ZONA  OF ENTRADA TO WS-ZONA-PROCESO
              PERFORM A2600-HALLAR-NOMBRE-ZONA
              MOVE LT-N-99              TO WS-CONT-LINEAS
           END-IF.


      *****************************************************************
      *                   A2100-OBTENER-CUENTA                        *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE SACA EL INFORME DE ESTADISTICAS Y SE       *
      * CIERRAN LOS FICHEROS.                                         *
      *****************************************************************
       A2100-OBTENER-CUENTA.

           MOVE COD-EMPRESA   OF ENTRADA TO ENTIDAD
           MOVE COD-SUC-ALTA  OF ENTRADA TO SUCURSAL
           MOVE NUM-CTA-INT   OF ENTRADA TO CTA-CUENTA-N
           MOVE COD-TIP-EXPE  OF ENTRADA TO EXPEDIENTE-N

           PERFORM A9000-OBTENER-DIG-CTRL.

           MOVE WS-CUENTA-CLIENTE TO CUENTA-CLIENTE.

      *****************************************************************
      *                   A2500-ESCRIBIR-DETALLE                      *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE COMPLETAN LOS CAMPOS A GRABAR PARA LOS     *
      * DISTINTOS REGISTROS DE DETALLE.                               *
      *****************************************************************
       A2500-ESCRIBIR-DETALLE.

           MOVE NOM-DENOM-SOCIAL OF ENTRADA TO NOMBRE-TITULAR.
           MOVE FEC-OPERACION    OF ENTRADA TO DD-MM-AAAA.
           MOVE DIA                         TO DIA1.
           MOVE MES                         TO MES1.
           MOVE ANYO                        TO ANYO1.
           MOVE DD-MM-AA                    TO FEC-OPERACION OF DETALLE.
           MOVE IMP-LIM-DISPOCTA OF ENTRADA TO LIMITE.
           MOVE IMP-MOVIMIENTO   OF ENTRADA TO CORRETAJE.
           ADD  IMP-LIM-DISPOCTA OF ENTRADA TO WS-T-LIMITE.
           ADD  IMP-MOVIMIENTO   OF ENTRADA TO WS-T-CORRETAJE.

           IF   IND-VCTO         OF ENTRADA = '0'
                MOVE SPACES                 TO MARCA-VCTO
           ELSE
                MOVE LT-ASTERISCOS          TO MARCA-VCTO
           END-IF.

           PERFORM IO1100-GRABAR-DETALLE.

      *****************************************************************
      *                   A2600-HALLAR-NOMBRE-ZONA                    *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE ACCCEDE A LA TABLA DE WORKING CON LOS      *
      * NOMBRES DE ZONA POR COD-EMPRESA Y COD-ZONA                    *
      *****************************************************************
       A2600-HALLAR-NOMBRE-ZONA.

            SET NO-ENCONTRADO TO TRUE.

            PERFORM VARYING INDICE FROM 1 BY 1 UNTIL ENCONTRADO
                                                  OR INDICE > MAX-INDICE
                IF  ZONTA(INDICE) = WS-ZONA-PROCESO
                    MOVE LITTA(INDICE)    TO ZONA
                    SET ENCONTRADO TO TRUE
                END-IF
            END-PERFORM.

            IF NO-ENCONTRADO
               MOVE LT-ZONA-NO-EXISTENTE   TO ZONA
            END-IF.

      *****************************************************************
      *                       8000-FINAL                           *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE SACA EL INFORME DE ESTADISTICAS Y SE       *
      * CIERRAN LOS FICHEROS.                                         *
      *****************************************************************
       8000-FINAL.

           MOVE WS-T-LIMITE             TO TOTAL-LIMITE.
           MOVE WS-T-CORRETAJE          TO TOTAL-CORRETAJE.
           PERFORM IO1100-GRABAR-TOTAL.

           CLOSE FCTCORSD IMPRES01.
           IF  RETURN-CODE   <=  LT-N-4
	       EXEC SQL COMMIT END-EXEC
	   END-IF.
           STOP RUN.

      *****************************************************************
      *                  A9000-OBTENER-DIG-CTRL                       *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE SACA EL INFORME DE ESTADISTICAS Y SE       *
      * CIERRAN LOS FICHEROS.                                         *
      *****************************************************************
       A9000-OBTENER-DIG-CTRL.

           COMPUTE DIGITO-I = E1 * LT-N-4  + E2 * LT-N-8 + E3 * LT-N-5 +
                              E4 * LT-N-10 + O1 * LT-N-9 + O2 * LT-N-7 +
                              O3 * LT-N-3  + O4 * LT-N-6
           COMPUTE DIGITO-D = N0 * LT-N-1 + N1 * LT-N-2 + N2 * LT-N-4  +
                              N3 * LT-N-8 + N4 * LT-N-5 + N5 * LT-N-10 +
                              N6 * LT-N-9 + D7 * LT-N-7 + G8 * LT-N-3  +
                              G9 * LT-N-6

           DIVIDE LT-N-11 INTO DIGITO-I GIVING COCIENTE
                                        REMAINDER RESTO-I.
           DIVIDE LT-N-11 INTO DIGITO-D GIVING COCIENTE
                                        REMAINDER RESTO-D.

           IF RESTO-I = ZEROES OR = LT-N-1
              MOVE RESTO-I TO I
           ELSE
              COMPUTE I = LT-N-11 - RESTO-I
           END-IF.

           IF RESTO-D = ZEROES OR = LT-N-1
              MOVE RESTO-D                  TO D
           ELSE
              COMPUTE D = LT-N-11 - RESTO-D
           END-IF.

      *****************************************************************
      *                     IO1100-LEER-FCTCORSD                      *
      *---------------------------------------------------------------*
      * EN ESTE PROCESO SE LEE-LOS REGISTROS DEL FICHERO DE ENTRADA   *
      *****************************************************************
       IO1100-LEER-FCTCORSD.

           READ FCTCORSD INTO ENTRADA
                AT END SET FIN-FICHERO TO TRUE.

      *****************************************************************
      *                     IO1100-GRABAR-CABECERAS                   *
      *****************************************************************
       IO1100-GRABAR-CABECERAS.

           ADD  LT-N-1            TO WS-CONT-PAGINAS.
           MOVE WS-CONT-PAGINAS   TO PAGINA.
           MOVE LT-N-12           TO WS-CONT-LINEAS.

           MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
              TO ENTIDAD-N.

           WRITE R-IMPRES01 FROM CABE-1 AFTER ADVANCING PAGE
           WRITE R-IMPRES01 FROM CABE-2 AFTER 1
           WRITE R-IMPRES01 FROM CABE-3 AFTER 1
           WRITE R-IMPRES01 FROM CABE-4 AFTER 1
           WRITE R-IMPRES01 FROM CABE-5 AFTER 1
           WRITE R-IMPRES01 FROM CABE-6 AFTER 2
           WRITE R-IMPRES01 FROM CABE-7 AFTER 1.


      *****************************************************************
      *                     IO1100-GRABAR-DETALLE                     *
      *****************************************************************
       IO1100-GRABAR-DETALLE.

           IF WS-CONT-LINEAS > LT-N-50
              PERFORM IO1100-GRABAR-CABECERAS
           END-IF.

           WRITE R-IMPRES01 FROM DETALLE AFTER 1.

           ADD 1 TO WS-CONT-LINEAS.

      *****************************************************************
      *                     IO1100-GRABAR-TOTAL                       *
      *****************************************************************
       IO1100-GRABAR-TOTAL.

           WRITE R-IMPRES01 FROM TOTAL   AFTER 2.

           ADD 1 TO WS-CONT-LINEAS.
