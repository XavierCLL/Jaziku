;**************************************************************************************
;Centro de Modelado Científico (CMC). La Universidad del Zulia   -- cmc.org.ve
;Observatorio Andino de Eventos Extraordinarios (OA)             -- ole2.org
;Copyleft: Ángel G. Muñoz S. -- agmunoz@cmc.org.ve
;Descripción: script NCL del OA y CMC para generar archivo netcdf con climatologia del pais
;***************************************************************************************
;---------------------------------------------------------------------------------------
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"
;--------------------------------------------------------------------------------------- 

begin
  npts = 321 ; Num estaciones
  ntim = 360; Num meses  total 456. para la climo: 360
  minlat=-55 ; lo obvio
  maxlat=-5
  minlon=-70
  maxlon=-35
  reso=60  ; Resolucion deseada en km


;*****************************************************************************
;Seccion Lectura Archivo ASCII
;*****************************************************************************
  data = asciiread("data_T.dat",(/ntim*npts,5/),"float")
printVarSummary(data)

; Años y meses
  ano1d= (data(::npts,0))  ;con el ::ALGO hacemos que lea cada ALGO pasos
  mes1d= (data(::npts,1))

; Para las latidudes de las estaciones, basta adquirir las primeras ntim lineas:
  lat1d = (data(0:npts-1,2))

; Idem para las longitudes
  lon1d  = (data(0:npts-1,3))

;***************************************************************************
;Abrimos archivo CRU para first guess del analisis objetivo
;**************************************************************************
  f    = addfile ("CRUTEM3v.nc", "r")
  pr   = f->temp(:,:,:)
  T    = f->T(:)
  lati = f->Y
  loni = f->X
  pr!0="time"
  pr!1="lat"
  pr!2="lon"
;printVarSummary(pr)

;*****************************************************************************
; Definimos la nueva malla para el Cressman
;*****************************************************************************
  lon = fspan(minlon, maxlon,floattoint(abs(minlon-maxlon)*111.111/reso)) ;Creamos la malla (longitud, res=30 km)
  nlon = dimsizes( lon)
  ;print(lon)
  lat = fspan(minlat, maxlat,floattoint(abs(maxlat-minlat)*111.111/reso))  ;Creamos la malla (latitud, res=30 km)
  nlat = dimsizes( lat)
 ; printVarSummary(lat)
 ; printVarSummary(lon)

;****************************************************
;Interpolacion a la malla del Cressman de la data CRU
;****************************************************
pre=linint2 (pr&lon, pr&lat, pr, False, lon, lat, 0)
pre@_FillValue=-99.90
pre@lon=lon
pre@lat=lat
pre!0="time"
pre!1="lat"
pre!2="lon"

printVarSummary(pre)
;print(pre)

;*****************************************************************************
; Definimos unos arreglos a usar
 temp1D=new((/ntim,npts/),typeof(data))
 temp2D=new((/ntim,npts,npts/),typeof(temp1D))

; Ciclo de lectura y almacenamiento en arreglos para la variable física 
  do i=0,ntim-1 
   temp1D(i,:)   = data(i*npts:(i+1)*npts-1,4)            
;   temp2D(i,:,:) = onedtond(temp1D(i,:),(/npts,npts/)) ; convertimos a 2D
  end do
;print(temp1D)
;**************************************************
;Esto Define los valores faltantes (superfluo)
  temp1D@_FillValue    = -99.90


; Assign named dimensions 

 ; temp2D!0 = "lat"
 ; temp2D!1 = "lon"

; Assign coordinate variables

 ; temp2D&lat = lat1d
 ; temp2D&lon = lon1d

  ;printVarSummary(temp2D)
;============================================================== ;
  grid =new((/nlat,nlon,ntim/),typeof(temp1D))
  grid!0="lat"
  grid!1="lon"
  grid!2="T"
  do nmo =0,ntim-1
    zVal = temp1D(nmo,:)
    rscan = (/0.5,0.3,0.1/)
    opt = True
    opt@guess = pre(nmo,:,:)  ; CRU como fisrt guess
    ;opt@zonal = True ; esta opción (recomendada) permite que FG = medias zonales
    grid(:,:,nmo) = obj_anal_ic(lon1d,lat1d,zVal,lon,lat, rscan, opt) 
    ;printVarSummary(grid)
    ;print(grid)
  end do

; Ahora control de calidad mínima: valores negativos tras Cressman-->Dato faltante
  do it=0,ntim-1
   do i=0,nlat-1
     do j=0,nlon-1
       if ((.not.ismissing(grid(i,j,it))).and.(grid(i,j,it).lt.0)) then 
        grid(i,j,it)=-999
       end if
     end do
   end do
  end do
;**************************************************
; Atributos requeridos para evitar warnings fastidiosos
;**************************************************
  grid&lon@units    = "degrees_east"
  grid&lat@units     = "degrees_north"
  ;pre&lon@units    = "degrees_east"
  ;pre&lat@units     = "degrees_north"
;**************************************************
;Esto Define los valores faltantes (superfluo)
  ;grid@_FillValue    = 0.0
  grid@_FillValue    = -999
  grid&T=T

;******************************
;Ahora rellenamos con Poisson relajado
;********************************

  guess     = 1                ; use zonal means
  is_cyclic = False             ; cyclic [global]
  nscan     = 1500             ; usually much less than this
  eps       = 1.e-2            ; variable dependent
  relc      = 0.6              ; relaxation coefficient
  opt2       = 0                ; not used

 do nme=0,ntim-1
   poisson_grid_fill(grid(:,:,nme), is_cyclic, guess, nscan, eps, relc, opt2)
 end do

;**************************************************************************
        filo = "climatologia_mens_t.nc"             ; Output file
        system("/bin/rm -f " + filo)    ; remove if exists
        fout1  = addfile (filo, "c")  ; open output file

    ;===================================================================
    ; explicitly declare file definition mode. Improve efficiency.
    ;===================================================================
        setfileoption(fout1,"DefineMode",True)

    ;===================================================================
    ; create global attributes of the file
    ;===================================================================
        fAtt               = True            ; assign file attributes
        fAtt@titulo        = "Temperatura Media Mensual 1970-2000 OSSA "
        fAtt@metodo        = "Cressman (1959) con Poisson (relajacion). Resolucion 60 km"
        fAtt@fuente        = "OSSA -- Centro de Modelado Cientifico (CMC) - LUZ"
        fAtt@autores       = "Angel G. Munoz (agmunoz@cmc.org.ve)"
       fAtt@creacion       = systemfunc ("date")

       ;filedimdef(fout1,"time",-1,True)
       fileattdef( fout1, fAtt )            ; copy file attributes
       T@units ="meses desde 1971-01-01"

       fout1->T        = T
       fout1->tmed     = grid

;*********************************************************************************



end
;------------------------------------------------------------------------------------- 