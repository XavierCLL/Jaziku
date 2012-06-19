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

def colombia(shape_path_in, shape_in, base_path_file):
    return '''

load "/usr/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "/usr/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "/usr/lib/ncarg/nclscripts/csm/contributed.ncl"
load "{shape_path}/gsn_draw_coordinates.ncl"


;tabla de acentos
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




undef("draw_outlines")
function draw_outlines(wks,map,fname)
local lnres, f, fname, segments, geometry, segsDims, geomDims, \
geom_segIndex, geom_numSegs, segs_xyzIndex, segs_numPnts, numFeatures
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
  lnres@gsLineThicknessF = 0.8
  ;lnres@gsLineColor      = "black"

  do i=0,numFeatures-1
     startSegment = geometry(i, geom_segIndex)
     numSegments  = geometry(i, geom_numSegs)
     do seg=startSegment, startSegment+numSegments-1
        startPT = segments(seg, segs_xyzIndex)
        endPT   = startPT + segments(seg, segs_numPnts) - 1

        dumstr = unique_string("primitive")
        map@$dumstr$ = gsn_add_polyline(wks, map, lon1(startPT:endPT),  \
                                        lat1(startPT:endPT), lnres)
     end do
  end do

  return(map)
end

undef("create_map")
function create_map(wks,lat,lon)
local gres, lnres, f, map, segments, geometry, segsDims, geomDims, \
geom_segIndex, geom_numSegs, segs_xyzIndex, segs_numPnts, numFeatures
begin

  minlat = min(lat)-2
  maxlat = max(lat)+4
  minlon = min(lon)-3
  maxlon = max(lon)+1

  f = addfile("{shape}","r")

  lon1 = f->x
  lat1 = f->y

  gres               = True
  gres@gsnDraw       = False
  gres@gsnFrame      = False
  gres@mpOutlineOn   = False
  gres@mpPerimOn     = True
  gres@mpOutlineDrawOrder = "PostDraw"
  gres@mpFillOn               = True
  gres@mpOceanFillColor       = 0
  gres@mpLandFillColor        = -1
  gres@mpInlandWaterFillColor = 0
  gres@mpFillAreaSpecifiers   = (/"Venezuela","Brazil", "Peru","Ecuador","Panama"/)
  gres@mpSpecifiedFillColors  = (/    0, 0, 0,  0, 0/)
  gres@mpFillDrawOrder        = "Draw"
  gres@pmTickMarkDisplayMode = "Always"
  gres@mpProjection  = "Mercator"
  gres@mpLimitMode   = "LatLon"

  gres@mpMinLatF     = min((/min(lat1),minlat/))
  gres@mpMaxLatF     = max((/max(lat1),maxlat/))
  gres@mpMinLonF     = min((/min(lon1),minlon/))
  gres@mpMaxLonF     = max((/max(lon1),maxlon/))

  map = gsn_csm_map(wks,gres)

  return(map)
end

begin
  USE_RASTER = False

  wks_type = "png"
  ;wks_type@wkPaperSize = "A3"
  ;wks_type@wkWidthwkPaperWidthF = 1000
  ;wks_type@wkPaperHeightF = 800
  ;wks = gsn_open_wks(wks_type,"example")

  ;wks_type@wkPSResolution = 4500

  wks = gsn_open_wks(wks_type,"{save_map}")

  ;gsn_define_colormap(wks,"BlWhRe")
  gsn_define_colormap(wks,"BlGrYeOrReVi200")
  ;gsn_reverse_colormap(wks)

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

  res@pmLabelBarOrthogonalPosF    = 0.03
  res@pmLabelBarWidthF              = 0.07

  res@cnLineLabelPlacementMode    = "Constant"
  res@cnLineDashSegLenF           = 0.00003
  res@cnLevelSelectionMode        = "ManualLevels"
  ;res@cnMinLevelValF              = -80
  ;res@cnMaxLevelValF              = 80
  res@cnLevelSpacingF             = 4
  res@cnFillOn                    = True
  res@cnLinesOn                   = False
  res@cnLineLabelsOn              = False
  res@cnLevelFlags          = new(139,"string")
  res@cnLevelFlags(:)          = "NoLine"
  res@cnLevelFlags(0::20)         = "LineAndLabel"
  res@cnFillDrawOrder             = "PreDraw"

  res@lbBoxLinesOn                = False
  res@tiMainString                = "Escenario de afectaci"+oacute+"n de la variable SST~C~bajo condiciones el ni"+ntilde+"o a rez 0 en el JJA"
  res@tiMainFontHeightF           = 0.02
  res@lbLabelAutoStride           = True
  res@lbPerimOn                   = False
  res@lbJustification             = "CenterCenter"
  res@lbOrientation               = "vertical"
  res@lbLabelFontHeightF          = 0.011
  res@lbTitleOn                   = True
  res@lbTitlePosition             = "Left"
  res@lbTitleString               = "Probabilidad"
  res@lbTitleFontHeightF          = 0.012
  res@tmXBLabelFontHeightF        = 0.005
  res@tmYLLabelFontHeightF        = 0.005

  res@sfXArray                    = lon
  res@sfYArray                    = lat

  contour = gsn_csm_contour(wks,idx,res)
  overlay(map,contour)

  map = draw_outlines(wks, map, "{shape}")

  pres = True
  maximize_output(wks,pres)

end
    '''.format(shape_path=shape_path_in,
               shape=shape_in,
               ncl_data=os.path.abspath(base_path_file) + '.tsv',
               save_map=os.path.abspath(base_path_file))


def make_ncl_file(grid, base_path_file, shape_path):
    try:
        shape_in = os.path.join(shape_path, "Colombia", "Colombia.shp")

        ncl_file_raw = colombia(shape_path, shape_in, base_path_file)

        ncl_file = os.path.join(os.path.abspath(base_path_file) + ".ncl")

        #print ncl_file_raw
        open_ncl_file = open(ncl_file, 'wb')
        open_ncl_file.write(ncl_file_raw)
        open_ncl_file.close()

        return ncl_file
    except Exception, e:
        print e
