      ****************************************************************
      **              B A N C O   D E L   P I C H I N C H A         **
      ****************************************************************
      **                     SchlumbergerSema                       **
      ****************************************************************
      ****************************************************************
      **    CAMARA ENTRANTE : TRATAMIENTO AUTOMATICO DE INCIDENCIAS **
      **                      PARA DEVOLUCION DEFINITIVA DE CHEQUES **
      ****************************************************************
      ****************************************************************
      **                                                            **
      **  MODULE NAME:    CAB1040                                   **
      **                                                            **
      **  DATE GENERATED: ABRIL 8  2002                             **
      **                                                            **
      **                                                            **
      **  DESCRIPTION:                                              **
      **                                                            **
      **         Proceso batch encargado de la busqueda de todos los**
      **         cheques y pagares recibidos y que han generado un  **
      **         intercambio porque no han podido ser cargados a    **
      **         clientes. Al ejecutarse, todos los intercambios    **
      **         que no hayan sido resueltos deben marcarse como    **
      **         devueltos y actualizar el estado de los cheques    **
      **         a pendiente  de devolucion. Estos  cheques se en-  **  
      **         viaran a la camara como devueltos en el proximo en-**
      **         vio.                                               **
      **============================================================**
      **                        MODIFICACIONES                      **
      **============================================================**
      ** GMG0902 04-06-98 Modificaciones en torno al Euro.          **
      **                                                            **
      ** MSINGAN 10-04-02 Se parametriza la Entidad y Centro utili- **
      **                  zando la macro INIBAT.                    **
      **                                                            **
      ** JVICI   14-06-02 Se introduce GXCOMMIT solo para poder para**
      **                  metrizar en la T18CHK01 cada cuantos regis**
      **                  tros procesados se hace COMMIT.           **
      ** ALEGUIZ 19-06-02 Se ordena el cursor de incidencias pendien**
      **                  tes por devolucion por centro origen. Se  **
      **                  crea una nueva operacion por cada centro  **
      **                  origen diferente leido del mismo.         **
      ** ....... ..-..-.. ......................................... **
      ** VRAMIRE 20-05-03 Control para grabar usuario que actualizo **
      **                  por ultima vez la incidencia.             **
      ** ....... ..-..-.. ......................................... **
      ** WGUERRE 08-03-04 Se graba el usuario que devolvio el cheque**
      **                  en la tabla de Protestos                  **
      ** ....... ..-..-.. ......................................... **
      ** WGUERRE 13.04.04 No tomar los registros generados para la  **
      **                  consideracion de las Notas de Debito      **
      **                                                            **
      ** WGUERRE 04.05.04 Se incluye en select de t30dor10 la fecha **
      **                  de vencimiento para que no de error 2112  **
      **                                                            **
      ** WGUERRE 16.08.04 Se elimina la rearrancabilidad, y adiciona**
      **                  el commit normal, ya que el cursor automa-**
      **                  ticamente comienza donde se quedo.        **
      **                  Se elimina porque este proceso es abierto **
      **                  en N procesos                             **
      **                                                            **
      ** WGUERRE 28.09.04 Se pone como fecha de devolucion la fecha **
      **                  de vencimiento del documento, reemplazando**
      **                  el 01.01.0001 que actualmente esta moviendo*
      **                  cuando no encuentra                       **
      **                                                            **
      ** FSALAZAR 28/01/08 Ingreso displays para determinar error   **
      **                  2207612, cual no desmarca consideracion en**
      **                  devolucion de cheques. Se homologa como   ** 
      **                  se encuentra batch en BP.                 **
      ** JTORRES 20/02/25 PRY-MIGRACION-AIX                         **
      **                  SE  ADICIONA ESPACIO  ENTRE APOSTROFE  Y  **
      **                  VARIABLES Y/O COMENTARIO DE "DISPLAY"     **
      **                  REF: MGRAIX                               **
      ****************************************************************


       IDENTIFICATION DIVISION.
       PROGRAM-ID. CAB1040.

       ENVIRONMENT DIVISION.
      ***********************

       CONFIGURATION SECTION.

       SPECIAL-NAMES.
           DECIMAL-POINT IS COMMA.


      *--------------------------------------------------------------*
      * INPUT-OUTPUT SECTION                                         *
      *--------------------------------------------------------------*

       INPUT-OUTPUT SECTION.

       FILE-CONTROL.

            SELECT IMPRES01 ASSIGN TO IMPRES01
                   ORGANIZATION IS SEQUENTIAL.

            SELECT IMPRES02 ASSIGN TO IMPRES02
                   ORGANIZATION IS SEQUENTIAL.

      * Archivo de opciones.
           SELECT FICCON01 ASSIGN TO FICCON01
                           FILE STATUS IS FS-FIC01.
                           

      *--------------------------------------------------------------*
      * DATA DIVISION                                                *
      *--------------------------------------------------------------*
       DATA DIVISION.

       FILE SECTION.
      *--------------------------------------------------------------*
      * LISTADO DE ERRORES                                           *
      *--------------------------------------------------------------*
       FD  IMPRES02
           RECORDING MODE IS F
           BLOCK CONTAINS 0 RECORDS
           LABEL RECORD ARE STANDARD
           DATA  RECORD IS  RECORD-PRN2.
       01  RECORD-PRN2               PIC X(133).


      *--------------------------------------------------------------*
      * LISTADO DE ESTADISTICAS                                      *
      *--------------------------------------------------------------*
       FD  IMPRES01
           RECORDING MODE IS F
           BLOCK CONTAINS 0 RECORDS
           LABEL RECORD ARE STANDARD
           DATA  RECORD IS  REG-IMPRES01.
       01  REG-IMPRES01              PIC X(133).


       FD  FICCON01 BLOCK 0
           RECORDING MODE IS F
           LABEL RECORD IS STANDARD.
       01  R-FICCON01                   PIC X(80).


       WORKING-STORAGE SECTION.
      ****************************************************************
      ** REPOSITORY WORKING STORAGE                                 **
      ****************************************************************

      *-------------------------------------------------------------*
      * COPY DE ERRORES DE PASIVO.                                  *
      *-------------------------------------------------------------*
       COPY PAERRCOD.

      *-------------------------------------------------------------*
      * VARIABLES Y CONSTANTES AUXILIARES.                          *
      *-------------------------------------------------------------*
       01  WS-VARIABLES.
           05  WS-LT-DEVUELTO        PIC X(2)     VALUE 'RE'.
           05  WS-LT-EXTRAIDO        PIC X(2)     VALUE 'EX'.
           05  WS-LT-PENDIENTE       PIC X(2)     VALUE 'PD'.
           05  WS-LT-VENC-PEND       PIC X(2)     VALUE 'VP'.
           05  WS-LT-PTE-DEVOL       PIC X(2)     VALUE 'DE'.
           05  WS-LT-PEND-RESOL      PIC X(2)     VALUE 'PR'.
           05  WS-LT-DEVUELTO-CONSID PIC X(2)     VALUE 'DV'.
           05  WS-TIMESTAMPSIGLO2    PIC X(26)    VALUE SPACES.
           05  WS-TIMESTAMPSIGLO3    PIC X(26)    VALUE SPACES.
           05  WG-COD-USUARIO        PIC X(08)    VALUE SPACES.
           05  WS-FECHA-PROC         PIC X(10)    VALUE SPACES.
       01  WS-COD-EMPRESA            PIC X(4). 
       01  WS-COD-CENTRO             PIC X(4).
       01  WS-COD-CENT-ORIG          PIC X(4).
       01  WS-FEM-CONTABLE           PIC X(10).
       01  WS-FEM-HOY                PIC X(10).
       01  WS-A-PROGRAMA             PIC X(7)     VALUE 'CAB1040'.
       01  WS-COD-INCID              PIC S9(6)V COMP-3.
       01  WS-COD-INCID1             PIC S9(6)V COMP-3.
       01  WS-COD-DESFI              PIC 9(10)    VALUE 4140270000.
       01  LT-N-INCORRIENTE          PIC 9(2)     VALUE 1.
       01  LT-9615                   PIC 9(5)     VALUE 9615.
       01  LT-N-4                    PIC 9(2)     VALUE 4.
       01  WS-CENTRO                 PIC X(4).
       01  WS-ERROR                  PIC 9(5)     VALUE 0.   
      *--  Control de rangos de ejecución. 
       01  WS-DEL-REGISTRO           PIC X(125)   VALUE ZEROS.
       01  FL                        REDEFINES WS-DEL-REGISTRO.
           05 FILLER                 PIC X.
           05 WS-CUENTA-INI          PIC 9(10).
           05 FILLER                 PIC X(02).
           05 WS-CUENTA-FIN          PIC 9(10).
           05 FILLER                 PIC X.
           05 WS-CUENTAS             PIC 9(08).
           05 FILLER                 PIC X.
           05 WS-REGISTROS           PIC 9(08).
           05 FILLER                 PIC X(84).
       01  REG-FICCON.
           05 WS-RANGO               PIC X(15).
           05 FILLER                 PIC X(65).       
       01  FS-FIC01                  PIC X(02)  VALUE '00'.
       01  WS-CTA-INI                PIC S9(10)V COMP-3.
       01  WS-CTA-FIN                PIC S9(10)V COMP-3.
      *-------------------------------------------------------------*
      * VARIABLES AUXILIARES                                        *
      *-------------------------------------------------------------*
       01  WS-NUM-CUENTA             PIC 9(10).
       01  WS-NUMCUEN REDEFINES WS-NUM-CUENTA.
           05  WS-NUM-CTA-INT        PIC 9(8).
           05  WS-COD-TIP-EXPE       PIC X(2).
       01  WS-VAR-AUX.
           05  WS-HORA6-AUX          PIC 9(6).
           05  WS-HORA6-AUX-R REDEFINES WS-HORA6-AUX.
               10  WS-HORA6          PIC 9(2).
               10  WS-MINUTOS6       PIC 9(2).
               10  WS-SEGUNDOS6      PIC 9(2).
           05  WS-HORA8-AUX.
               10  WS-HORA8          PIC X(2).
               10  FILLER            PIC X(1)     VALUE '.'.
               10  WS-MINUTOS8       PIC X(2).
               10  FILLER            PIC X(1)     VALUE '.'.
               10  WS-SEGUNDOS8      PIC X(2).
           05  WS-COD-CENT-COMP      PIC 9(4)     VALUE ZEROS.
       01  NUMERO-NUM                PIC 9(15).
       01  NUMERO-NUM-R REDEFINES NUMERO-NUM.
           05  FILLER-NUM            PIC 9(11).
           05  WS-NUMERO-NUM         PIC X(4).
       01  WS-NUMERO-DOCUMENTO       PIC X(10).
       01  FILLER1 REDEFINES WS-NUMERO-DOCUMENTO.
           05  FILLER                PIC 9(03).
           05  WS-NUM-CHEQUE         PIC 9(07).
      *--------------------------------------------------------------*
      * VARIABLES AUXILIARES PARA FECHAS.                            *
      *--------------------------------------------------------------*
       01  WS-FEM-MAQUINA            PIC X(10)    VALUE SPACES.
       01  FECHA-DMA                 PIC X(10).
       01  FECHA-DMA-R  REDEFINES FECHA-DMA.
           05  DIA-DMA               PIC 9(2).
           05  FILLER                PIC X(1).
           05  MES-DMA               PIC 9(2).
           05  FILLER                PIC X(1).
           05  ANNO-DMA              PIC 9(4).
           05  ANNO-DMA-R REDEFINES ANNO-DMA.
               10  ANNO-DMA12        PIC 99.
               10  ANNO-DMA34        PIC 99.
      *--------------------------------------------------------------*
      * VARIABLES AUXILIAR PARA FORMATEAR EL TIMESTAMPSIGLO          *
      *--------------------------------------------------------------*
       01  TIMESTAMP-AUX.
           05  FECHA-AUX.
               10  ANNO              PIC 9(4).
               10  GUION1            PIC X       VALUE '-'.
               10  MES               PIC 9(2).
               10  GUION2            PIC X       VALUE '-'.
               10  DIA               PIC 9(2).
           05  GUION3                PIC X       VALUE '-'.
           05  HORA-AUX.
               10  HORA              PIC 9(2).
               10  PUNTO1            PIC X       VALUE '.'.
               10  MINUTO            PIC 9(2).
               10  PUNTO2            PIC X       VALUE '.'.
               10  SEGUNDO           PIC 9(2).
           05  PUNTO3                PIC X       VALUE '.'.
           05  TIMESTAMP-RESTO       PIC 9(6).
       01  HORA-AUX-2.
           05  HORA-2                PIC 9(2).
           05  FILLER                PIC X       VALUE '.'.
           05  MINUTO-2              PIC 9(2).
           05  FILLER                PIC X       VALUE '.'.
           05  SEGUNDO-2             PIC 9(2).
      *--------------------------------------------------------------*
      * VARIABLES AUXILIAR PARA FORMATEAR EL TIMESTAMP-HOY           *
      *--------------------------------------------------------------*
       01  WS-TIMESTAMP-HOY.
           05  FECHA-HOY.
               10  ANNO-HOY          PIC 9(4).
               10  GUION1-HOY        PIC X       VALUE '-'.
               10  MES-HOY           PIC 9(2).
               10  GUION2-HOY        PIC X       VALUE '-'.
               10  DIA-HOY           PIC 9(2).
           05  GUION3-HOY            PIC X       VALUE '-'.
           05  HORA-AUX-HOY.
               10  HORA-HOY          PIC 9(2).
               10  PUNTO1-HOY        PIC X       VALUE '.'.
               10  MINUTO-HOY        PIC 9(2).
               10  PUNTO2-HOY        PIC X       VALUE '.'.
               10  SEGUNDO-HOY       PIC 9(2).
           05  PUNTO3-HOY            PIC X       VALUE '.'.
           05  TIMESTAMP-RESTO-HOY   PIC 9(6)    VALUE ZEROS.
      *-------------------------------------------------------------*
      * CAMPOS ALFANUMERICOS                                        *
      *-------------------------------------------------------------*
       01  WS-ALFANUMERICOS.
           05  WS-TIEMPO             PIC 9(6).
           05  FILLER  REDEFINES  WS-TIEMPO.
               10  WS-HORA           PIC 9(2).
               10  WS-MINUTOS        PIC 9(2).
               10  WS-SEGUNDOS       PIC 9(2).
      *-------------------------------------------------------------*
      * CAMPOS NUMERICOS                                            *
      *-------------------------------------------------------------*
       01  WS-NUMERICOS.
           05  WS-IMPRES             PIC 9(1)    VALUE ZEROS.
           05  WS-RETURN-CODE        PIC 9(2)    VALUE ZEROS.
      *-------------------------------------------------------------*
      * CONTADORES:                                                 *
      *-------------------------------------------------------------*
       01  WS-CONTADORES.
           05  WS-CONTA-PAGINA       PIC 9(7)    VALUE ZEROS.
           05  WS-NUM-LINEAS         PIC 9(2)    VALUE 70.
      *--------------------------------------------------------------*
      * VARIABLES DE INFORMACION DE ERRORES                          *
      *--------------------------------------------------------------*
       01  AREA-INFORMACION.
           05  WS-PROGRAMA           PIC X(8)    VALUE 'CAB1040'.
           05  WS-PARRAFO            PIC X(34).
           05  WS-TEXTO              PIC X(38).
      *--------------------------------------------------------------*
      * REARRANCABILIDAD.                                            *
      *--------------------------------------------------------------*
      *-- -Se guarda la informacion relevante para un rearranque, en
      *-- -este caso solo informacion del listado de estadisticas, por
      *-- -que al programa no le hace falta nada para rearrancar correc
      *-- -tamente.
      * @GXINISAV()
       01 WS-AREA-REARRANQUE.
          05 FILLER                  PIC X(10) VALUE 'CAB1040.'.
          05 FILLER                  PIC X(14) VALUE ' REG.LEIDOS.:'.
          05 WS-CONT-LEIDOS          PIC 9(7).
          05 FILLER                  PIC X(14) VALUE ' REG.MODIFIC:'.
          05 WS-CONT-MODIFI          PIC 9(7).
      * @GXFINSAV()
      *-------------------------------------------------------------*
      * LITERALES                                                   *
      *-------------------------------------------------------------*
       01  LT-LITERALES.
           05  LT-B                  PIC X(1)    VALUE 'B'.
           05  LT-A-1                PIC X(1)    VALUE '1'.
           05  LT-UNO                PIC 9(1)    VALUE 1.
           05  LT-N-14               PIC 9(2)    VALUE 14.
           05  LT-N-16               PIC 9(2)    VALUE 16.
           05  LT-N-21016            PIC 9(5)    VALUE 21016.
           05  LT-A-01               PIC X(2)    VALUE '01'.
           05  LT-A-40502            PIC X(5)    VALUE '40502'.
           05  LT-DEBE               PIC X(1)    VALUE 'D'.
           05  LT-HABER              PIC X(1)    VALUE 'H'.
           05  LT-ALTA               PIC X(1)    VALUE 'A'.
           05  LT-CAMARA             PIC X(1)    VALUE 'C'.
           05  LT-CA                 PIC X(2)    VALUE 'CA'.
           05  LT-20                 PIC X(2)    VALUE '20'.
           05  LT-ENCONTRADO         PIC X(10)   VALUE 'ENCONTRADO'.
           05  LT-FECHA-MINIMA       PIC X(10)   VALUE '01.01.0001'.
           05  LT-MOT-FONDOS-INSUF   PIC X(2)    VALUE '06'.
           05  LT-COD-RAD            PIC X(2)    VALUE '07'.
           05  LT-CHEQUE-DEVUELTO      PIC X(30)   VALUE
               'CHEQUE DEVUELTO               '.
           05  LT-SALDO-INSUF          PIC X(40)   VALUE
               'CAMARA ENTRANTE - FONDOS INSUFICIENTES'.
           05  LT-CONCEPTO-DEVOL       PIC X(40)   VALUE
               'DEVOLUCION DE CAMARA ENTRANTE '.
           05  LT-A-PARRAFO1000        PIC X(34)   VALUE
               'PARRAFO 1000-INICIO'.
           05  LT-A-PARRAFO2000        PIC X(34)   VALUE
               'PARRAFO 2000-PROCES'.
           05  LT-A-PARRAFO1100        PIC X(34)   VALUE
               'PARRAFO A1100-OBTENER-HCT'.
           05  LT-A-PARRAFO1200        PIC X(34)   VALUE
               'PARRAFO A1200-ABRIR-CURSOR-EXTR'.
           05  LT-A-PARRAFO1300        PIC X(34)   VALUE
               'PARRAFO A1300-LEER-EXTRAIDOS'.
           05  LT-A-PARRAFO1400        PIC X(34)   VALUE
               'PARRAFO A1400-CERRAR-CURSOR-EXTR'.
           05  LT-A-PARRAFO1500        PIC X(34)   VALUE
               'PARRAFO A1500-ABRIR-CURSOR-PEND'.
           05  LT-A-PARRAFO1600        PIC X(34)   VALUE
               'PARRAFO A1600-LEER-PENDIENTES'.
           05  LT-A-PARRAFO1700        PIC X(34)   VALUE
               'PARRAFO A1700-CERRAR-CURSOR-PEND'.
           05  LT-A-PARRAFO2150        PIC X(34)   VALUE
               'PARRAFO A2150-LEER-FECHA-DEVOL.'.
           05  LT-A-PARRAFO8000        PIC X(34)   VALUE
               'PARRAFO 8000-FINAL'.
           05  LT-A-PARRAFO3100        PIC X(34)   VALUE
               'PARRAFO A3100-OBTENER-DESC-EMPRESA'.
           05  LT-A-PARRAFO9100        PIC X(34)   VALUE
               'PARRAFO A9100-ROLLBACK'.
           05  LT-ERROR-SELECT-T30DOR10 PIC X(38)  VALUE
               'ERROR LEYENDO TABLA T30DOR10'.
           05  LT-ERROR-SELECT-T12JOB34 PIC X(38)  VALUE
               'ERROR LEYENDO TABLA T12JOB34'.
           05  LT-ERROR-AQGETPSI       PIC X(38)   VALUE
               'ERROR EN MACRO GETPARAM'.
           05  LT-ERROR-AQINIENV       PIC X(38)   VALUE
               'ERROR EN MACRO INIENV'.
           05  LT-ERROR-AQININOD       PIC X(38)   VALUE
               'ERROR EN MACRO ININODO'.
           05  LT-ERROR-AQNUEOPE       PIC X(38)   VALUE
               'ERROR EN MACRO NUEVAOPE'.
           05  LT-ERROR-CENTRO         PIC X(38)   VALUE
               'ERROR AL OBTENER DESCRIPCION CENTRO'.
           05  LT-ERROR-PARAM-HORA     PIC X(38)   VALUE
               'ERROR EN OBTENCION DE HORA GENERICA'.
           05  LT-ERROR-LANZAMIENTO.
               10 LT-ERROR-HORA-A      PIC X(30)   VALUE
               'LANZAR LA CAD. DESPUES DE LAS:'.
               10 LT-ERROR-HORA-N      PIC X(8).
           05  LT-ERR-OPEN-CURSOR-EXTR PIC X(38)   VALUE
               'ERROR EN APERTURA DE EXTRAIDOS'.
           05  LT-ERR-OPEN-CURSOR-PEND PIC X(38)   VALUE
               'ERROR EN APERTURA DE PENDIENTES'.
           05  LT-ERROR-EXTRAIDOS      PIC X(38)   VALUE
               'ERROR EN LECTURA DE EXTRAIDOS'.
           05  LT-ERROR-PENDIENTES     PIC X(38)   VALUE
               'ERROR EN LECTURA DE PENDIENTES'.
           05  LT-ERR-CLOSE-CURSOR-EXTR PIC X(38)  VALUE
               'ERROR EN CIERRE DE EXTRAIDOS'.
           05  LT-ERR-CLOSE-CURSOR-PEND PIC X(38)  VALUE
               'ERROR EN CIERRE DE PENDIENTES'.
           05  LT-ERROR-ROLLBACK        PIC X(38)  VALUE
               'ERROR AL HACER ROLLBACK'.
           05  LT-ERROR-TCS05002        PIC X(38)  VALUE
               'ERROR EN SERVICIO TCS05002'.
           05  LT-ERROR-INTER1          PIC X(47)  VALUE
               'ERROR: HAY INTERCAMBIOS PENDIENTES DE LANZADOR.'.
           05  LT-ERROR-INTER2          PIC X(76)  VALUE
             'NO EJECUTAR ESTE PROGRAMA HASTA QUE SE HAYA TERMINADO EL PROCESO DE LANZADOR'.
       01  LT-ERR-GXINIBAT              PIC X(40)   VALUE
            'INICIANDO MACRO (INIBAT).        '.
      *-------------------------------------------------------------*
      * SWITCHES                                                    *
      *-------------------------------------------------------------*
       01  SW-ENCONTRADO             PIC X(2)    VALUE SPACES.
           88  NO-ENCONTRADO                     VALUE 'SI'.
       01  SW-STATUS-FILE            PIC X(2)    VALUE SPACES.
           88  END-OF-FILE                       VALUE 'SI'.
       01  ESTADO-PROCESO            PIC 9(2)    VALUE ZEROS.
           88 PROCESO-OK                         VALUE 00.
           88 PROCESO-WARNING                    VALUE 04.
           88 PROCESO-ERROR                      VALUE 16.
      *-------------------------------------------------------------*
      *  DESCRIPCION DEL INFORME DE ERRORES                         *
	  
	  
      *-------------------------------------------------------------*
       01  CABE-1.
           05  ENTIDAD-N             PIC X(4).
           05  FILLER                PIC X(3)    VALUE ' - '.
           05  ENTIDAD-A             PIC X(30).
           05  FILLER                PIC X(94)   VALUE SPACES.
       01  CABE-2.
           05 FILLER                 PIC X(8)    VALUE 'CAB1040 '.
           05 FILLER                 PIC X(34)   VALUE SPACES.
           05 FILLER                 PIC X(50)   VALUE
           '  D I A G N O S T I C O    D E    E R R O R E S  '.
           05 FILLER                 PIC X(18)   VALUE SPACES.
           05 FILLER                 PIC X(09)   VALUE 'FECHA : '.
           05 DATUM                  PIC X(10)   VALUE SPACES.
       01  CABE-3.
           05 FILLER                 PIC X(1)    VALUE 'L'.
           05 FILLER                 PIC X(2)    VALUE 'CA'.
           05 FILLER                 PIC X(6)    VALUE '1040D2'.
           05 FILLER                 PIC X(34)   VALUE SPACES.
           05 FILLER                 PIC X(47)   VALUE ALL '-'.
           05 FILLER                 PIC X(20)   VALUE SPACES.
           05 FILLER                 PIC X(09)   VALUE 'HORA  :  '.
           05 FILLER                 PIC X(2)    VALUE SPACES.
           05 HOURS                  PIC 9(02).
           05 FILLER                 PIC X(1)    VALUE ':'.
           05 MINUTES                PIC 9(02).
           05 FILLER                 PIC X(1)    VALUE ':'.
           05 SECONDS                PIC 9(02).
       01  CABE-4.
           05 CABE-CENT-RESP         PIC X(4)    VALUE SPACES.
           05 FILLER                 PIC X(1)    VALUE SPACES.
           05 FILLER                 PIC X(1)    VALUE '-'.
           05 FILLER                 PIC X(1)    VALUE SPACES.
           05 CABE-DEL-CENT          PIC X(15)   VALUE SPACES.
           05 FILLER                 PIC X(88)   VALUE SPACES.
           05 FILLER                 PIC X(8)    VALUE 'PAGINA: '.
           05 FILLER                 PIC X(1)    VALUE SPACES.
           05 PAGINA                 PIC ZZZZ.ZZ9.
       01  CABE-5.
           05 FILLER                 PIC X(132)  VALUE SPACES.
       01  CABE-6.
           05 FILLER                 PIC X(24)   VALUE SPACES.
           05 FILLER                 PIC X(10)   VALUE 'COD.ERROR'.
           05 FILLER                 PIC X(9)    VALUE SPACES.
           05 FILLER                 PIC X(12)   VALUE 'DESCRIPCION'.
       01  CABE-7.
           05 FILLER                 PIC X(23)   VALUE SPACES.
           05 FILLER                 PIC X(12)   VALUE ALL '-'.
           05 FILLER                 PIC X(7)    VALUE SPACES.
           05 FILLER                 PIC X(42)   VALUE ALL '-'.
       01  DETAILIMP.
         02  DET-1.
           05 FILLER                 PIC X(24)   VALUE SPACES.
           05 CODIGO                 PIC X(10)   VALUE SPACES.
           05 FILLER                 PIC X(9)    VALUE SPACES.
           05 DESC-ERROR1            PIC X(47)   VALUE SPACES.
           05 FILLER                 PIC X(43)   VALUE SPACES.
         02  DET-2.
           05 FILLER                 PIC X(24)   VALUE SPACES.
           05 FILLER                 PIC X(7)    VALUE SPACES.
           05 FILLER                 PIC X(12)   VALUE SPACES.
           05 DESC-ERROR2            PIC X(76)   VALUE SPACES.
           05 FILLER                 PIC X(14)   VALUE SPACES.
      *-------------------------------------------------------------*
      *  DESCRIPCION DEL INFORME DE ESTADISTICAS                    *
      *-------------------------------------------------------------*
       01  CABE-2E.
           05 FILLER                 PIC X(8)    VALUE 'CAB1040 '.
           05 FILLER                 PIC X(34)   VALUE SPACES.
           05 FILLER                 PIC X(50)   VALUE
           ' L I S T A D O    D E    E S T A D I S T I C A S  '.
           05 FILLER                 PIC X(18)   VALUE SPACES.
           05 FILLER                 PIC X(09)   VALUE 'FECHA : '.
           05 DATUM                  PIC X(10)   VALUE SPACES.
       01  CABE-3E.
           05 FILLER                 PIC X(1)    VALUE 'L'.
           05 FILLER                 PIC X(2)    VALUE 'CA'.
           05 FILLER                 PIC X(6)    VALUE '1040D1'.
           05 FILLER                 PIC X(34)   VALUE SPACES.
           05 FILLER                 PIC X(47)   VALUE ALL '-'.
           05 FILLER                 PIC X(20)   VALUE SPACES.
           05 FILLER                 PIC X(09)   VALUE 'HORA  :  '.
           05 FILLER                 PIC X(2)    VALUE SPACES.
           05 HOURS                  PIC 9(02).
           05 FILLER                 PIC X(1)    VALUE ':'.
           05 MINUTES                PIC 9(02).
           05 FILLER                 PIC X(1)    VALUE ':'.
           05 SECONDS                PIC 9(02).
       01  CABE-4E.
           05 CENTRO-N               PIC X(4)    VALUE SPACES.
           05 FILLER                 PIC X(1)    VALUE SPACES.
           05 FILLER                 PIC X(1)    VALUE '-'.
           05 FILLER                 PIC X(1)    VALUE SPACES.
           05 CENTRO-A               PIC X(40)   VALUE SPACES.
           05 FILLER                 PIC X(63)   VALUE SPACES.
           05 FILLER                 PIC X(8)    VALUE 'PAGINA: '.
           05 FILLER                 PIC X(1)    VALUE SPACES.
           05 PAGINA                 PIC 9(1)    VALUE 1.
       01  CABE-5E.
           05 FILLER                 PIC X(132)  VALUE ALL '='.
       01  DET-LEIDOS.
           05 FILLER                 PIC X(41)   VALUE SPACES.
           05 FILLER                 PIC X(46)   VALUE
             'NUMERO DE CHEQUES PENDIENTES LEIDOS ....... : '.
           05 REG-LEIDOS             PIC Z.ZZZ.ZZ9.
       01  DET-DEVUELTOS.
           05 FILLER                 PIC X(41)   VALUE SPACES.
           05 FILLER                 PIC X(46)   VALUE
             'NUMERO DE CHEQUES DEVUELTOS EN CAB1040 .... : '.
           05 REG-DEVUELTOS          PIC Z.ZZZ.ZZ9.
      *-------------------------------------------------------------*
      * INCLUDE DE TABLAS                                           *
      *-------------------------------------------------------------*

      *--- Include de la tabla de cheques recibidos

           EXEC SQL
                INCLUDE T30DOR10
           END-EXEC.


      *--- Include de la tabla de incidencias

           EXEC SQL
                INCLUDE T12INC06
           END-EXEC.


      *--- Include de la tabla que contiene nombre de programa, centro
      *--- origen y centro operativo

           EXEC SQL
                INCLUDE T12JOB34
           END-EXEC.


      *--- Include de la tabla de cheques considerados

           EXEC SQL
                INCLUDE T30RCI01
           END-EXEC.


      *--- Include de la tabla de parametros

           EXEC SQL
                INCLUDE T06TC002
           END-EXEC.


      *--- Include de la tabla de talonarios cheques

           EXEC SQL
                INCLUDE T12TAL17
           END-EXEC.


      *-------------------------------------------------------------*
      * DECLARACION DEL CURSOR SOBRE LA TABLA T12INC06 PARA OBTENER *
      * LOS CHEQUES Y PAGARES RECIBIDOS CON ESTADO DE LA INCIDENCIA *
      * "EXTRAIDO"                                                  *
      *-------------------------------------------------------------*

           EXEC SQL
                DECLARE CURSOR-EXTR CURSOR WITH HOLD FOR
                SELECT
                   COD_CENT_DEST,
                   NUM_INCID,
                   NUM_TRASP_INCID,
                   NUM_SEC_PP,
                   COD_EMPRESA,
                   COD_INCID,
                   FEC_VENCIMIENTO,
                   HOR_VTO,
                   FEC_OPERACION,
                   FEC_VALOR,
                   CLA_INCID,
                   IMP_MOVIMIENTO,
                   IMP_PENDIENTE,
                   IND_NATURALEZA,
                   DEL_CONCEPTO,
                   COD_REFER,
                   COD_PROCED,
                   COD_EMPOR,
                   COD_CENT_ORIG,
                   COD_CENTRO,
                   COD_ENTIDAD,
                   COD_SUCURSAL,
                   COD_DIG_CONTROL,
                   NUM_CTA,
                   COD_EST_INCID,
                   COD_MONEDA,
                   IND_EXIS_DOC,
                   IND_DEV_AUTO,
                   IND_AVISO,
                   IND_REINT,
                   COD_EMIS_DOM,
                   DEL_EMIS_DOMIC,
                   FEC_EMISION,
                   COD_REF_ABON,
                   COD_ENT_DOM,
                   COD_SUC_DOM,
                   COD_CLA_DOM,
                   NUM_CTA_DOM,
                   NOM_LOCALIDAD,
                   NUM_SEC_EMIS,
                   NOM_COMPACTADO,
                   NUM_SICA,
                   COD_ENT_SICA,
                   DEC_SUCURSAL,
                   ORDENANTE_MOVIMIEN,
                   BENEFICIARIO_MOVIM,
                   TXT_BENEF,
                   NUMERO_DOCUMENTO,
                   COD_REF_DOC,
                   FEC_RESOL,
                   COD_DOMINIO,
                   NUM_NODO,
                   NUM_MENSAJE,
                   COD_USUARIO_RES,
                   HOR_RESOL,
                   COD_RESOL,
                   DEL_CONCEPTO2,
                   FEC_VALOR2,
                   COD_REFERENCIA2,
                   COD_NUM_DOC_OFICIA,
                   COD_LETRA_NIF,
                   COD_CENT_FTRAS,
                   COD_ENT_CT_RES,
                   COD_SUC_CT_RES,
                   COD_CLV_RESOL,
                   NUM_CTA_RES,
                   IMP_RESOL,
                   CLA_RESOL,
                   IND_RETRO_INC,
                   COD_OPER_ENC,
                   TIMESTAMP_SIGLO,
                   IND_MOD_TABLA,
                   IMP_MOVTO_ORIG,
                   D_IMP_MOVTO_ORIG,
                   F_IMP_MOVTO_ORIG,
                   T_IMP_MOVTO_ORIG,
                   C_IMP_MOVTO_ORIG,
                   TIPCTA,
                   NUM_CT_CONT_CREA,
                   COD_CENTIM,
                   NUM_CT_CONT_RESOL,
                   COD_CENTIM1,
                   COD_DOMINIO2,
                   NUM_NODO2,
                   NUM_MENSAJE2,
                   COD_USU_ALTA,
                   D_IMP_RESOL,
                   F_IMP_RESOL,
                   T_IMP_RESOL,
                   C_IMP_RESOL
                FROM T12INC06
                WHERE (COD_INCID      = :WS-COD-INCID    OR
                       COD_INCID      = :WS-COD-INCID1)  AND
                       COD_EST_INCID  = :WS-LT-EXTRAIDO
           END-EXEC.


      *-------------------------------------------------------------*
      * DECLARACION DEL CURSOR SOBRE LA TABLA T12INC06 PARA OBTENER *
      * LOS CHEQUES Y PAGARES RECIBIDOS CON ESTADO DE LA INCIDENCIA *
      * "PENDIENTE " O "VENCIDO PENDIENTE"                          *
      *-------------------------------------------------------------*

      *--  WGUERRE  13.04.2004
      *--  No tomar los registros generados para la consideracion de
      *--  la Notas de Debito.
           EXEC SQL
                DECLARE CURSOR-PEND CURSOR WITH HOLD FOR
                SELECT
                   COD_CENT_DEST,
                   NUM_INCID,
                   NUM_TRASP_INCID,
                   NUM_SEC_PP,
                   COD_EMPRESA,
                   COD_INCID,
                   FEC_VENCIMIENTO,
                   HOR_VTO,
                   FEC_OPERACION,
                   FEC_VALOR,
                   CLA_INCID,
                   IMP_MOVIMIENTO,
                   IMP_PENDIENTE,
                   IND_NATURALEZA,
                   DEL_CONCEPTO,
                   COD_REFER,
                   COD_PROCED,
                   COD_EMPOR,
                   COD_CENT_ORIG,
                   COD_CENTRO,
                   COD_ENTIDAD,
                   COD_SUCURSAL,
                   COD_DIG_CONTROL,
                   NUM_CTA,
                   COD_EST_INCID,
                   COD_MONEDA,
                   IND_EXIS_DOC,
                   IND_DEV_AUTO,
                   IND_AVISO,
                   IND_REINT,
                   COD_EMIS_DOM,
                   DEL_EMIS_DOMIC,
                   FEC_EMISION,
                   COD_REF_ABON,
                   COD_ENT_DOM,
                   COD_SUC_DOM,
                   COD_CLA_DOM,
                   NUM_CTA_DOM,
                   NOM_LOCALIDAD,
                   NUM_SEC_EMIS,
                   NOM_COMPACTADO,
                   NUM_SICA,
                   COD_ENT_SICA,
                   DEC_SUCURSAL,
                   ORDENANTE_MOVIMIEN,
                   BENEFICIARIO_MOVIM,
                   TXT_BENEF,
                   NUMERO_DOCUMENTO,
                   COD_REF_DOC,
                   FEC_RESOL,
                   COD_DOMINIO,
                   NUM_NODO,
                   NUM_MENSAJE,
                   COD_USUARIO_RES,
                   HOR_RESOL,
                   COD_RESOL,
                   DEL_CONCEPTO2,
                   FEC_VALOR2,
                   COD_REFERENCIA2,
                   COD_NUM_DOC_OFICIA,
                   COD_LETRA_NIF,
                   COD_CENT_FTRAS,
                   COD_ENT_CT_RES,
                   COD_SUC_CT_RES,
                   COD_CLV_RESOL,
                   NUM_CTA_RES,
                   IMP_RESOL,
                   CLA_RESOL,
                   IND_RETRO_INC,
                   COD_OPER_ENC,
                   TIMESTAMP_SIGLO,
                   IND_MOD_TABLA,
                   IMP_MOVTO_ORIG,
                   D_IMP_MOVTO_ORIG,
                   F_IMP_MOVTO_ORIG,
                   T_IMP_MOVTO_ORIG,
                   C_IMP_MOVTO_ORIG,
                   TIPCTA,
                   NUM_CT_CONT_CREA,
                   COD_CENTIM,
                   NUM_CT_CONT_RESOL,
                   COD_CENTIM1,
                   COD_DOMINIO2,
                   NUM_NODO2,
                   NUM_MENSAJE2,
                   COD_USU_ALTA,
                   D_IMP_RESOL,
                   F_IMP_RESOL,
                   T_IMP_RESOL,
                   C_IMP_RESOL
                FROM T12INC06
                WHERE (COD_INCID     = :WS-COD-INCID     OR
                       COD_INCID     = :WS-COD-INCID1)   AND
                      (COD_EST_INCID = :WS-LT-PENDIENTE  OR
                       COD_EST_INCID = :WS-LT-VENC-PEND) AND
                       FEC_VENCIMIENTO <= :WS-FEM-HOY    AND
                       COD_REF_DOC     <> '41680'        AND
                      (NUM_CTA    BETWEEN :WS-CTA-INI AND
                                          :WS-CTA-FIN)
                ORDER BY COD_CENT_ORIG
           END-EXEC.
      *--  WGUERRE  13.04.2004



      ****************************************************************
      ****************************************************************
      ** L I N K A G E  S E C T I O N                               **
      ****************************************************************
      ****************************************************************
       LINKAGE SECTION.



      ****************************************************************
      ****************************************************************
      ** USER PROCEDURE DIVISION                                    **
      ****************************************************************
      ****************************************************************
       PROCEDURE DIVISION.

      **INICIO-PROGRAMA-CAB1040
           PERFORM 1000-INICIO.
           PERFORM 2000-PROCESO UNTIL NO-ENCONTRADO.
           PERFORM 8000-FINAL.
      **FINAL-PROGRAMA-CAB1040


      ****************************************************************
      **  1000-INICIO.                                              **
      **------------------------------------------------------------**
      ** -El control de los errores de DB2 se pasa a la aplicacion. **
      ** -El control de los servicios  se pasa a la aplicacion.     **
      ** -Se incrementa el numero de mensaje y se inicializa el     **
      **     identificador de la operacion.                         **
      ** -Se inicializa el numero de nodo.                          **
      ** -Se abre listado de estadisticas.                          **
      ** -Se inicializa la aqbf y variables de entorno.             **
      ** -Se obtiene el HTC y el TIMESTAMP del momento del lanza-   **
      **     miento de la cadena. si el timestamp del momento es    **
      **     mayor que el HTC, se para el proceso.                  **
      ** -Se llama al servico de obtencion de parametros para recu- **
      **     perar en centro de compensacion.                       **
      ** -Se abren cursores.                                        **
      ** -Se comprueba si en la tabla de incidencias hay cheques    **
      **     extraidos. si es asi, se genera un listado de errores  **
      **     y se para el proceso hasta que acabe el lanzador.      **
      ** -Se leen todos los cheques que esten pendientes o vencidos **
      **     pendientes y se tratan.                                **
      ****************************************************************
       1000-INICIO.

           INITIALIZE RETURN-CODE.
      *----> Anulacion del control de errores de DB2
           @DEFINE(NO-ERROSQL).

      *----> Gestionar errores de servicios invocados
           @CTRLERR(APLICACION).

      *--  -- Se obtiene la fecha de proceso
           EXEC SQL
                SELECT TO_CHAR(CURRENT_DATE,'YYYY-MM-DD')
                  INTO :WS-FECHA-PROC
                  FROM DUAL
           END-EXEC.
           display 'CAB1040 -fecha-proc ' WS-FECHA-PROC 


           @INIBAT()

           IF TIPO-ERROR OF S21-AREA-ERROR > ZEROS
              SET PROCESO-ERROR       TO TRUE
               MOVE NUM-ERROR OF S21-AREA-ERROR TO WS-ERROR
	      @LOGERR(ERROR,WS-ERROR,LT-ERR-GXINIBAT)
           END-IF.


      *----> Inicializacion de Numnodo para la grabacion en RAD
           @ININODO()

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
               MOVE LT-A-PARRAFO1000  TO WS-PARRAFO
               MOVE LT-ERROR-AQININOD TO WS-TEXTO
               MOVE NUM-ERROR OF S21-AREA-ERROR TO WS-ERROR
	       @ERROR(ERROR,WS-ERROR,AREA-INFORMACION)
           END-IF.

           EXEC SQL
                COMMIT
           END-EXEC.

           MOVE ZEROS TO WS-CONT-LEIDOS
                         WS-CONT-MODIFI.

      *----> Se abre listado de estadisticas.
           OPEN OUTPUT  IMPRES01.

           MOVE COD-EMPRESA  OF S21-AREA-ENTORNO TO WS-COD-EMPRESA.
           MOVE COD-CENTRO   OF S21-AREA-ENTORNO TO WS-COD-CENTRO.
           MOVE FEM-CONTABLE OF S21-AREA-ENTORNO TO WS-FEM-CONTABLE.
           MOVE FEM-MAQUINA  OF S21-AREA-ENTORNO TO WS-FEM-MAQUINA.


      *--  -Espacios a la variable de control de cambio de centro
      *--  -origen del intercambio (el centro gestor de la camara donde
      *--  -se recibio el cheque).
           MOVE SPACES       TO WS-CENTRO.

           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO FEM-OPERACION        OF S21-AREA-ENTORNO.

           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO WS-FEM-HOY.

           MOVE WS-A-PROGRAMA
             TO COD-USUARIO          OF S21-AREA-ENTORNO.

      *----> Se obtiene el HCT y el timestamp del momento
           PERFORM A1100-OBTENER-HCT.

           PERFORM A1110-OBTENER-TIMESTAMP-MTO.

      *     IF WS-TIMESTAMPSIGLO2 > WS-TIMESTAMPSIGLO3

      *         MOVE LT-A-PARRAFO1000 TO WS-PARRAFO

      *         MOVE HOR-GENERICA     OF MSG-OUT-PAS43001(1)
      *           TO LT-ERROR-HORA-N

      *         MOVE LT-ERROR-LANZAMIENTO TO WS-TEXTO
      *         SET  LT-NO-HORA-CIERRE    TO TRUE
      *         @ERROR(ERROR,WS-PA-NUM-ERROR,AREA-INFORMACION)
      *     END-IF.

      *----> Se formatea el mensaje de entrada de PAS43001
      *----> para obtener el centro de compensacion
           MOVE 'V'
             TO ACC-SERV             OF MSG-IN-PAS43001.

           MOVE '0'
             TO IND-TIPO-LIS         OF MSG-IN-PAS43001.

           MOVE LT-20
             TO COD-SUBSIS           OF MSG-IN-PAS43001.

           MOVE 4
             TO NUM-PARAM            OF MSG-IN-PAS43001.

           MOVE COD-EMPRESA          OF S21-AREA-ENTORNO
             TO COD-EMPRESA          OF MSG-IN-PAS43001.


            @INVOCAR(PAS43001,B)

           MOVE NUMERO               OF MSG-OUT-PAS43001(1)
             TO NUMERO-NUM.

           MOVE WS-NUMERO-NUM        TO WS-COD-CENT-COMP.

           PERFORM A1200-ABRIR-CURSOR-EXTR.

           PERFORM A1300-LEER-EXTRAIDOS.

      *----> Si existe algun registro en el cursor significa que hay
      *----> alguna incidencia que se esta preocesando por el lanzador
      *----> de operaciones y no se debe continuar con la ejecucion de
      *----> este proceso.

           EVALUATE TRUE

               WHEN IND-SQL-CORRECTO
                 IF COD-EMPRESA OF T12INC06 = COD-EMPRESA OF
                                              S21-AREA-ENTORNO

                     MOVE LT-ENCONTRADO      TO CODIGO
                     MOVE LT-ERROR-INTER1    TO DESC-ERROR1
                     MOVE LT-ERROR-INTER2    TO DESC-ERROR2
                     PERFORM A3000-OBTENER-LISTADO
                     MOVE LT-A-PARRAFO1300   TO WS-PARRAFO
                     MOVE LT-ERROR-EXTRAIDOS TO WS-TEXTO
                     @ERROR(ERROR,00999,AREA-INFORMACION)
                 END-IF

               WHEN IND-NO-ENCONTRADO
                     CONTINUE

               WHEN OTHER
                     MOVE LT-A-PARRAFO1300   TO WS-PARRAFO
                     MOVE LT-ERROR-EXTRAIDOS TO WS-TEXTO
                     @ERROR(ERROR,SQLCODE,AREA-INFORMACION)

           END-EVALUATE.

           PERFORM A1800-OBTENER-CABE-ESTAD.

           PERFORM A1400-CERRAR-CURSOR-EXTR.

           PERFORM A1450-OBTIENE-RANGO.

           PERFORM A1500-ABRIR-CURSOR-PEND.

           PERFORM A1600-LEER-PENDIENTES.

           MOVE COD-CENT-ORIG    OF T12INC06
             TO COD-CENTRO       OF S21-AREA-ENTORNO.


      *--------------------------------------------------------------*
      * -SE LLAMA AL SERVICIO DE OBTENCION DE PARAMETROS PARA RECU-  *
      *  PERAR LA HORA GENRICA.                                      *
      * -SE FORMATEA EL TIMESTAMPSIGLO2 A PARTIR DE LA FECHA DEL DIA *
      *  Y DE LA HORA GENERICA OBTENIDA EN EL SERVICIO PAS43001.     *
      * -EL VALOR OBTENIDO SE GUARDA EN LA VARIABLE HOST WS-TIMESTAMP*
      *  SIGLO2.                                                     *
      *--------------------------------------------------------------*
       A1100-OBTENER-HCT.

      *----->Se obtiene la hora generica de cierre del truncamiento
           MOVE 'V'
             TO ACC-SERV             OF MSG-IN-PAS43001.

           MOVE '0'
             TO IND-TIPO-LIS         OF MSG-IN-PAS43001.

           MOVE COD-EMPRESA          OF S21-AREA-ENTORNO
             TO COD-EMPRESA          OF MSG-IN-PAS43001.

           MOVE LT-CA
             TO COD-SUBSIS           OF MSG-IN-PAS43001.

           MOVE 1
             TO NUM-PARAM            OF MSG-IN-PAS43001.


            @INVOCAR(PAS43001,B)

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
               MOVE LT-A-PARRAFO1100    TO WS-PARRAFO
               MOVE LT-ERROR-PARAM-HORA TO WS-TEXTO
               @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.

      *----> Se formatea el timestamp.
           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO FECHA-DMA.

           MOVE DIA-DMA              TO DIA.
           MOVE MES-DMA              TO MES.
           MOVE ANNO-DMA             TO ANNO.

           MOVE HOR-GENERICA         OF MSG-OUT-PAS43001(1)
             TO HORA-AUX-2.
           display 'CAB1040 PAS43001 HORA '   
                      HOR-GENERICA OF MSG-OUT-PAS43001(1)

           MOVE HORA-2    OF HORA-AUX-2 TO HORA    OF HORA-AUX.
           MOVE MINUTO-2  OF HORA-AUX-2 TO MINUTO  OF HORA-AUX.
           MOVE SEGUNDO-2 OF HORA-AUX-2 TO SEGUNDO OF HORA-AUX.

           MOVE ZEROS     TO TIMESTAMP-RESTO.
           MOVE TIMESTAMP-AUX        TO WS-TIMESTAMPSIGLO2.


      *--------------------------------------------------------------*
      * -SE FORMATEA TIMESTAMP-HOY CON LA FECHA DEL DIA Y LA HORA DE *
      *     EJECUCION DE LA CADENA.                                  *
      *--------------------------------------------------------------*
       A1110-OBTENER-TIMESTAMP-MTO.

           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO FECHA-DMA.

           MOVE DIA-DMA              TO DIA-HOY.
           MOVE MES-DMA              TO MES-HOY.
           MOVE ANNO-DMA             TO ANNO-HOY.

           MOVE HOR-MAQUINA          OF S21-AREA-ENTORNO
             TO WS-TIEMPO.

           MOVE WS-HORA              TO HORA-HOY.
           MOVE WS-MINUTOS           TO MINUTO-HOY.
           MOVE WS-SEGUNDOS          TO SEGUNDO-HOY.

           MOVE WS-TIMESTAMP-HOY     TO WS-TIMESTAMPSIGLO3.


      ****************************************************************
      ** SE ABRE CURSOR DE EXTRAIDOS                                **
      ****************************************************************
       A1200-ABRIR-CURSOR-EXTR.

           MOVE LT-N-14  TO WS-COD-INCID.
           MOVE LT-N-16  TO WS-COD-INCID1.

           EXEC SQL
               OPEN CURSOR-EXTR
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           display 'A1200 RC-OPN-CUR-EXTR ' SQLCODE ' ' SQLSTATE

           IF NOT IND-SQL-CORRECTO
               MOVE LT-ERR-OPEN-CURSOR-EXTR TO WS-TEXTO
               MOVE LT-A-PARRAFO1200        TO WS-PARRAFO
               @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      ** SE LEEN LOS REGISTROS EXTRAIDOS                            **
      ****************************************************************
       A1300-LEER-EXTRAIDOS.

           EXEC SQL
                 FETCH CURSOR-EXTR
                 INTO
                    :T12INC06.COD-CENT-DEST,
                    :T12INC06.NUM-INCID,
                    :T12INC06.NUM-TRASP-INCID,
                    :T12INC06.NUM-SEC-PP,
                    :T12INC06.COD-EMPRESA,
                    :T12INC06.COD-INCID,
                    :T12INC06.FEC-VENCIMIENTO,
                    :T12INC06.HOR-VTO,
                    :T12INC06.FEC-OPERACION,
                    :T12INC06.FEC-VALOR,
                    :T12INC06.CLA-INCID,
                    :T12INC06.IMP-MOVIMIENTO,
                    :T12INC06.IMP-PENDIENTE,
                    :T12INC06.IND-NATURALEZA,
                    :T12INC06.DEL-CONCEPTO,
                    :T12INC06.COD-REFER,
                    :T12INC06.COD-PROCED,
                    :T12INC06.COD-EMPOR,
                    :T12INC06.COD-CENT-ORIG,
                    :T12INC06.COD-CENTRO,
                    :T12INC06.COD-ENTIDAD,
                    :T12INC06.COD-SUCURSAL,
                    :T12INC06.COD-DIG-CONTROL,
                    :T12INC06.NUM-CTA,
                    :T12INC06.COD-EST-INCID,
                    :T12INC06.COD-MONEDA,
                    :T12INC06.IND-EXIS-DOC,
                    :T12INC06.IND-DEV-AUTO,
                    :T12INC06.IND-AVISO,
                    :T12INC06.IND-REINT,
                    :T12INC06.COD-EMIS-DOM,
                    :T12INC06.DEL-EMIS-DOMIC,
                    :T12INC06.FEC-EMISION,
                    :T12INC06.COD-REF-ABON,
                    :T12INC06.COD-ENT-DOM,
                    :T12INC06.COD-SUC-DOM,
                    :T12INC06.COD-CLA-DOM,
                    :T12INC06.NUM-CTA-DOM,
                    :T12INC06.NOM-LOCALIDAD,
                    :T12INC06.NUM-SEC-EMIS,
                    :T12INC06.NOM-COMPACTADO,
                    :T12INC06.NUM-SICA,
                    :T12INC06.COD-ENT-SICA,
                    :T12INC06.DEC-SUCURSAL,
                    :T12INC06.ORDENANTE-MOVIMIEN,
                    :T12INC06.BENEFICIARIO-MOVIM,
                    :T12INC06.TXT-BENEF,
                    :T12INC06.NUMERO-DOCUMENTO,
                    :T12INC06.COD-REF-DOC,
                    :T12INC06.FEC-RESOL,
                    :T12INC06.COD-DOMINIO,
                    :T12INC06.NUM-NODO,
                    :T12INC06.NUM-MENSAJE,
                    :T12INC06.COD-USUARIO-RES,
                    :T12INC06.HOR-RESOL,
                    :T12INC06.COD-RESOL,
                    :T12INC06.DEL-CONCEPTO2,
                    :T12INC06.FEC-VALOR2,
                    :T12INC06.COD-REFERENCIA2,
                    :T12INC06.COD-NUM-DOC-OFICIA,
                    :T12INC06.COD-LETRA-NIF,
                    :T12INC06.COD-CENT-FTRAS,
                    :T12INC06.COD-ENT-CT-RES,
                    :T12INC06.COD-SUC-CT-RES,
                    :T12INC06.COD-CLV-RESOL,
                    :T12INC06.NUM-CTA-RES,
                    :T12INC06.IMP-RESOL,
                    :T12INC06.CLA-RESOL,
                    :T12INC06.IND-RETRO-INC,
                    :T12INC06.COD-OPER-ENC,
                    :T12INC06.TIMESTAMP-SIGLO,
                    :T12INC06.IND-MOD-TABLA,
                    :T12INC06.IMP-MOVTO-ORIG,
                    :T12INC06.D-IMP-MOVTO-ORIG,
                    :T12INC06.F-IMP-MOVTO-ORIG,
                    :T12INC06.T-IMP-MOVTO-ORIG,
                    :T12INC06.C-IMP-MOVTO-ORIG,
                    :T12INC06.TIPCTA,
                    :T12INC06.NUM-CT-CONT-CREA,
                    :T12INC06.COD-CENTIM,
                    :T12INC06.NUM-CT-CONT-RESOL,
                    :T12INC06.COD-CENTIM1,
                    :T12INC06.COD-DOMINIO2,
                    :T12INC06.NUM-NODO2,
                    :T12INC06.NUM-MENSAJE2,
                    :T12INC06.COD-USU-ALTA,
                    :T12INC06.D-IMP-RESOL,
                    :T12INC06.F-IMP-RESOL,
                    :T12INC06.T-IMP-RESOL,
                    :T12INC06.C-IMP-RESOL
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           display 'A1300-Fecth code: ' SQLCODE  ' ' SQLSTATE.      


      ****************************************************************
      ** SE CIERRA CURSOR DE EXTRAIDOS                              **
      ****************************************************************
       A1400-CERRAR-CURSOR-EXTR.

           EXEC SQL
               CLOSE CURSOR-EXTR
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           display 'A1400 RC-CLS-CUR-EXTR ' SQLCODE ' ' SQLSTATE.

           IF NOT IND-SQL-CORRECTO
              MOVE LT-ERR-CLOSE-CURSOR-EXTR TO WS-TEXTO
              MOVE LT-A-PARRAFO1400         TO WS-PARRAFO
              @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      ** Se obtiene rango de ejecución                              **
      ****************************************************************
       A1450-OBTIENE-RANGO.
           OPEN INPUT FICCON01.
           IF FS-FIC01 NOT EQUAL '00'
              STRING 'ERR EN FICCON FS: ' 
                      FS-FIC01
                      DELIMITED BY SIZE
                 INTO WS-TEXTO
              MOVE 8 TO RETURN-CODE
              MOVE 'A1450-OBTIENE-RANGOS '  TO WS-PARRAFO
              @ERROR(ERROR,33445,AREA-INFORMACION)
           END-IF.
           
           READ FICCON01 INTO REG-FICCON AT END
              STRING 'ERR AL LEER FICCON FS: ' 
                      FS-FIC01
                      DELIMITED BY SIZE
                 INTO WS-TEXTO
              MOVE 8        TO RETURN-CODE
              MOVE 'A1450-OBTIENE-RANGOS '  TO WS-PARRAFO
              @ERROR(ERROR,33446,AREA-INFORMACION)
           END-READ.
           IF FS-FIC01 NOT EQUAL '00' AND '97'
              STRING 'ERR AL LEER1 FICCON FS: ' 
                      FS-FIC01
                      DELIMITED BY SIZE
                 INTO WS-TEXTO
              MOVE 8        TO RETURN-CODE
              MOVE 'A1450-OBTIENE-RANGOS '  TO WS-PARRAFO
              @ERROR(ERROR,33446,AREA-INFORMACION)
           END-IF.

           CLOSE FICCON01.

           display 'A1450-Rango recibido: ' WS-RANGO.

           EXEC SQL
               SELECT DEL_REGISTRO
                 INTO :WS-DEL-REGISTRO
                 FROM T06TC002
                WHERE COD_TABLA_ID    = 'CARANGOS'
                  AND COD_IDIOMA      = '1'
                  AND CODIGO_REGISTRO = :WS-RANGO
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           display 'A1450-Despues select t06tc002 sql: ' SQLCODE
           ' ' SQLSTATE  '  Datos del rango: ' WS-DEL-REGISTRO

           IF NOT IND-SQL-CORRECTO
              MOVE 'ERR AL OBTENER RANGOS'  TO WS-TEXTO
              MOVE 'A1450-OBTIENE-RANGOS '  TO WS-PARRAFO
              @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      ** SE ABRE CURSOR DE PENDIENTES O VENCIDOS PENDIENTES         **
      ****************************************************************
       A1500-ABRIR-CURSOR-PEND.
           display 'A1500-Fecha hoy     : ' ws-fem-hoy
                   'Cuenta Inicial: ' ws-cuenta-ini
                   'Cuenta Final  : ' ws-cuenta-fin
           
           MOVE WS-CUENTA-INI   TO WS-CTA-INI
           MOVE WS-CUENTA-FIN   TO WS-CTA-FIN
           
           MOVE LT-N-14  TO WS-COD-INCID.
           MOVE LT-N-16  TO WS-COD-INCID1.

           EXEC SQL
               OPEN CURSOR-PEND
           END-EXEC.
           
           MOVE SQLSTATE TO SQLSTATE-SIGLO.
           display 'A1500 Open sql: ' SQLCODE ' ' SQLSTATE.

           IF NOT IND-SQL-CORRECTO
              MOVE LT-ERR-OPEN-CURSOR-PEND TO WS-TEXTO
              MOVE LT-A-PARRAFO1500         TO WS-PARRAFO
              @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      ** SE LEEN LOS REGISTROS PENDIENTES O VENCIDOS PENDIENTES     **
      ****************************************************************
       A1600-LEER-PENDIENTES.

           EXEC SQL
                 FETCH CURSOR-PEND
                 INTO
                    :T12INC06.COD-CENT-DEST,
                    :T12INC06.NUM-INCID,
                    :T12INC06.NUM-TRASP-INCID,
                    :T12INC06.NUM-SEC-PP,
                    :T12INC06.COD-EMPRESA,
                    :T12INC06.COD-INCID,
                    :T12INC06.FEC-VENCIMIENTO,
                    :T12INC06.HOR-VTO,
                    :T12INC06.FEC-OPERACION,
                    :T12INC06.FEC-VALOR,
                    :T12INC06.CLA-INCID,
                    :T12INC06.IMP-MOVIMIENTO,
                    :T12INC06.IMP-PENDIENTE,
                    :T12INC06.IND-NATURALEZA,
                    :T12INC06.DEL-CONCEPTO,
                    :T12INC06.COD-REFER,
                    :T12INC06.COD-PROCED,
                    :T12INC06.COD-EMPOR,
                    :T12INC06.COD-CENT-ORIG,
                    :T12INC06.COD-CENTRO,
                    :T12INC06.COD-ENTIDAD,
                    :T12INC06.COD-SUCURSAL,
                    :T12INC06.COD-DIG-CONTROL,
                    :T12INC06.NUM-CTA,
                    :T12INC06.COD-EST-INCID,
                    :T12INC06.COD-MONEDA,
                    :T12INC06.IND-EXIS-DOC,
                    :T12INC06.IND-DEV-AUTO,
                    :T12INC06.IND-AVISO,
                    :T12INC06.IND-REINT,
                    :T12INC06.COD-EMIS-DOM,
                    :T12INC06.DEL-EMIS-DOMIC,
                    :T12INC06.FEC-EMISION,
                    :T12INC06.COD-REF-ABON,
                    :T12INC06.COD-ENT-DOM,
                    :T12INC06.COD-SUC-DOM,
                    :T12INC06.COD-CLA-DOM,
                    :T12INC06.NUM-CTA-DOM,
                    :T12INC06.NOM-LOCALIDAD,
                    :T12INC06.NUM-SEC-EMIS,
                    :T12INC06.NOM-COMPACTADO,
                    :T12INC06.NUM-SICA,
                    :T12INC06.COD-ENT-SICA,
                    :T12INC06.DEC-SUCURSAL,
                    :T12INC06.ORDENANTE-MOVIMIEN,
                    :T12INC06.BENEFICIARIO-MOVIM,
                    :T12INC06.TXT-BENEF,
                    :T12INC06.NUMERO-DOCUMENTO,
                    :T12INC06.COD-REF-DOC,
                    :T12INC06.FEC-RESOL,
                    :T12INC06.COD-DOMINIO,
                    :T12INC06.NUM-NODO,
                    :T12INC06.NUM-MENSAJE,
                    :T12INC06.COD-USUARIO-RES,
                    :T12INC06.HOR-RESOL,
                    :T12INC06.COD-RESOL,
                    :T12INC06.DEL-CONCEPTO2,
                    :T12INC06.FEC-VALOR2,
                    :T12INC06.COD-REFERENCIA2,
                    :T12INC06.COD-NUM-DOC-OFICIA,
                    :T12INC06.COD-LETRA-NIF,
                    :T12INC06.COD-CENT-FTRAS,
                    :T12INC06.COD-ENT-CT-RES,
                    :T12INC06.COD-SUC-CT-RES,
                    :T12INC06.COD-CLV-RESOL,
                    :T12INC06.NUM-CTA-RES,
                    :T12INC06.IMP-RESOL,
                    :T12INC06.CLA-RESOL,
                    :T12INC06.IND-RETRO-INC,
                    :T12INC06.COD-OPER-ENC,
                    :T12INC06.TIMESTAMP-SIGLO,
                    :T12INC06.IND-MOD-TABLA,
                    :T12INC06.IMP-MOVTO-ORIG,
                    :T12INC06.D-IMP-MOVTO-ORIG,
                    :T12INC06.F-IMP-MOVTO-ORIG,
                    :T12INC06.T-IMP-MOVTO-ORIG,
                    :T12INC06.C-IMP-MOVTO-ORIG,
                    :T12INC06.TIPCTA,
                    :T12INC06.NUM-CT-CONT-CREA,
                    :T12INC06.COD-CENTIM,
                    :T12INC06.NUM-CT-CONT-RESOL,
                    :T12INC06.COD-CENTIM1,
                    :T12INC06.COD-DOMINIO2,
                    :T12INC06.NUM-NODO2,
                    :T12INC06.NUM-MENSAJE2,
                    :T12INC06.COD-USU-ALTA,
                    :T12INC06.D-IMP-RESOL,
                    :T12INC06.F-IMP-RESOL,
                    :T12INC06.T-IMP-RESOL,
                    :T12INC06.C-IMP-RESOL
           END-EXEC.

           MOVE SQLSTATE  TO SQLSTATE-SIGLO.
           display 'A1600 RC-CUR-INC ' SQLCODE ' ' SQLSTATE

           EVALUATE TRUE
               WHEN IND-NO-ENCONTRADO
                    SET NO-ENCONTRADO TO TRUE

               WHEN IND-SQL-CORRECTO
                    ADD 1 TO WS-CONT-LEIDOS

               WHEN OTHER
                     MOVE LT-A-PARRAFO1600     TO WS-PARRAFO
                     MOVE LT-ERROR-PENDIENTES  TO WS-TEXTO
                     @LOGERR(ERROR,LT-N-21016,AREA-INFORMACION)
                     PERFORM A9100-ROLLBACK
                     @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-EVALUATE.


      ****************************************************************
      ** SE CIERRA CURSOR DE PENDIENTES                             **
      ****************************************************************
       A1700-CERRAR-CURSOR-PEND.

           EXEC SQL
               CLOSE CURSOR-PEND
           END-EXEC.

           MOVE SQLSTATE  TO SQLSTATE-SIGLO.
           display 'A1700 RC-CUR-INC ' SQLCODE ' ' SQLSTATE

           IF  NOT IND-SQL-CORRECTO
               MOVE LT-ERR-CLOSE-CURSOR-PEND TO WS-TEXTO
               MOVE LT-A-PARRAFO1700         TO WS-PARRAFO
               @LOGERR(ERROR,LT-N-21016,AREA-INFORMACION)
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      ** SE FORMATEA LA CABECERA DEL LISTADO DE ESTADISTICAS        **
      ****************************************************************
       A1800-OBTENER-CABE-ESTAD.

           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO DATUM                OF CABE-2E.

           MOVE HOR-MAQUINA          OF S21-AREA-ENTORNO
             TO WS-TIEMPO.

           MOVE WS-HORA              TO HOURS   OF CABE-3E.
           MOVE WS-MINUTOS           TO MINUTES OF CABE-3E.
           MOVE WS-SEGUNDOS          TO SECONDS OF CABE-3E.

      *----> Se obtiene la empresa y su descripcion.
           PERFORM A3100-OBTENER-DESC-EMPRESA.

           MOVE NOMBRE               OF TL-T06TC005(1)
             TO ENTIDAD-A.

           MOVE WS-COD-EMPRESA       TO ENTIDAD-N.

      *----> Se llama al servicio TCS07002 para obtener la descripcion
      *----> del centro
           MOVE 'V'
             TO ACC-SERV             OF MSG-IN-TCS07002.

           MOVE '0'
             TO IND-TIPO-LIS         OF MSG-IN-TCS07002.

           MOVE 1
             TO NUM-CLAVE            OF MSG-IN-TCS07002.

           MOVE COD-EMPRESA          OF S21-AREA-ENTORNO
             TO COD-EMPRESA          OF MSG-IN-TCS07002.

           MOVE WS-COD-CENTRO
             TO COD-CENTRO           OF MSG-IN-TCS07002.


            @INVOCAR(TCS07002,C)

           display 'A1800 RC-TCS07002 ' NUM-ERROR OF S21-AREA-ERROR
	   IF TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
              MOVE LT-A-PARRAFO1300  TO WS-PARRAFO
              MOVE LT-ERROR-CENTRO   TO WS-TEXTO
              @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.

           MOVE WS-COD-CENTRO
             TO CENTRO-N             OF CABE-4E.

           MOVE NOMBRE               OF MSG-OUT-TCS07002(1)
             TO CENTRO-A             OF CABE-4E.


      ****************************************************************
      ** -SE LLAMA AL SERVICIO DE MODIFICACION DE UN REGISTRO DE IN-**
      **     CIDENCIA (OBS20007).                                   **
      ** -SE GRABA EN RAD                                           **
      ** -SE LEE SIGUIENTE REGISTRO DE LA TABLA DE INCIDENCIAS      **
      ****************************************************************
       2000-PROCESO.
             display '2000 -PROCESO '.
      *----> Se comprueba que el codigo de empresa leido de T12INC06
      *----> es igual al de la AQBF en vez de seleccionar registros
      *----> de la tabla con cod-empresa = aqbf-cod-empresa para evitar
      *----> tablespace scan y multiple index scan.

           MOVE WS-A-PROGRAMA        TO COD-USUARIO OF S21-AREA-ENTORNO.

           IF COD-EMPRESA OF T12INC06 = COD-EMPRESA OF S21-AREA-ENTORNO

      *---    -> Se obtiene en nuevo numero de operacion por cada
      *---    -> cheque que debe ser devuelto
               @NUEVAOPE()

               IF  TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
                   MOVE LT-A-PARRAFO2000  TO WS-PARRAFO
                   MOVE LT-ERROR-AQNUEOPE TO WS-TEXTO
                   @ERROR(ERROR,,AREA-INFORMACION)
               END-IF

               IF  COD-CENT-ORIG OF T12INC06 NOT EQUAL WS-CENTRO
      *--         -El centro origen del intercambio (el responsable de
      *--         -la camara que recibio el cheque) se toma como centro
      *--         -origen y de imputacion para realizar la contabilidad.
                   MOVE COD-CENT-ORIG OF T12INC06
                                      TO COD-CENTRO OF S21-AREA-ENTORNO
                                         WS-CENTRO
               END-IF

      * VR-2003-05-20-I-Obtiene ultimo usuario que tomo accion
               PERFORM A2500-ACTUAL-ESTADO-INCID
      * VR-2003-05-20-F-Obtiene ultimo usuario que tomo accion

               PERFORM A2100-FORMATEAR-OBS20007

               @INVOCAR(OBS20007,C)

               display '2000 RC-OBS20007 ' NUM-ERROR OF S21-AREA-ERROR
				IF  TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
                   PERFORM A9100-ROLLBACK
                   @ERROR(ERROR,)
               END-IF

               PERFORM A2200-FORMATEAR-CAS10010

      *-->     CAMBIO TEMPORAL POR ERROR EN DATOS EN CAS10010
      *--      ERROR 8192 
      *         IF NUM-CTA-DOM OF T12INC06 EQUAL 4902311
      *            CONTINUE
      *         ELSE

                  @INVOCAR(CAS10010,B)

                  display '2000 -RC-CAS10010 ' 
					 NUM-ERROR OF S21-AREA-ERROR
				IF  TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
                      PERFORM A9100-ROLLBACK
                      @ERROR(ERROR,)
                  END-IF
      *         END-IF

               ADD 1 TO WS-CONT-MODIFI
               PERFORM A2300-GRABAR-RAD

               IF  DEL-CONCEPTO OF T12INC06 = LT-SALDO-INSUF  OR
                   TXT-BENEF OF T12INC06 (1:2) = LT-MOT-FONDOS-INSUF
