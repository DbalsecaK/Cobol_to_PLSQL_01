      *************************
       IDENTIFICATION DIVISION.
      *************************

       PROGRAM-ID. CTB0006.
       AUTHOR. TERESA DE LUCAS JUNCO.
       DATE-COMPILED.

      *****************************************************************
      **************  C A J A  E S P A # A  -  S I G L O  *************
      *****************************************************************
      *                                                               *
      * PROGRAMA.......: CTB0006                                      *
      * APLICACION.....: CONVIVENCIA.                                 *
      * FEC.CODIFICAC..: 15-03-94.                                    *
      *                                                               *
      * FUNCIONES:  ESTA RUTINA CALCULA LOS DIGITOS DE CONTROL DEL    *
      *             NUMERO CUENTA CLIENTE (CCC).                      *
      *                                                               *
      * ENTRADA..:  CT0006P                                           *
      *                                                               *
      * SALIDA...:  CT0006P                                           *
      *                                                               *
      * =====================> MODIFICACIONES <====================== *
      *                                                               *
      *   AUTOR    FECHA            CAUSA DE LA MODIFICACION          *
      * --------- -------- ------------------------------------------ *
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
      * DECLARACION CONSTANTES Y VARIABLES        *
      *                                           *
      *********************************************

       01  LT-ALFANUMERICAS.
           05 LT-A-0                        PIC X        VALUE '0'.
           05 LT-A-1                        PIC X        VALUE '1'.
           05 LT-A-NO-NUMERICO              PIC X(30)    VALUE
                 'DATOS DE ENTRADA NO NUMERICOS'.


       01  LT-NUMERICAS.
           05 LT-N-1                        PIC 9        VALUE 1.
           05 LT-N-2                        PIC 9        VALUE 2.
           05 LT-N-3                        PIC 9        VALUE 3.
           05 LT-N-4                        PIC 9        VALUE 4.
           05 LT-N-5                        PIC 9        VALUE 5.
           05 LT-N-6                        PIC 9        VALUE 6.
           05 LT-N-7                        PIC 9        VALUE 7.
           05 LT-N-8                        PIC 9        VALUE 8.
           05 LT-N-9                        PIC 9        VALUE 9.
           05 LT-N-10                       PIC 9(2)     VALUE 10.
           05 LT-N-11                       PIC 9(2)     VALUE 11.
           05 LT-N-3030                     PIC 9(04)    VALUE 3030.

       01  WS-N-NRO-ERROR                   PIC 9(06)    VALUE ZEROS.

       01  WS-CUENTA-CLIENTE.
           05 ENTIDAD.
              10 E1                         PIC 9(01) VALUE ZEROS.
              10 E2                         PIC 9(01) VALUE ZEROS.
              10 E3                         PIC 9(01) VALUE ZEROS.
              10 E4                         PIC 9(01) VALUE ZEROS.
           05 SUCURSAL.
              10 O1                         PIC 9(01) VALUE ZEROS.
              10 O2                         PIC 9(01) VALUE ZEROS.
              10 O3                         PIC 9(01) VALUE ZEROS.
              10 O4                         PIC 9(01) VALUE ZEROS.
           05 DIGITOS-CONTROL.
              10 I                          PIC 9(01) VALUE ZEROS.
              10 D                          PIC 9(01) VALUE ZEROS.
           05 CUENTA.
              10 N0                         PIC 9(01) VALUE ZEROS.
              10 N1                         PIC 9(01) VALUE ZEROS.
              10 N2                         PIC 9(01) VALUE ZEROS.
              10 N3                         PIC 9(01) VALUE ZEROS.
              10 N4                         PIC 9(01) VALUE ZEROS.
              10 N5                         PIC 9(01) VALUE ZEROS.
              10 N6                         PIC 9(01) VALUE ZEROS.
              10 D7                         PIC 9(01) VALUE ZEROS.
              10 G8                         PIC 9(01) VALUE ZEROS.
              10 G9                         PIC 9(01) VALUE ZEROS.


       01  DIGITO-I                         PIC 9(03) VALUE ZEROS.
       01  DIGITO-D                         PIC 9(03) VALUE ZEROS.
       01  COCIENTE                         PIC 9(03) VALUE ZEROS.
       01  RESTO-I                          PIC 9(02) VALUE ZEROS.
       01  RESTO-D                          PIC 9(02) VALUE ZEROS.



      *********************************************
      * AREA PARA LA RUTINA DE ERROR              *
      *********************************************

       COPY CT0014P.


       LINKAGE SECTION.
      *****************

      *********************************************
      *                                           *
      * AREAS DE ENTRADA/SALIDA                   *
      *                                           *
      *********************************************

       COPY CT0006P.



      *****************************************************************
      ************  P R O C E D U R E   D I V I S I O N  **************
      *****************************************************************
       PROCEDURE DIVISION USING CT0006P.
       
           INITIALIZE WS-CUENTA-CLIENTE.
      **INICIO-PROGRAMA-CTB0006

           PERFORM  1000-INICIO.

           PERFORM  2000-PROCESO.

            PERFORM 8000-FINAL.
      **FINAL-PROGRAMA-CTB0006


       1000-INICIO.
      *****************************************************************
      *  INICIALIZAR COPY DEL MENSAJE DE ERROR
      *****************************************************************

           INITIALIZE  CT0014P.


       2000-PROCESO.
      *****************************************************************
      *  COMPROBAMOS SI LOS DATOS DE ENTRADA SON NUMERICOS
      *  CALCULAMOS LOS DIGITOS DE CONTROL
      *****************************************************************

           PERFORM A2100-COMPROBAR-DATOS
           PERFORM A2200-CALCULAR-DIGITOS.

           MOVE DIGITOS-CONTROL             TO DIG-CONTROL OF CT0006P.


       A2100-COMPROBAR-DATOS.
      ****************************************************************
      *  COMPROBAMOS SI LOS DATOS QUE NOS VIENEN SON NUMERICOS
      ****************************************************************

           IF COD-ENTIDAD  OF CT0006P IS NOT NUMERIC OR
              COD-SUCURSAL OF CT0006P IS NOT NUMERIC OR
              NUM-CTA      OF CT0006P IS NOT NUMERIC
              MOVE COD-ENTIDAD  OF CT0006P  TO COD-ENTIDAD  OF CT0014P
              MOVE NUM-CTA      OF CT0006P  TO NUM-CTA      OF CT0014P
              MOVE COD-SUCURSAL OF CT0006P  TO COD-SUCURSAL OF CT0014P
              MOVE LT-A-NO-NUMERICO         TO DESCRIPCION  OF CT0014P
              MOVE LT-N-3030                TO WS-N-NRO-ERROR

              SET ERROR-DATOS               TO TRUE
              @LOGERR(ERROR,WS-N-NRO-ERROR,CT0014P)
           ELSE
              SET CTA-OK                    TO TRUE
           END-IF.


       A2200-CALCULAR-DIGITOS.
      ****************************************************************
      *  OBTENERMOS LOS DIGITOS DE CONTROL DE LA CUENTA-CLIENTE
      ****************************************************************

           MOVE COD-ENTIDAD  OF CT0006P     TO ENTIDAD
           MOVE COD-SUCURSAL OF CT0006P     TO SUCURSAL
           MOVE NUM-CTA      OF CT0006P     TO CUENTA

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
      *  FINALIZAR EL PROGRAMA
      ****************************************************************

           GOBACK.
