
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CTB3004.
       AUTHOR. GLADYS ALBAN (ECUADOR).
       INSTALLATION. BCOPICHINCHA.
      *****************************************************************
      *     ---------- DATOS DE IDENTIFICACION DEL PROGRAMA -------   *
      *                                                               *
      * PROGRAMA       : CTB3004                                      *
      * APLICACION     : PASIVO.PROTESTOS                             *
      * FEC.CODIFICAC. : 26.11.2001                                   *
      *                                                               *
      * FUNCION: - Genera un archivo (CTDSUPB) del cual se tomaran los*
      *            datos de los protestos de la quincena, para repor- *
      *            tar a la Superintendencia de Bancos.               *
      *                                                               *
      * TABLAS :                                                      *
      *       T08CT093 -> Tabla de Protestos.                         *
      *       T08CT003 -> Tabla de Ctas.                              *
      *                                                               *
      * ================  MODIFICACIONES ========================     *
      *                                                               *
      *   AUTOR     FECHA     CAUSA DE LA MODIFICACION                *
      * -------- ---------- ----------------------------------------- *
      * MGARCES  07.01.2003 CORRECCION FECHAS DE LA QUINCENA          *
      * FSALAZA  27.03.2003 CORRIGE LA DATA DE DIRECCION QUE NO ESTA  *
      *                     SIENDO INFORMADO EN FICHERO Y REPORTE.    *
      *****************************************************************


       ENVIRONMENT DIVISION.

       CONFIGURATION SECTION.

       SPECIAL-NAMES.
           DECIMAL-POINT IS COMMA.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.

           SELECT CTDSUPB ASSIGN TO CTDSUPB
      *           ORGANIZATION IS LINE SEQUENTIAL
                  FILE STATUS IS WS-STATUS.

           SELECT IMPRES01 ASSIGN TO IMPRES01
                  FILE STATUS IS WS-FS01.

           SELECT FICCON  ASSIGN TO FICCON01
                  FILE STATUS IS WS-ESTADO.

      ***************
       DATA DIVISION.
      ***************

       FILE SECTION.
      **************

       FD  CTDSUPB RECORDING MODE IS F.
       01  REG-CTDSUPB             PIC X(190).

       FD  IMPRES01 RECORDING MODE IS F.
       01  REG-IMPRES01            PIC X(133).

       FD  FICCON  RECORDING MODE IS F
           LABEL RECORDS STANDARD.
       01  R-FICCON                PIC X(80).



       WORKING-STORAGE SECTION.
      *************************


      ****************************************************************
      **          DESCRIPCION DE AREAS DE TRABAJO DB2               **
      ****************************************************************

      *- tabla de cuentas/cheques
           EXEC SQL
                INCLUDE T08CT093
           END-EXEC.

      *- tabla de empresa/centros direcciones
           EXEC SQL
                INCLUDE T37OBS11
           END-EXEC.

      *- include tabla de provincia y municipios:
           EXEC SQL
                INCLUDE T06TC007
           END-EXEC.

      *- tabla de codigos.
           EXEC SQL
                INCLUDE T06TC002
           END-EXEC.

      *- tabla de datos personas fisica:
           EXEC SQL
                INCLUDE T04CPE02
           END-EXEC.

      *- tabla de datos personas juridicas:
           EXEC SQL
                INCLUDE T04CPE03
           END-EXEC.


      *----------------
      *   LITERALES
      *----------------
       01 LITERALES.
           05 LT-A-EPR0015            PIC X(7)   VALUE 'EPR0015'.
           05 LT-A-VALIDAR            PIC X      VALUE 'V'.

      *------------------------------------------------------
      * DEFINICION DE FICHERO DE CONTROL EN JCL
      *------------------------------------------------------
       01 FICCON-REG.
           05  FIC-COD-FECHA     PIC X(01)      VALUE SPACES.
           05  FIC-FECHA-INI     PIC X(10)      VALUE SPACES.
           05  FILLER            PIC X(01)      VALUE SPACES.
           05  FIC-FECHA-FIN     PIC X(10)      VALUE SPACES.
           05  FILLER            PIC X(58)      VALUE SPACES.

      *--------------------------------------
      *         VARIABLES AUXILIARES DEL FICCON
      *--------------------------------------

       01 ESTATUS.
          05 W-ESTADO              PIC X(2) VALUE SPACES.

      *   CONVIERTE LA FECHAS DE RANGO EN ESTE FORMATO PARA VALIDARLAS
      *   CON LA RUTINA EPR0015

       01  W-COD-VAL             PIC X VALUE SPACES.
       01  WS-PUNTO              PIC 9(8) VALUE ZEROS.

       01  W-FEC-VAL.
           03 W-DD-VAL           PIC 99 VALUE ZEROS.
           03 FILLER             PIC X  VALUE '.'.
           03 W-MM-VAL           PIC 99 VALUE ZEROS.
           03 FILLER             PIC X  VALUE '.'.
           03 W-AAAA-VAL         PIC 9(4).



       01  WK-INDI            PIC XX       VALUE SPACES.
       01  WK-INDI-R REDEFINES WK-INDI.
           02 WK-INDI-1       PIC X.
           02 WK-INDI-2       PIC X.
       01  WK-CONVER          PIC 9(03) COMP VALUE ZEROS.
       01  WK-CONVER-R REDEFINES WK-CONVER.
           02 WK-CONVER-1     PIC X(01).
           02 WK-CONVER-2     PIC X(01).

       01  IND-NULL-COD-OFICIAL   PIC S9(4) COMP VALUE ZEROS.
       01  IND-NULL-COD-OFICIA    PIC S9(4) COMP VALUE ZEROS.

      ****************************************************************
      *                     VARIABLES AUXILIARES                     *
      ****************************************************************
       01  WS-FEC-AUX.
           05 FEC-CANC-DIA             PIC 9(02)    VALUE ZEROES.
           05 FILLER                   PIC X(01)    VALUE '/'.
           05 FEC-CANC-MES             PIC X(02)    VALUE SPACES.
           05 FILLER                   PIC X(01)    VALUE '/'.
           05 FEC-CANC-ANO             PIC X(04)    VALUE SPACES.

       01  WS-FECHA-AUXI.
           05 WS-ANIO-AUXI        PIC X(4)          VALUE SPACES.
           05 F                   PIC X             VALUE '/'.
           05 WS-MES-AUXI         PIC 9(2)          VALUE ZEROS.
           05 F                   PIC X             VALUE '/'.
           05 WS-DIA-AUXI         PIC 9(2)          VALUE ZEROS.

       01  WS-FECHA-AUXI2.
           05 WS-ANIO-AUXI2        PIC X(4)          VALUE SPACES.
           05 F                   PIC X             VALUE '/'.
           05 WS-MES-AUXI2         PIC 9(2)          VALUE ZEROS.
           05 F                   PIC X             VALUE '/'.
           05 WS-DIA-AUXI2         PIC 9(2)          VALUE ZEROS.

       01  WS-FECHA-INICIAL.
           05 WS-DIA-I            PIC X(2).
           05 F                   PIC X             VALUE '/'.
           05 WS-MES-I            PIC X(2).
           05 F                   PIC X             VALUE '/'.
           05 WS-ANIO-I           PIC X(4).

       01  WS-FECHA-TABLA-I.
           05 WS-ANIO-TI          PIC X(4).
           05 F                   PIC X             VALUE '-'.
           05 WS-MES-TI           PIC X(2).
           05 F                   PIC X             VALUE '-'.
           05 WS-DIA-TI           PIC X(2).
           05 F                   PIC X(16)
                                  VALUE '-00.00.00.000000'.

       01  WS-FECHA-TABLA-IF      PIC X(26).

       01  WS-FECHA-FINAL.
           05 WS-DIA-F            PIC X(2).
           05 F                   PIC X             VALUE '/'.
           05 WS-MES-F            PIC X(2).
           05 F                   PIC X             VALUE '/'.
           05 WS-ANIO-F           PIC X(4).

       01  WS-FECHA-TABLA-F.
           05 WS-ANIO-TF          PIC X(4).
           05 F                   PIC X             VALUE '-'.
           05 WS-MES-TF           PIC X(2).
           05 F                   PIC X             VALUE '-'.
           05 WS-DIA-TF           PIC X(2).
           05 F                   PIC X(16)
                                  VALUE '-23.59.59.999999'.

       01  WS-FECHA-TABLA-FF      PIC X(26).

       01  WS-STATUS                   PIC 9(2).
       01  WS-MESX                     PIC 9(2) VALUE 0.
       01  WS-FS01                     PIC 9(2).
       01  WS-ESTADO                   PIC 9(2).

       01  WS-FEC-PROTESTO             PIC X(10)      VALUE SPACES.
       01  WS-FECHA                    PIC X(10)      VALUE SPACES.

       01  WS-TIMESTAMP-ALTA.
           05 WS-TIMES-PROTESTO   PIC X(10) VALUE SPACES.
           05 F                   PIC X(16) VALUE SPACES.

       01  WS-COD-PERSONA              PIC S9(9) VALUE ZEROS.
       01  WS-IND-TIPO-PERSONA         PIC X(1)  VALUE SPACES.
       01  WS-COD-PERSON               PIC 9(9)  VALUE ZEROS.
       01  WS-COD-EXT-DOC-CP           PIC X(14) VALUE SPACES.
       01  WS-NUM-DIRECCION            PIC S9(3) COMP-3.
       01  WS-IND                  PIC S9(9)  VALUE ZEROS.
       01  WS-COD-TIP-EXPE         PIC X(2).
       01  WS-NUM-CTA-INT          PIC S9(8)V USAGE COMP-3.
       01  WS-NUM-CTA-XXX          PIC  9(8).
       01  WS-IND-ORD              PIC 9(2) VALUE ZEROS.
       01  WS-IND-AUX              PIC 9(2) VALUE ZEROS.
       01  WS-NUM-ORDEN-INTERV-AUX PIC 9(7) VALUE ZEROS.
       01  WS-NUM-ORDEN-INTERV-AU1 PIC 9(7) VALUE ZEROS.
       01  WS-OFICIAL              PIC 9(7) VALUE ZEROS.
       01  WS-COCIENTE             PIC 9(4) VALUE ZEROS.
       01  WS-RESTO                PIC 9(4) VALUE ZEROS.
       01  WS-SALDO                PIC 9(15)V99 VALUE ZEROS.
       01  WS-BANDERA              PIC 9 VALUE ZEROS.
       01  WS-BANDERA-TOT          PIC 9 VALUE 1.
       01  WSN-CONTLIN             PIC 9(2)  COMP   VALUE 90.
       01  WSN-CONTPAG             PIC 9(6)  COMP   VALUE  0.
       01  WS-COD-EMPRESA          PIC X(4)  VALUE SPACES.
       01  WS-NUM-FILAS            PIC 9(3)  VALUE ZEROS.

       01  WS-AAMM.
           05   WS-ANIO-SAL PIC 9(4).
           05   WS-MES-SAL  PIC 99.

      **************************************************************
      *  VARIABLES QUE IDENTIFICA LA OFICINA PROPIETARIA DE LA CTA
      **************************************************************
       01  WS-COD-SUC-PROPIE       PIC X(4)        VALUE SPACES.
       01  WS-COD-SUC-PROPIE-ANT   PIC X(4)        VALUE SPACES.
       01  WS-COD-CENTRO-ORI       PIC S9(4)V USAGE COMP-3.


      **************************************************************
      *  VARIABLES DE TRABAJO DE TOTALES POR OFICINA
      **************************************************************
       01  WS-TOT-IMP-PROTESTO      PIC 9(15)V99     VALUE ZEROS.
       01  WS-TOT-IMP-MULTA         PIC 9(15)V99     VALUE ZEROS.
       01  WS-TOT-IMP-MULTA-COBRADA PIC 9(15)V99     VALUE ZEROS.
       01  WS-TOT-SALDO             PIC 9(15)V99     VALUE ZEROS.


      **************************************************************
      *  VARIABLES DE TRABAJO DE TOTALES GLOBALES
      **************************************************************
       01  WS-GLO-IMP-MULTA         PIC 9(15)V99     VALUE ZEROS.
       01  WS-GLO-IMP-MULTA-COBRADA PIC 9(15)V99     VALUE ZEROS.
       01  WS-GLO-SALDO             PIC 9(15)V99     VALUE ZEROS.

      **************************************************************
      *  VARIABLES QUE IDENTIFICAN A LOS CLIENTES
      **************************************************************
       01  WS-NUM-CTA-INT-ANT          PIC S9(8)V     VALUE ZEROS.
       01  WS-NUM-CTA-INT-AUX          PIC  9(9)      VALUE ZEROS.
      *01  WS-CUENTA                   PIC  9(9)      VALUE ZEROS.

       01  WS-NUM-CTA-INT-S.
           05  WS-NUM-CTA-INT-SN       PIC 9(7)       VALUE ZEROS.
           05  WS-NUM-CTA-INT-SD       PIC 9(1)       VALUE ZEROS.

       01  WS-CODIGO-REGISTRO.
           05  WS-COD-PAIS             PIC X(4)       VALUE SPACES.
           05  WS-COD-PROVINCIA        PIC X(11)      VALUE SPACES.

       01  WS-VALO-1      PIC 9(10)V99         VALUE ZEROS.
       01  WS-VALO-1-R REDEFINES WS-VALO-1.
           02 WS-VALO-1E  PIC 9(10).
           02 WS-VALO-1D  PIC 9(02).

       01  WS-CEDULA      PIC X(14)            VALUE SPACES.
       01  FILLER      REDEFINES WS-CEDULA.
           02 FILLER      PIC X(01).
           02 WS-CEDULAD  PIC X(13).

       01  WS-CUENTA-N    PIC 9(10).
       01  WS-CUENTA-R REDEFINES WS-CUENTA-N.
           02 WS-CUENTA   PIC 9(8).
           02 WS-TIP-EX   PIC 9(2).

      **************************************************************
      *  CONSTANTES DE LOS MESES DEL A#O
      **************************************************************
       01  WS-TABLA-MESES.
           02 FILLER          PIC XXX VALUE 'ENE'.
           02 FILLER          PIC XXX VALUE 'FEB'.
           02 FILLER          PIC XXX VALUE 'MAR'.
           02 FILLER          PIC XXX VALUE 'ABR'.
           02 FILLER          PIC XXX VALUE 'MAY'.
           02 FILLER          PIC XXX VALUE 'JUN'.
           02 FILLER          PIC XXX VALUE 'JUL'.
           02 FILLER          PIC XXX VALUE 'AGO'.
           02 FILLER          PIC XXX VALUE 'SEP'.
           02 FILLER          PIC XXX VALUE 'OCT'.
           02 FILLER          PIC XXX VALUE 'NOV'.
           02 FILLER          PIC XXX VALUE 'DIC'.
       01  WS-TABLA-MESES-R   REDEFINES WS-TABLA-MESES.
           02 WS-MES          PIC X(03) OCCURS 12 TIMES.


      ****************************************************************
      **                CONSTANTES ALFANUMERICAS                    **
      ****************************************************************
       01  LT-NUMERICOS.
           05 LTN-1                        PIC 9(01) VALUE 1.
           05 LTN-2                        PIC 9(01) VALUE 2.
           05 LT-N-4                       PIC 9(2) VALUE 4.
           05 LTN-MAX-8                    PIC 9(01) VALUE 8.
           05 LTN-53                       PIC 9(02) VALUE 53.
           05 LTN-ERROR                    PIC 99    VALUE 16.
           05 LTN-407                      PIC 999   VALUE 407.


       01  LT-ALFANUMERICOS.
           05 LTA-C                        PIC X(01) VALUE 'C'.
           05 LTA-E                        PIC X(01) VALUE 'E'.
           05 LTA-F                        PIC X(01) VALUE 'F'.
           05 LTA-CURSOR                   PIC X(10) VALUE 'CURSOR'.
           05 LTA-CSR2                     PIC X(10) VALUE 'CURSOR2'.
           05 LTA-NOMBRE-PRG               PIC X(10) VALUE 'CTB3004'.
           05 LTA-T08CT093                 PIC X(10) VALUE 'T08CT093'.
           05 LTA-GXINIBAT                 PIC X(10) VALUE 'GXINIBAT'.
           05 LTA-PARRAFA1100              PIC X(30) VALUE
                            'A1100-INICIALIZAR-ENTORNO'.
           05 LTA-ERROR-CODIGO             PIC X(18) VALUE
                            'COD.DOC.OFI.ERRADO'.
           05 LTA-ERROR-EST-CTA            PIC X(18) VALUE
                            'EST. CUENTA ERRADO'.
           05 LTA-ERR-COD-DESAU            PIC X(18) VALUE
                            'COD.DESAUT. ERRADO'.
           05 LTA-ERROR                    PIC X(10) VALUE 'HAY ERROR.'.
           05 LT-A-PARRAFO1200             PIC X(30) VALUE
                            'A1200-OBTENER-DESC-EMPRESA'.
           05 LT-A-ERROR-EMPRESA       PIC X(48) VALUE
                            'ERROR AL OBTENER DESCRIPCION EMPRESA'.
           05 LTA-NO-HAY-REG-T08CT093      PIC X(30) VALUE
                            'NO HAY REGISTROS EN T08CT093'.



      ****************************************************************
      *                       CURSORES                               *
      ****************************************************************
           EXEC SQL DECLARE CUR-SOR1 CURSOR FOR

              SELECT
                       NUM_CHEQUE,
                       NUM_CTA_INT,
                       IMP_CHEQUE,
                       IMP_PROTESTO,
                       COD_TIP_EXPE,
                       COD_EMPRESA,
                       IMP_MULTA,
                       IMP_MULTA_COBRADA,
                       IND_ESTADO_CTA,
                       TIMESTAMP_ALTA,
                       COD_SUC_PROPIE
              FROM     T08CT093
              WHERE  IND_ESTADO_CTA <> 'A' AND
              (TIMESTAMP_ALTA BETWEEN :WS-FECHA-TABLA-IF AND
                                      :WS-FECHA-TABLA-FF)
              ORDER BY COD_SUC_PROPIE, NUM_CTA_INT
           END-EXEC.


       01  SALIDA.
           05  DSUP-NUMF  PIC 9(03).
           05  DSUP-CODB  PIC 9(08).
           05  DSUP-AAMM  PIC 9(06).
           05  DSUP-QUIN  PIC 9(01).
           05  DSUP-NOMB  PIC X(50).
           05  SUPB-IDEN                    PIC X.
           05  SUPB-COD-ID                  PIC X(13).
           05  DSUP-CIUD  PIC X(15).
           05  DSUP-DIRE  PIC X(35).
           05  SUPB-CTA                     PIC 9(10).
           05  SUPB-CHEQUE                  PIC 9(06).
           05  SUPB-VALCH                   PIC 9(07).
           05  DSUP-PUN1  PIC X(01).
           05  DSUP-DEVA  PIC 9(02).
           05  DSUP-DIAP  PIC 9(02).
           05  DSUP-MUL5  PIC 9(06).
           05  DSUP-PUN2  PIC X(01).
           05  DSUP-MUD5  PIC 9(02).
           05  DSUP-VALC  PIC 9(06).
           05  DSUP-PUN3  PIC X(01).
           05  DSUP-VADC  PIC 9(02).
           05  DSUP-VAPC  PIC 9(06).
           05  DSUP-PUN4  PIC X(01).
           05  DSUP-VDPC  PIC 9(02).
           05  DSUP-ANOS  PIC 9(01).
           05  DSUP-INDI  PIC X(02).

      *---------------------------------------------------------------
      * DESCRIPCION  DE  CABECERA.                                   *
      *---------------------------------------------------------------

       01  CAB-1.
           05 FILLER            PIC X(26)    VALUE
                                'BANCO DEL PICHINCHA - 0010'.
           05 FILLER            PIC X(25)    VALUE SPACES.
           05 FILLER            PIC X(30)    VALUE
                                '* SUPERINTENDENCIA DE BANCOS *'.
      *    05 FILLER            PIC X(106)    VALUE SPACES.

       01  CAB-2.
           05 FILLER            PIC X(35)    VALUE
                                'DIRECCION GENERAL DE ESTADISTICA   '.
           05 FILLER            PIC X(31)    VALUE
                                'INFORME DE CHEQUES PROTESTADOS '.
           05 FILLER            PIC X(35)    VALUE
                                'POR FALTA O INSUFICIENCIA DE FONDOS'.
           05 FILLER            PIC X(12)    VALUE SPACES.
           05 FILLER            PIC X(19)    VALUE
                                'PROGRAMA    CTB3004'.


       01  CAB-3.
           05 FILLER            PIC X(21)    VALUE
                                'Y ESTUDIOS ECONOMICOS'.
           05 FILLER            PIC X(14)    VALUE SPACES.
           05 FILLER            PIC X(07)    VALUE 'DOLARES'.
           05 FILLER            PIC X(71)    VALUE SPACES.
           05 FILLER            PIC X(9)     VALUE 'PAGINA.'.
           05 PAGINA            PIC ZZZZZZ.ZZ9.


       01  CAB-4.
           05  FILLER PIC X VALUE ' '.
           05  FILLER           PIC X(132)   VALUE SPACES.


       01  CAB-5.
           05 FILLER            PIC X(09)    VALUE 'CODIGO:  '.
           05 ENTIDAD-N         PIC ZZZZ9999.
           05 FILLER            PIC X(1)     VALUE ' '.
           05 ENTIDAD-A         PIC X(20)    VALUE SPACES.
           05 FILLER            PIC X(01)    VALUE SPACES.
           05 FILLER            PIC X(9)     VALUE 'OFICINA:'.
           05 CENTRO-A          PIC X(18)    VALUE SPACES.
           05 FILLER            PIC X(11)    VALUE 'PROVINCIA: '.
           05 PROVINCIA-A       PIC X(18)    VALUE SPACES.
           05 FILLER            PIC X(04)    VALUE SPACES.
           05 FILLER            PIC X(13)    VALUE 'QUINCENA DEL'.
           05 QUI-1-SAL         PIC 99.
           05 FILLER            PIC X(4)     VALUE ' AL '.
           05 QUI-2-SAL         PIC 99.
           05 FILLER            PIC X(4)     VALUE ' DE '.
           05 MES-SAL           PIC XXX.
           05 FILLER            PIC X        VALUE ' '.
           05 ANO-SAL           PIC 9999.

       01  CAB-52.
           05 FILLER            PIC X(09)    VALUE 'CODIGO:  '.
           05 ENTIDAD-N-2       PIC ZZZZ9999.
           05 FILLER            PIC X(1)     VALUE ' '.
           05 ENTIDAD-A-2       PIC X(20)    VALUE SPACES.
           05 FILLER            PIC X(01)    VALUE SPACES.
           05 FILLER            PIC X(9)     VALUE 'OFICINA:'.
           05 CENTRO-A-2        PIC X(18)    VALUE SPACES.
           05 FILLER            PIC X(11)    VALUE 'PROVINCIA: '.
           05 PROVINCIA-A-2     PIC X(18)    VALUE SPACES.
           05 FILLER            PIC X(07)    VALUE SPACES.
      *    MMMMMMMMMMMMM
           05 FILLER            PIC X(04)    VALUE 'DEL '.
           05 QUI-1-SAL-I       PIC 99.
           05 FILLER            PIC X(1)     VALUE '/'.
           05 MES-SAL-I         PIC XXX.
           05 FILLER            PIC X(1)     VALUE '/'.
           05 ANO-SAL-I         PIC 9999.
           05 FILLER            PIC X(4)     VALUE ' AL '.
           05 QUI-2-SAL-F       PIC 99.
           05 FILLER            PIC X(1)     VALUE '/'.
           05 MES-SAL-F         PIC XXX.
           05 FILLER            PIC X(1)     VALUE '/'.
           05 ANO-SAL-F         PIC 9999.

       01  CAB-6.
           05 FILLER            PIC X(132)        VALUE ALL '-'.

       01  CAB-7.
           05  FILLER PIC X VALUE ' '.
           05  FILLER PIC X(44) VALUE '          N O M B R E S'.
           05  FILLER PIC X(24) VALUE '  CEDULA/R.U.C.  CIUDAD'.
           05  FILLER PIC X(05) VALUE SPACES.
           05  FILLER PIC X(58) VALUE '             DIRECCION'.

       01  CAB-8.
           05  FILLER PIC X     VALUE ' '.
           05  FILLER PIC X(28) VALUE SPACES.
           05  FILLER PIC X(16) VALUE 'VALOR DEL'.
           05  FILLER PIC X(13) VALUE 'VALOR DEL'.
           05  FILLER PIC X(21) VALUE 'FECHA DEL'.
           05  FILLER PIC X(05) VALUE SPACES.
           05  FILLER PIC X(41) VALUE ' M   U   L   T   A   S'.
           05  FILLER PIC X(7)  VALUE 'CIERRE'.

       01  CAB-9.
           05  FILLER PIC X VALUE ' '.
           05  FILLER PIC X(12) VALUE SPACES.
           05  FILLER PIC X(18) VALUE 'CHEQUE'.
           05  FILLER PIC X(15) VALUE 'CHEQUE'.
           05  FILLER PIC X(13) VALUE 'PROTESTO'.
           05  FILLER PIC X(13) VALUE 'PROTESTO'.
           05  FILLER PIC X(05) VALUE SPACES.
           05  FILLER PIC X(25) VALUE ' "A" 10%    "B" COBRADO '.
           05  FILLER PIC X(25) VALUE ' "C"  SALDO    CUENTA   '.
           05  FILLER PIC X(5)  VALUE '1/3'.


       01  DETALLE-NOM.
           05  FILLER            PIC X(1)       VALUE SPACES.
           05  CLIENT-ED         PIC X(45).
      *    05  CEDULA-ED         PIC ZZZZZ9999999999.
           05  CEDULA-ED         PIC X(15).
           05  FILLER            PIC X    VALUE SPACES.
           05  DET-CIU           PIC X(13)  VALUE SPACES.
           05  FILLER            PIC X(04)  VALUE SPACES.
           05  DIREC-ED-1        PIC X(35)  VALUE SPACES.
           05  DIREC-ED-2        PIC X(18)  VALUE SPACES.


       01  DETALLE-CHE.
           05  FILLER            PIC X(13)  VALUE SPACES.
           05  CHEQUE-ED         PIC 9(6).
           05  FILLER            PIC X(5)   VALUE SPACES.
           05  VALORC-ED         PIC ZZZ.ZZZ.ZZ9,99.
           05  FILLER            PIC XX     VALUE SPACES.
           05  VALORP-ED         PIC ZZZ.ZZZ.ZZ9,99.
           05  FILLER            PIC XXXX   VALUE SPACES.
           05  ANO-ED            PIC 9999.
           05  FILLER            PIC X      VALUE '/'.
           05  MES-ED            PIC XXX.
           05  FILLER            PIC X      VALUE '/'.
           05  DIA-ED            PIC 99.
           05  FILLER            PIC X(03)  VALUE SPACES.
           05  CINCO-ED          PIC ZZZZZ.ZZ9,99B.
           05  FILLER            PIC X(02)  VALUE SPACES.
           05  MULTA-ED          PIC ZZZZZ.ZZ9,99B.
           05  SALDO-ED          PIC ZZZZZ.ZZ9,99.
           05  CUENTA-ED1        PIC ZZ9(10).
      *    05  GUIONE            PIC X VALUE '-'.
      *    05  CUENTA-ED2        PIC 9.
           05  FILLER            PIC X      VALUE SPACES.
           05  IZQUIE-ED         PIC X      VALUE SPACES.
           05  CIERRE-ED         PIC Z.
           05  DERECH-ED         PIC X      VALUE SPACES.
           05  FILLER            PIC X      VALUE SPACES.
           05  CIERRE-EDA        PIC X(3)   VALUE SPACES.


       01  DETALLE-TOT.
           05  FILLER            PIC X(32)  VALUE SPACES.
           05  PASAN-ED          PIC X(8)   VALUE SPACES.
           05  TOT-PRO           PIC ZZZ.ZZZ.ZZ9,99.
           05  FILLER            PIC X(17)  VALUE SPACES.
           05  TOT-UNO           PIC ZZZ.ZZZ.ZZ9,99.
           05  FILLER            PIC XXX    VALUE SPACES.
           05  TOT-DOS           PIC ZZZZZ.ZZ9,99.
           05  FILLER            PIC X      VALUE SPACES.
           05  TOT-TRE           PIC ZZZZZ.ZZ9,99.
           05  FILLER            PIC X(19)  VALUE SPACES.

       01  DETALLE-GLO-1.
      *    05  FILLER PIC X VALUE '1'.
           05  FILLER PIC X VALUE ' '.
           05  FILLER PIC X(35) VALUE SPACES.
           05  FILLER PIC X(51) VALUE
               'TOTAL GENERAL MULTAS COBRADAS POR CHQS. PROTESTADOS'.
           05  FILLER PIC X(45) VALUE SPACES.

       01  DETALLE-GLO-2.
           05  FILLER PIC X VALUE ' '.
           05  FILLER PIC X(131) VALUE ALL ' '.

       01  DETALLE-GLO-3.
           05  FILLER PIC X(42) VALUE SPACES.
           05  FILLER PIC X(26) VALUE 'TOTAL "A" 10%'.
           05  TOTA-1 PIC ZZ.ZZZ.ZZZ.ZZZ,99.
           05  FILLER PIC X(47) VALUE SPACES.

       01  DETALLE-GLO-4.
           05  FILLER PIC X(42) VALUE SPACES.
           05  FILLER PIC X(26) VALUE 'TOTAL "B" COBRADO'.
           05  TOTA-2 PIC ZZ.ZZZ.ZZZ.ZZZ,99.
           05  FILLER PIC X(47) VALUE SPACES.

       01  DETALLE-GLO-5.
           05  FILLER PIC X(42) VALUE SPACES.
           05  FILLER PIC X(26) VALUE 'TOTAL "C" SALDO'.
           05  TOTA-3 PIC ZZ.ZZZ.ZZZ.ZZZ,99.
           05  FILLER PIC X(47) VALUE SPACES.


      ****************************************************************
      *          VARIABLES PARA PASO DE CAMPOS A MACRO DE ERROR      *
      ****************************************************************

       01  AREA-ERROR.
         05 CLV-GENERAL                          PIC X(20)
                 VALUE SPACES.
         05 NOM-PROGRAMA                         PIC X(8)
                 VALUE SPACES.
         05 NOM-PARRAFO                          PIC X(30)
                 VALUE SPACES.
         05 NOM-TABLA                            PIC X(10)
                 VALUE SPACES.
         05 DEL-INCID                            PIC X(30)
                 VALUE SPACES.
         05 COD-EMPRESA                          PIC X(4)
                 VALUE SPACES.
         05 FEM-OPERACION                        PIC X(10)
                 VALUE SPACES.

       01  MENSAJES-ERROR.
           05  MENSAJE-ERROR.
               10  FILLER                  PIC X(9)
                                   VALUE 'ERROR EN '.
               10  ERR-RECURSO             PIC X(9).
               10  ERR-NOMBRE              PIC X(8).
               10  FILLER                  PIC X(6)
                                   VALUE ' AL-> '.
               10  ERR-ACCION              PIC X(6).

      *---- VARIABLE PARA FORMATEAR EL ERROR

       01  AREA-INFORMACION.
           05  WS-PARRAFO         PIC X(30) VALUE SPACES.
           05  WS-TEXTO1          PIC X(50) VALUE SPACES.



      **********************************************
      *                                            *
      * COPY DE ERRORES.                           *
      *                                            *
      **********************************************

       COPY CT0009P.

       COPY EP0015P.


      ****************************************************************
      *                        SWITCHES                              *
      ****************************************************************
       01  WS-SWITCHES.
           05 SW-ERROR                      PIC X         VALUE '0'.
              88 HAY-ERROR                                VALUE '1'.
              88 NO-HAY-ERROR                             VALUE '0'.

           05 SW-FIN-CURSOR                 PIC X         VALUE 'N'.
              88 NO-FIN-CURSOR                            VALUE 'N'.
              88 FIN-CURSOR                               VALUE 'S'.

           05 SW-FIN-CURSOR2                PIC X         VALUE 'N'.
              88 NO-FIN-CURSOR2                           VALUE 'N'.
              88 FIN-CURSOR2                              VALUE 'S'.

           05  SW-PRIMER-REGISTRO           PIC X         VALUE 'S'.
              88 NO-ES-PRIMER-REGISTRO                    VALUE 'N'.
              88 PRIMER-REGISTRO                          VALUE 'S'.

           05  SW-FIN-FICCON                PIC X         VALUE 'N'.
               88 FIN-FICCON                              VALUE 'S'.
               88 NO-FIN-FICCON                           VALUE 'N'.

      *****************************************************************
      *         A R E A S   D E   E N T R A D A / S A L I D A         *
      *****************************************************************
       LINKAGE SECTION.

      *****************************************************************
      *            P R O C E D U R E    D I V I S I O N               *
      *****************************************************************
       PROCEDURE DIVISION.

      **INICIO-PROGRAMA-CTB3004

           PERFORM    A1000-INICIO.
           PERFORM    A2000-PROCESO UNTIL FIN-CURSOR.
           PERFORM    A4000-TOTALES-OFICINA.
           PERFORM    A6000-TOTALES-GLOBALES.
           PERFORM    A8000-FINAL.

      **FINAL-PROGRAMA-CTB3004

           GOBACK.

      *****************************************************************
      *******************        I N I C I O         ******************
      *****************************************************************
      ********************
       A1000-INICIO.
      ********************

           INITIALIZE RETURN-CODE

           PERFORM A1100-INICIALIZAR-ENTORNO.

           OPEN  INPUT   FICCON

           IF WS-ESTADO   NOT = 00   AND   NOT =  97
              DISPLAY 'ERROR AL ABRIR FICCON01: ' WS-ESTADO
              MOVE 12 TO RETURN-CODE
              PERFORM A8000-FINAL
           END-IF.

           PERFORM A1200-LEER-FICCON.

           PERFORM A1210-INICIALIZAR-FECHAS.

           OPEN OUTPUT CTDSUPB.

           IF WS-STATUS  NOT =  ZEROS
              MOVE 'FICHERO'  TO ERR-RECURSO
              MOVE 'FCTCORSD' TO ERR-NOMBRE
              MOVE 'OPEN'     TO ERR-ACCION
             @ERROR(FATAL,WS-STATUS,MENSAJE-ERROR)
           END-IF.

           OPEN OUTPUT IMPRES01.

           IF WS-FS01 NOT EQUAL ZEROS
              MOVE 'REPORTE'  TO ERR-RECURSO
              MOVE 'IMPRES01' TO ERR-NOMBRE
              MOVE 'OPEN'     TO ERR-ACCION
             @ERROR(FATAL,WS-FS01,MENSAJE-ERROR)
           END-IF.

           PERFORM A1200-OBTENER-DESC-EMPRESA.


       A1200-LEER-FICCON.
      *--------------------------------------------------
      * SE LEE EL FICHERO DE CONTROL QUE CONTIENE EL CDIGO (F)
      * Y LA FECHA INGRESADAS POR EL USUARIO.
      *--------------------------------------------------

           READ FICCON    INTO FICCON-REG
             AT END
              SET FIN-FICCON   TO TRUE

            NOT AT END
             IF WS-ESTADO   NOT = 00
                DISPLAY 'ERROR AL LEER  FICCON01: ' WS-ESTADO
                MOVE 12 TO RETURN-CODE
                PERFORM A8000-FINAL

              ELSE
                 DISPLAY 'FECHAS LEIDAS DE FICCON01: '
                 FIC-COD-FECHA ' ' FIC-FECHA-INI ' ' FIC-FECHA-FIN

                 MOVE FIC-COD-FECHA TO W-COD-VAL


                 IF FIC-COD-FECHA  = LTA-F
                    INITIALIZE EP0015P

                    MOVE FIC-FECHA-INI(1:2) TO W-DD-VAL   WS-DIA-I
                    MOVE FIC-FECHA-INI(4:2) TO W-MM-VAL   WS-MES-I
                    MOVE FIC-FECHA-INI(7:4) TO W-AAAA-VAL WS-ANIO-I
                    MOVE W-FEC-VAL          TO FEM-INICIO OF EP0015P

                    PERFORM A1200-VALIDA-FECHAS

                    MOVE FIC-FECHA-FIN(1:2) TO W-DD-VAL   WS-DIA-F
                    MOVE FIC-FECHA-FIN(4:2) TO W-MM-VAL   WS-MES-F
                    MOVE FIC-FECHA-FIN(7:4) TO W-AAAA-VAL WS-ANIO-F
                    MOVE W-FEC-VAL          TO FEM-INICIO OF EP0015P

                    PERFORM A1200-VALIDA-FECHAS

                  ELSE
                      PERFORM A6100-CAL-FECHAS
                 END-IF

                 MOVE WS-FECHA-INICIAL(7:4) TO WS-AAMM(1:4)
                 MOVE WS-FECHA-INICIAL(4:2) TO WS-AAMM(5:2)
                 MOVE WS-AAMM     TO DSUP-AAMM

                 IF   WS-FECHA-INICIAL(1:2) = '01'
                    MOVE 1 TO DSUP-QUIN
                 ELSE
                    MOVE 2 TO DSUP-QUIN
                 END-IF

                 MOVE WS-FECHA-INICIAL(1:2)
                   TO QUI-1-SAL
                      QUI-1-SAL-I

                 MOVE WS-FECHA-FINAL  (1:2)
                   TO QUI-2-SAL
                      QUI-2-SAL-F

                 MOVE WS-FECHA-INICIAL(4:2)
                   TO WS-MESX

                 MOVE WS-MES (WS-MESX)
                   TO MES-SAL
                      MES-SAL-F
                      MES-SAL-I

                 MOVE WS-FECHA-INICIAL(7:4)
                   TO ANO-SAL
                      ANO-SAL-I
                      ANO-SAL-F
             END-IF

           END-READ.


       A1200-VALIDA-FECHAS.
      ****************************************************************
      * -> VALIDA LAS FECHAS DESDE HASTA                             *
      ****************************************************************

             SET        NATURAL  OF EP0015P        TO TRUE.
             MOVE LT-A-VALIDAR
               TO IND-OPERACION  OF EP0015P.

             CALL LT-A-EPR0015  USING PAR-DUMMY PAR-DUMMY  EP0015P.

             IF NUM-RESPUESTA OF EP0015P NOT = ZEROS
               MOVE SPACES               TO CLV-GENERAL    OF AREA-ERROR
               MOVE 'CTB3004'            TO NOM-PROGRAMA   OF AREA-ERROR
               MOVE 'EPR0015'            TO NOM-TABLA      OF AREA-ERROR
               MOVE 'A1200'
                 TO NOM-PARRAFO    OF AREA-ERROR
               MOVE 'FECHA NO VALIDA'
                                         TO DEL-INCID      OF AREA-ERROR
               MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                  TO COD-EMPRESA    OF AREA-ERROR
               MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
                 TO FEM-OPERACION  OF AREA-ERROR
               DISPLAY 'NUM-RESP   ' NUM-RESPUESTA OF EP0015P
               DISPLAY 'AREA-ERROR ' AREA-ERROR
               @LOGERR(ERROR,,AREA-ERROR)
               SET HAY-ERROR                       TO TRUE
             END-IF.


       A1100-INICIALIZAR-ENTORNO.
      ****************************************************************
      * -> INICIALIZACION AUTOMATICA DE BATCH                        *
      ****************************************************************

           @INIBAT()

           IF TIPO-ERROR OF S21-AREA-ERROR > LT-RET-AVISO
              MOVE SPACES               TO CLV-GENERAL    OF AREA-ERROR
              MOVE LTA-NOMBRE-PRG       TO NOM-PROGRAMA   OF AREA-ERROR
              MOVE LTA-GXINIBAT         TO NOM-TABLA      OF AREA-ERROR
              MOVE LTA-PARRAFA1100      TO NOM-PARRAFO    OF AREA-ERROR
              MOVE 'ERROR AL INICIAR ENTORNO     '
                                        TO DEL-INCID      OF AREA-ERROR
              MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                 TO COD-EMPRESA    OF AREA-ERROR
              MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
               TO FEM-OPERACION  OF AREA-ERROR
              DISPLAY 'TIPO-ERROR ' TIPO-ERROR OF S21-AREA-ERROR
              DISPLAY AREA-ERROR
              @ERROR(ERROR,TIPO-ERROR OF S21-AREA-ERROR,AREA-ERROR)
     **       SET HAY-ERROR                       TO TRUE
     **       PERFORM  A8000-FINAL
           END-IF.

           @DEFINE(NO-ERROSQL).

           @CTRLERR(APLICACION).


       A1210-INICIALIZAR-FECHAS.
      *****************************************************************
      * -> ABRIMOS Y HACEMOS PRIMERA LECTURA DEL CURSOR               *
      * -> PROCESAMOS DATOS                                           *
      * -> SE REAlIZA LA IMPRESION                                    *
      *****************************************************************

           PERFORM A2250-FECHA-TABLA.

           DISPLAY 'FECHA INICIAL T ' WS-FECHA-TABLA-IF
           DISPLAY 'FECHA FINAL   T ' WS-FECHA-TABLA-FF

           PERFORM IO1100-OPEN-CURSOR.

           PERFORM IO1200-FETCH-CURSOR.
           PERFORM A2620-CUENTA-VIEJA.

           SET NO-ES-PRIMER-REGISTRO TO TRUE

           MOVE COD-SUC-PROPIE OF T08CT093 TO
                WS-COD-SUC-PROPIE-ANT

           MOVE 13            TO    WK-CONVER
           MOVE WK-CONVER-2   TO    WK-INDI-1
           MOVE 10            TO    WK-CONVER
           MOVE WK-CONVER-2   TO    WK-INDI-2

           MOVE WK-INDI       TO DSUP-INDI

           PERFORM A1200-CODIGO-OFICINA

           MOVE ZEROS TO     WS-NUM-CTA-INT-ANT.


       A1200-CODIGO-OFICINA.
      *****************************************************************
      * -> INVOCAMOS A LA TABLA T37OBS11   PARA OBTENER, EL CODIGO    *
      * -> DE OFICINA DEFINIDO POR LA SIB                             *
      *****************************************************************

            MOVE COD-EMPRESA OF S21-AREA-ENTORNO
              TO WS-COD-EMPRESA

            MOVE COD-SUC-PROPIE OF T08CT093
              TO WS-COD-CENTRO-ORI

            EXEC SQL

                 SELECT COD_SUPER_PRT

                 INTO   :T37OBS11.COD-SUPER-PRT

                 FROM   T37OBS11

                 WHERE  COD_CENTRO_ORI =:WS-COD-CENTRO-ORI
                  AND   COD_EMPRESA    =:WS-COD-EMPRESA
                  AND   COD_REGISTRO   = 4

            END-EXEC.

            MOVE     SQLSTATE TO SQLSTATE-SIGLO.

            EVALUATE TRUE

               WHEN IND-SQL-CORRECTO
                    MOVE COD-SUPER-PRT OF T37OBS11
                      TO DSUP-CODB

               WHEN IND-NO-ENCONTRADO
                    MOVE ZEROS
                      TO DSUP-CODB
                    MOVE SPACES TO CLV-GENERAL   OF AREA-ERROR
                    MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA  OF AREA-ERROR
                    MOVE SPACES          TO NOM-TABLA     OF AREA-ERROR
                    MOVE 'A1200-CODIGO-OFICINA'
                                         TO NOM-PARRAFO    OF AREA-ERROR
                    MOVE 'COD-SUC-PRO.INVALIDO'
                                         TO DEL-INCID   OF AREA-ERROR
                    DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
                    DISPLAY AREA-ERROR

               WHEN OTHER
                    MOVE SPACES          TO CLV-GENERAL   OF AREA-ERROR
                    MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA  OF AREA-ERROR
                    MOVE LTA-CURSOR      TO NOM-TABLA     OF AREA-ERROR
                    MOVE 'A1200-CODIGO-OFICINA'
                                         TO NOM-PARRAFO    OF AREA-ERROR
                    MOVE 'ERROR DE DB2.'
                                         TO DEL-INCID   OF AREA-ERROR
                    DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
                    DISPLAY AREA-ERROR
                    SET HAY-ERROR              TO TRUE
                    PERFORM  A8000-FINAL

            END-EVALUATE.


       A1200-OBTENER-DESC-EMPRESA.
      ************************************************************
      **  A1200-OBTENER-DESC-EMPRESA
      ** OBTIENE LA DESCRIPCION DE LA EMPRESA DESDE ENTORNO.
      *************************************************************

           MOVE 'V'
           TO ACC-SERV                 OF MSG-IN-TCS05002.

           MOVE '0'
           TO IND-TIPO-LIS             OF MSG-IN-TCS05002.

           MOVE 1
           TO NUM-CLAVE                OF MSG-IN-TCS05002.

           MOVE 1
           TO NUM-CONDICION-ADICIONAL  OF MSG-IN-TCS05002.

           MOVE COD-EMPRESA OF S21-AREA-ENTORNO
           TO COD-EMPRESA              OF MSG-IN-TCS05002.


           @INVOCAR(TCS05002,B)

           IF TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
              MOVE LT-A-PARRAFO1200 TO WS-PARRAFO
              MOVE LT-A-ERROR-EMPRESA TO WS-TEXTO1

             @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.

           MOVE NOMBRE OF TL-T06TC005(1) TO ENTIDAD-A.
      *    MOVE COD-EMPRESA OF S21-AREA-ENTORNO TO ENTIDAD-N.

      *****************************************************************
      *****************        P R O C E S O          *****************
      *****************************************************************
       A2000-PROCESO.
      ****************

      *---------------------------------------------------------------*
      * SE INICIALIZAN LOS CAMPOS PARA ADAPTARSE AL DISE#O DE L.ACOSTA*
      *---------------------------------------------------------------*

           MOVE ZEROS  TO  DSUP-NUMF
           MOVE '.'    TO  DSUP-PUN1
           MOVE ZEROS  TO  DSUP-DEVA
           MOVE ZEROS  TO  DSUP-DIAP
           MOVE ZEROS  TO  DSUP-MUL5
           MOVE '.'    TO  DSUP-PUN2
           MOVE ZEROS  TO  DSUP-MUD5
           MOVE ZEROS  TO  DSUP-VALC
           MOVE '.'    TO  DSUP-PUN3
           MOVE ZEROS  TO  DSUP-VADC
           MOVE ZEROS  TO  DSUP-VAPC
           MOVE '.'    TO  DSUP-PUN4
           MOVE ZEROS  TO  DSUP-VDPC
           MOVE ZEROS  TO  DSUP-ANOS

      *---------------------------------------------------------------*
      * SE MUEVEN LOS CAMPOS LEIDOS A SALIDA                          *
      *---------------------------------------------------------------*
           MOVE NUM-CHEQUE        OF T08CT093
             TO SUPB-CHEQUE       OF SALIDA.
           MOVE IMP-CHEQUE        OF T08CT093
             TO WS-VALO-1
           MOVE WS-VALO-1E
             TO SUPB-VALCH        OF SALIDA.

           MOVE WS-VALO-1D
             TO DSUP-DEVA         OF SALIDA

           MOVE IMP-MULTA-COBRADA OF T08CT093
             TO WS-VALO-1

           MOVE WS-VALO-1E
             TO DSUP-VALC         OF SALIDA.

           MOVE WS-VALO-1D
             TO DSUP-VADC         OF SALIDA

           MOVE IMP-MULTA         OF T08CT093
             TO WS-VALO-1

           MOVE WS-VALO-1E
             TO DSUP-MUL5         OF SALIDA.

           MOVE WS-VALO-1D
             TO DSUP-MUD5         OF SALIDA

           COMPUTE WS-SALDO = IMP-MULTA         OF T08CT093 -
                   IMP-MULTA-COBRADA OF T08CT093

           MOVE WS-SALDO
             TO WS-VALO-1

           MOVE WS-VALO-1E
             TO DSUP-VAPC         OF SALIDA.

           MOVE WS-VALO-1D
             TO DSUP-VDPC         OF SALIDA

           MOVE LTN-407
             TO DSUP-NUMF         OF SALIDA


           PERFORM A2300-FECHA-PROTESTO.


      *    PERFORM A2400-IND-EST-CUENTA.
      *    IF TIPO-ERROR OF S21-AREA-ERROR = 0
              PERFORM A2600-VALIDAC-INTERV
              IF TIPO-ERROR OF S21-AREA-ERROR = 0
      *          WS-COD-PERSONA NOT EQUAL ZEROS
                 PERFORM A2800-COD-DOC-OFICIAL
