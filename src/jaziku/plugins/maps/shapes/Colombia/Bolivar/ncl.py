#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2012 IDEAM
#
# This file is part of Jaziku.
#
# Jaziku is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jaziku is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jaziku.  If not, see <http://www.gnu.org/licenses/>.

import os

def code(map_properties):
    return '''


load "/usr/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "/usr/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "/usr/lib/ncarg/nclscripts/csm/contributed.ncl"

;################## accent table

Agrave = "A~H-15V6F35~A~FV-6H3~" ; À
agrave = "a~H-13V2F35~A~FV-2H3~" ; à
Aacute = "A~H-15V6F35~B~FV-6H3~" ; Á
aacute = "a~H-13V2F35~B~FV-2H3~" ; á
Acirc = "A~H-15V6F35~C~FV-6H3~" ; Â
acirc = "a~H-13V2F35~C~FV-2H3~" ; â
Atilde = "A~H-15V6F35~D~FV-6H3~" ; Ã
atilde = "a~H-13V2F35~D~FV-2H3~" ; ã
Auml = "A~H-15V6F35~H~FV-6H3~" ; Ä
auml = "a~H-13V2F35~H~FV-2H3~" ; ä

Egrave = "E~H-15V6F35~A~FV-6H3~" ; È
egrave = "e~H-13V2F35~A~FV-2H3~" ; è
Eacute = "E~H-15V6F35~B~FV-6H3~" ; É
eacute = "e~H-13V2F35~B~FV-2H3~" ; é
Ecirc = "E~H-15V6F35~C~FV-6H3~" ; Ê
ecirc = "e~H-13V2F35~C~FV-2H3~" ; ê
Euml = "E~H-15V6F35~H~FV-6H3~" ; Ë
euml = "e~H-13V2F35~H~FV-2H3~" ; ë

Igrave = "I~H-10V6F35~A~FV-6H3~" ; Ì
igrave = "i~H-10V2F35~A~FV-2H3~" ; ì
Iacute = "I~H-08V6F35~B~FV-6H3~" ; Í
iacute = "i~H-08V2F35~B~FV-2~" ; í
Icirc = "I~H-09V6F35~C~FV-6H3~" ; Î
icirc = "i~H-09V2F35~C~FV-2H3~" ; î
Iuml = "I~H-09V6F35~H~FV-6H3~" ; Ï
iuml = "i~H-09V2F35~H~FV-2H3~" ; ï

Ograve = "O~H-15V6F35~A~FV-6H3~" ; Ò
ograve = "o~H-13V2F35~A~FV-2H3~" ; ò
Oacute = "O~H-15V6F35~B~FV-6H3~" ; Ó
oacute = "o~H-13V2F35~B~FV-2H3~" ; ó
Ocirc = "O~H-16V6F35~C~FV-6H3~" ; Ô
ocirc = "o~H-14V2F35~C~FV-2H3~" ; ô
Otilde = "O~H-15V6F35~D~FV-6H3~" ; Õ
otilde = "o~H-13V2F35~D~FV-2H3~" ; õ
Ouml = "O~H-16V6F35~H~FV-6H3~" ; Ä
ouml = "o~H-14V2F35~H~FV-2H3~" ; ä

Ugrave = "U~H-15V6F35~A~FV-6H3~" ; Ù
ugrave = "u~H-13V2F35~A~FV-2H3~" ; ù
Uacute = "U~H-13V6F35~B~FV-6H3~" ; Ú
uacute = "u~H-13V2F35~B~FV-2H3~" ; ú
Ucirc = "U~H-15V6F35~C~FV-6H3~" ; Û
ucirc = "u~H-13V2F35~C~FV-2H3~" ; û
Uuml = "U~H-15V6F35~H~FV-6H3~" ; Ü
uuml = "u~H-13V2F35~H~FV-2H3~" ; ü

Cedil = "C~H-15F35~K~FH2~" ; Ç
cedil = "c~H-13F35~K~FH2~" ; ç

Ntilde = "N~H-15V6F35~D~FV-6H3~" ; Ñ
ntilde = "n~H-13V2F35~D~FV-2H3~" ; ñ

;################## subtitles

procedure subtitles(wks:graphic,plot:graphic,lstr:string,cstr:string, \
                    rstr:string,tres)
local txres, font_height, amres
begin
  if(tres) then
    txres = tres     ; Copy resources
  else
    txres = True
  end if
;
; Retrieve font height of left axis string and use to calculate size of
; subtitles.
;
  if(.not.isatt(txres,"txFontHeightF")) then
    getvalues plot
      "tiXAxisFontHeightF" : font_height
    end getvalues

    txres@txFontHeightF = font_height*0.4    ; tamao font
  end if

;
; Set some some annotation resources.
;
  amres                  = True
  if(.not.isatt(txres,"amOrthogonalPosF")) then
    amres@amOrthogonalPosF = -0.51   ; Top of plot plus a little extra
                                     ; to stay out of the tickmarks.
  else
    amres@amOrthogonalPosF = txres@amOrthogonalPosF
  end if

;
; Create three strings to put at the top, using a slightly
; smaller font height than the axis titles.
;
  if(lstr.ne."") then
    txidl = gsn_create_text(wks, lstr, txres)

    amres@amJust           = "BottomLeft"
    amres@amParallelPosF   = -0.5   ; Left-justified
    annoidl = gsn_add_annotation(plot, txidl, amres)
  end if

  if(cstr.ne."") then
    txidc = gsn_create_text(wks, cstr, txres)

    amres@amJust           = "BottomCenter"
    amres@amParallelPosF   = 0.0   ; Centered
    annoidc = gsn_add_annotation(plot, txidc, amres)

  end if

  if(rstr.ne."") then
    txidr = gsn_create_text(wks, rstr, txres)

    amres@amJust           = "BottomRight"
    amres@amParallelPosF   = 0.5   ; Right-justifed
    annoidr = gsn_add_annotation(plot, txidr, amres)
  end if
end

;################## function draw_outlines

undef("draw_outlines")
function draw_outlines(wks,map,fname)
local lnres, f, fname, segments, geometry, segsDims, geomDims, geom_segIndex, geom_numSegs, segs_xyzIndex, segs_numPnts, numFeatures
begin

  f = addfile(fname,"r")

  segments = f->segments
  geometry = f->geometry
  segsDims = dimsizes(segments)
  geomDims = dimsizes(geometry)

  geom_segIndex = f@geom_segIndex
  geom_numSegs  = f@geom_numSegs
  segs_xyzIndex = f@segs_xyzIndex
  segs_numPnts  = f@segs_numPnts
  numFeatures   = geomDims(0)

  lon1 = f->x
  lat1 = f->y

  lnres                  = True
  lnres@gsLineThicknessF = 1
  lnres@gsLineColor      = "black"

  do i=0,numFeatures-1
     startSegment = geometry(i, geom_segIndex)
     numSegments  = geometry(i, geom_numSegs)
     do seg=startSegment, startSegment+numSegments-1
        startPT = segments(seg, segs_xyzIndex)
        endPT   = startPT + segments(seg, segs_numPnts) - 1

        dumstr = unique_string("primitive")
        map@$dumstr$ = gsn_add_polyline(wks, map, lon1(startPT:endPT),                                          lat1(startPT:endPT), lnres)
     end do
  end do

  return(map)
end

;################## function create_map

undef("create_map")
function create_map(wks,lat,lon)
local gres, lnres, f, map, segments, geometry, segsDims, geomDims, geom_segIndex, geom_numSegs, segs_xyzIndex, segs_numPnts, numFeatures
begin

  minlat = min(lat)
  maxlat = max(lat)
  minlon = min(lon)-0.0001
  maxlon = max(lon)+0.0001

  f = addfile("{shape}","r")

  lon1 = f->x
  lat1 = f->y

  gres               = True
  gres@gsnDraw       = False
  gres@gsnFrame      = False
  gres@mpDataSetName         = "Earth..4"   ; This new database contains
  gres@mpDataBaseVersion     = "MediumRes"  ; resolution database
  gres@mpOutlineOn   = False
  gres@mpPerimOn     = True
  gres@mpOutlineDrawOrder = "PostDraw"
  gres@mpFillOn               = True
  gres@mpOceanFillColor       = -1
  gres@mpLandFillColor        = -1
  gres@mpInlandWaterFillColor = -1
  ;gres@mpFillAreaSpecifiers   = (/"Venezuela","Brazil", "Peru","Ecuador","Panama"/)
  ;gres@mpSpecifiedFillColors  = (/    0, 0, 0,  0, 0/)
  gres@mpFillDrawOrder        = "Draw"
  gres@pmTickMarkDisplayMode = "Always"
  gres@mpProjection  = "Mercator"
  gres@mpLimitMode   = "LatLon"
  gres@tmXBLabelFontHeightF        = 0.009
  gres@tmYLLabelFontHeightF        = 0.009

  gres@mpMinLatF     = minlat
  gres@mpMaxLatF     = maxlat
  gres@mpMinLonF     = minlon
  gres@mpMaxLonF     = maxlon

  map = gsn_csm_map(wks,gres)

  return(map)
end

;################## function shape mask

undef("shape_mask")
function shape_mask(lat,lon,idx)
begin
  MASK_INSIDE = False

  minlat = min(lat)
  maxlat = max(lat)
  minlon = min(lon)
  maxlon = max(lon)

  nlat            = {lat_size}
  nlon            = {lon_size}


  data = new((/nlat,nlon/),float)
  iter = 0
  invlat = nlat-1

  do ind_lon = 0, nlon - 1
    do ind_lat = 0,nlat - 1
      data(invlat-ind_lat,ind_lon) = idx(iter)
      iter=iter+1
    end do
  end do

  data@_FillValue = -9999

;---Create dummy 1D lat/lon arrays
  lat1d       = fspan(minlat,maxlat,nlat)
  lon1d       = fspan(minlon,maxlon,nlon)
  lat1d@units = "degrees_north"
  lon1d@units = "degrees_east"

;---Attach lat/lon coordinate array information.
  data!0      = "lat"
  data!1      = "lon"
  data&lat    = lat1d
  data&lon    = lon1d

  f = addfile("{shape}","r")

  mrb_lon = f->x
  mrb_lat = f->y
  nmrb    = dimsizes(mrb_lon)

  min_mrb_lat = min(mrb_lat)
  max_mrb_lat = max(mrb_lat)
  min_mrb_lon = min(mrb_lon)
  max_mrb_lon = max(mrb_lon)

  if(MASK_INSIDE) then
  ;---Start with data filled in.
    data_mask = data
  else
  ;---Start with data all missing
    data_mask = new(dimsizes(data),typeof(data),data@_FillValue)
    copy_VarCoords(data,data_mask)
  end if

  ilt_mn = ind(min_mrb_lat.gt.lat1d)
  ilt_mx = ind(max_mrb_lat.lt.lat1d)
  iln_mn = ind(min_mrb_lon.gt.lon1d)
  iln_mx = ind(max_mrb_lon.lt.lon1d)
  ilt1   = ilt_mn(dimsizes(ilt_mn)-1)    ; Start of lat box
  iln1   = iln_mn(dimsizes(iln_mn)-1)    ; Start of lon box
  ilt2   = ilt_mx(0)                     ; End of lat box
  iln2   = iln_mx(0)                     ; End of lon box

  if(MASK_INSIDE) then
  ;---Put missing values in the areas that we want masked.
    do ilt=ilt1,ilt2
      do iln=iln1,iln2
        if(gc_inout(lat1d(ilt),lon1d(iln),mrb_lat,mrb_lon)) then
          data_mask(ilt,iln) = data_mask@_FillValue
        end if
      end do
    end do
  else
  ;---Put data back in the areas that we don't want masked.
    do ilt=ilt1,ilt2
      do iln=iln1,iln2
        if(gc_inout(lat1d(ilt),lon1d(iln),mrb_lat,mrb_lon)) then
          data_mask(ilt,iln) = data(ilt,iln)
        end if
      end do
    end do
  end if

  return(data_mask)
end

;################## MAIN

begin
  USE_RASTER = False
  ENABLE_MASK = {enable_mask}

  wks_type = "png"
  ;wks_type@wkPaperSize = "A3"
  ;wks_type@wkWidthwkPaperWidthF = 1000
  ;wks_type@wkPaperHeightF = 800
  ;wks = gsn_open_wks(wks_type,"example")

  ;wks_type@wkPSResolution = 4500

  wks = gsn_open_wks(wks_type,"{save_map}")

  ;gsn_define_colormap(wks,"BlWhRe")
  gsn_define_colormap(wks,"{colormap}")
  gsn_reverse_colormap(wks)

  fname = "{ncl_data}"
  lines = asciiread(fname,-1,"string")

  delim = str_get_tab()
  lat = stringtofloat(str_get_field(lines(1:),1,delim))
  lon = stringtofloat(str_get_field(lines(1:),2,delim))
  idx = stringtofloat(str_get_field(lines(1:),3,delim))

  map = create_map(wks,lat,lon)

  res                             = True
  res@gsnDraw                     = False
  res@gsnFrame                    = False
  res@gsnSpreadColors             = True
  ;res@gsnSpreadColorStart         = 24
  ;res@gsnSpreadColorEnd           = -26

  if(USE_RASTER) then
   res@cnFillMode                 = "RasterFill"
   res@cnRasterSmoothingOn        = True
  else
    res@cnFillMode                = "AreaFill"
    res@cnSmoothingOn             = True
  end if

  ;colors bar
  res@pmLabelBarOrthogonalPosF    = 0.02
  res@pmLabelBarWidthF              = 0.05

  res@cnLineLabelPlacementMode    = "Constant"
  res@cnLineDashSegLenF           = 0.00003
  res@cnLevelSelectionMode        = "ExplicitLevels"
  res@cnLevels                    = {color_bar_levels}
  res@cnLevelSpacingF             = {color_bar_step}
  res@cnFillOn                    = True
  res@cnLinesOn                   = False
  res@cnLineLabelsOn              = False
  res@cnLevelFlags                = new(139,"string")
  res@cnLevelFlags(:)             = "NoLine"
  res@cnLevelFlags(0::20)         = "LineAndLabel"
  res@cnFillDrawOrder             = "PreDraw"

  res@lbBoxLinesOn                = False
  res@tiMainString                = {title}
  res@tiMainFontHeightF           = 0.022
  res@tiMainOffsetYF              = 0.03
  res@lbLabelAutoStride           = True
  res@lbPerimOn                   = False
  res@lbJustification             = "CenterCenter"
  res@lbOrientation               = "vertical"
  res@lbLabelFontHeightF          = 0.011
  res@lbTitleOn                   = {color_bar_title_on}
  res@lbTitlePosition             = "Left"
  res@lbTitleString               = "{below}                                              {normal}                                               {above}"
  res@lbTitleFontHeightF          = 0.015
  res@lbTitleDirection            = "Across"
  res@lbTitleAngleF               = 90
  res@lbLabelAutoStride           =   True
  ;res@cnLabelBarEndStyle          = "IncludeMinMaxLabels"


  if(ENABLE_MASK) then
    data_mask = shape_mask(lat, lon, idx)
    contour = gsn_csm_contour(wks,data_mask,res)
  else
    res@sfXArray                    = lon
    res@sfYArray                    = lat
    contour = gsn_csm_contour(wks,idx,res)
  end if

  overlay(map,contour)

  ;## subtitles
  txres             = True                         ; Text resources desired
  txres@txFontColor = "black"
  txres@txFontHeightF = 0.011
  subtitles(wks,contour,{name},{analysis},{units},txres)

  map = draw_outlines(wks, map, "{shape}")

  pres = True
  maximize_output(wks,pres)

end

    '''.format(shape=map_properties.shape,
               ncl_data=os.path.abspath(map_properties.base_path_file) + '.tsv',
               save_map=os.path.abspath(map_properties.base_path_file),
               title=map_properties.title,
               below=_("Below"),
               normal=_("Normal"),
               above=_("Above"),
               color_bar_title_on=map_properties.color_bar_title_on,
               color_bar_levels=map_properties.color_bar_levels,
               color_bar_step=map_properties.color_bar_step,
               colormap=map_properties.colormap,
               lat_size=map_properties.lat_size,
               lon_size=map_properties.lon_size,
               name='''"{0}"'''.format(map_properties.name),
               analysis=map_properties.analysis,
               units=map_properties.units,
               enable_mask=map_properties.shape_mask)