DISP  *            DISPLAY 'Informar Protesto'
                   PERFORM A2400-GENERAR-PROTESTO
				END-IF

      *--  FSALAZAR 28/01/2009. Homologar BP, consideracion CHQS....
      *--  JHTORRES 01.06.2005 Cambiar estdo de cheque
      *--  JHTORRES 15.07.2005 validar primero que cheque este
      *--                      pagado por camara para llamar
      *--                      OBS10005
      *--  WGUERRE  07.03.2006
      *--  Si es cuenta de chq. de gerencia no debe entrar a
      *--  consulta estado del cheque
               IF NUM-CTA      OF T12INC06 NOT EQUAL 0
                  PERFORM A2550-CONSULTAR-ESTADO-CHEQUE
                  
                  display 'CAB1040 -ESTADO-CHQ ' 
                      COD-EST-SOP OF MSG-OUT-OBS10002 
                  
                  IF COD-EST-SOP OF MSG-OUT-OBS10002 EQUAL '89'
                     PERFORM A2600-ACTUALIZA-ESTADO-CHEQUE
                  END-IF
               END-IF
      *--  JHTORRES 01.06.2005
      *--  FSALAZAR-END-28/01/2009.  

               INITIALIZE S21-AREA-ERROR

           END-IF.
           
      *--  WGUERRE  16.08.2004
      *--  Se elimina la rearrancabilidad, y se adiciona el commit
      *--  normal, ya que el cursor automaticamente comienza donde
      *--  se quedo.
      *--  Se elimina porque este proceso es abierto en N procesos
           EXEC SQL COMMIT END-EXEC.
           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF  NOT IND-SQL-CORRECTO
               MOVE LT-ERR-CLOSE-CURSOR-PEND TO WS-TEXTO
               MOVE LT-A-PARRAFO1700         TO WS-PARRAFO
               @LOGERR(ERROR,LT-N-21016,AREA-INFORMACION)
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      *     @GXCOMMIT().
           IF WS-CONT-LEIDOS IS NOT NUMERIC
              MOVE ZERO     TO WS-CONT-LEIDOS.
           IF WS-CONT-MODIFI IS NOT NUMERIC
              MOVE ZERO     TO WS-CONT-MODIFI.

           PERFORM A1600-LEER-PENDIENTES.


      ****************************************************************
      ** -SE FORMATEA EL MENSAJE DE ENTRADA DEL SERVICIO OBS20007   **
      **  PARA LA MODIFICACION DE LA TABLA DE INCIDENCIAS           **
      ****************************************************************
       A2100-FORMATEAR-OBS20007.
           display 'A2100 -FORMAT OBS20007 '.
           
           MOVE CORR T12INC06
             TO OBREGINT             OF MSG-IN-OBS20007.

           MOVE LT-DEBE
             TO IND-NATURALEZA       OF MSG-IN-OBS20007.

           MOVE WS-LT-DEVUELTO
             TO COD-EST-INCID        OF MSG-IN-OBS20007.

           MOVE FEC-VENCIMIENTO      OF T12INC06
             TO FEM-VENCIMIENTO      OF MSG-IN-OBS20007.

           MOVE FEC-OPERACION        OF T12INC06
             TO FEM-OPERACION        OF MSG-IN-OBS20007.

           MOVE FEC-VALOR            OF T12INC06
             TO FEM-VALOR            OF MSG-IN-OBS20007.

           MOVE IMP-MOVIMIENTO       OF T12INC06
             TO IMPMOVIMIENTO        OF MSG-IN-OBS20007.

           MOVE FEC-EMISION          OF T12INC06
             TO FEM-EMISION          OF MSG-IN-OBS20007.

           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO FEM-RESOL            OF MSG-IN-OBS20007.

           MOVE LT-N-INCORRIENTE
             TO COD-RESOL            OF MSG-IN-OBS20007.

           MOVE COD-DOMINIO          OF S21-AREA-ENTORNO
             TO COD-DOMINIO          OF MSG-IN-OBS20007.

           MOVE NUM-NODO             OF S21-AREA-ENTORNO
             TO NUM-NODO             OF MSG-IN-OBS20007.

           MOVE NUM-MENSAJE          OF S21-AREA-ENTORNO
             TO NUM-MENSAJE          OF MSG-IN-OBS20007.

           MOVE WS-A-PROGRAMA
             TO COD-USUARIO-RES      OF MSG-IN-OBS20007.

           MOVE HOR-MAQUINA          OF S21-AREA-ENTORNO
             TO WS-HORA6-AUX.

           MOVE WS-HORA6             TO WS-HORA8.
           MOVE WS-MINUTOS6          TO WS-MINUTOS8.
           MOVE WS-SEGUNDOS6         TO WS-SEGUNDOS8.

           MOVE WS-HORA8-AUX
             TO HOR-RESOL            OF MSG-IN-OBS20007.

           MOVE DEL-CONCEPTO         OF T12INC06
             TO DEL-CONCEPTO2        OF MSG-IN-OBS20007.

           MOVE FEC-VALOR            OF T12INC06
             TO FEM-VALOR2           OF MSG-IN-OBS20007.

           MOVE COD-REFER            OF T12INC06
             TO COD-REFERENCIA2      OF MSG-IN-OBS20007.

           MOVE SPACES
             TO COD-CENT-FTRAS       OF MSG-IN-OBS20007
                COD-ENT-CT-RES       OF MSG-IN-OBS20007.

           MOVE ZEROS
             TO COD-SUC-CT-RES       OF MSG-IN-OBS20007
                COD-CLV-RESOL        OF MSG-IN-OBS20007
                NUM-CTA-RES          OF MSG-IN-OBS20007.

           MOVE IMP-MOVIMIENTO       OF T12INC06
             TO IMP-RESOL            OF MSG-IN-OBS20007.

           MOVE COD-MONEDA           OF T12INC06
             TO D-IMP-RESOL          OF MSG-IN-OBS20007.

           MOVE '01.01.0001'
             TO F-IMP-RESOL          OF MSG-IN-OBS20007.

           MOVE LT-B
             TO CLA-RESOL            OF MSG-IN-OBS20007.

           MOVE ZEROS
             TO COD-OPER-ENC         OF MSG-IN-OBS20007.

           MOVE TIMESTAMP-SIGLO      OF T12INC06
             TO TIMESTAMP-SIGLOM     OF MSG-IN-OBS20007.

           MOVE '1' TO IND-ENVIO-INF OF MSG-IN-OBS20007.

           SET  RESOL-TOTAL          TO TRUE.


      ****************************************************************
      ** -SE OBTIENE LA FECHA DE DEVOLUCION DEL CHEQUE DE T30DOR10  **
      **  PARA SER INFORMADO AL SERVICIO CAS10010 DE ACTUALIZACION  **
      **  DE CHEQUES RECIBIDOS PARA SER DEVUELTOS.                  **
      ****************************************************************
       A2150-LEER-FECHA-DEVOL.