AGU>>            IF SUPB-IDEN <> ' '
                 IF TIPO-ERROR OF S21-AREA-ERROR = 0
      *             PERFORM A2900-UBICACION-CLIENTE
      *             IF TIPO-ERROR OF S21-AREA-ERROR = 0

      *******************************************************
      * GRABAMOS LOS CAMPOS DEL FICHERO CTDSUPB;            *
      * Y, SACAMOS EL RESPECTIVO REPORTE                    *
      *******************************************************
                       PERFORM IO1600-REPORTE-CTDSUPB
                       PERFORM IO1600-GRABAR-CTDSUPB
      *             END-IF
                 END-IF
AGU>>            END-IF                 
              END-IF.
      *    END-IF.

           PERFORM IO1200-FETCH-CURSOR.


       A2250-FECHA-TABLA.
      **********************
      ****************************************************************
      * TRASPASO DE LA FECHA PARA LA CONDICION DEL CURSOR
      ****************************************************************

           MOVE WS-DIA-I    OF WS-FECHA-INICIAL
             TO WS-DIA-TI   OF WS-FECHA-TABLA-I.

           MOVE WS-MES-I    OF WS-FECHA-INICIAL
             TO WS-MES-TI   OF WS-FECHA-TABLA-I.

           MOVE WS-ANIO-I   OF WS-FECHA-INICIAL
             TO WS-ANIO-TI  OF WS-FECHA-TABLA-I.

           MOVE WS-DIA-F    OF WS-FECHA-FINAL
             TO WS-DIA-TF   OF WS-FECHA-TABLA-F.

           MOVE WS-MES-F    OF WS-FECHA-FINAL
             TO WS-MES-TF   OF WS-FECHA-TABLA-F.

           MOVE WS-ANIO-F   OF WS-FECHA-FINAL
             TO WS-ANIO-TF  OF WS-FECHA-TABLA-F.

           MOVE WS-FECHA-TABLA-I
             TO WS-FECHA-TABLA-IF.

           MOVE WS-FECHA-TABLA-F
             TO WS-FECHA-TABLA-FF.


       A2300-FECHA-PROTESTO.
      **********************
      ****************************************************************
      * DE LA TABLA DE PROTESTOS DE SELECCIONA LA FECHA DEL PROTESTO*
      ****************************************************************

      *    EXEC SQL
      *     SELECT DATE (TIMESTAMP_ALTA)
      *     INTO :WS-FEC-PROTESTO
      *     FROM T08CT093
      *     WHERE  IND_ESTADO_CTA <> 'A' AND
      *            (TIMESTAMP_ALTA BETWEEN :WS-FECHA-TABLA-IF AND
      *                                    :WS-FECHA-TABLA-FF)
      *    END-EXEC.

           MOVE TIMESTAMP-ALTA OF T08CT093 TO
                WS-TIMESTAMP-ALTA
           MOVE WS-TIMES-PROTESTO TO WS-FEC-PROTESTO.



      **********************
      *A2400-IND-EST-CUENTA.
      **********************
      **************************************************************
      * -- Se invoca al servicio CTS60004, para que proporcione el *
      *    indicador del estado de la cuenta.                      *
      **************************************************************

      *    MOVE COD-TIP-EXPE    OF T08CT093
      *      TO COD-TIP-EXPE    OF MSG-IN-CTS60004

      *    MOVE NUM-CTA-INT     OF T08CT093
      *      TO NUM-CTA-INT     OF MSG-IN-CTS60004

      *    MOVE COD-EMPRESA     OF T08CT093
      *      TO COD-EMPRESA     OF MSG-IN-CTS60004


      *    @INVOCAR(CTS60004,B)

      *    IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
      *       MOVE 'A2400-IND-EST-CTA'
      *                            TO NOM-PARRAFO    OF AREA-ERROR
      *       MOVE 'ERROR INVOCAR CTS60004'
      *                            TO DEL-INCID      OF AREA-ERROR
      *       MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
      *          TO COD-EMPRESA    OF AREA-ERROR
      *       MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
      *        TO FEM-OPERACION  OF AREA-ERROR
      *       @ERROR(,,AREA-ERROR)
      *       SET HAY-ERROR                       TO TRUE
      *       PERFORM  A8000-FINAL

      *    END-IF.


       A2600-VALIDAC-INTERV.
      **********************
      ****************************************************************
      * -- Se invoca al servicio PES11001, el cual retornara el COD- *
      *    PERSONA, COD-EXT-DOC-CP, COD-TIPO-INTERVEN, NUM-ORDEN-IN  *
      *    TERV.  Se valida, si hay mas de un interviniente, se toma *
      *    los datos que tenga el numero menor en el campo NUM-ORDEN *
      *    -INTERV.                                                  *
      ****************************************************************

           MOVE COD-TIP-EXPE    OF T08CT093
             TO COD-TIP-EXPE    OF MSG-IN-PES11001.

           MOVE NUM-CTA-INT     OF T08CT093
             TO NUM-CTA-INT     OF MSG-IN-PES11001.

           MOVE COD-EMPRESA     OF T08CT093
             TO COD-EMPRESA     OF MSG-IN-PES11001.

           MOVE '0'  TO IND-TIPO-LIS    OF MSG-IN-PES11001.

           MOVE COD-IDIOMA OF S21-AREA-ENTORNO
             TO COD-IDIOMA        OF MSG-IN-PES11001.

           MOVE '01' TO COD-TIPO-INTERVEN OF MSG-IN-PES11001.

           @INVOCAR(PES11001,C)

           IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
              MOVE 'A2600-VALIDAC-INTERV'
                                   TO NOM-PARRAFO    OF AREA-ERROR
              MOVE 'ERROR INVOCAR PES11001'
                                   TO DEL-INCID      OF AREA-ERROR
              MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                TO  COD-EMPRESA    OF AREA-ERROR
              MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
                TO  FEM-OPERACION  OF AREA-ERROR
              DISPLAY 'TIPO-ERROR     ' TIPO-ERROR OF S21-AREA-ERROR
              DISPLAY 'AREA-ERROR     ' AREA-ERROR
              DISPLAY 'COD-TIP-EXPE   ' COD-TIP-EXPE    OF T08CT093
              DISPLAY 'NUM-CTA-INT    ' NUM-CTA-INT     OF T08CT093
              DISPLAY 'NUM-RESPUESTA ' NUM-RESPUESTA OF MSG-OUT-PES11001
              DISPLAY 'COD-PERSONA ' COD-PERSONA  OF MSG-OUT-PES11001(1)
              DISPLAY 'COD-EXT-D ' COD-EXT-DOC-CP OF MSG-OUT-PES11001(1)
              MOVE ZEROS  TO  WS-COD-PERSONA
              MOVE SPACES TO  WS-COD-EXT-DOC-CP
              @LOGERR(AVISO,TIPO-ERROR OF S21-AREA-ERROR,AREA-ERROR)
           ELSE
            IF NUM-RESPUESTA          OF MSG-OUT-PES11001 = 1
               MOVE COD-PERSONA       OF MSG-OUT-PES11001(1)
                 TO WS-COD-PERSONA
               MOVE IND-TIPO-PERSONA  OF MSG-OUT-PES11001(1)
                 TO WS-IND-TIPO-PERSONA
               MOVE COD-EXT-DOC-CP    OF MSG-OUT-PES11001(1)
                 TO WS-COD-EXT-DOC-CP
      *        MOVE COD-TIPO-INTERVEN TO MSG-OUT-PES11001(WS-IND)
      *          TO WS-COD-TIPO-INTERVEN
            ELSE
               PERFORM A2650-MENOR-NUM-INTERVENCIONES
               MOVE COD-PERSONA  OF MSG-OUT-PES11001(WS-IND-AUX)
                 TO WS-COD-PERSONA
               MOVE IND-TIPO-PERSONA  OF MSG-OUT-PES11001(WS-IND-AUX)
                 TO WS-IND-TIPO-PERSONA
               MOVE COD-EXT-DOC-CP OF MSG-OUT-PES11001(WS-IND-AUX)
                 TO WS-COD-EXT-DOC-CP
      *        MOVE COD-TIPO-INTERVEN TO MSG-OUT-PES11001(WS-IND-AUX)
      *          TO WS-COD-TIPO-INTERVEN
            END-IF
           END-IF.



       A2800-COD-DOC-OFICIAL.
      ***************************************************************
      * -- Se invoca al servico PES01003 para obtener el COD-DOC-   *
      *    OFICIAL, siendo 1 = cedula, 3 = pasaporte, 10 = RUC, 8 = *
      *    codigo asignado y cualquier otro codigo sera errado.     *
      ***************************************************************

      *    MOVE WS-COD-PERSONA
      *    MOVE WS-COD-EXT-DOC-CP
      *      TO SUPB-COD-ID       OF  SALIDA.

           MOVE WS-COD-EXT-DOC-CP
             TO WS-CEDULA

           MOVE WS-CEDULAD
             TO SUPB-COD-ID       OF  SALIDA.

           MOVE LTA-C
             TO TIP-MOVIM    OF MSG-IN-PES01003

            MOVE WS-COD-PERSONA
              TO COD-PERSONA    OF MSG-IN-PES01003


            @INVOCAR(PES01003,B)


             IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
                MOVE 'A2800-COD-DOC-OFICIA'
                                     TO NOM-PARRAFO    OF AREA-ERROR
                MOVE 'ERROR INVOCAR PES01003'
                                     TO DEL-INCID      OF AREA-ERROR
                MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                   TO COD-EMPRESA    OF AREA-ERROR
                MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
                   TO FEM-OPERACION  OF AREA-ERROR
                DISPLAY 'TIPO-ERROR  ' TIPO-ERROR OF S21-AREA-ERROR
                DISPLAY 'AREA-ERROR  ' AREA-ERROR
                DISPLAY 'COD-PERSONA ' WS-COD-PERSONA
                DISPLAY 'NOM-DENO ' NOM-DENOM-SOCIAL OF MSG-OUT-PES01003
                DISPLAY 'COD-DOC- ' COD-DOC-OFICIAL OF MSG-OUT-PES01003
                MOVE 'ERROR *** ' TO DSUP-NOMB OF SALIDA
                DISPLAY 'CTA-VIEJA ' CTA-VIEJA
                DISPLAY 'CTA-NUEVA ' CTA-NUEVA
                MOVE ZEROS  TO WS-OFICIAL
                               COD-DOC-OFICIAL OF MSG-OUT-PES01003
                MOVE SPACES TO SUPB-IDEN OF SALIDA
                @LOGERR(AVISO,TIPO-ERROR OF S21-AREA-ERROR,AREA-ERROR)

             ELSE
              MOVE NOM-DENOM-SOCIAL OF MSG-OUT-PES01003  TO
                   DSUP-NOMB        OF SALIDA


            MOVE COD-DOC-OFICIAL OF MSG-OUT-PES01003  TO WS-OFICIAL

            EVALUATE COD-DOC-OFICIAL OF MSG-OUT-PES01003

             WHEN  1
                MOVE 'C'
                  TO SUPB-IDEN           OF SALIDA
      *      WHEN  3
      *         MOVE 'P'
      *           TO SUPB-IDEN           OF SALIDA
             WHEN  10
                MOVE 'R'
                  TO SUPB-IDEN           OF SALIDA
             WHEN  8
                MOVE 'C'
                  TO SUPB-IDEN           OF SALIDA

             WHEN  3
                MOVE LTA-E
                  TO SUPB-IDEN           OF SALIDA
                PERFORM A3000-DATOS-PASAPORTE

             WHEN  OTHER

                   MOVE ' '
                     TO SUPB-IDEN           OF SALIDA
                     
