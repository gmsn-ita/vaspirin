      program broad
C
C     INTERPOLATE TO PLOT-GRID AND CONVOLUTE WITH LORENTZIAN
C     (ENERGY DEPENDENT HALFWIDTH ) FOR LIFE-TIME BROADENING
C     AND GAUSSIAN SPECTROMETER RESOLUTION.
C
      IMPLICIT REAL (A-H,O-Z)
C
      PARAMETER (natmax=31)
      PARAMETER (NGC=100)
      PARAMETER (n0=301)
      PARAMETER (norb=18)
      PARAMETER (nfile=24)
C
      DIMENSION E0(N0),A0(N0),alorb(n0,norb,natmax),bs(norb)
      DIMENSION GC(-NGC:NGC),AH(-NGC:NGC)
      CHARACTER*80 header
      CHARACTER*233 spd
      CHARACTER*6 filename(nfile)
C
      DATA PI/3.141596/
      spd="#energy          s-u        s-d        py-u"//
     &"        py-d         pz-u        pz-d"//
     &"       px-u        px-d        dxy-u        dxy-d"//
     &"       dyz-u       dyz-d      dz2-u"//
     &"       dz2-d       dxz-u       dxz-d"//
     &"       dx2-u       dx2-d        "
      filename(1)="O_1"
      filename(2)="O_2"
      filename(3)="O_3"
      filename(4)="O_4"
      filename(5)="O_5"
      filename(6)="O_6"
      filename(7)="O_7"
      filename(8)="O_8"
      filename(9)="O_9"
      filename(10)="O_10"
      filename(11)="O_11"
      filename(12)="O_12"
      filename(13)="O_13"
      filename(14)="O_14"
      filename(15)="O_15"
      filename(16)="O_16"
      filename(17)="V_1"
      filename(18)="V_2"
      filename(19)="V_3"
      filename(20)="La_4"
      filename(21)="La_1"
      filename(22)="La_2"
      filename(23)="La_3"
      filename(24)="La_4"
C
C
C     SET FERMI ENERGY EQUAL TO ZERO 
C
      hws=0.20
C
      open (99,file="DOSCAR")
      print *, "DOSCAR"
      read (99,*) nat
      read (99,*) 
      read (99,*) 
      read (99,*) 
      read (99,101) header
c
c     open output lateron 
c
      read (99,*) e_max,e_min,ne,ef
      ESTEP= (e_max-e_min)/float(ne-1)
C
C     SET UP GAUSSIAN CONVOLUTION FUNCTION
C
      AFAC=-ALOG(5.E-1)/(HWS/2.0E0)**2
      BFAC=SQRT(AFAC/PI)
      DO  I=-NGC,NGC
      GC(I)=EXP(-AFAC*(I*ESTEP)**2)*BFAC
      end do


      DO I=1,ne
c      print *,'1'
      read (99,*) e,a0(i)
      E0(I)=E-EF
c      print *,'3'
      end do
C
C     CONVOLUTE NOW
C


      open (98,file="Total")
      write (98,102) header
      DO I=1,ne
      b0=CONVGAU(A0,I,GC,AH,ESTEP,NGC,n0)
      if (b0 .lt. 0.0) b0=0.0
      write (98,*) e0(i),b0
      end do
      do n=1,nat
c
c     read DOS
c
      read (99,*) 
      

      DO I=1,ne
      read (99,100) e,(alorb(i,j,n),j=1,norb)
      end do
      end do
c
c     average DOS
c


c      DO I=1,ne
c      DO j=1,norb
c      do n=1,nat,4
c      alorb(i,j,n)=(alorb(i,j,n)+alorb(i,j,n+1)
c     +             +alorb(i,j,n+2)+alorb(i,j,n+3))/4.0
c      end do
c      end do
c      end do
c      ifile=0


      do n=1,nfile,1
      ifile=ifile+1
c
c     open output lateron 
c
      open (ifile+1111,file=filename(ifile))
      write (ifile+1111,102) header
      write (ifile+1111,103) filename(ifile)
      write (ifile+1111,104) spd
C
C     CONVOLUTE NOW
C



      DO I=1,ne
      DO j=1,norb
      bs(j)=CONVGAU(alorb(1,j,n),I,GC,AH,ESTEP,NGC,n0)
      if (bs(j) .lt. 0.0) bs(j)=0.0
      end do
      write (ifile+1111,100) e0(i),(bs(j),j=1,norb)
      end do
      end do
C
C
      stop
 100  format(f11.3,18e12.4)
 101  format(a80)
 102  format("#",a80)
 103  format("#atom:",a6)
 104  format(a233)
      END
      REAL FUNCTION CONVGAU(A1,IND,GC,AH,ESTEP,NGC,N1)
C
      IMPLICIT REAL (A-H,O-Z)
C
C     DO THE CONVOLUTION INTEGRAL BY TRAPEZOIDAL RULE
C
      DIMENSION A1(N1), GC(-NGC:NGC), AH(-NGC:NGC)
C


      DO 10 I=-NGC,NGC
   10 AH(I)=0.D0
      DO 20 I=0,NGC
      IMX=IND+I
      IF(IMX.GT.N1) GOTO 30
   20 AH(I)=A1(IMX)*GC(I)
   30 DO 40 I=-1,-NGC,-1
      IMX=IND+I
      IF(IMX.LT.1) GOTO 50
   40 AH(I)=A1(IMX)*GC(I)
   50 SUM=0.D0
      DO 60 I=-NGC,NGC
   60 SUM=SUM+AH(I)
C
      CONVGAU=SUM*ESTEP
C
      RETURN
      END