MGRAIX     display 'A2150- FEC-DV -> NoINCID ' NUM-INCID OF T12INC06
             'FEC-VENC ' FEC-VENCIMIENTO  OF T12INC06

           MOVE NUM-INCID            OF T12INC06
             TO NUM-INCID            OF T30DOR10

           MOVE FEC-VENCIMIENTO      OF T12INC06
             TO FEC-ABONO-CEDENTE    OF T30DOR10

           EXEC SQL
                SELECT FEC_DEVOLUCION,
                       COD_DOMINIO,
                       NUM_NODO,
                       NUM_OPERACION
                  INTO :T30DOR10.FEC-DEVOLUCION,
                       :T30DOR10.COD-DOMINIO,
                       :T30DOR10.NUM-NODO,
                       :T30DOR10.NUM-OPERACION
                  FROM T30DOR10
                 WHERE NUM_INCID         = :T30DOR10.NUM-INCID
                   AND FEC_ABONO_CEDENTE = :T30DOR10.FEC-ABONO-CEDENTE
           END-EXEC.

           MOVE SQLSTATE  TO SQLSTATE-SIGLO.
           display 'A2150 -RC-T30DOR10 ' SQLCODE ' ' SQLSTATE.

           EVALUATE TRUE
               WHEN IND-SQL-CORRECTO
                    CONTINUE

               WHEN IND-NO-ENCONTRADO
      *-->          WGUERRE  27.09.2004
      *--           Si no encuentra registro se pone como fecha de
      *--           devolucion la misma del vencimiento, ya que si
      *--           tiene 01.01.0001 no sale en el DEVUCAM
                    MOVE LT-FECHA-MINIMA TO FEC-DEVOLUCION OF T30DOR10
                    MOVE FEC-VENCIMIENTO                   OF T12INC06 
                      TO FEC-DEVOLUCION                    OF T30DOR10

               WHEN OTHER
                    display '** Erro al leer incidencia en dor10: '
                            num-incid of t30dor10
                            
                    MOVE LT-A-PARRAFO2150         TO WS-PARRAFO
                    MOVE LT-ERROR-SELECT-T30DOR10 TO WS-TEXTO
                    @LOGERR(ERROR,LT-N-21016,AREA-INFORMACION)
                    PERFORM A9100-ROLLBACK
                    @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-EVALUATE.


      ****************************************************************
      ** -SE FORMATEA EL MENSAJE DE ENTRADA DEL SERVICIO CAS10010   **
      ****************************************************************
       A2200-FORMATEAR-CAS10010.
           display 'A2200 -DATOS CAS10010 '
           
           PERFORM A2150-LEER-FECHA-DEVOL

           MOVE FEC-DEVOLUCION       OF T30DOR10
             TO FEC-DEVOLUCION       OF MSG-IN-CAS10010.

           MOVE FEC-OPERACION        OF T12INC06
             TO FEC-PRESENT          OF MSG-IN-CAS10010.

           MOVE COD-ENTIDAD          OF T12INC06
             TO COD-ENTIDAD          OF MSG-IN-CAS10010.

           MOVE COD-SUC-DOM          OF T12INC06
             TO COD-CENT-DES         OF MSG-IN-CAS10010.

           MOVE NUM-CTA-DOM          OF T12INC06
             TO NUM-SEC-EFE          OF MSG-IN-CAS10010.

      * -- Se informa el motivo de la Incidencia (corresponde a los 2
      * -- primeros caracteres de TXT-BENEF) como Codigo de Devolucin
           MOVE TXT-BENEF            OF T12INC06 (1:2)
             TO COD-DEV              OF MSG-IN-CAS10010.

           MOVE ZEROS
             TO IMP-PAGO-PARCIAL     OF MSG-IN-CAS10010.

           MOVE COD-MONEDA           OF T12INC06
             TO COD-MONEDA           OF MSG-IN-CAS10010.

           MOVE WS-LT-PTE-DEVOL
             TO COD-ESTDOC           OF MSG-IN-CAS10010.

           MOVE NUM-INCID            OF T12INC06
             TO NUM-INCID            OF MSG-IN-CAS10010.

           IF COD-DOMINIO OF T30DOR10 NOT NUMERIC
              MOVE ZEROS 
                TO COD-DOMINIO          OF MSG-IN-CAS10010
           ELSE
              MOVE COD-DOMINIO          OF T30DOR10
                TO COD-DOMINIO          OF MSG-IN-CAS10010
           END-IF

           IF NUM-NODO OF T30DOR10 NOT NUMERIC
              MOVE ZEROS 
                TO NUM-NODO             OF MSG-IN-CAS10010
           ELSE
              MOVE NUM-NODO             OF T30DOR10
                TO NUM-NODO             OF MSG-IN-CAS10010
           END-IF

           IF NUM-OPERACION OF T30DOR10 NOT NUMERIC
              MOVE ZEROS 
                TO NUM-OPERACION        OF MSG-IN-CAS10010
           ELSE
              MOVE NUM-OPERACION        OF T30DOR10
                TO NUM-OPERACION        OF MSG-IN-CAS10010
           END-IF.


      ****************************************************************
      ** SE ESCRIBE EN RAD                                          **
      ****************************************************************
       A2300-GRABAR-RAD.
           display 'A2300 -GRABAR RAD PAS43003'
      *----> Indicador de pago en efectivo.
           MOVE ZEROS
             TO IND-PAGO-EFEC        OF MSG-IN-PAS43003.

      *----> Codigo de centro origen de la operacion.
           MOVE WS-CENTRO
             TO COD-CENT-ORIG        OF MSG-IN-PAS43003.

      *----> Codigo de operacion(resolucion de intercambio)
           MOVE LT-A-40502
             TO COD-OPERACION        OF MSG-IN-PAS43003.

      *----> Codigo destino final
           MOVE WS-COD-DESFI
             TO COD-DESFI            OF MSG-IN-PAS43003.

      *----> Concepto destino final
           MOVE LT-CONCEPTO-DEVOL
             TO DEL-CONCEPTO         OF MSG-IN-PAS43003.

      *----> Indicador de naturaleza.
           MOVE LT-DEBE
             TO IND-NATURALEZA       OF MSG-IN-PAS43003.

      *----> Centro destino de la operacion (compensacion).
           MOVE WS-CENTRO
             TO COD-CENTIM           OF MSG-IN-PAS43003.

      *----> Codigo de RAD (Identificador de la parte variable).
           MOVE LT-COD-RAD
             TO COD-RAD              OF MSG-IN-PAS43003.

      *----> Fecha de valor.
           MOVE FEC-VALOR            OF T12INC06
             TO FEM-VALOR            OF MSG-IN-PAS43003.

      *----> Importe de la operacion.
           MOVE IMP-PENDIENTE        OF T12INC06
             TO IMP-ORIG-OPE         OF MSG-IN-PAS43003
                IMP-CUENTA           OF MSG-IN-PAS43003.

      *----> Moneda de la operacion.
           MOVE COD-MONEDA           OF T12INC06
             TO D-IMP-ORIG-OPE       OF MSG-IN-PAS43003
                D-IMP-CUENTA         OF MSG-IN-PAS43003.

            @INVOCAR(PAS43003,B)

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,)
           END-IF.


      ****************************************************************
      ** SE GENERA PROTESTO PARA CHEQUE DEVUELTO POR FONDOS         **
      ** INSUFICIENTES LLAMANDO AL SERVICIO CTS22014.               **
      ****************************************************************
       A2400-GENERAR-PROTESTO.
            display 'A2400 -PROTESTA CTS22014 '
      
      *--  WGUERRE  08.03.2004
      *--  Se recupera el usuario que devolvio el cheque desde la
      *--  la tabla de consideracion
           PERFORM 2410-OBTENGO-USU-CONSI
           MOVE COD-USUARIO          OF S21-AREA-ENTORNO
             TO WG-COD-USUARIO

           IF COD-USUARIO OF T30RCI01 EQUAL '00000000'
              IF COD-ASESOR OF T30RCI01 NOT EQUAL SPACES
                 MOVE COD-ASESOR     OF T30RCI01
                   TO COD-USUARIO    OF S21-AREA-ENTORNO
              END-IF
           ELSE
              MOVE COD-USUARIO       OF T30RCI01
                TO COD-USUARIO       OF S21-AREA-ENTORNO
           END-IF.
      *--  WGUERRE  08.03.2004


           MOVE NUM-CTA              OF T12INC06
             TO WS-NUM-CUENTA

           MOVE WS-NUM-CTA-INT
             TO NUM-CTA-INT          OF MSG-IN-CTS22014.

           MOVE WS-COD-TIP-EXPE
             TO COD-TIP-EXPE         OF MSG-IN-CTS22014.

           MOVE COD-EMPRESA          OF T12INC06
             TO COD-EMPRESA          OF MSG-IN-CTS22014.

           MOVE COD-SUC-DOM          OF T12INC06
             TO COD-SUC-PROPIE       OF MSG-IN-CTS22014.

           MOVE COD-MONEDA           OF T12INC06
             TO COD-MONEDA           OF MSG-IN-CTS22014.

           MOVE NUMERO-DOCUMENTO     OF T12INC06
             TO NUM-CHEQUE           OF MSG-IN-CTS22014.

           MOVE IMP-MOVIMIENTO       OF T12INC06
             TO IMP-CHEQUE           OF MSG-IN-CTS22014
                IMP-PROTESTO         OF MSG-IN-CTS22014.

           MOVE LT-CAMARA
             TO TIPO-PROTESTO        OF MSG-IN-CTS22014.

           MOVE LT-ALTA
             TO ACC-SERV             OF MSG-IN-CTS22014.

           MOVE ZEROS
             TO SAL-DISPONIBLE       OF MSG-IN-CTS22014.


            @INVOCAR(CTS22014,A)

           MOVE WG-COD-USUARIO
             TO COD-USUARIO          OF S21-AREA-ENTORNO.

           DISPLAY 'CAB1040 RC-CTS22014 ' TIPO-ERROR OF S21-AREA-ERROR ' '
              NUM-ERROR  OF S21-AREA-ERROR. 
	   IF  TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS AND
               NUM-ERROR  OF S21-AREA-ERROR NOT EQUAL LT-9615
               MOVE NUM-ERROR  OF S21-AREA-ERROR TO WS-ERROR