AGU>> *            MOVE 'A2800-COD-DOC-OFICIA'
      *              TO NOM-PARRAFO    OF AREA-ERROR
      *            MOVE LTA-ERROR-CODIGO
      *              TO DEL-INCID      OF AREA-ERROR
      *            DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
      *            DISPLAY 'COD-DOC-OFICIAL '
      *                COD-DOC-OFICIAL OF MSG-OUT-PES01003
      *            DISPLAY 'AREA-ERROR ' AREA-ERROR
      *            @ERROR(ERROR,SQLSTATE-SIGLO,AREA-ERROR)

            END-EVALUATE

           END-IF.


       A2900-UBICACION-CLIENTE.
      ***********************
      ***************************************************************
      * -- SE ACCESA A LA T04DOM10 PARA OBTENER LA UBICACION        *
      *    DEL CLIENTE                                              *
      ***************************************************************

           PERFORM A2900-NUM-DIRECCION

           PERFORM A2900-DATOS-DIRECCION.


       A2900-NUM-DIRECCION.
      ***********************
      ***************************************************************
      * -- SE ACCESA PARA SELECCIONAR EL NUM-DIRECCION.             *
      ***************************************************************

            MOVE COD-EMPRESA OF S21-AREA-ENTORNO
              TO COD-EMPRESA OF MSG-IN-PES11003

            MOVE COD-TIP-EXPE    OF T08CT093
              TO COD-TIP-EXPE OF MSG-IN-PES11003

            MOVE NUM-CTA-INT OF T08CT093
              TO WS-NUM-CTA-XXX
                 NUM-CTA-INT  OF MSG-IN-PES11003

            MOVE WS-COD-PERSONA
              TO COD-PERSONA    OF MSG-IN-PES11003
                 WS-COD-PERSON

            MOVE '0'
              TO IND-TIPO-LIS   OF MSG-IN-PES11003

            MOVE 'V'
              TO IND-SITPRO     OF MSG-IN-PES11003

            MOVE 1
              TO COD-IDIOMA     OF MSG-IN-PES11003

            MOVE ZEROS
              TO IND-ACCESO OF MSG-IN-PES11003

            @INVOCAR(PES11003,B)

           IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
              MOVE ZEROS TO WS-NUM-DIRECCION
              MOVE 'A2900-NUM-DIRECCION    '
                                   TO NOM-PARRAFO    OF AREA-ERROR
              MOVE 'ERROR INVOCAR PES11003'
                                   TO DEL-INCID      OF AREA-ERROR
              MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                 TO COD-EMPRESA    OF AREA-ERROR
              MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
                 TO FEM-OPERACION  OF AREA-ERROR
              DISPLAY 'TIPO-ERROR ' TIPO-ERROR OF S21-AREA-ERROR
              DISPLAY  AREA-ERROR
      *       @ERROR(,,AREA-ERROR)
      *       SET HAY-ERROR                       TO TRUE
      *       PERFORM  A8000-FINAL
           ELSE
      *       DISPLAY 'NUM-DIRECCION '
      *                NUM-DIRECCION   OF MSG-OUT-PES11003(1)
      *          ' '   NUM-DIRECCION   OF MSG-OUT-PES11003(2)
      *          ' '   NUM-DIRECCION   OF MSG-OUT-PES11003(3)
      *          ' '   NUM-DIRECCION   OF MSG-OUT-PES11003(4)
      *          ' '   NUM-DIRECCION   OF MSG-OUT-PES11003(5)
      *          ' '   NUM-DIRECCION   OF MSG-OUT-PES11003(6)

              MOVE NUM-RESPUESTA OF MSG-OUT-PES11003 TO WS-NUM-FILAS
      *       DISPLAY 'NUM-RESPU '  WS-NUM-FILAS

              MOVE NUM-DIRECCION   OF MSG-OUT-PES11003(1)
                TO WS-NUM-DIRECCION
      *       DISPLAY 'NUM-DIRECCION ' WS-NUM-DIRECCION
           END-IF.


       A2900-DATOS-DIRECCION.
      ***********************
      ***************************************************************
      * -- SE ACCESA PARA SELECCIONAR LOS DATOS DE LA DIRECCION     *
      ***************************************************************
            INITIALIZE MSG-IN-PES10001

            IF WS-NUM-DIRECCION  EQUAL ZEROS
               MOVE 'D'
                 TO IND-TIPO-LIS   OF MSG-IN-PES10001
            END-IF

            MOVE WS-COD-PERSONA
              TO COD-PERSONA    OF MSG-IN-PES10001
                 WS-COD-PERSON

      *     display 'ws-direc ' ws-num-direccion
            MOVE WS-NUM-DIRECCION
              TO NUM-DIRECCION  OF MSG-IN-PES10001


            @INVOCAR(PES10001,C)

           IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
              MOVE SPACES   TO DSUP-CIUD
                               DET-CIU     OF    DETALLE-NOM
                               DSUP-DIRE
                               DIREC-ED-1  OF    DETALLE-NOM
              MOVE 'A2900-DATOS-DIRECCION  '
                                   TO NOM-PARRAFO    OF AREA-ERROR
              MOVE 'ERROR INVOCAR PES10001'
                                   TO DEL-INCID      OF AREA-ERROR
              MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                 TO COD-EMPRESA    OF AREA-ERROR
              MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
                 TO FEM-OPERACION  OF AREA-ERROR
              DISPLAY 'TIPO-ERROR ' TIPO-ERROR OF S21-AREA-ERROR
              DISPLAY  AREA-ERROR
      *       @ERROR(,,AREA-ERROR)
      *       SET HAY-ERROR                       TO TRUE
      *       PERFORM  A8000-FINAL
           ELSE
              MOVE NOM-POBLACION OF MSG-OUT-PES10001(1) TO DSUP-CIUD
                                    DET-CIU     OF    DETALLE-NOM
      *       DISPLAY 'COD-PERSON ' WS-COD-PERSON
      *       DISPLAY 'CIUDAD '     DET-CIU     OF    DETALLE-NOM
              MOVE NOM-VIA       OF MSG-OUT-PES10001(1) TO DSUP-DIRE
                                    DIREC-ED-1  OF    DETALLE-NOM
      *       DISPLAY 'DIRECCION '  DIREC-ED-1  OF    DETALLE-NOM
           END-IF.


       A3000-DATOS-PASAPORTE.
      ***********************
      * TIPO de persona 0 = fisica 1 = juridica
      ***********************

      *    DISPLAY 'TIPO PERSONA ' WS-IND-TIPO-PERSONA
           IF WS-IND-TIPO-PERSONA = '0'
              PERFORM A3010-T04CPE02
           ELSE
           IF WS-IND-TIPO-PERSONA = '1'
              MOVE WS-COD-PERSONA
                TO COD-PERSONA    OF T04CPE03
              MOVE COD-EMPRESA    OF T08CT093
                TO COD-EMPRESA    OF T04CPE03

              EXEC SQL
                 SELECT COD_DOC_OFICIAL    ,
                        COD_NUM_DOC_OFICIA
                 INTO   :T04CPE03.COD-DOC-OFICIAL
                            :IND-NULL-COD-OFICIAL,
                        :T04CPE03.COD-NUM-DOC-OFICIA
                           :IND-NULL-COD-OFICIA
                 FROM   T04CPE03

                 WHERE  COD_PERSONA =:T04CPE03.COD-PERSONA
                  AND   COD_EMPRESA =:T04CPE03.COD-EMPRESA

              END-EXEC

              MOVE     SQLSTATE TO SQLSTATE-SIGLO

              IF IND-SQL-CORRECTO
                 IF IND-NULL-COD-OFICIAL = -1
                    OR IND-NULL-COD-OFICIA = -1
                    CONTINUE
                 ELSE
                 IF COD-DOC-OFICIAL OF T04CPE03 = 14
                    AND IND-NULL-COD-OFICIA  NOT = -1
                        MOVE COD-NUM-DOC-OFICIA   OF T04CPE03
                          TO SUPB-COD-ID          OF  SALIDA
      *                 DISPLAY 'CEDULA    ' WS-CEDULA
      *                 DISPLAY 'PASAPORTE ' SUPB-COD-ID
                 END-IF
              END-IF
           END-IF.


       A3010-T04CPE02.
      **********************************************************
      *    DISPLAY ' COD-PERSONA ' WS-COD-PERSONA
      *    DISPLAY ' COD-EMRESA  ' COD-EMPRESA    OF T08CT093
           MOVE WS-COD-PERSONA
             TO COD-PERSONA    OF T04CPE02
           MOVE COD-EMPRESA    OF T08CT093
             TO COD-EMPRESA    OF T04CPE02
           EXEC SQL
                 SELECT COD_DOC_OFICIAL    ,
                        COD_NUM_DOC_OFICIA
                 INTO   :T04CPE02.COD-DOC-OFICIAL
                             :IND-NULL-COD-OFICIAL   ,
                        :T04CPE02.COD-NUM-DOC-OFICIA
                             :IND-NULL-COD-OFICIA
                 FROM   T04CPE02

                 WHERE  COD_PERSONA =:T04CPE02.COD-PERSONA
                  AND   COD_EMPRESA =:T04CPE02.COD-EMPRESA

            END-EXEC.

            MOVE     SQLSTATE TO SQLSTATE-SIGLO

           IF IND-SQL-CORRECTO
                 IF IND-NULL-COD-OFICIAL = -1
                    OR IND-NULL-COD-OFICIA = -1
                    CONTINUE
                 ELSE
              IF COD-DOC-OFICIAL OF T04CPE02 = 14
                 AND IND-NULL-COD-OFICIA NOT = -1
                     MOVE COD-NUM-DOC-OFICIA   OF T04CPE02
                       TO SUPB-COD-ID          OF  SALIDA
      *                   DISPLAY 'CEDULA    ' WS-CEDULA
      *                   DISPLAY 'PASAPORTE ' SUPB-COD-ID
                 END-IF
              END-IF
           END-IF.

      *****************************************************************
      **********************        F I N       ***********************
      *****************************************************************

      ***************
       A8000-FINAL.
      ***************
      *****************************************************************
      * -COMPROBAMOS SI EXISTE UN ERROR CONTROLADO                    *
      * -CERRAMOS FICHEROS                                            *
      *****************************************************************

           IF PRIMER-REGISTRO
              DISPLAY 'CODIGO SQLSTATE-SIGLO ' SQLSTATE-SIGLO
              DISPLAY AREA-ERROR
              STOP RUN
           END-IF.

           IF HAY-ERROR
              DISPLAY 'CODIGO SQLSTATE-SIGLO ' SQLSTATE-SIGLO
              DISPLAY AREA-ERROR
              MOVE 16  TO RETURN-CODE 
              STOP RUN
           END-IF.

           IF FIN-CURSOR
              EXEC SQL CLOSE CUR-SOR1 END-EXEC
           ELSE
              CONTINUE
           END-IF.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF NOT IND-SQL-CORRECTO
              DISPLAY 'FILE STATUS ' SQLSTATE-SIGLO
              MOVE 'CUR-SOR1'     TO ERR-RECURSO
              MOVE 'T08CT093'    TO ERR-NOMBRE
              MOVE 'CLOSE'       TO ERR-ACCION
              DISPLAY 'MENSAJE ' MENSAJE-ERROR
           END-IF.

           CLOSE   CTDSUPB

           IF HAY-ERROR OR WS-STATUS NOT = ZEROS
              DISPLAY 'FILE STATUS ' WS-STATUS
              MOVE 'FICHERO'  TO ERR-RECURSO
              MOVE 'CTDSUPB ' TO ERR-NOMBRE
              MOVE 'CLOSE'    TO ERR-ACCION
              DISPLAY 'MENSAJE ' MENSAJE-ERROR
           END-IF.

           CLOSE   IMPRES01


           IF WS-FS01 NOT = ZEROS
              DISPLAY 'FILE STATUS ' WS-FS01
              MOVE 'REPORTE'  TO ERR-RECURSO
              MOVE 'IMPRES01' TO ERR-NOMBRE
              MOVE 'CLOSE'    TO ERR-ACCION
              DISPLAY 'MENSAJE ' MENSAJE-ERROR
           END-IF.

           IF  RETURN-CODE   <=  LT-N-4
	       EXEC SQL COMMIT END-EXEC
	   END-IF.
           STOP RUN.

      **********************
       IO1100-OPEN-CURSOR.
      **********************
      *****************************************************************
      * --> OPEN DEL CURSOR                                           *
      *****************************************************************
            
            EXEC SQL
               OPEN CUR-SOR1
            END-EXEC

            MOVE SQLSTATE           TO SQLSTATE-SIGLO.

            EVALUATE TRUE
               WHEN IND-SQL-CORRECTO
                   CONTINUE
               WHEN OTHER
                   MOVE SPACES          TO CLV-GENERAL    OF AREA-ERROR
                   MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA   OF AREA-ERROR
                   MOVE LTA-CURSOR      TO NOM-TABLA      OF AREA-ERROR
                   MOVE 'IO1100-OPEN-CURSOR'
                                        TO NOM-PARRAFO    OF AREA-ERROR
                   MOVE 'ERROR EN OPEN CURSOR         '
                                        TO DEL-INCID      OF AREA-ERROR
                   MOVE  COD-EMPRESA OF S21-AREA-ENTORNO

                                        TO COD-EMPRESA    OF AREA-ERROR
                   MOVE  FEM-OPERACION OF S21-AREA-ENTORNO

                                        TO FEM-OPERACION  OF AREA-ERROR
                   @LOGERR(ERROR,SQLSTATE-SIGLO,AREA-ERROR)
                   SET HAY-ERROR              TO TRUE
                   PERFORM  A8000-FINAL
            END-EVALUATE.

      **********************
       IO1200-FETCH-CURSOR.
      **********************
      *****************************************************************
      * --> LEEMOS DEL CURSOR                                         *
      *****************************************************************
            EXEC SQL
               FETCH CUR-SOR1
                INTO
                     :T08CT093.NUM-CHEQUE,
                     :T08CT093.NUM-CTA-INT,
                     :T08CT093.IMP-CHEQUE,
                     :T08CT093.IMP-PROTESTO,
                     :T08CT093.COD-TIP-EXPE,
                     :T08CT093.COD-EMPRESA,
                     :T08CT093.IMP-MULTA,
                     :T08CT093.IMP-MULTA-COBRADA,
                     :T08CT093.IND-ESTADO-CTA,
                     :T08CT093.TIMESTAMP-ALTA,
                     :T08CT093.COD-SUC-PROPIE
            END-EXEC

            MOVE SQLSTATE           TO SQLSTATE-SIGLO.

            EVALUATE TRUE
               WHEN IND-SQL-CORRECTO
                    CONTINUE
               WHEN IND-NO-ENCONTRADO
                    IF PRIMER-REGISTRO
                       MOVE SPACES          TO CLV-GENERAL
                                            OF AREA-ERROR
                       MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA
                                            OF AREA-ERROR
                       MOVE LTA-CURSOR      TO NOM-TABLA
                                            OF AREA-ERROR
                       MOVE 'IO1200-FETCH-CURSOR'
                         TO NOM-PARRAFO    OF AREA-ERROR
                       MOVE LTA-NO-HAY-REG-T08CT093
                         TO DEL-INCID      OF AREA-ERROR
                       MOVE COD-EMPRESA OF S21-AREA-ENTORNO
                         TO COD-EMPRESA    OF AREA-ERROR
                       MOVE FEM-OPERACION OF S21-AREA-ENTORNO
                         TO FEM-OPERACION  OF AREA-ERROR

                       SET HAY-ERROR       TO TRUE
                       SET FIN-CURSOR      TO TRUE
                       PERFORM  A8000-FINAL

                    ELSE
                       SET FIN-CURSOR            TO TRUE
                    END-IF
               WHEN OTHER
                   MOVE SPACES          TO CLV-GENERAL    OF AREA-ERROR
                   MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA   OF AREA-ERROR
                   MOVE LTA-CURSOR      TO NOM-TABLA      OF AREA-ERROR
                   MOVE 'IO1200-FETCH-CURSOR'
                                        TO NOM-PARRAFO    OF AREA-ERROR
                   MOVE 'ERROR AL LEER CURSOR         '
                                        TO DEL-INCID      OF AREA-ERROR
                   MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                                        TO COD-EMPRESA    OF AREA-ERROR

                   MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
                                        TO FEM-OPERACION  OF AREA-ERROR

                   SET HAY-ERROR             TO TRUE
                   SET FIN-CURSOR            TO TRUE
                   PERFORM  A8000-FINAL
            END-EVALUATE.


      **********************
       A2650-MENOR-NUM-INTERVENCIONES.
      **********************
      *****************************************************************
      * --> ALGORITMO PARA DETERMINAR EL MENOR NUM DE INTERVENCIONES  *
      *****************************************************************
            MOVE NUM-ORDEN-INTERV OF MSG-OUT-PES11001(1)
            TO WS-NUM-ORDEN-INTERV-AU1




      *        NUM-ORDEN-INTERV OF MSG-OUT-PES11001(1)
            MOVE NUM-ORDEN-INTERV OF MSG-OUT-PES11001(LTN-1)
                                  TO WS-NUM-ORDEN-INTERV-AUX
            MOVE LTN-1  TO WS-IND-AUX
            MOVE LTN-2  TO WS-IND-ORD
      *     PERFORM  UNTIL WS-IND-ORD  >   LTN-MAX-8
            PERFORM  UNTIL WS-IND-ORD  >
                           NUM-RESPUESTA OF MSG-OUT-PES11001
            MOVE NUM-ORDEN-INTERV OF MSG-OUT-PES11001(WS-IND-ORD)
            TO WS-NUM-ORDEN-INTERV-AU1
      *        NUM-ORDEN-INTERV OF MSG-OUT-PES11001(WS-IND-ORD)

            IF NUM-ORDEN-INTERV OF MSG-OUT-PES11001(WS-IND-ORD)
               NOT = ZEROS
               IF NUM-ORDEN-INTERV OF MSG-OUT-PES11001(WS-IND-ORD) <
                                      WS-NUM-ORDEN-INTERV-AUX
                  MOVE NUM-ORDEN-INTERV OF MSG-OUT-PES11001(WS-IND-ORD)
                                        TO WS-NUM-ORDEN-INTERV-AUX
                  MOVE WS-IND-ORD TO WS-IND-AUX

               END-IF
            END-IF

            ADD LTN-1   TO WS-IND-ORD

            END-PERFORM.



       IO1600-GRABAR-CTDSUPB.
      ****************************************************
      * EN ESTE PROCESO SE GRABA EL REGISTRO DE SALIDA.  *
      ****************************************************

           MOVE WS-FEC-PROTESTO   TO WS-FECHA-AUXI2
           STRING  WS-ANIO-AUXI2   WS-MES-AUXI2  
             DELIMITED BY SIZE INTO DSUP-AAMM OF SALIDA.

           MOVE WS-CUENTA-N
             TO SUPB-CTA          OF SALIDA.

           WRITE REG-CTDSUPB FROM SALIDA.

           IF WS-STATUS NOT = ZERO
               MOVE 'FICHERO'     TO ERR-RECURSO
               MOVE 'FALLA'       TO ERR-NOMBRE
               MOVE 'IMP. SALIDA' TO ERR-ACCION
               @ERROR(FATAL,WS-STATUS,MENSAJE-ERROR)
           END-IF.


       IO1600-REPORTE-CTDSUPB.
      ****************************************************
      * EN ESTE PROCESO SE LISTA EL REGISTRO DE SALIDA.  *
      ****************************************************

           PERFORM A2600-QUIEBRE-OFICINA.

      ***********************
       A2600-QUIEBRE-OFICINA.
      ***********************
      **********************************************************
      * Se calcula el total de comisiones pendientes por oficina
      * propietaria de la cuenta.
      **********************************************************

           IF COD-SUC-PROPIE OF T08CT093 =
              WS-COD-SUC-PROPIE-ANT
              PERFORM A2610-QUIEBRE-CUENTA
           ELSE
              PERFORM A2800-TOTALES-OFICINA
              PERFORM A1200-CODIGO-OFICINA
              PERFORM A2610-QUIEBRE-CUENTA
              MOVE COD-SUC-PROPIE OF T08CT093 TO
              WS-COD-SUC-PROPIE-ANT
           END-IF.

      ***********************
       A2610-QUIEBRE-CUENTA.
      ***********************

           IF NUM-CTA-INT    OF T08CT093 =
              WS-NUM-CTA-INT-ANT
              PERFORM A2200-IMPRIMIR-CTA
           ELSE
              MOVE ZEROS TO WS-BANDERA
              PERFORM A2900-UBICACION-CLIENTE
              PERFORM A2620-CUENTA-VIEJA
              PERFORM A2200-IMPRIMIR-CTA
              MOVE NUM-CTA-INT    OF T08CT093 TO
                   WS-NUM-CTA-INT-ANT
           END-IF.

      ***********************
       A2620-CUENTA-VIEJA.
      ***********************
           MOVE COD-TIP-EXPE    OF T08CT093
             TO COD-TIP-EXPE    OF MSG-IN-CTS10139
           MOVE NUM-CTA-INT     OF T08CT093
             TO NUM-CTA-INT     OF MSG-IN-CTS10139
           MOVE COD-EMPRESA     OF T08CT093
             TO COD-EMPRESA     OF MSG-IN-CTS10139

           @INVOCAR(CTS10139,A)

           IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
           DISPLAY 'ERROR ' TIPO-ERROR OF S21-AREA-ERROR
              MOVE 'A2620-CTA-VIEJA  '
                                   TO NOM-PARRAFO    OF AREA-ERROR
              MOVE 'ERROR INVOCAR CTS10139'
                                   TO DEL-INCID      OF AREA-ERROR
              MOVE  COD-EMPRESA OF S21-AREA-ENTORNO
                 TO COD-EMPRESA    OF AREA-ERROR
              MOVE  FEM-OPERACION OF S21-AREA-ENTORNO
               TO FEM-OPERACION  OF AREA-ERROR
              @ERROR(,,AREA-ERROR)
              SET HAY-ERROR                       TO TRUE
              PERFORM  A8000-FINAL
           END-IF.
      *    DISPLAY 'CTA-VIEJA ' CTA-VIEJA
      *    DISPLAY 'CTA-NUEVA ' CTA-NUEVA
           IF CTA-VIEJA NOT = 0
              MOVE CTA-VIEJA TO WS-CUENTA-N
           ELSE
              MOVE NUM-CTA-INT  OF T08CT093
                TO WS-CUENTA
              MOVE COD-TIP-EXPE OF T08CT093
                TO WS-TIP-EX.

      *    DISPLAY 'CUENTA    ' WS-CUENTA-N.

      ***********************
       A2200-IMPRIMIR-CTA.
      **************************

           IF WS-BANDERA = 0
              PERFORM A2300-IMPRIMIR-NOMBRE
              PERFORM A2300-IMPRIMIR-CHEQUE
            ELSE
              PERFORM A2300-IMPRIMIR-CHEQUE
           END-IF.

      ******************************
       A2300-IMPRIMIR-NOMBRE.
      *****************************************************************
      * -> SE IMPRIMEN DATOS DE LOS CLIENTES                          *
      *****************************************************************

           MOVE WS-CUENTA-N
             TO SUPB-CTA          OF SALIDA.

           WRITE   REG-IMPRES01 FROM CAB-4

           IF WSN-CONTLIN > LTN-53
             PERFORM A4000-TOTALES-PAGINA
             PERFORM A4000-CABECERAS
             ADD     1            TO WSN-CONTPAG
             MOVE    10           TO WSN-CONTLIN
             MOVE    WSN-CONTPAG  TO PAGINA
             WRITE   REG-IMPRES01 FROM CAB-1 AFTER ADVANCING PAGE
             WRITE   REG-IMPRES01 FROM CAB-2
             WRITE   REG-IMPRES01 FROM CAB-3
      *      WRITE   REG-IMPRES01 FROM CAB-4

             IF W-COD-VAL = 'F'
                WRITE   REG-IMPRES01 FROM CAB-52
             ELSE
                WRITE   REG-IMPRES01 FROM CAB-5
             END-IF

             WRITE   REG-IMPRES01 FROM CAB-6
             WRITE   REG-IMPRES01 FROM CAB-7
             WRITE   REG-IMPRES01 FROM CAB-8
             WRITE   REG-IMPRES01 FROM CAB-9
             WRITE   REG-IMPRES01 FROM CAB-6
             WRITE   REG-IMPRES01 FROM CAB-4
           END-IF.


           MOVE NOM-DENOM-SOCIAL OF MSG-OUT-PES01003
             TO CLIENT-ED        OF    DETALLE-NOM

           MOVE WS-COD-EXT-DOC-CP
             TO CEDULA-ED       OF    DETALLE-NOM

      *    MOVE SPACES
      *      TO DET-CIU         OF    DETALLE-NOM

      *    MOVE SPACES
      *      TO DIREC-ED-1      OF    DETALLE-NOM

           MOVE SPACES
             TO DIREC-ED-2      OF    DETALLE-NOM

           WRITE REG-IMPRES01 FROM DETALLE-NOM AFTER 1

           ADD 2 TO WSN-CONTLIN.

           MOVE 1 TO WS-BANDERA.


      ******************************
       A2300-IMPRIMIR-CHEQUE.
      *****************************************************************
      * -> SE IMPRIMEN DATOS DE LOS CLIENTES VALORES                  *
      *****************************************************************

           IF WSN-CONTLIN > LTN-53
              PERFORM A2300-IMPRIMIR-NOMBRE
           END-IF.

           MOVE NUM-CHEQUE        OF T08CT093
             TO CHEQUE-ED         OF    DETALLE-CHE

           MOVE IMP-CHEQUE        OF T08CT093
             TO VALORC-ED         OF    DETALLE-CHE

           MOVE IMP-PROTESTO      OF T08CT093
             TO VALORP-ED         OF    DETALLE-CHE


           MOVE WS-FEC-PROTESTO   TO WS-FECHA-AUXI
           MOVE WS-ANIO-AUXI
             TO ANO-ED            OF    DETALLE-CHE

           MOVE WS-MES(WS-MES-AUXI)
             TO MES-ED            OF    DETALLE-CHE

           MOVE WS-DIA-AUXI
             TO DIA-ED            OF    DETALLE-CHE
                DSUP-DIAP

           MOVE IMP-MULTA         OF T08CT093
             TO CINCO-ED          OF    DETALLE-CHE

           MOVE IMP-MULTA-COBRADA OF T08CT093
             TO MULTA-ED          OF    DETALLE-CHE

           COMPUTE WS-SALDO = IMP-MULTA         OF T08CT093 -
                   IMP-MULTA-COBRADA OF T08CT093

           MOVE WS-SALDO
             TO SALDO-ED          OF    DETALLE-CHE


           MOVE NUM-CTA-INT  OF T08CT093  TO WS-NUM-CTA-INT-AUX

      *    MGDA 18-10-2002
           MOVE WS-CUENTA-N
             TO CUENTA-ED1        OF    DETALLE-CHE
      *    MGDA 18-10-2002

           COMPUTE WS-TOT-IMP-PROTESTO = WS-TOT-IMP-PROTESTO +
                   IMP-PROTESTO      OF T08CT093

           COMPUTE WS-TOT-IMP-MULTA = WS-TOT-IMP-MULTA +
                   IMP-MULTA         OF T08CT093

           COMPUTE WS-TOT-IMP-MULTA-COBRADA = WS-TOT-IMP-MULTA-COBRADA +
                   IMP-MULTA-COBRADA OF T08CT093

           COMPUTE WS-TOT-SALDO = WS-TOT-SALDO +
                   WS-SALDO

           WRITE REG-IMPRES01 FROM DETALLE-CHE AFTER 1

           ADD 1 TO WSN-CONTLIN.

      ***********************
       A2800-TOTALES-OFICINA.
      ***********************************************************
      * Para la impresion de los totales por oficina propietaria
      * de la cuenta.
      ***********************************************************

           PERFORM A4000-TOTALES-OFICINA.

           MOVE 70    TO WSN-CONTLIN.
           MOVE ZEROS TO WS-BANDERA.

      ******************
       A4000-CABECERAS.
      **************************************************************
      * SE RELLENAN LOS CAMPOS VARIABLES DE CABECERAS
      **************************************************************
            MOVE COD-SUC-PROPIE OF T08CT093 TO
                 WS-COD-SUC-PROPIE

            PERFORM A4110-BUSCA-CENTRO.

            PERFORM A4110-BUSCA-PROVINCIA.

      ******************************
       A4000-TOTALES-PAGINA.
      *****************************************************************
      * -> SE IMPRIMEN LOS TOTALES DE PAGINA QUE PASAN A LA SIGUIENTE *
      *****************************************************************

           IF WS-BANDERA-TOT = ZEROS
              MOVE 'PASAN: '                TO  PASAN-ED
              MOVE WS-TOT-IMP-PROTESTO      TO  TOT-PRO
              MOVE WS-TOT-IMP-MULTA         TO  TOT-UNO
              MOVE WS-TOT-IMP-MULTA-COBRADA TO  TOT-DOS
              MOVE WS-TOT-SALDO             TO  TOT-TRE

              WRITE REG-IMPRES01 FROM DETALLE-TOT AFTER 1

              ADD 1 TO WSN-CONTLIN
           END-IF.

           MOVE ZEROS TO WS-BANDERA-TOT.


      ******************************
       A4000-TOTALES-OFICINA.
      *****************************************************************
      * -> SE IMPRIMEN LOS TOTALES POR OFICINA                        *
      *****************************************************************

           WRITE   REG-IMPRES01 FROM CAB-6

           MOVE 'TOTAL: '                TO  PASAN-ED
           MOVE WS-TOT-IMP-PROTESTO      TO  TOT-PRO
           MOVE WS-TOT-IMP-MULTA         TO  TOT-UNO
           MOVE WS-TOT-IMP-MULTA-COBRADA TO  TOT-DOS
           MOVE WS-TOT-SALDO             TO  TOT-TRE

           WRITE REG-IMPRES01 FROM DETALLE-TOT AFTER 1

           ADD 1 TO WSN-CONTLIN.
           MOVE 1 TO WS-BANDERA-TOT

           COMPUTE WS-GLO-IMP-MULTA = WS-GLO-IMP-MULTA +
                   WS-TOT-IMP-MULTA

           COMPUTE WS-GLO-IMP-MULTA-COBRADA = WS-GLO-IMP-MULTA-COBRADA +
                   WS-TOT-IMP-MULTA-COBRADA

           COMPUTE WS-GLO-SALDO = WS-GLO-SALDO +
                   WS-TOT-SALDO

           MOVE ZEROS TO WS-TOT-IMP-PROTESTO
           MOVE ZEROS TO WS-TOT-IMP-MULTA
           MOVE ZEROS TO WS-TOT-IMP-MULTA-COBRADA
           MOVE ZEROS TO WS-TOT-SALDO.

      **********************
       A4110-BUSCA-CENTRO.
      **************************************************************
      * - BUSCA EL CENTRO DEPENDIENTE DEL COD-CENT-ORIGEN DE LA    *
      *   ENTRADA.                                                 *
      **************************************************************

            MOVE COD-EMPRESA OF S21-AREA-ENTORNO
              TO WS-COD-EMPRESA

            EXEC SQL

                 SELECT COD_CENTRO,
                        NOMBRE,
                        COD_PAIS,
                        COD_PROVINCIA
                 INTO   :T06TC007.COD-CENTRO,
                        :T06TC007.NOMBRE,
                        :T06TC007.COD-PAIS,
                        :T06TC007.COD-PROVINCIA
                 FROM   T06TC007

                 WHERE  COD_CENTRO  =:WS-COD-SUC-PROPIE
                  AND   COD_EMPRESA =:WS-COD-EMPRESA

            END-EXEC.

            MOVE     SQLSTATE TO SQLSTATE-SIGLO.

            EVALUATE TRUE

               WHEN IND-SQL-CORRECTO
                    MOVE NOMBRE OF T06TC007
                      TO CENTRO-A       OF CAB-5
                         CENTRO-A-2     OF CAB-52
                    MOVE COD-CENTRO OF T06TC007 TO ENTIDAD-N   OF CAB-5
                                       ENTIDAD-N-2   OF CAB-52
                    MOVE COD-PROVINCIA OF T06TC007
                                     TO PROVINCIA-A OF CAB-5
                                        PROVINCIA-A-2 OF CAB-52

               WHEN IND-NO-ENCONTRADO
                    MOVE SPACES
                      TO CENTRO-A       OF CAB-5
                         CENTRO-A-2     OF CAB-52
                    MOVE ZEROS          TO ENTIDAD-N   OF CAB-5
                                           PROVINCIA-A OF CAB-5
                                           PROVINCIA-A-2 OF CAB-52
                                           ENTIDAD-N-2   OF CAB-52
                    MOVE SPACES TO CLV-GENERAL   OF AREA-ERROR
                    MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA  OF AREA-ERROR
                    MOVE LTA-CURSOR      TO NOM-TABLA     OF AREA-ERROR
                    MOVE 'A4110-BUSCA-CENTRO'
                                         TO NOM-PARRAFO    OF AREA-ERROR
                    MOVE 'COD-CENTRO NO VALIDO'
                                         TO DEL-INCID   OF AREA-ERROR
                    DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
                    DISPLAY AREA-ERROR
                    SET HAY-ERROR              TO TRUE
                    PERFORM  A8000-FINAL

               WHEN OTHER
                    MOVE SPACES          TO CLV-GENERAL   OF AREA-ERROR
                    MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA  OF AREA-ERROR
                    MOVE LTA-CURSOR      TO NOM-TABLA     OF AREA-ERROR
                    MOVE 'A4110-BUSCA-CENTRO'
                                         TO NOM-PARRAFO    OF AREA-ERROR
                    MOVE 'ERROR DE DB2.'
                                         TO DEL-INCID   OF AREA-ERROR
                    DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
                    DISPLAY AREA-ERROR
                    SET HAY-ERROR              TO TRUE
                    PERFORM  A8000-FINAL

            END-EVALUATE.

      **********************
       A4110-BUSCA-PROVINCIA.
      **************************************************************
      * - BUSCA LA DESCRIPCION DE LA PROVINCIA DE LA OFICINA       *
      **************************************************************

            MOVE  COD-PAIS OF T06TC007
              TO  WS-COD-PAIS

            MOVE  COD-PROVINCIA OF T06TC007
              TO  WS-COD-PROVINCIA

            MOVE WS-CODIGO-REGISTRO TO CODIGO-REGISTRO OF T06TC002

      *     DISPLAY 'CODIGO-REGISTRO. ' CODIGO-REGISTRO OF T06TC002

            EXEC SQL

                 SELECT DEL_REGISTRO
                 INTO   :T06TC002.DEL-REGISTRO
                 FROM   T06TC002

                 WHERE COD_TABLA_ID    = 'TC53PROV'
                 AND   CODIGO_REGISTRO = :T06TC002.CODIGO-REGISTRO

            END-EXEC.

            MOVE     SQLSTATE TO SQLSTATE-SIGLO.

            EVALUATE TRUE

               WHEN IND-SQL-CORRECTO
                    MOVE DEL-REGISTRO   OF T06TC002
                      TO PROVINCIA-A OF CAB-5
                         PROVINCIA-A-2 OF CAB-52

               WHEN IND-NO-ENCONTRADO
                    MOVE SPACES TO         PROVINCIA-A OF CAB-5
                    MOVE SPACES TO         PROVINCIA-A-2 OF CAB-52
                    MOVE SPACES TO CLV-GENERAL   OF AREA-ERROR
                    MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA  OF AREA-ERROR
                    MOVE LTA-CURSOR      TO NOM-TABLA     OF AREA-ERROR
                    MOVE 'A4110-BUSCA-PROVINCIA'
                                         TO NOM-PARRAFO    OF AREA-ERROR
                    MOVE 'COD-PROVINCIA NO VALIDO'
                                         TO DEL-INCID   OF AREA-ERROR
                    DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
                    DISPLAY AREA-ERROR
                    SET HAY-ERROR              TO TRUE
                    PERFORM  A8000-FINAL

               WHEN OTHER
                    MOVE SPACES          TO CLV-GENERAL   OF AREA-ERROR
                    MOVE LTA-NOMBRE-PRG  TO NOM-PROGRAMA  OF AREA-ERROR
                    MOVE LTA-CURSOR      TO NOM-TABLA     OF AREA-ERROR
                    MOVE 'A4110-BUSCA-PROVINCIA'
                                         TO NOM-PARRAFO    OF AREA-ERROR
                    MOVE 'ERROR DE DB2.'
                                         TO DEL-INCID   OF AREA-ERROR
                    DISPLAY 'SQLSTATE-SIGLO ' SQLSTATE-SIGLO
                    DISPLAY AREA-ERROR
                    SET HAY-ERROR              TO TRUE
                    PERFORM  A8000-FINAL

            END-EVALUATE.

      ******************************
       A6000-TOTALES-GLOBALES.
      ******************************
      *****************************************************************
      * -> SE IMPRIMEN LOS TOTALES GLOBALES DEL REPORTE               *
      *****************************************************************

           WRITE   REG-IMPRES01 FROM DETALLE-GLO-1 AFTER ADVANCING PAGE

           WRITE   REG-IMPRES01 FROM DETALLE-GLO-2

           MOVE    WS-GLO-IMP-MULTA  TO  TOTA-1
           WRITE   REG-IMPRES01 FROM DETALLE-GLO-3

           MOVE    WS-GLO-IMP-MULTA-COBRADA TO  TOTA-2
           WRITE   REG-IMPRES01 FROM DETALLE-GLO-4

           MOVE    WS-GLO-SALDO             TO  TOTA-3
           WRITE   REG-IMPRES01 FROM DETALLE-GLO-5.

      *----------------------------------------------------------
       A6100-CAL-FECHAS.
      *    MOVE FIC-FECHA-INI TO WS-FEC-AUX (PARA PRUEBAS)
           MOVE FEM-MAQUINA  OF S21-AREA-ENTORNO TO WS-FEC-AUX
           DISPLAY WS-FEC-AUX

           IF FEC-CANC-DIA  > 21
              MOVE '.' TO WS-FEC-AUX(3:1)
              MOVE '.' TO WS-FEC-AUX(6:1)
              MOVE '16' TO FEC-CANC-DIA
              MOVE WS-FEC-AUX
                TO WS-FECHA-INICIAL
              PERFORM A6102-CAL-FIN-MES
              PERFORM A6110-CAL-DIA-ANTERIOR
              MOVE WS-FEC-AUX
                TO WS-FECHA-FINAL
           ELSE
              IF FEC-CANC-DIA  > 07 AND < 22
                 MOVE '.' TO WS-FEC-AUX(3:1)
                 MOVE '.' TO WS-FEC-AUX(6:1)
                 MOVE '01' TO FEC-CANC-DIA
                 MOVE WS-FEC-AUX
                   TO WS-FECHA-INICIAL
                 MOVE '15' TO FEC-CANC-DIA
                 MOVE WS-FEC-AUX
                   TO WS-FECHA-FINAL
              ELSE
                 MOVE '01' TO FEC-CANC-DIA
                 MOVE '.' TO WS-FEC-AUX(3:1)
                 MOVE '.' TO WS-FEC-AUX(6:1)
                 PERFORM A6110-CAL-DIA-ANTERIOR
                 MOVE WS-FEC-AUX
                   TO WS-FECHA-FINAL
                 MOVE '16' TO FEC-CANC-DIA
                 MOVE WS-FEC-AUX
                   TO WS-FECHA-INICIAL
              END-IF
           END-IF.

       A6102-CAL-FIN-MES.
      *----------------------------------------------------------
      *  - CALCULO FECHA SIGUIENTE MES                          *
      *----------------------------------------------------------

           INITIALIZE EP0015P.
      *--- OBTENER FECHA DE INICIO (UN DIA ANTES)
           SET  NATURAL OF EP0015P    TO TRUE
           MOVE 28                    TO FEC-CANC-DIA
           MOVE WS-FEC-AUX            TO FEM-INICIO     OF EP0015P
           MOVE 'I'                   TO IND-OPERACION  OF EP0015P
           MOVE 5                     TO NUM-DIAS-MOVIM OF EP0015P
           CALL LT-A-EPR0015 USING PAR-DUMMY
                                   PAR-DUMMY
                                   EP0015P.

           IF NUM-RESPUESTA     OF EP0015P NOT = 0
              CONTINUE
           ELSE
              MOVE FEM-FIN OF EP0015P(7:4) TO FEC-CANC-ANO
              MOVE FEM-FIN OF EP0015P(4:2) TO FEC-CANC-MES
              MOVE 01                      TO FEC-CANC-DIA
              MOVE '.' TO WS-FEC-AUX(3:1)
              MOVE '.' TO WS-FEC-AUX(6:1)
           END-IF.


       A6110-CAL-DIA-ANTERIOR.
      *----------------------------------------------------------
      *  - CALCULO DE 1   DIA  ATRAS A PARTIR DE LA FECHA DE PROC
      *----------------------------------------------------------
           INITIALIZE EP0015P.
      *--- OBTENER FECHA DE INICIO (UN DIA ANTES)
           SET  NATURAL OF EP0015P    TO TRUE
           MOVE WS-FEC-AUX          TO FEM-INICIO     OF EP0015P
           MOVE 'D'                   TO IND-OPERACION  OF EP0015P
           MOVE 1                     TO NUM-DIAS-MOVIM OF EP0015P
           CALL LT-A-EPR0015 USING PAR-DUMMY
                                   PAR-DUMMY
                                   EP0015P.

           IF NUM-RESPUESTA     OF EP0015P NOT = 0
              CONTINUE
           ELSE
              MOVE FEM-FIN OF EP0015P(7:4) TO FEC-CANC-ANO
              MOVE FEM-FIN OF EP0015P(4:2) TO FEC-CANC-MES
              MOVE FEM-FIN OF EP0015P(1:2) TO FEC-CANC-DIA
              MOVE '.' TO WS-FEC-AUX(3:1)
              MOVE '.' TO WS-FEC-AUX(6:1)
           END-IF.

