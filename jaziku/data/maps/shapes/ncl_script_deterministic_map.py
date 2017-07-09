#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2017 Xavier Corredor Ll. - IDEAM
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


# this ncl code for generic regions

def code(map_properties):
    #  if particular_properties_deterministic_map not defined in {region}.py, these are the default values:
    if map_properties.particular_properties_deterministic_map == {}:
        map_properties.particular_properties_deterministic_map = {"tiMainFontHeightF": 0.0185}  # main font height

    map_properties_vars = {
        'ncarg_root': os.environ.get('NCARG_ROOT'),
        'jaziku_ncl_plugins': os.path.abspath(os.path.join(env.globals_vars.JAZIKU_DIR, 'data', 'maps', 'ncl_plugins')),
        'shape': map_properties.shape,
        'stations_file': os.path.abspath(map_properties.base_path_file) + '_stations.tsv',
        'label_marks_stations': _('Stations'),
        'save_map': os.path.abspath(map_properties.base_path_file),
        'title': map_properties.title,
        'tiMainFontHeightF': map_properties.particular_properties_deterministic_map["tiMainFontHeightF"],
        'colormap': map_properties.colormap,
        'minlat': map_properties.minlat,
        'maxlat': map_properties.maxlat,
        'minlon': map_properties.minlon,
        'maxlon': map_properties.maxlon,
        'thresholds': map_properties.thresholds,
        'legend_units': env.var_D.UNITS,
        'mode_calculation_series': env.config_run.get_MODE_CALCULATION_SERIES_i18n("D"),
        'analysis_interval': env.config_run.get_ANALYSIS_INTERVAL_i18n(),
        'name': '''"{0}"'''.format(map_properties.name),
        'subtitle': map_properties.subtitle,
        'text_bottom_left': map_properties.text_bottom_left,
        'units': _("Deterministic")
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
  lnres@gsLineThicknessF = 1
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
function create_map(wks,minlat,maxlat,minlon,maxlon)
local gres, lnres, f, map, segments, geometry, segsDims, geomDims, geom_segIndex, geom_numSegs, segs_xyzIndex, segs_numPnts, numFeatures
begin

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
  gres@tmXBLabelFontHeightF        = 0.011
  gres@tmYLLabelFontHeightF        = 0.011

  gres@tiMainString                = {title}
  gres@tiMainFont                  = "helvetica"
  ;gres@gsnStringFont              = "helvetica-bold"
  gres@tiMainFontHeightF           = {tiMainFontHeightF}
  gres@tiMainOffsetYF              = 0.03

  gres@mpMinLatF     = minlat
  gres@mpMaxLatF     = maxlat
  gres@mpMinLonF     = minlon
  gres@mpMaxLonF     = maxlon

  map = gsn_csm_map(wks,gres)

  return(map)
end

;*****************************************
;################## function get_color
;*****************************************
; get code color from Colors_7_categories.rgb

undef("get_color")
function get_color(color)
begin
  if (color .eq. "strong below") then
    return(2)
  end if
  if (color .eq. "moderate below") then
    return(3)
  end if
  if (color .eq. "weak below") then
    return(4)
  end if
  if (color .eq. "normal") then
    return(5)
  end if
  if (color .eq. "weak above") then
    return(6)
  end if
  if (color .eq. "moderate above") then
    return(7)
  end if
  if (color .eq. "strong above") then
    return(8)
  end if
  return(1) ; else ('nan' value for example) return black
end


;*****************************************
;################## MAIN
;*****************************************

begin

  wks_type = "png"
  wks = gsn_open_wks(wks_type,"{save_map}")
  ;drawNDCGrid(wks)

  ;gsn_define_colormap(wks,"BlWhRe")
  gsn_define_colormap(wks,"{colormap}")
  ;gsn_reverse_colormap(wks)

  minlat = {minlat}
  maxlat = {maxlat}
  minlon = {minlon}
  maxlon = {maxlon}

  map = create_map(wks,minlat,maxlat,minlon,maxlon)

  map = draw_outlines(wks, map, "{shape}")

  ;*****************************************
  ; plotting marks of stations

  num_thresholds = 7

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

  polyres               = True          ; poly marker mods desired
  ;polyres@gsMarkerIndex = 16            ; choose circle as polymarker
  polyres@gsMarkerSizeF = 0.009          ; select size to avoid streaking
  polyres@gsMarkerThicknessF = 1

  are_there_nan = False

  do i=0,number_of_stations-1
     if (index_positions_of_stations(i) .eq. "nan") then
        polyres@gsMarkerIndex = 4            ; choose circle as polymarker
        are_there_nan = True
     else
        polyres@gsMarkerIndex = 16            ; choose circle as polymarker
     end if

     polyres@gsMarkerColor = get_color(index_positions_of_stations(i))  ; choose color
     gsn_polymarker(wks,map,lon_of_stations(i),lat_of_stations(i),polyres)
  end do

  ;*****************************************
  ; plotting legend of 'stations'

  ; Set up some legend resources.
  lgres                    = True
  lgres@lgAutoManage       = True
  lgres@lgItemType = "Markers"
  lgres@lgMarkerIndexes = 16            ; choose circle as polymarker
  lgres@lgMonoMarkerIndex = False
  lgres@lgMarkerSizeF = 0.008          ; select size to avoid streaking
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

  ;*****************************************
  ; plotting legend of thresholds

  thresholds = (/{thresholds}/)
  legend_labels = new(dimsizes(thresholds)+1,string)
  nlegend_labels = dimsizes(legend_labels)

  do i = 0, nlegend_labels-1
    if (i.eq.0) then
      legend_labels(i) = "<"+thresholds(i)
    end if
    if (i.eq.nlegend_labels-1) then
      legend_labels(i) = ">"+thresholds(i-1)
    end if
    if (i.gt.0.and.i.lt.nlegend_labels-1) then
      legend_labels(i) = thresholds(i-1) + " to " + thresholds(i)
    end if
  end do

  ;legend_labels = (/"<11%","22% to 33%","33% to 44%","66% to 77%","77% to 88%","88% to 99%",">90%"/)
  ; invert order
  legend_labels = legend_labels(::-1)

  ;*****
  ; Calculate X-axi legend location on NDC
  relation = ({maxlat}-{minlat})/({maxlon}-{minlon})

  xleg = 0.5 + (0.1)*3/relation
  if (xleg .gt. 0.8 ) then
    xleg = 0.8
  end if
  xleg = xleg + 0.015

  xtxt = xleg + 0.015

  ;*****
  ; title of legend

  txres               = True
  txres@txFontHeightF = 0.012
  ;txres@txFont = "helvetica-bold"
  txres@txJust = "CenterLeft"

  title_legend = (/"{legend_units}"/)
  gsn_text_ndc(wks,title_legend,xtxt-0.02,0.605,txres)

  txres@txFontHeightF = 0.0098

  title_legend = (/"{mode_calculation_series} ({analysis_interval})"/)
  gsn_text_ndc(wks,title_legend,xtxt-0.02,0.589,txres)

  ;*****
  ; legend

  delete(txres)
  txres               = True
  txres@txFontHeightF = 0.011
  ;txres@txFont = "helvetica"
  txres@txJust = "CenterLeft"

  yleg = new(num_thresholds+1,float)
  yleg(0) = 0.567
  do i = 1, num_thresholds
    yleg(i) = yleg(i-1) - 0.022
  end do

  ytxt = yleg

  ;colors = (/"#DD4620", "#DD8620","#DDC620", "#62AD29", "#60C7F1", "#6087F1", "#6047F1"/)
  colors =  (/"strong below","moderate below","weak below","normal","weak above","moderate above","strong above"/)
  ; invert order
  legend_colors = colors(::-1)

  gsres               = True
  gsres@gsMarkerIndex = 16
  gsres@gsMarkerThicknessF = 1
  gsres@gsMarkerSizeF = 0.009

  do i = 0, num_thresholds
    if (i.ne.num_thresholds) then
      gsres@gsMarkerColor = get_color(legend_colors(i))
      gsn_polymarker_ndc(wks,xleg,yleg(i),gsres)
      gsn_text_ndc(wks,legend_labels(i),xtxt,ytxt(i),txres)
    else
      ;this is for 'nan' legend
      if are_there_nan then
        gsres@gsMarkerIndex = 4
        gsres@gsMarkerColor = 1
        gsn_polymarker_ndc(wks,xleg,yleg(i),gsres)
        gsn_text_ndc(wks,"nan",xtxt,ytxt(i),txres)
      end if
    end if
  end do
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
  subtitles(wks,map,{name},{subtitle},"{units}",txres)

  pres = True
  maximize_output(wks,pres)

end

    '''.format(**map_properties_vars)