DISP  *        DISPLAY 'Error llamada servicio de Protesto'
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,WS-ERROR)
           END-IF.


      ****************************************************************
      ** Obtengo el usuario de consideracion que devolvio el cheque **
      ** para grabarlo en la tabla de Protestos                     **
      ****************************************************************
       2410-OBTENGO-USU-CONSI.

           MOVE NUM-INCID            OF T12INC06
             TO NUM-INCID            OF T30RCI01

           EXEC SQL
                SELECT COD_USUARIO,
                       COD_ASESOR
                  INTO :T30RCI01.COD-USUARIO,
                       :T30RCI01.COD-ASESOR
                  FROM T30RCI01
                 WHERE TO_CHAR(TIMESTAMP_SIGLO,'YYYY-MM-DD')
                                       <= :WS-FECHA-PROC
                   AND TO_CHAR(FEC_VENCIMIENTO,'YYYY-MM-DD')
                                       >= :WS-FECHA-PROC
                   AND NUM_INCID        = :T30RCI01.NUM-INCID
                   AND IND_EST_REG      =  'A'
           END-EXEC.

            MOVE SQLSTATE  TO SQLSTATE-SIGLO.
            display 'A2410 -rc-T30RCI01 '  SQLCODE ' ' SQLSTATE 
             ' incid '  NUM-INCID   OF T30RCI01

           EVALUATE TRUE
               WHEN IND-SQL-CORRECTO
                    CONTINUE

               WHEN IND-NO-ENCONTRADO
                    MOVE 'CAB1040'     TO COD-USUARIO  OF T30RCI01

               WHEN OTHER
                    display 'Error en SELECT de T30RCI01 - '
                            ' Num-Incid ' NUM-INCID OF T30RCI01
                            ' - Sqlcode: ' SQLCODE
                    MOVE 'CAB1040'     TO COD-USUARIO  OF T30RCI01
           END-EVALUATE.


      * -> JANZOLA. 2002.03.12
      *****************************************************************
      **  A2500-ACTUAL-ESTADO-INCIDENCIA.                            **
      *****************************************************************
      ** SE ACTUALIZA EL ESTADO DE LA INCIDENCIA DE CONSIDERACION A  **
      ** DEVUELTO (DV).                                              **
      *****************************************************************
       A2500-ACTUAL-ESTADO-INCID.
           display 'A2500 -ACTUAL-ESTADO CAS01005'
      * ----> Actualizar Estado de Incidencia de Consideracin

           INITIALIZE MSG-IN-CAS01005
                      MSG-OUT-CAS01005

           MOVE COD-EMPRESA   OF T12INC06
             TO COD-EMPRESA   OF CA01005I OF MSG-IN-CAS01005.

           MOVE COD-CENT-DEST OF T12INC06
             TO COD-CEN-DEST  OF CA01005I OF MSG-IN-CAS01005.

           MOVE NUM-CTA       OF T12INC06
             TO NUM-CTA       OF CA01005I OF MSG-IN-CAS01005.

           MOVE LT-UNO
             TO NUM-REGS      OF CA01005I OF MSG-IN-CAS01005.

           MOVE NUM-INCID     OF T12INC06
             TO NUM-INCID     OF CA01005I OF MSG-IN-CAS01005 (LT-UNO).

           MOVE TIMESTAMP-SIGLO OF T12INC06
             TO TIMESTAMP-SIGLO
                              OF CA01005I OF MSG-IN-CAS01005 (LT-UNO).

           MOVE WS-LT-PEND-RESOL
             TO COD-EST-ANT   OF CA01005I OF MSG-IN-CAS01005 (LT-UNO).

           MOVE WS-LT-DEVUELTO-CONSID
             TO IND-ACCION    OF CA01005I OF MSG-IN-CAS01005 (LT-UNO).

           MOVE LT-CHEQUE-DEVUELTO
             TO DEL-CONCEPTO  OF CA01005I OF MSG-IN-CAS01005 (LT-UNO).


            @INVOCAR(CAS01005,C).

           display 'CAB1040 RC-CAS01005 ' NUM-ERROR OF S21-AREA-ERROR
           ' ' TIPO-ERROR OF S21-AREA-ERROR.
           

      *****************************************************************
      ** A2550-CONSULTAR-ESTADO-CHEQUE           JHTORRES 2005/07/15 **
      *****************************************************************
      ** SE LLAMA AL SERVICIO DE CONSULTA DE DATOS DEL CHEQUE PARA   **
      ** PODER CONOCER EL ESTADO DEL SOPORTE.                        **
      *****************************************************************
       A2550-CONSULTAR-ESTADO-CHEQUE.
           DISPLAY 'CAB1040 A2550- : ' NUM-CTA OF T12INC06 ' - '
                    WS-NUM-CHEQUE.

           MOVE NUM-CTA              OF T12INC06
             TO WS-NUM-CUENTA

      *-> JHTORRES 2006-02-17
      *->          Separo numero de cheque
           PERFORM A2610-OBT-COD-PRIM-SEC.
      *-> JHTORRES 2006-02-17

           MOVE COD-PRIM-SOP         OF  T12TAL17
             TO COD-PRIM-SOP         OF MSG-IN-OBS10002.

           MOVE COD-SEC-SOP          OF T12TAL17
             TO COD-SEC-SOP          OF MSG-IN-OBS10002.

      *-> JHTORRES 2006-02-16
      *->          BUSCAMOS DIGITO VERIFICADOR DEL CHEQUE
           PERFORM A2551-OBT-DIG-CONTR-CH.
      *-> JHTORRES 2006-02-16


           MOVE DIG-CONTROL1         OF MSG-OUT-OBS11007
             TO NUM-CHEQUE-DIGIT     OF MSG-IN-OBS10002.

           MOVE WS-NUM-CHEQUE
             TO NUM-CHEQUE           OF MSG-IN-OBS10002.

           MOVE COD-EMPRESA          OF T12INC06
             TO COD-EMPRESA          OF MSG-IN-OBS10002.

           MOVE WS-NUM-CTA-INT
             TO NUM-CTA-INT          OF MSG-IN-OBS10002.

           MOVE WS-COD-TIP-EXPE
             TO COD-TIP-EXPE         OF MSG-IN-OBS10002.


            @INVOCAR(OBS10002,B).

           IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
               MOVE 'A2550-'          TO WS-PARRAFO
               MOVE 'ERROR-OBS10002'  TO WS-TEXTO
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.


      *****************************************************************
      ** A2551-OBT-DIG-CONTR-CH                  JHTORRES 2006/02/16 **
      *****************************************************************
       A2551-OBT-DIG-CONTR-CH.
           DISPLAY 'CAB1040 A2551- : '
                    NUM-CTA        OF T12INC06 ' - '
                    WS-NUM-CHEQUE ' - '
                    COD-PRIM-SOP   OF T12TAL17 ' - '
                    COD-SEC-SOP    OF T12TAL17.

           SET RECU OF ACC-SERV OF MSG-IN-OBS11007 TO TRUE

           MOVE COD-PRIM-SOP       OF T12TAL17
                                   TO COD-PRIM-SOP OF MSG-IN-OBS11007

           MOVE COD-SEC-SOP        OF T12TAL17
                                   TO COD-SEC-SOP  OF MSG-IN-OBS11007

           MOVE '0000'        TO COD-IDENTIFICADOR OF MSG-IN-OBS11007

           MOVE WS-NUM-CHEQUE
                                   TO NUM-CHEQUE   OF MSG-IN-OBS11007


           @INVOCAR(OBS11007,D)

           IF TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
               MOVE 'A2551-'          TO WS-PARRAFO
               MOVE 'ERROR-OBS11007'  TO WS-TEXTO
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.


      *****************************************************************
      ** A2600-ACTUALIZA-ESTADO-CHEQUE           JHTORRES 2005/06/01 **
      *****************************************************************
      ** SE ACTUALIZA ESTADO DEL CHEQUE LLALAMDO AL SERVICIO OBS10005**
      *****************************************************************
       A2600-ACTUALIZA-ESTADO-CHEQUE.
           display 'CAB1040 -A2600 ACTUAL CHQ OBS10005 '.
           
           INITIALIZE  MSG-IN-OBS10005.
           INITIALIZE  MSG-OUT-OBS10005 REPLACING ALPHANUMERIC DATA
                                    BY SPACES  NUMERIC DATA BY ZEROS.

           MOVE COD-PRIM-SOP        OF  T12TAL17
             TO COD-PRIM-SOP        OF  MSG-IN-OBS10005.

           MOVE COD-SEC-SOP         OF  T12TAL17
             TO COD-SEC-SOP         OF  MSG-IN-OBS10005.

           MOVE WS-NUM-CHEQUE
             TO NUM-TALONARIO       OF  MSG-IN-OBS10005.

           MOVE COD-EMPRESA         OF  T12INC06
             TO COD-EMPRESA         OF  MSG-IN-OBS10005.

           MOVE COD-SUCURSAL        OF  T12INC06
             TO COD-CENTRO          OF  MSG-IN-OBS10005.

           MOVE WS-NUM-CTA-INT
             TO NUM-CTA-INT         OF  MSG-IN-OBS10005.

           MOVE WS-COD-TIP-EXPE
             TO COD-TIP-EXPE        OF  MSG-IN-OBS10005.

           MOVE COD-MONEDA          OF  T12INC06
             TO COD-MONEDA-CTA      OF  MSG-IN-OBS10005.

           SET ACTIVADO  OF  MSG-IN-OBS10005  TO  TRUE.

           MOVE WS-COD-CENTRO
             TO COD-CENT-BAJA       OF  MSG-IN-OBS10005
                COD-CENT-ALTA       OF  MSG-IN-OBS10005.

           MOVE FEM-MAQUINA         OF  S21-AREA-ENTORNO
             TO FEM-VENCIMIENTO     OF  MSG-IN-OBS10005
                FEM-ALTA            OF  MSG-IN-OBS10005
                FEM-BAJA            OF  MSG-IN-OBS10005.

           MOVE '01.01.0001'
             TO FEM-VENCIMIENTO2    OF  MSG-IN-OBS10005.

           MOVE IMP-MOVIMIENTO      OF  T12INC06
             TO IMP-CHEQUE          OF  MSG-IN-OBS10005.

           PERFORM A2620-OBT-TIMESTAMP-CTA

           MOVE TIMESTAMP-SIGLOM    OF  MSG-OUT-CTS10028
             TO TIMESTAMP-SIGLOM    OF  MSG-IN-OBS10005.


           @INVOCAR(OBS10005,B)

           DISPLAY 'CAB1040 A2600-ACTUALIZA DESPUES OBS10005: '
                   TIPO-ERROR       OF  S21-AREA-ERROR ' - '
                   NUM-ERROR        OF  S21-AREA-ERROR ' - '
                   NUM-CTA          OF T12INC06        ' - '
                   WS-NUM-CHEQUE                       ' - '
                   COD-PRIM-SOP     OF T12TAL17        ' - '
                   COD-SEC-SOP      OF T12TAL17

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
               MOVE 'A2600-'          TO WS-PARRAFO
               MOVE 'ERROR-OBS10005'  TO WS-TEXTO
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.


      *****************************************************************
      ** A2610-OBT-COD-PRIM-SEC                  JHTORRES 2005/06/01 **
      *****************************************************************
      **  LEE LA TABLA T12TAL17 PARA OBTENER EL CODIGO PRIMARIO Y    **
      **  SECUNDARIO DE SOPORTE.                                     **
      *****************************************************************
       A2610-OBT-COD-PRIM-SEC.

           MOVE COD-EMPRESA        OF  T12INC06
                                   TO  COD-EMPRESA    OF T12TAL17

           MOVE WS-COD-TIP-EXPE    TO  COD-TIP-EXPE   OF T12TAL17

           MOVE WS-NUM-CTA-INT     TO  NUM-CTA-INT    OF T12TAL17

           MOVE NUMERO-DOCUMENTO   OF  T12INC06
                                   TO  WS-NUMERO-DOCUMENTO

           MOVE WS-NUM-CHEQUE      TO  NUM-CHEQUE     OF T12TAL17
                                       NUM-CHEQUE-FIN OF T12TAL17

           EXEC SQL
                SELECT  COD_PRIM_SOP,
                        COD_SEC_SOP
                  INTO :T12TAL17.COD-PRIM-SOP,
                       :T12TAL17.COD-SEC-SOP
                  FROM  T12TAL17
                 WHERE  COD_EMPRESA    =  :T12TAL17.COD-EMPRESA
                   AND  COD_TIP_EXPE   =  :T12TAL17.COD-TIP-EXPE
                   AND  NUM_CTA_INT    =  :T12TAL17.NUM-CTA-INT
                   AND  NUM_CHEQUE     <= :T12TAL17.NUM-CHEQUE
                   AND  NUM_CHEQUE_FIN >= :T12TAL17.NUM-CHEQUE-FIN
           END-EXEC

           MOVE SQLSTATE TO SQLSTATE-SIGLO
           display 'CAB1040 A2610-RC-T12TAL17 ' SQLCODE ' ' SQLSTATE.
           IF  NOT IND-SQL-CORRECTO
               DISPLAY ' CAB1040 Erro al leer soporte T12TAl17: '
                         WS-NUM-CUENTA
               MOVE 'A2610-'                 TO WS-PARRAFO
               MOVE 'ERROR-SELECT-T12TAL17'  TO WS-TEXTO
               @LOGERR(ERROR,SQLCODE,AREA-INFORMACION)
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


      *****************************************************************
      ** A2620-OBT-TIMESTAMP-CTA                 JHTORRES 2005/06/01 **
      *****************************************************************
      **  LLAMA AL SERVICIO CTS10028, PARA OBTENER EL TIMESTAMP DE   **
      **  LA CUENTA.                                                 **
      *****************************************************************
       A2620-OBT-TIMESTAMP-CTA.
           display 'CAB1040 -A2620-OBT-TIMESTAMP-CTA '  
           WS-NUM-CTA-INT  ' Exp: ' WS-COD-TIP-EXPE.
           
           MOVE  WS-NUM-CTA-INT
             TO  NUM-CTA-INT       OF MSG-IN-CTS10028

           MOVE  WS-COD-TIP-EXPE
             TO  COD-TIP-EXPE      OF MSG-IN-CTS10028

           MOVE  COD-EMPRESA       OF  T12INC06
             TO  COD-EMPRESA       OF MSG-IN-CTS10028


           @INVOCAR(CTS10028,B)

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
               MOVE 'A2620-'           TO WS-PARRAFO
               MOVE 'ERROR-CTS10028 '  TO WS-TEXTO
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      ** SE ESCRIBE EN EL LISTADO EL AVISO                          **
      ****************************************************************
       A3000-OBTENER-LISTADO.
           display 'CAB1040 -A3000 IMPRESOS '

           IF WS-IMPRES = ZEROS
              OPEN OUTPUT IMPRES02
              MOVE 1 TO WS-IMPRES
           END-IF.

      *----> Se obtiene la empresa y su descripcion.
           PERFORM A3100-OBTENER-DESC-EMPRESA.

           MOVE NOMBRE               OF TL-T06TC005(1) TO ENTIDAD-A.
           MOVE WS-COD-EMPRESA       TO ENTIDAD-N.

      *----> Se obtiene la descripcion del centro responsable
           MOVE WS-COD-CENT-COMP     TO CABE-CENT-RESP.

           PERFORM A3200-OBTENER-ENT-REMITENTE.

           IF WS-NUM-LINEAS > 64
              PERFORM A3300-CABECERA-LISTADO
           END-IF.

           ADD 1 TO WS-NUM-LINEAS.
           WRITE RECORD-PRN2 FROM DET-1 AFTER 1.

           ADD 1 TO WS-NUM-LINEAS.
           WRITE RECORD-PRN2 FROM DET-2 AFTER 1.


      ****************************************************************
      **  SE LLAMA AL SERVICIO DE TCS05002 PARA LA OBTENCION DE LA  **
      **  DESCRIPCION DE LA EMPRESA.                                **
      ****************************************************************
       A3100-OBTENER-DESC-EMPRESA.
           display 'A3100- EMPRE-TCS05002 '.
           MOVE 'V'
             TO ACC-SERV             OF MSG-IN-TCS05002.

           MOVE '0'
             TO IND-TIPO-LIS         OF MSG-IN-TCS05002.

           MOVE 1
             TO NUM-CLAVE            OF MSG-IN-TCS05002.

           MOVE 1
             TO NUM-CONDICION-ADICIONAL OF MSG-IN-TCS05002.

           MOVE COD-EMPRESA          OF S21-AREA-ENTORNO
             TO COD-EMPRESA          OF MSG-IN-TCS05002.

            @INVOCAR(TCS05002,B)

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT EQUAL ZEROS
               MOVE LT-A-PARRAFO3100  TO WS-PARRAFO
               MOVE LT-ERROR-TCS05002 TO WS-TEXTO
               MOVE NUM-ERROR OF S21-AREA-ERROR  TO WS-ERROR
	       PERFORM A9100-ROLLBACK
               @ERROR(ERROR,WS-ERROR,AREA-INFORMACION)
           END-IF.


      ****************************************************************
      **  SE OBTIENE EL DEPARTAMENTO DE COMPENSACION Y DESCRIPCION  **
      **  PARA LA CABECERA DEL LISTADO.                             **
      ****************************************************************
       A3200-OBTENER-ENT-REMITENTE.
            display 'A3200-OBTENER-ENT-REMI-TCS07002 '.

      *----> Se accede al servicio validacion de centro para obtener
      *----> la descripcion del centro responsable

           MOVE 'V'
             TO ACC-SERV             OF MSG-IN-TCS07002.

           MOVE '0'
             TO IND-TIPO-LIS         OF MSG-IN-TCS07002.

           MOVE 1
             TO NUM-CLAVE            OF MSG-IN-TCS07002.

           MOVE COD-EMPRESA          OF S21-AREA-ENTORNO
             TO COD-EMPRESA          OF MSG-IN-TCS07002.

           MOVE WS-COD-CENT-COMP
             TO COD-CENTRO           OF MSG-IN-TCS07002.


           @INVOCAR(TCS07002,C)

           IF  TIPO-ERROR OF S21-AREA-ERROR NOT = ZEROS
               MOVE NUM-ERROR OF S21-AREA-ERROR  TO WS-ERROR
	       @LOGERR(ERROR,WS-ERROR)
               PERFORM A9100-ROLLBACK
               @ERROR(ERROR,WS-ERROR)
           END-IF.

           MOVE NOMBRE               OF MSG-OUT-TCS07002(1)
             TO CABE-DEL-CENT.


      ****************************************************************
      ** SE ESCRIBE LA CABECERA DEL LISTADO DE ERRORES.             **
      ****************************************************************
       A3300-CABECERA-LISTADO.
           display 'A3300-CABEZON '

           MOVE 7                    TO WS-NUM-LINEAS.
           ADD  1                    TO WS-CONTA-PAGINA.
           MOVE WS-CONTA-PAGINA      TO PAGINA  OF CABE-4.

           MOVE FEM-MAQUINA          OF S21-AREA-ENTORNO
             TO DATUM                OF CABE-2.

           MOVE HOR-MAQUINA          OF S21-AREA-ENTORNO
             TO WS-TIEMPO.

           MOVE WS-HORA              TO HOURS   OF CABE-3.
           MOVE WS-MINUTOS           TO MINUTES OF CABE-3.
           MOVE WS-SEGUNDOS          TO SECONDS OF CABE-3.

           WRITE RECORD-PRN2 FROM CABE-1 AFTER ADVANCING PAGE.
           WRITE RECORD-PRN2 FROM CABE-2 AFTER 1.
           WRITE RECORD-PRN2 FROM CABE-3 AFTER 1.
           WRITE RECORD-PRN2 FROM CABE-4 AFTER 1.
           WRITE RECORD-PRN2 FROM CABE-5 AFTER 1.
           WRITE RECORD-PRN2 FROM CABE-6 AFTER 1.
           WRITE RECORD-PRN2 FROM CABE-7 AFTER 1.


      ****************************************************************
      ** -SE CIERRA EL CURSOR DE LOS CHEQUES "PENDIENTES"           **
      **  O  "VENCIDO PENDIENTE".                                   **
      ** -SI ESTA ABIERTO EL FICHERO DE ERRORES, SE CIERRA.         **
      ** -SE CIERRA LA FICHA DE JCL.                                **
      ** -SE ESCRIBEN ESTADISTICAS DE CAB1040.                      **
      ** -SE CIERRA LISTADO.                                        **
      ****************************************************************
       8000-FINAL.
           display '8000-FINAL '.

           PERFORM A1700-CERRAR-CURSOR-PEND.

           IF WS-IMPRES = ZEROS
              CONTINUE
           ELSE
              CLOSE IMPRES02
           END-IF.

           PERFORM A8100-ESCRIBIR-ESTADIST.

           CLOSE IMPRES01.


      *--  -Para que queden inializados en en la tabla de rearranque.
           MOVE ZERO     TO WS-CONT-LEIDOS.
           MOVE ZERO     TO WS-CONT-MODIFI.

           IF  RETURN-CODE   <=  LT-N-4
	       EXEC SQL COMMIT END-EXEC
	   END-IF.

           GOBACK.


      ****************************************************************
      ** SE ESCRIBEN LAS CABECERAS Y EL DETALLE DEL LISTADO.        **
      ****************************************************************
       A8100-ESCRIBIR-ESTADIST.
           display 'A8100-ESCRIBE-ESTD ' 

           WRITE REG-IMPRES01 FROM CABE-1  AFTER ADVANCING PAGE.
           WRITE REG-IMPRES01 FROM CABE-2E AFTER 1.
           WRITE REG-IMPRES01 FROM CABE-3E AFTER 1.
           WRITE REG-IMPRES01 FROM CABE-4E AFTER 1.
           WRITE REG-IMPRES01 FROM CABE-5E AFTER 1.

           MOVE WS-CONT-LEIDOS  TO REG-LEIDOS.
           MOVE WS-CONT-MODIFI  TO REG-DEVUELTOS.

           WRITE REG-IMPRES01 FROM DET-LEIDOS.
           WRITE REG-IMPRES01 FROM DET-DEVUELTOS.


      ****************************************************************
      ** SE EFECTUA ROLLBACK                                        **
      ****************************************************************
       A9100-ROLLBACK.
           display 'A9100-ROLLBACK '

           EXEC SQL
               ROLLBACK
           END-EXEC.

           MOVE SQLSTATE TO SQLSTATE-SIGLO.

           IF  NOT IND-SQL-CORRECTO
               MOVE LT-A-PARRAFO9100  TO WS-PARRAFO
               MOVE LT-ERROR-ROLLBACK TO WS-TEXTO
               @ERROR(ERROR,SQLCODE,AREA-INFORMACION)
           END-IF.


