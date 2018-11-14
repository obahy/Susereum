      * HTTP Server for IBM i example
      * Installing and running an ILE RPG CGI program
      * http://www-03.ibm.com/systems/power/software/i/http/examples/ile-rpg.html
      *
      *
      *
      **************************************************************************
      * Variables for the CGI interface API for QtmhRdStIn.                    *
     DBufIn            S           1024a   INZ
     DBufInLn          S              9b 0 INZ(1024)
     DStdInLn          S              9b 0
      **************************************************************************
      * Variables for the CGI interface API for QtmhGetEnv.
     DEnvRec           S           1024A   INZ
     DEnvRecLen        S              9B 0 INZ(1024)
     DEnvLen           S              9B 0 INZ
     DEnvName          S             25A   INZ('CONTENT_LENGTH')
     DEnvNameLen       S              9B 0 INZ(14)
      **************************************************************************
      *Variables for the CGI interface API for QtmhWrStout.
     DBufOut           S           2048a   INZ
     DBufOutln         S              9b 0
      *************************************************************************
      ***                   Data structure for error reporting.             ***
      *** Copied from QSYSINC/QRPGLESRC(QUSEC).                             ***
      *** The QUSBPRV must be initialized to 16.                            ***
      *** This is the common error structure that is passed to the CGI APIs;***
      *** QtmhWrStOut, QtmhRdStin, QtmhGetEnv and QtmhCvtDb.  The Error     ***
      *** structure is documented in the "iSeries System API Reference".     ***
      *************************************************************************
     DQUSEC            DS
     D*                                             Qus EC
     D QUSBPRV                 1      4B 0 INZ(16)
     D*                                             Bytes Provided
     D QUSBAVL                 5      8B 0
     D*                                             Bytes Available
     D QUSEI                   9     15
     D*                                             Exception Id
     D QUSERVED               16     16
      **************************************************************************
      *** Constants for names of CGI APIs.                                   ***
     DAPIStdIn         C                   'QtmhRdStin'
     DAPIStdOut        C                   'QtmhWrStout'
     DAPIGetEnv        C                   'QtmhGetEnv'
      **************************************************************************
      * Prototype for c2n procedure that converts content length to numeric. ***
     Dc2n              PR            30p 9
     Dc                              32
     DcLen                            9B 0
      **************************************************************************
      * Compile-time array for HTML output.                                  ***
     Darrsize          C                   23
     Dhtml             S             80    DIM(arrsize) PERRCD(1) CTDATA
     DContentLn        S              9B 0 INZ(0)
     DEnvCL            S             20A   INZ('CONTENT_LENGTH')
     DEnvSS            S             20A   INZ('SERVER_SOFTWARE')
     DEnvMethod        S             20A   INZ('REQUEST_METHOD')
     DEnvQS            S             20A   INZ('QUERY_STRING')
     DEnvMDResp        S             30A   INZ
     DEnvSSResp        S             50A   INZ
     DEResp            S              4A   INZ
     D**************************************************************************
     D* Define line feed that is required when writing data to std output.   ***
     Dlinefeed         C                   x'15'
     Dbreak            C                   '<br>'
     Dmaxdataln        S              4B 0 INZ(1024)
     D**************************************************************************
     D* Some local variables used for adding newline in std output buffer.   ***
     Dcnt              S              4B 0 INZ(1)
     DWORK2            S             80A   INZ
     DResult           S              9B 0 INZ
      **************************************************************************
      * Start of CGI Program execution section...
      **************************************************************************
      * Initialize error code structure for error ids.
      * This allows for 7 bytes in QUSEI for error message id.
     C                   Z-ADD     16            QUSBPRV
      **************************************************************************
      **** Read the Environment variable, REQUEST_METHOD.
      **************************************************************************
     C                   MOVEL     EnvMethod     EnvName
     C                   Z-ADD     14            EnvNameLen
     C                   callb     APIGetEnv
     C                   parm                    EnvRec
     C                   parm                    EnvRecLen
     C                   parm                    EnvLen
     C                   parm                    EnvName
     C                   parm                    EnvNameLen
     C                   parm                    QUSEC
     C                   MOVEL     EnvRec        EnvMDResp
      **************************************************************************
      **** Is the REQUEST_METHOD, POST?
     C     4             subst     EnvRec:1      EResp
     C     EResp         ifeq      'POST'
      **************************************************************************
      * Get Environment Variable 'Content_Length' using 'QtmhGetEnv' API
     C                   MOVEL     EnvCL         EnvName
     C                   Z-ADD     14            EnvNameLen
     C                   CALLB     APIGetEnv
     C                   parm                    EnvRec
     C                   parm                    EnvRecLen
     C                   parm                    EnvLen
     C                   parm                    EnvName
     C                   parm                    EnvNameLen
     C                   parm                    QUSEC
      * Convert Content_Length to numeric.
     C                   eval      ContentLn=c2n(EnvRec : EnvLen)
      * When the Content Length is greater than the buffer, Read maxdataln.
     C     ContentLn     ifgt      maxdataln
     C                   Z-ADD     maxdataln     ContentLn
     C                   endif
      * Specify InDataLn to Content_Length value.  Never should a CGI program
      * ever attempt to read more than content length.  Specification of more
      * than content length in InDataLn is not defined.
     C                   Z-ADD     ContentLn     BufInLn
      **************************************************************************
      * Read standard input
     C                   callb     APIStdIn
     C                   parm                    BufIn
     C                   parm                    BufInLn
     C                   parm                    StdInLn
     C                   parm                    QUSEC
     C                   MOVEL     StdInLn       Result
     C                   else
      **************************************************************************
      **** Read the Environment variable, QUERY_STRING.
      **************************************************************************
     C                   MOVEL     EnvQS         EnvName
     C                   Z-ADD     12            EnvNameLen
     C                   callb     APIGetEnv
     C                   parm                    EnvRec
     C                   parm                    EnvRecLen
     C                   parm                    EnvLen
     C                   parm                    EnvName
     C                   parm                    EnvNameLen
     C                   parm                    QUSEC
      **************************************************************************
      **** Check length of environment value is less than
      **** the receive buffer.  When this occurs, the
      **** QtmhGetEnv sets the EnvLen to the actual value
      **** length without changing the receive buffer.
     C     EnvLen        ifgt      maxdataln
     C                   eval      Bufin='Data buffer +
     C                              not big enough for +
     C                              available input data.'
     C                   Z-ADD     80            Result
     C                   else
     C                   MOVEL     EnvRec        BufIn
     C                   MOVEL     EnvLen        Result
     C                   endif
     C                   endif
      **************************************************************************
      **** Read the Environment variable, SERVER_SOFTWARE.
      **************************************************************************
     C                   MOVEL     EnvSS         EnvName
     C                   Z-ADD     15            EnvNameLen
     C                   callb     APIGetEnv
     C                   parm                    EnvRec
     C                   parm                    EnvRecLen
     C                   parm                    EnvLen
     C                   parm                    EnvName
     C                   parm                    EnvNameLen
     C                   parm                    QUSEC
     C                   MOVEL     EnvRec        EnvSSResp
      **************************************************************************
      **** Put the data written to standard output in buffer; bufout.        ***
      **************************************************************************
      * For each line of HTML, move it to BufOut and set the
      * output buffer's length(BufOutLn).
     C                   do        arrsize       i                 5 0
      * Write out HTTP response and HTML lines.
     C     i             iflt      17
     C     BufOut        cat       html(i):0     BufOut
     C     BufOut        cat       linefeed:0    BufOut
     C                   endif
      * Add the data read from standard input or QUERY_STRING.
     C     i             ifeq      17
     D* Add html break to BufOut string written to standard output
     D* when input is greater than 79.
     C     Result        dowgt     79
     C     80            SUBST     BufIn:cnt     WORK2
     C                   cat       work2:0       BufOut
     C                   cat       break:0       BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*                  cat       linefeed:0    BufOut
     C                   add       80            cnt
     C                   sub       80            Result
     C                   ENDDO
     C                   IF        Result > 0
     C                   clear                   WORK2
     C     Result        SUBST     BufIn:cnt     WORK2
     C                   cat       work2:0       BufOut
     C                   cat       break:0       BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*                  cat       linefeed:0    BufOut
     C                   ENDIF
     C                   endif
      * Add the Environment variable header line for REQUEST_METHOD.
     C     i             ifeq      18
     C     BufOut        cat       html(i):0     BufOut
     C     BufOut        cat       break:0       BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*    BufOut        cat       linefeed:0    BufOut
     C                   endif
      * Display the Environment variable REQUEST_METHOD.
     C     i             ifeq      19
     C     BufOut        cat       EnvMDResp:0   BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*    BufOut        cat       linefeed:0    BufOut
     C                   endif
      * Add the Environment variable header line for SERVER_SOFTWARE.
     C     i             ifeq      20
     C     BufOut        cat       html(i):0     BufOut
     C     BufOut        cat       break:0       BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*    BufOut        cat       linefeed:0    BufOut
     C                   endif
      * Display the Environment variable SERVER_SOFTWARE.
     C     i             ifeq      21
     C     BufOut        cat       EnvSSResp:0   BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*    BufOut        cat       linefeed:0    BufOut
     C                   endif
      * Write out closing HTML lines.
     C     i             ifgt      21
     C     BufOut        cat       html(i):0     BufOut
      * For V4R2, the newline after 254 characters is not needed.
     C*    BufOut        cat       linefeed:0    BufOut
     C                   endif
     C                   enddo
      **************************************************************************
      **** Get length of data to be sent to standard output.
      **************************************************************************
     C                   z-add     1             i
     C     arrsize       mult      80            i
     C     a             doune     ' '
     C     1             subst     bufout:i      a                 1
     C                   sub       1             i
     C                   enddo
     C     i             add       1             BufOutLn
      **************************************************************************
      **** Send BufOut to standard output.
      **************************************************************************
     C                   callb     APIStdOut
     C                   parm                    BufOut
     C                   parm                    BufOutLn
     C                   parm                    QUSEC
      **************************************************************************
      * Return to caller
      **************************************************************************
     C                   return
      ********************************************************
      * Function: Convert a character to numeric value.      *
      ********************************************************
      * nomain c2n subprocedure
     Pc2n              B
     Dc2n              PI            30p 9
     Dc                              32
     DcLen                            9B 0
      * variables
     Dn                s             30p 9
     Dwknum            s             30p 0
     DpowerOfTen       s             10I 0
     Dsign             s              1  0 inz(1)
     Ddecpos           s              3  0 inz(0)
     Dindecimal        s              1    inz('0')
     Di                s              3  0
     Dj                s              3  0
     D                 ds
     Dalpha1                          1
     Dnumber1                         1  0 overlay(alpha1) inz(0)
     C                   eval      c = %triml(c)
     C                   eval      j = cLen
     C     1             do        j             i
     C                   eval      alpha1=%subst(c:i:1)
     C                   select
     C                   when      alpha1='-'
     C                   eval      sign= -1
     C                   when      alpha1='.'
     C                   eval      indecimal='1'
     C                   when      alpha1 >='0' and alpha1 <= '9'
     C                   eval      wknum  = wknum  * 10 + number1
     C                   if        indecimal = '1'
     C                   eval      decpos = decpos + 1
     C                   endif
     C                   endsl
     C                   enddo
     C                   eval(h)   powerOfTen = 10 ** decpos
     C     wknum         div(h)    powerOfTen    n
     C                   if        sign = -1
     C                   eval      n = -n
     C                   endif
     C                   return    n
     Pc2n              E
      **************************************************************************
      * Compile-time array follows:
      **************************************************************************
      * A line MUST follow Content-type with only a single newline(x'15').  If
      * this newline does not exist, Then NO data will be served to the client.
      * This newline represents the end of the HTTP header and the data follows.
**CTDATA HTML
Content-type: text/html

<html>
<head>
<title>Sample iSeries RPG program executed by HTTP Server as a CGI</title>
</head>
<body>
<h1>Sample iSeries RPG program.</h1>
<br>
<br>
<p>This is sample output using iSeries HTTP Server CGI APIs from an RPG
program.  This program reads the input data from Query_String
environment variable when the Request_Method is GET and reads
standard input when the Request_Method is POST.
<p>Server input:<br>

<p>Environment variable - REQUEST_METHOD:

<p>Environment variable - SERVER_SOFTWARE:

</body>
</html>
