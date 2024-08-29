from django.shortcuts import render
import pandas as pd
import sys
import numpy as np
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd
#from geopandas import GeoDataFrame
#import fiona
#from shapely import wkt
#from shapely.wkt import loads
import folium
from folium.plugins import MousePosition, StripePattern, MeasureControl, LocateControl
from branca.element import *
#from folium import plugins
#from zipfile import ZipFile
import geotable
import branca
from datetime import date
from datetime import datetime
from cadastre.db_connect import cadastre_df

# Create your views here.
def index(request):
    # Loading the geo data
    global licence_type

    #creating a categorical legend
    legend_html = '''
    {% macro html(this, kwargs) %}
    <style>
    #mydiv {
      position: absolute; 
        top: 250px;
        left: 50px;
        width: 320px;
        height: 170px; 
        z-index:9998;
        font-size:14px;
        background-color: #ffffff;
        opacity: 1;
        font-family: monospace;
    }
    
    /* Responsive layout - when the screen is less than 300px wide, don't show the legend */
    @media only screen and (max-width: 500px) {
      #mydiv {
        display: none;
      }
    }
    </style>
    
    <div id="mydiv">
        <p>&emsp;<strong>Active</strong></p>
        <p><a style="color:#336699;font-size:20px;margin-left:20px;"><i class="fa fa-square" aria-hidden="true"></i></a>&emsp;Precious Metals</p>
        <p><a style="color:#03cafc;font-size:20px;margin-left:20px;"><i class="fa fa-square" aria-hidden="true"></i></a>&emsp;Base Metals</p>
        <p><a style="color:#cc9900;font-size:20px;margin-left:20px;"><i class="fa fa-square" aria-hidden="true"></i></a>&emsp;Special Grant (more than 25 ha)</p>
        <p>&emsp;<strong>Note: This legend is draggable.</strong></p>
    </div>
    
    <script>
    //Make the DIV element draggagle:
    dragElement(document.getElementById("mydiv"));
    
    function dragElement(elmnt) {
      var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
      if (document.getElementById(elmnt.id )) {
        /* if present, the header is where you move the DIV from:*/
        document.getElementById(elmnt.id ).onmousedown = dragMouseDown;
      } else {
        /* otherwise, move the DIV from anywhere inside the DIV:*/
        elmnt.onmousedown = dragMouseDown;
      }
    
      function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
      }
    
      function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
      }
    
      function closeDragElement() {
        /* stop moving when mouse button is released:*/
        document.onmouseup = null;
        document.onmousemove = null;
      }
    }
    </script>


<!--------------------------------------------------------------------------------------------------------------------->
<style>   
        #dropbtn {
          background-color: #04AA6D;
          color: white;
          padding: 10px;
          font-size: 16px;
          border: none;
        }
        
        #dropdown {
          position: absolute;
          display: inline-block;
        }
        
        #dropdown-content {
          display: none;
          position: absolute;
          background-color: #f1f1f1;
          min-width: 160px;
          box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
          z-index: 1;
        }
        
        #dropdown-content a {
          color: black;
          padding: 12px 16px;
          text-decoration: none;
          display: block;
        }
        
        #dropdown-content a:hover {background-color: #04AA6D; color: white}
        
        #dropdown:hover #dropdown-content {display: block;}
        
        #dropdown:hover #dropbtn {background-color: #3e8e41;}
        
        #search-container button {
          float: center;
          padding: 6px 10px;
          margin-top: 8px;
          margin-right: 16px;
          background: #ddd;
          font-size: 17px;
          border: none;
          cursor: pointer;
        }
        
        #search-container button:hover {
          background: #ccc;
        }
        
        #sticky {
          position: fixed;
          top: 0
          width: 100%;
        }
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
        </style> 
                
        <div id = "myMenu" style="
        position: fixed; 
        top: 10px;
        left: 50px;
        width: auto;
        height: auto; 
        z-index:9998;
        font-size:14px;
        background-color: #ffffff;
        opacity: 1;
        font-family: monospace;
        ">
            <div id="dropdown">
              <button id="dropbtn">☰</button>
              <div id="dropdown-content">
                <a data-dismiss = "modal" data-toggle="modal" data-target="#aboutModal" data-backdrop="true" href="#">About</a>
                <a data-toggle="modal" data-target="#disclaimerModal" data-backdrop="true" href="#">Disclaimer</a>
                <a data-toggle="modal" data-target="#searchModal" data-backdrop="true" href="#">Search</a>
              </div>
            </div>
        </div>
        
    <!-- About Modal -->      
      <div class="modal fade" id="aboutModal" role="dialog" data-dismiss="modal">        
        <div class="modal-dialog", style = "top: 100px">        
          <!-- Modal content-->
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal">&times;</button>
              <h4 class="modal-title"><strong>Retias Consulting - Mining Cadastre Solution</strong></h4>
            </div>
            <div class="modal-body">
              <p><h7>Retias Consulting provides data science solutions which solves problems for both private and government institutions.</h7></p>
              <p><h7>This platform provides a geospatial solution which is intended to provide transparency in the accounting for mining claims as well as ease
              with tracking of active, expired as well as transferred mining claims.</h7></p>
              <p><h7>Contact Information:</h7><br>
              <h7><i class="fa fa-paper-plane-o" style = "color:#04AA6D"></i> <a href="https://www.retiasconsulting.com/en/contact/" target="_blank"><nobr>info@retiasconsulting.com</nobr></a></h7><br>
              <h7><i class="fa fa-globe" style = "color:#04AA6D"></i> <a href="https://www.retiasconsulting.com/en" target="_blank"><nobr>www.retiasconsulting.com</nobr></a></h7>              
            </div>
            <div class="modal-footer">
                <p><h7>&copy<script>document.write( new Date().getFullYear() );</script> | Retias Consulting | All Rights Reserved | v 0.1</h7></p>
            </div>
          </div>          
        </div>
      </div>
      
    <!-- Disclaimer Modal  -->
      <div class="modal fade" id="disclaimerModal" role="dialog">
        <div class="modal-dialog", style = "top: 100px">        
          <!-- Modal content-->
          <div class="modal-content">
            <div class="modal-header">
              <button type="button" class="close" data-dismiss="modal">&times;</button>
              <h4 class="modal-title"><strong>Disclaimer</strong></h4>
            </div>
            <div class="modal-body">
              <p>Whilst we try to ensure accuracy and completeness of the information presented in this tool, we cannot guarantee that it will be completely free from errors.</p>
              <p>The companies providing the geospatial information of their mining claims should ensure that the information is accurate and acceptable to ensure reliableness of the tool. 
                 Any discrepancies or errors should be immediately reported to Retias Consulting using the provided contact details.</p>
              <p><strong>This tool is not compatible with mobile device browsers. For optimal user experience, use a PC browser.</strong></p>
              <p>Retias Consulting owns the intellectual property rights to this tool. These intellectual property rights are reserved.</p>
            </div>
          </div>          
        </div>
      </div>
      
    <!-- Search Modal  -->
      <div class="modal fade" id="searchModal" role="dialog" data-dismiss="modal">
        <div class="modal-dialog", style = "top: 100px">        
          <!-- Modal content-->
          <div class="modal-content">
            <div class="modal-body">
              <button type="button" class="close" data-dismiss="modal">&times;</button>
              <div class="search-container">
                <form  action="#">
                  <input type="text" placeholder="Search.." name="search" style = "width:80%">
                  <button type="submit"><i class="fa fa-search"></i></button>
                </form>
              </div>
            </div>
          </div>          
        </div>
      </div>
      
      <script>
        window.onscroll = function() {myFunction()};
    
        var header = document.getElementById("myMenu");
        var sticky = header.offsetTop;
    
        function myFunction() {
          if (window.scrollY > sticky) {
            header.classList.add("sticky");
          } else {
            header.classList.remove("sticky");
          }
        }
        </script>   

    {% endmacro %}
    '''
    legend = branca.element.MacroElement()
    legend._template = branca.element.Template(legend_html)


    ##rendering the map in folium to plot the polygons
    f = folium.Figure(width='100%', height='100%')
    map_cad = folium.Map(location=[-18.88, 29.69],tiles = "Stamen Terrain", zoom_start = 12, control_scale = True).add_to(f)

    ##plugins
    mouse_coord = MousePosition(
        position="topright",
        separator=" | ",
        lng_first=True,
        prefix="Coordinates:"
    ).add_to(map_cad)
    LocateControl(
        position="topright"
    ).add_to(map_cad)

    geom = gpd.GeoDataFrame(cadastre_df(), crs='epsg:4326')

    for j in range(0, len(geom)):
        if  int(geom['Area'][j])<=25 and (geom['Mineral'][j]=='Gold Reef'):
            licence_type = 'Precious Metals'
            block_style = lambda x:{'fillColor': '#336699', 'fillOpacity': 0.6, 'color': '#101010', 'opacity': 0.1}
        elif int(geom['Area'][j])<=25 and (geom['Mineral'][j]!='Gold Reef'):
            licence_type = 'Base Metals'
            block_style = lambda x:{'fillColor': '#03cafc', 'fillOpacity': 0.6, 'color': '#101010', 'opacity': 0.1}
        elif int(geom['Area'][j]) > 25:
            licence_type = 'Special Grant'
            block_style = lambda x:{'fillColor': '#cc9900', 'fillOpacity': 0.6, 'color': '#101010','opacity':0.1}

        #Expiring Claims
        due_inspection = (datetime.strptime(geom['Ins Date'][j],'%Y/%m/%d').date()-datetime.now().date()).days
        if due_inspection in range(0,60):
            block_style = lambda x: {'fillPattern': StripePattern(angle=0.5, color='#cc0000', weight = 6, opacity =0.1),'fillColor': '#cc0000', 'fillOpacity': 0.7, 'color': '#cc0000', 'opacity': 0.2}



        ##adding hover function
        highlight_block = lambda x: {'fillColor': '#000000','color':'#000000','fillOpacity': 0.50,'weight': 0.3}

        tooltip1 = '<i>' + licence_type + '</i> ' + '&emsp;' + '<strong>' + ('<a style="color:#cc0000";>Due for Inspection</a>' if (due_inspection in range(0,60)) else '<a style="color:#39ff14";>Active</a>') + '</strong>' + '<br>' +'<strong>' + str(geom['Group Name'][j]) + '</strong>' + '<br><br>' + '<i>Block Name:</i> ' + '<strong>' + str(
            geom['Claim Name'][j]) + '</strong>' + '<br>' + '<i>Registration Number:</i> ' + '<strong>'+  str(geom['Reg Number'][j]) + '</strong>' + '<br>' + '<i>Registration Date:</i> <strong>'+  str(geom['Reg Date'][j])  + '</strong><br>' + '<i>Inspection Due:</i> <strong>' +  str(geom['Ins Date'][j]) + '</strong><br>'
        tooltip2 = '<i>Commodities:</i> <strong>' +  str(geom['Mineral'][j]) +'</strong>' + '<br>' + '<i>Area:</i> <strong>' + str(format(float(geom['Area'][j]),".2f")) +' ha</strong>' + '<br>' + '<i>Coordinates:</i> ' + '<strong>' + str(format(eval(geom['Centre Points'][j])[0][0],".4f")) + " | " + str(format(eval(geom['Centre Points'][j])[0][1],".4f")) + '</strong>'
        folium.GeoJson(data=geom.geometry.iloc[j], name='Blocks', tooltip = tooltip1 + tooltip2 , style_function = block_style, highlight_function = highlight_block, control=False).add_to(map_cad)


    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Terrain',
        overlay=False,
        control=True
    ).add_to(map_cad)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Maps',
        overlay=False,
        control=True
    ).add_to(map_cad)
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(map_cad)

    MeasureControl(position='topright', primary_length_unit='kilometers', secondary_length_unit='miles',
                   primary_area_unit='sqmeters', secondary_area_unit='hectares',).add_to(map_cad)

    folium.LayerControl().add_to(map_cad)
    map_cad.get_root().add_child(legend)


    m = map_cad._repr_html_()
    context = {
        'm': m,
    }
    return render(request, 'index.html', context)
