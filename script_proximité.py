import sys
print(sys.version)
# chargement des algorithmes de la boite à outils
import processing 
# chargement des méthodes spécifiques aux projets QGIS
from qgis.core import QgsProject

#Nettoyage des couches du projet
QgsProject.instance().removeAllMapLayers()

## arrondissements
uri = "C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/arrondissements.shp"
arrondissements = iface.addVectorLayer(uri,"arrondissements", "ogr")

## gares
uri = "C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/gares_sncf.shp"
gares = iface.addVectorLayer(uri,"gares", "ogr")

# reprojection de la couche en EPSG:2154
gares_reproject = processing.runAndLoadResults(
    "native:reprojectlayer", 
    {'INPUT':gares,
    'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:2154'),
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
QgsProject.instance().mapLayersByName('Reprojeté')[0].setName("gares_cor")

## espaces_verts
uri = "C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/espaces_verts.shp"
espaces_verts = iface.addVectorLayer(uri,"espaces_verts", "ogr")


## piscines
uri = "C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/piscines.shp"
piscines = iface.addVectorLayer(uri,"piscines", "ogr")

## metros
uri = "C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/entrees_sorties_metro.shp"
metro = iface.addVectorLayer(uri,"entrees_sorties_metro", "ogr")


for layer in QgsProject.instance().mapLayers().values():
    crs = layer.crs().authid()
    print("{} : {}".format(layer.name(), crs))


# buffer_gares
buffer_gares = processing.run(
    "native:buffer", 
    {'INPUT':gares_reproject,
     'DISTANCE':1000, 
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# buffer_metro
buffer_metro = processing.run(
    "native:buffer", 
    {'INPUT':metro,
     'DISTANCE':300,
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# buffer ev
buffer_espaces_verts = processing.run(
    "native:buffer", 
    {'INPUT':espaces_verts,
     'DISTANCE':200, 
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']


# buffer piscines
buffer_piscines = processing.run(
    "native:buffer", 
    {'INPUT':piscines,
     'DISTANCE':500,
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

intersection_gm = processing.run(
    "native:intersection", 
    {'INPUT':buffer_gares,
    'OVERLAY':buffer_metro,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

intersection_gmev = processing.run(
    "native:intersection", 
    {'INPUT':intersection_gm,
    'OVERLAY':buffer_espaces_verts,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

intersection_gmevp = processing.run(
    "native:intersection", 
    {'INPUT':intersection_gmev,
    'OVERLAY':buffer_piscines,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']


join = processing.runAndLoadResults("native:joinattributesbylocation", {'INPUT':intersection_gmevp,'JOIN':'C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/arrondissements.shp','PREDICATE':[0],'JOIN_FIELDS':[],'METHOD':2,'DISCARD_NONMATCHING':False,'PREFIX':'','OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

fusion = processing.runAndLoadResults("native:dissolve", {'INPUT':join,'FIELD':['insee'],'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

champs = processing.runAndLoadResults("native:fieldcalculator", {'INPUT':fusion,'FIELD_NAME':'surface','FIELD_TYPE':0,'FIELD_LENGTH':0,'FIELD_PRECISION':0,'FORMULA':' round( $area,3) ','OUTPUT':'TEMPORARY_OUTPUT'})


