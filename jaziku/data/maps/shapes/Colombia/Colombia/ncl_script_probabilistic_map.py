#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2014 IDEAM
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
from jaziku import env

def code(map_properties):

    map_properties_vars = {
        'ncarg_root': os.environ.get('NCARG_ROOT'),
        'jaziku_ncl_plugins': os.path.abspath(os.path.join(env.globals_vars.JAZIKU_DIR,'data','maps','ncl_plugins')),
        'shape': map_properties.shape,
        'interpolation_file': os.path.abspath(map_properties.base_path_file) + '.tsv',
        'stations_file': os.path.abspath(map_properties.base_path_file) + '_stations.tsv',
        'marks_stations': env.config_run.settings['marks_stations'],
        'label_marks_stations': _('Stations'),
        'save_map': os.path.abspath(map_properties.base_path_file),
        'title': map_properties.title,
        'below': _("Below"),
        'normal': _("Normal"),
        'above': _("Above"),
        'color_bar_title_on': map_properties.color_bar_title_on,
        'color_bar_levels': map_properties.color_bar_levels,
        'color_bar_step': map_properties.color_bar_step,
        'colormap': map_properties.colormap,
        'name': '''"{0}"'''.format(map_properties.name),
        'subtitle': map_properties.subtitle,
        'text_bottom_left': map_properties.text_bottom_left,
        'units': map_properties.units
    }

    return '''
load "{ncarg_root}/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "{ncarg_root}/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "{ncarg_root}/lib/ncarg/nclscripts/csm/contributed.ncl"

;load particular ncl scripts of Jaziku
load "{jaziku_ncl_plugins}/accent_table.ncl"

;*****************************************
;################## subtitles
;*****************************************

procedure subtitles(wks:graphic,plot:graphic,lstr:string,cstr:string, rstr:string,tres)
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

;*****************************************
;################## function draw_outlines
;*****************************************

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
  lnres@gsLineThicknessF = 0.3
  lnres@gsLineColor      = (/"(/0.00, 0.00, 0.00/)"/)

  do i=0,numFeatures-1
     startSegment = geometry(i, geom_segIndex)
     numSegments  = geometry(i, geom_numSegs)
     do seg=startSegment, startSegment+numSegments-1
        startPT = segments(seg, segs_xyzIndex)
        endPT   = startPT + segments(seg, segs_numPnts) - 1

        dumstr = unique_string("primitive")
        map@$dumstr$ = gsn_add_polyline(wks, map, lon1(startPT:endPT), lat1(startPT:endPT), lnres)
     end do
  end do

  return(map)
end

;*****************************************
;################## function create_map
;*****************************************

undef("create_map")
function create_map(wks,lat,lon)
local gres, lnres, f, map, segments, geometry, segsDims, geomDims, geom_segIndex, geom_numSegs, segs_xyzIndex, segs_numPnts, numFeatures
begin

  minlat = min(lat)
  maxlat = max(lat)
  minlon = min(lon)
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
  gres@mpOceanFillColor       = 0
  gres@mpLandFillColor        = -1
  gres@mpInlandWaterFillColor = 0
  gres@mpFillAreaSpecifiers   = (/"Venezuela","Brazil", "Peru","Ecuador","Panama"/)
  gres@mpSpecifiedFillColors  = (/    0, 0, 0,  0, 0/)
  gres@mpFillDrawOrder        = "Draw"
  gres@pmTickMarkDisplayMode = "Always"
  gres@mpProjection  = "Mercator"
  gres@mpLimitMode   = "LatLon"
  gres@tmXBLabelFontHeightF        = 0.011
  gres@tmYLLabelFontHeightF        = 0.011

  gres@mpMinLatF     = minlat
  gres@mpMaxLatF     = maxlat
  gres@mpMinLonF     = minlon
  gres@mpMaxLonF     = maxlon

  map = gsn_csm_map(wks,gres)

  return(map)
end

;*****************************************
;################## MAIN
;*****************************************

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
  gsn_define_colormap(wks,"{colormap}")
  gsn_reverse_colormap(wks)

  fname = "{interpolation_file}"
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
  res@pmLabelBarWidthF            = 0.05

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
  res@tiMainFontHeightF           = 0.023
  res@tiMainOffsetYF              = 0.03
  res@lbLabelAutoStride           = True
  res@lbPerimOn                   = False
  res@lbJustification             = "CenterCenter"
  res@lbOrientation               = "vertical"
  res@lbLabelFontHeightF          = 0.011
  res@lbTitleOn                   = {color_bar_title_on}
  res@lbTitlePosition             = "Left"
  res@lbTitleString               = "{below}                                {normal}                                 {above}"
  res@lbTitleFontHeightF          = 0.015
  res@lbTitleDirection            = "Across"
  res@lbTitleAngleF               = 90
  res@lbLabelAutoStride           =   True
  ;res@cnLabelBarEndStyle          = "IncludeMinMaxLabels"

  res@sfXArray                    = lon
  res@sfYArray                    = lat

  contour = gsn_csm_contour(wks,idx,res)
  overlay(map,contour)
  map = draw_outlines(wks, map, "{shape}")

  ;*****************************************
  ; plotting marks of stations

  if({marks_stations}) then
    fname = "{stations_file}"
    lines_stations = asciiread(fname,-1,"string")

    delim = str_get_tab()
    lat_of_stations = stringtofloat(str_get_field(lines_stations(1:),1,delim))
    lon_of_stations = stringtofloat(str_get_field(lines_stations(1:),2,delim))
    index_of_stations = stringtofloat(str_get_field(lines_stations(1:),3,delim))
    index_positions_of_stations = str_get_field(lines_stations(1:),4,delim)

    number_of_stations = dimsizes(index_of_stations)

    lat_of_stations@long_name = "latitude"
    lat_of_stations!0="lat"
    lat_of_stations&lat=lat_of_stations
    nlat_of_stations=dimsizes(lat_of_stations)

    lon_of_stations@long_name = "longitude"
    lon_of_stations!0="lon"
    lon_of_stations&lon=lon_of_stations
    nlon_of_stations=dimsizes(lon_of_stations)

    ;clean stations points with 'nan' values
    do i=0,number_of_stations-1
        if (index_positions_of_stations(i) .eq. "nan") then
            ;gsn_polymarker(wks,map,lon_of_stations(i),lat_of_stations(i),polyres)
            lat_of_stations(i) = -999
            lon_of_stations(i) = -999
        end if
    end do

    polyres               = True          ; poly marker mods desired
    polyres@gsMarkerIndex = 4            ; choose circle as polymarker
    polyres@gsMarkerSizeF = 0.0028          ; select size to avoid streaking
    polyres@gsMarkerColor = (/"(/0.00, 0.00, 0.00/)"/)   ; choose color
    polyres@gsMarkerThicknessF = 0.7
    dum1 = gsn_add_polymarker(wks,contour,lon_of_stations,lat_of_stations,polyres)  ; draw polymarkers

    ;*****************************************
    ; plotting legend of 'stations'

    ; Set up some legend resources.
    lgres                    = True
    lgres@lgAutoManage       = True
    lgres@lgItemType = "Markers"
    lgres@lgMarkerIndexes = 4            ; choose circle as polymarker
    lgres@lgMonoMarkerIndex = False
    lgres@lgMarkerSizeF = 0.003          ; select size to avoid streaking
    lgres@lgMarkerThicknessF = 0.8
    lgres@lgLabelFontHeightF = .015            ; set the legend label font thickness
    lgres@vpWidthF           = 0.075           ; width of legend (NDC)
    lgres@vpHeightF          = 0.018            ; height of legend (NDC)
    lgres@lgRightMarginF = 0.25
    lgres@lgLeftMarginF = 0.2
    lgres@lgTopMarginF = 0.02
    lgres@lgBottomMarginF = 0.02
    lgres@lgBoxMinorExtentF = 0.25
    lgres@lgMonoDashIndex    = False
    lgres@lgPerimThicknessF = 0.8            ; thicken the box perimeter
    lgres@lgLabelAutoStride = True
    lgres@lgPerimFill = "Solid"
    lgres@lgPerimFillColor = (/"(/1.00, 1.00, 1.00/)"/)
    labels = (/"{label_marks_stations}"/)

    ; Create the legend.
    lbid   = gsn_create_legend(wks,1,labels,lgres)         ; create legend

    ; Set up resources to attach legend to map.
    amres = True
    amres@amJust = "BottomRight"
    amres@amParallelPosF   =  0.5 	         ; positive move legend to the right
    amres@amOrthogonalPosF = 0.5                 ; positive move the legend down
    annoid1 = gsn_add_annotation(map,lbid,amres)   ; attach legend to plot

  end if
  ;*****************************************

  ;*****************************************
  ; plotting text BottomLeft
  txres                    = True
  txres@lgAutoManage       = True
  txres@txFontHeightF = 0.0085
  txt_bl = gsn_create_text(wks, {text_bottom_left}, txres)

  amres_bl = True
  amres_bl@amParallelPosF   = -0.49   ; This is the right edge of the plot.
  amres_bl@amOrthogonalPosF = 0.495    ; This is the bottom edge of the plot.
  amres_bl@amJust           = "BottomLeft"

  annoid1 = gsn_add_annotation(map, txt_bl, amres_bl)
  ;*****************************************

  ;## add subtitles
  txres             = True                         ; Text resources desired
  txres@txFontColor = (/"(/0.00, 0.00, 0.00/)"/)
  txres@txFontHeightF = 0.011
  subtitles(wks,contour,{name},{subtitle},{units},txres)

  pres = True
  maximize_output(wks,pres)

end

    '''.format(**map_properties_vars)


