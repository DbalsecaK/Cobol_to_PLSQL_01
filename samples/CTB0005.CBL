      *************************
       IDENTIFICATION DIVISION.
      *************************

       PROGRAM-ID. CTB0005.
       AUTHOR. TERESA DE LUCAS JUNCO.
       DATE-COMPILED.

      *****************************************************************
      **************  C A J A  E S P A # A  -  S I G L O  *************
      *****************************************************************
      *                                                               *
      * PROGRAMA.......: CTB0005                                      *
      * APLICACION.....: CONVIVENCIA.                                 *
      * FEC.CODIFICAC..: 15-03-94.                                    *
      *                                                               *
      * FUNCIONES:  ESTA RUTINA OBTINE LA CUENTA CLIENTE A TRAVES DE  *
      *             LOS DATOS QUE LE PASAN.                           *
      *                                                               *
      * ENTRADA..:  CT0003P                                           *
      *                                                               *
      * SALIDA...:  CT0003P                                           *
      *                                                               *
      * =====================> MODIFICACIONES <====================== *
      *                                                               *
      *   AUTOR    FECHA            CAUSA DE LA MODIFICACION          *
      * --------- -------- ------------------------------------------ *
      * TERESA    07-05-95 PARA OBTENER EL CCC, COGER LA SUCURSAL PRO-*
      *                    PIETARIA DE LA CTA NO LA DE LA CTA VIEJA.  *
      * ......... DD-MM-AA .......................................... *
      * ......... DD-MM-AA .......................................... *
      * ......... DD-MM-AA .......................................... *
      * ......... DD-MM-AA .......................................... *
      *                                                               *
      *                                                               *
      *****************************************************************
      **********************
       ENVIRONMENT DIVISION.
      **********************

       CONFIGURATION SECTION.
      ***********************
       SPECIAL-NAMES.
      * PARA SERVICIOS FCP DESARROLLADOS EN LAN ELIMINAR ESTA CLAUSULA.
           DECIMAL-POINT IS COMMA.
      ***************
       DATA DIVISION.
      ***************

       WORKING-STORAGE SECTION.
      *************************

      *********************************************
      *                                           *
      * INCLUDE DE LA TABLA CTA.NUEVA/CTA.VIEJA   *
      *                                           *
      *********************************************

           EXEC SQL
                INCLUDE T08CT037
           END-EXEC.


      *********************************************
      *                                           *
      * DECLARACION CONSTANTES Y VARIABLES        *
      *                                           *
      *********************************************

       01  LT-ALFANUMERICAS.
           05 LT-A-1                        PIC X(01)    VALUE '1'.
           05 LT-A-2                        PIC X(01)    VALUE '2'.
           05 LT-A-02                       PIC X(02)    VALUE '02'.
           05 LT-A-04                       PIC X(02)    VALUE '04'.
           05 LT-A-30                       PIC X(02)    VALUE '30'.
           05 LT-A-31129999                 PIC X(10)    VALUE
                                                         '31.12.9999'.
           05 LT-A-N                        PIC X(01)    VALUE 'N'.
           05 LT-A-V                        PIC X(01)    VALUE 'V'.
           05 LT-A-PUNTO                    PIC X(01)    VALUE '.'.
           05 LT-A-T08CT037                 PIC X(08)    VALUE
                                                         'T08CT037'.
           05 LT-A-ERROR-DB2                PIC X(29)    VALUE
             'ERROR DE DB2 AL LEER LA TABLA'.
           05 LT-A-INDICADOR-ERRONEO.
              10 FILLER                     PIC X(28)    VALUE
                 'IND. TIPO DE CUENTA ERRONEO '.
              10 INDICADOR                  PIC X.


       01  LT-NUMERICAS.
           05 LT-N-1                        PIC 9(01)    VALUE 1.
           05 LT-N-2                        PIC 9(01)    VALUE 2.
           05 LT-N-3                        PIC 9(01)    VALUE 3.
           05 LT-N-4                        PIC 9(01)    VALUE 4.
           05 LT-N-5                        PIC 9(01)    VALUE 5.
           05 LT-N-6                        PIC 9(01)    VALUE 6.
           05 LT-N-7                        PIC 9(01)    VALUE 7.
           05 LT-N-8                        PIC 9(01)    VALUE 8.
           05 LT-N-9                        PIC 9(01)    VALUE 9.
           05 LT-N-10                       PIC 9(02)    VALUE 10.
           05 LT-N-11                       PIC 9(02)    VALUE 11.
           05 LT-N-3030                     PIC 9(05)    VALUE 3030.
           05 LT-N-21016                    PIC 9(05)    VALUE 21016.

       01  WS-N-NRO-ERROR                   PIC 9(06)    VALUE ZEROS.


       01  WS-CUENTA-CLIENTE.
           05 ENTIDAD.
              10 E1                         PIC 9(01).
              10 E2                         PIC 9(01).
              10 E3                         PIC 9(01).
              10 E4                         PIC 9(01).
           05 SUCURSAL                      PIC 9(04).
           05 FILLER REDEFINES SUCURSAL.
              10 O1                         PIC 9(01).
              10 O2                         PIC 9(01).
              10 O3                         PIC 9(01).
              10 O4                         PIC 9(01).
           05 DIGITOS-CONTROL.
              10 I                          PIC 9(01).
              10 D                          PIC 9(01).
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


       01  WS-NUM-CUENTA                    PIC 9(13).
       01  WS-NUM-CTA-R REDEFINES WS-NUM-CUENTA.
           05 AHORRO                        PIC 9(03).
           05 OFICINA                       PIC 9(03).
           05 CUENTA-ALF.
              10 NUMERO                     PIC 9(6).
              10 DIGITO                     PIC 9(1).
           05 NUMERO-CUENTA REDEFINES CUENTA-ALF
                                            PIC 9(7).

       01  DIGITO-I                         PIC 9(03).
       01  DIGITO-D                         PIC 9(03).
       01  COCIENTE                         PIC 9(03).
       01  RESTO-I                          PIC 9(02).
       01  RESTO-D                          PIC 9(02).


       01  WS-SQLCODE                       PIC S999.
           88 SQL-CORRECTO                             VALUE ZEROES.
           88 NO-ENCONTRADO                            VALUE +100.


      *********************************************
      * AREA PARA LA RUTINA DE ERROR              *
      *********************************************

       COPY CT0013P.


       LINKAGE SECTION.
      *****************

      *********************************************
      *                                           *
      * AREAS DE ENTRADA/SALIDA                   *
      *                                           *
      *********************************************

       COPY CT0003P.



      *****************************************************************
      ************  P R O C E D U R E   D I V I S I O N  **************
      *****************************************************************
       PROCEDURE DIVISION USING CT0003P.

      **INICIO-PROGRAMA-CTB0005

           PERFORM  1000-INICIO.

           PERFORM  2000-PROCESO.

            PERFORM 8000-FINAL.
      **FINAL-PROGRAMA-CTB0005


       1000-INICIO.
      *****************************************************************
      *  DESACTIVAR CONTROL ERRORES DE ARQUITECTURA
      *  INICIALIZAR COPY DE LA TABLA
      *****************************************************************

           @DEFINE(NO-ERROSQL).
           INITIALIZE  T08CT037
                       CT0013P.


       2000-PROCESO.
      *****************************************************************
      *  ANALIZAMOS EL IND-GENER
      *  CUANDO NO ES NI 1 NI 2 SE PRODUCE UN ERROR
      *****************************************************************

           EVALUATE IND-GENER OF CT0003P
            WHEN LT-A-N
                 PERFORM A2100-OBTENER-CUENTA-NUEVA
            WHEN LT-A-V
                 PERFORM A2200-OBTENER-CUENTA-VIEJA
            WHEN OTHER
                 MOVE LT-A-2                TO CODIGORETORNO OF CT0003P
                 PERFORM A2300-AQERRLOG
           END-EVALUATE.


       A2100-OBTENER-CUENTA-NUEVA.
      ****************************************************************
      *  A PARTIR DE LA CUENTA VIEJA OBTENGO LA NUEVA (T08CT037)
      ****************************************************************

           MOVE NUM-CTA-VIEJO OF CT0003P   TO NUM-CTA-VIEJO OF T08CT037
           MOVE COD-EMPRESA-1 OF CT0003P   TO COD-EMPRESA-1 OF T08CT037

           PERFORM IO1100-LEER-CUENTA-NUEVA


           EVALUATE TRUE
               WHEN SQL-CORRECTO
                    MOVE ZEROS             TO CODIGORETORNO OF CT0003P
                    PERFORM A3000-RELLENAR-CCC-NUEVA
               WHEN NO-ENCONTRADO
                    MOVE LT-A-1            TO CODIGORETORNO OF CT0003P
                    PERFORM A5000-CCC-DESDE-VIEJA
               WHEN OTHER
                    MOVE LT-A-2            TO CODIGORETORNO OF CT0003P
                    PERFORM A5000-CCC-DESDE-VIEJA
                    @LOGERR(ERROR,WS-N-NRO-ERROR,CT0013P)
           END-EVALUATE.
           MOVE WS-CUENTA-CLIENTE          TO CUENTA-CLIENTE OF CT0003P.


       A2200-OBTENER-CUENTA-VIEJA.
      ****************************************************************
      *  A PARTIR DE LA CUENTA NUEVA OBTENGO LA CUENTA VIEJA ULTIMA
      *  QUE SE CONTROLA DESDE LA FEC-VALOR  (T08CT037)
      ****************************************************************

           MOVE COD-TIP-EXPE OF CT0003P    TO COD-TIP-EXPE OF T08CT037
           MOVE NUM-CTA-INT  OF CT0003P    TO NUM-CTA-INT  OF T08CT037
           MOVE COD-EMPRESA  OF CT0003P    TO COD-EMPRESA  OF T08CT037
           MOVE LT-A-31129999              TO FEC-VALOR    OF T08CT037

           PERFORM IO1200-LEER-CUENTA-VIEJA


           EVALUATE TRUE
            WHEN SQL-CORRECTO
                 MOVE ZEROS             TO CODIGORETORNO OF CT0003P
                 PERFORM A4000-RELLENAR-CCC-VIEJA
            WHEN NO-ENCONTRADO
                 MOVE LT-A-1               TO CODIGORETORNO OF CT0003P
                 PERFORM A6000-CCC-DESDE-NUEVA
            WHEN OTHER
                 MOVE LT-A-2               TO CODIGORETORNO OF CT0003P
                 PERFORM A6000-CCC-DESDE-NUEVA
                 @LOGERR(ERROR,WS-N-NRO-ERROR,CT0013P)
           END-EVALUATE.
           MOVE WS-CUENTA-CLIENTE          TO CUENTA-CLIENTE OF CT0003P.


       A2300-AQERRLOG.
      ****************************************************************
      *  ERROR PRODUCIDO AL ENVIARNOS UN INDICADOR DEL TIPO DE CUENTA
      *  PEDIDA ERRONEO
      ****************************************************************

           IF NUM-CTA-VIEJO OF CT0003P NOT = ZEROES
              MOVE LT-A-PUNTO               TO PUNTO1V OF CT0013P
                                               PUNTO2V OF CT0013P
                                               PUNTO3V OF CT0013P
              MOVE SPACES                   TO ESPACIO1V OF CT0013P
              MOVE COD-EMPRESA-1 OF CT0003P TO COD-EMPRESA-1 OF CT0013P
              MOVE NUM-CTA-VIEJO OF CT0003P TO WS-NUM-CUENTA
              MOVE OFICINA OF WS-NUM-CTA-R  TO OFICINA OF CT0013P
              MOVE AHORRO OF WS-NUM-CTA-R   TO AHORRO OF CT0013P
              MOVE NUMERO OF WS-NUM-CTA-R   TO NUMERO-CUENTA OF CT0013P
              MOVE DIGITO OF WS-NUM-CTA-R   TO DIGITO-CONTROL OF CT0013P

           ELSE
              MOVE LT-A-PUNTO               TO PUNTO1N OF CT0013P
                                               PUNTO2N OF CT0013P
              MOVE SPACES                   TO ESPACIO1N OF CT0013P
              MOVE COD-EMPRESA  OF CT0003P  TO COD-EMPRESA OF CT0013P
              MOVE NUM-CTA-INT  OF CT0003P  TO NUM-CTA-INT OF CT0013P
              MOVE COD-TIP-EXPE OF CT0003P  TO COD-TIP-EXPE OF CT0013P
           END-IF.
           MOVE LT-N-3030                   TO WS-N-NRO-ERROR
           MOVE IND-GENER                   TO INDICADOR
           MOVE LT-A-INDICADOR-ERRONEO      TO DESCRIPCION OF CT0013P
           @LOGERR(ERROR,WS-N-NRO-ERROR,CT0013P).


       A3000-RELLENAR-CCC-NUEVA.
      ****************************************************************
      *  MOVER LOS DATOS OBTENIDOS AL MENSAJE DE SALIDA
      ****************************************************************

           MOVE COD-TIP-EXPE  OF T08CT037 TO COD-TIP-EXPE OF CT0003P
                                             EXPEDIENTE-N
           MOVE NUM-CTA-INT   OF T08CT037 TO NUM-CTA-INT OF CT0003P
                                             CTA-CUENTA-N
           MOVE COD-EMPRESA   OF T08CT037 TO COD-EMPRESA OF CT0003P
                                             ENTIDAD
           MOVE COD-SUCURSAL  OF T08CT037 TO SUCURSAL

           PERFORM A7000-OBTENER-DIGITOS-CONTROL.


       A4000-RELLENAR-CCC-VIEJA.
      ****************************************************************
      *  MOVER LOS DATOS OBTENIDOS AL MENSAJE DE SALIDA
      ****************************************************************

           MOVE COD-EMPRESA-1 OF T08CT037 TO COD-EMPRESA-1 OF CT0003P
                                             ENTIDAD
           MOVE NUM-CTA-VIEJO OF T08CT037 TO NUM-CTA-VIEJO OF CT0003P
                                             WS-NUM-CUENTA
           MOVE OFICINA OF WS-NUM-CTA-R   TO SUCURSAL
           MOVE AHORRO OF WS-NUM-CTA-R    TO CTA-AHORRO-V
           MOVE ZEROS                     TO CERO-V
           MOVE NUMERO-CUENTA OF WS-NUM-CTA-R
                                          TO CTA-CUENTA-V

           PERFORM A7000-OBTENER-DIGITOS-CONTROL.


       A5000-CCC-DESDE-VIEJA.
      ****************************************************************
      *  OBTENERMOS LA CUENTA-CLIENTE DESDE NUM-CTA-VIEJO, CUANDO NO
      *  HEMOS ENCONTRADO SU CORRESPONDIENTE NUM_CTA_INT
      *  MOVEMOS DATOS PARA PRODUCIR AQERRLOG
      ****************************************************************

           MOVE SPACES                     TO CUENTA-VIEJA OF CT0013P
           MOVE LT-A-PUNTO                  TO PUNTO1V OF CT0013P
                                               PUNTO2V OF CT0013P
                                               PUNTO3V OF CT0013P
           MOVE SPACES                      TO ESPACIO1V OF CT0013P
           MOVE LT-N-21016                 TO WS-N-NRO-ERROR
           MOVE LT-A-ERROR-DB2             TO DESCRIPCION OF CT0013P
           MOVE LT-A-T08CT037              TO NOM-TABLA OF CT0013P
           MOVE COD-EMPRESA-1 OF CT0003P   TO ENTIDAD
                                              COD-EMPRESA-1 OF CT0013P
           MOVE NUM-CTA-VIEJO OF CT0003P   TO WS-NUM-CUENTA
           MOVE OFICINA OF WS-NUM-CTA-R    TO SUCURSAL
                                              OFICINA OF CT0013P
           MOVE AHORRO   OF WS-NUM-CTA-R     TO CTA-AHORRO-V
                                                AHORRO  OF CT0013P
           MOVE ZEROS                      TO CERO-V
           MOVE NUMERO-CUENTA OF WS-NUM-CTA-R
                                           TO CTA-CUENTA-V
           MOVE NUMERO OF WS-NUM-CTA-R     TO NUMERO-CUENTA OF CT0013P
           MOVE DIGITO OF WS-NUM-CTA-R     TO DIGITO-CONTROL OF CT0013P

           PERFORM A7000-OBTENER-DIGITOS-CONTROL.


       A6000-CCC-DESDE-NUEVA.
      ****************************************************************
      *  OBTENERMOS LA CUENTA-CLIENTE DESDE NUM-CTA-INT, CUANDO NO
      *  HEMOS ENCONTRADO SU CORRESPONDIENTE NUM_CTA_VIEJO
      *  MOVEMOS DATOS PARA PRODUCIR AQERRLOG
      ****************************************************************

           MOVE SPACES                      TO CUENTA-NUEVA OF CT0013P
           MOVE LT-A-PUNTO                  TO PUNTO1N OF CT0013P
                                               PUNTO2N OF CT0013P
           MOVE SPACES                      TO ESPACIO1N OF CT0013P
           MOVE LT-N-21016                  TO WS-N-NRO-ERROR
           MOVE LT-A-ERROR-DB2              TO DESCRIPCION OF CT0013P
           MOVE LT-A-T08CT037               TO NOM-TABLA OF CT0013P

           MOVE COD-EMPRESA  OF CT0003P     TO ENTIDAD
                                               COD-EMPRESA OF CT0013P
           MOVE COD-SUCURSAL-ALTA
                             OF CT0003P     TO SUCURSAL
           MOVE NUM-CTA-INT  OF CT0003P     TO CTA-CUENTA-N
                                               NUM-CTA-INT OF CT0013P
           MOVE COD-TIP-EXPE OF CT0003P     TO EXPEDIENTE-N
                                               COD-TIP-EXPE OF CT0013P

           PERFORM A7000-OBTENER-DIGITOS-CONTROL.


       A7000-OBTENER-DIGITOS-CONTROL.
      ****************************************************************
      *  OBTENERMOS LOS DIGITOS DE CONTROL DE LA CUENTA-CLIENTE
      ****************************************************************

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
              MOVE RESTO-I                  TO I
           ELSE
              COMPUTE I = LT-N-11 - RESTO-I
           END-IF.

           IF RESTO-D = ZEROES OR = LT-N-1
              MOVE RESTO-D                  TO D
           ELSE
              COMPUTE D = LT-N-11 - RESTO-D
           END-IF.


       8000-FINAL.
      ****************************************************************
      *  CONTROLAR EL CODIGO DE RETORNO
      *  FINALIZAR EL PROGRAMA
      ****************************************************************

           GOBACK.


       IO1100-LEER-CUENTA-NUEVA.
      ****************************************************************
      *  SE LEERA CUENTA NUEVA
      ****************************************************************

           EXEC SQL
                SELECT COD_TIP_EXPE    ,
                       NUM_CTA_INT     ,
                       COD_EMPRESA     ,
                       COD_SUCURSAL
                INTO  :T08CT037.COD-TIP-EXPE  ,
                      :T08CT037.NUM-CTA-INT   ,
                      :T08CT037.COD-EMPRESA   ,
                      :T08CT037.COD-SUCURSAL
                FROM  T08CT037
                WHERE NUM_CTA_VIEJO   = :T08CT037.NUM-CTA-VIEJO  AND
                      COD_EMPRESA_1   = :T08CT037.COD-EMPRESA-1
           END-EXEC

           MOVE SQLCODE     TO WS-SQLCODE.


       IO1200-LEER-CUENTA-VIEJA.
      ****************************************************************
      *  SE LEERA CUENTA VIEJA ULTIMA
      ****************************************************************

           EXEC SQL
                SELECT FEC_VALOR       ,
                       NUM_CTA_VIEJO   ,
                       COD_EMPRESA_1
                INTO  :T08CT037.FEC-VALOR      ,
                      :T08CT037.NUM-CTA-VIEJO  ,
                      :T08CT037.COD-EMPRESA-1
                FROM T08CT037
                WHERE COD_TIP_EXPE    = :T08CT037.COD-TIP-EXPE       AND
                      NUM_CTA_INT     = :T08CT037.NUM-CTA-INT        AND
                      COD_EMPRESA     = :T08CT037.COD-EMPRESA        AND
                      FEC_VALOR      <= :T08CT037.FEC-VALOR
                AND
                  FEC_VALOR  =(SELECT MAX(FEC_VALOR)
                               FROM T08CT037
                      WHERE COD_TIP_EXPE    = :T08CT037.COD-TIP-EXPE AND
                            NUM_CTA_INT     = :T08CT037.NUM-CTA-INT  AND
                            COD_EMPRESA     = :T08CT037.COD-EMPRESA  AND
                            FEC_VALOR      <= :T08CT037.FEC-VALOR )
           END-EXEC.

           MOVE SQLCODE     TO WS-SQLCODE.
