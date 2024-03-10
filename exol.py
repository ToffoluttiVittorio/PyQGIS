import sys
print(sys.version)
# chargement des algorithmes de la boite à outils
import processing 
# chargement des méthodes spécifiques aux projets QGIS
from qgis.core import QgsProject

#Nettoyage des couches du projet
QgsProject.instance().removeAllMapLayers()

## arrondissements
uri = "D:/LZ/lyon/input/arrondissements.shp"
arrondissements = iface.addVectorLayer(uri,"arrondissements", "ogr")

## gares
uri = "D:/LZ/lyon/input/gares_sncf.shp"
gares = iface.addVectorLayer(uri,"gares", "ogr")
# reprojection de la couche en EPSG:2154
gares_reproject = processing.runAndLoadResults(
    "native:reprojectlayer", 
    {'INPUT':gares,
    'TARGET_CRS':QgsCoordinateReferenceSystem('EPSG:2154'),
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
project.mapLayersByName('Reprojeté')[0].setName("gares_L93")

## métros
uri = "D:/LZ/lyon/input/entrees_sorties_metro.shp"
metro = iface.addVectorLayer(uri,"entrees_sorties_metro", "ogr")

## piscines
uri = "D:/LZ/lyon/input/piscines.shp"
piscines = iface.addVectorLayer(uri,"piscines", "ogr")

## espaces_verts
uri = "D:/LZ/lyon/input/espaces_verts.shp"
espaces_verts = iface.addVectorLayer(uri,"espaces_verts", "ogr")

## Contrôle des projections
for layer in QgsProject.instance().mapLayers().values():
    crs = layer.crs().authid()
    print("{} : {}".format(layer.name(), crs))

# Extraction de la gare de Part-Dieu
#expression = "nom = 'Gare de Lyon Part-Dieu'"
#partdieu = processing.runAndLoadResults(
#    "native:extractbyexpression",
#    {'INPUT':gares_reproject, 
#     'EXPRESSION': expression,
#     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
     
# Création d'un tampon de 1000m
""" buffer_partdieu = processing.runAndLoadResults(
    "native:buffer", 
    {'INPUT':partdieu,
     'DISTANCE':1000, #Taille du tampon (en unités de la couche)
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# Intersection des stations de métros
metro_1000m = processing.runAndLoadResults(
    "native:intersection", 
    {'INPUT':metro,
    'OVERLAY':buffer_partdieu,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# Renommer la couche intersectée
## identifier la couche
project =  QgsProject.instance()
print(project.mapLayers())
for id, layer in project.mapLayers().items():
        print(layer.name())

## renommer
project.mapLayersByName('Intersection')[0].setName("metro_1000m")

# sauvegarder une couche 
## Sélectionner une couche par son nom (premier élément de la liste retourné)
layer = project.mapLayersByName('metro_1000m')[0]

# Chemin de sauvegarde via une chaîne de caractères
output_path="D:/LZ/lyon/output/metro1000m.gpkg"

## Appel de la méthode avec précision du fournisseur 'ogr' et du SRC cible (RGF93/L93)
QgsVectorLayerExporter.exportLayer(
                                layer = layer, 
                                uri = output_path, 
                                providerKey = 'ogr', 
                                destCRS = QgsCoordinateReferenceSystem('EPSG:2154')) """


# Création d'un tampon de 1000m
buffer_gares = processing.run(
    "native:buffer", 
    {'INPUT':gares_reproject,
     'DISTANCE':1000, #Taille du tampon (en unités de la couche)
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# Création d'un tampon de 300m
buffer_metro = processing.run(
    "native:buffer", 
    {'INPUT':metro,
     'DISTANCE':300, #Taille du tampon (en unités de la couche)
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# Création d'un tampon de 300m
buffer_espaces_verts = processing.run(
    "native:buffer", 
    {'INPUT':espaces_verts,
     'DISTANCE':200, #Taille du tampon (en unités de la couche)
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']


# Création d'un tampon de 500m
buffer_piscines = processing.run(
    "native:buffer", 
    {'INPUT':piscines,
     'DISTANCE':500, #Taille du tampon (en unités de la couche)
     'SEGMENTS':5,
     'END_CAP_STYLE':0,
     'JOIN_STYLE':0,
     'MITER_LIMIT':2,
     'DISSOLVE':False,
     'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

intersection_gares_metro = processing.run(
    "native:intersection", 
    {'INPUT':buffer_gares,
    'OVERLAY':buffer_metro,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

intersection_gares_metro_EV = processing.run(
    "native:intersection", 
    {'INPUT':intersection_gares_metro,
    'OVERLAY':buffer_espaces_verts,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

intersection_gares_metro_EV_piscines = processing.run(
    "native:intersection", 
    {'INPUT':intersection_gares_metro_EV,
    'OVERLAY':buffer_piscines,
    'INPUT_FIELDS':[],
    'OVERLAY_FIELDS':[],
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

#jointure par loc
jointurespatiale = processing.runAndLoadResults("native:joinattributesbylocation", {'INPUT':intersection_gares_metro_EV_piscines,'JOIN':'D:/LZ/lyon/input/arrondissements.shp','PREDICATE':[0],'JOIN_FIELDS':[],'METHOD':2,'DISCARD_NONMATCHING':False,'PREFIX':'','OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

# fusion par arrondissement
fusion_arrondissement = processing.runAndLoadResults("native:dissolve", {'INPUT':jointurespatiale,'FIELD':['insee'],'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
## renommer
project.mapLayersByName('Couche regroupée')[0].setName("fusion par arrondissement")

calculchamps = processing.runAndLoadResults("native:fieldcalculator", {'INPUT':fusion_arrondissement,'FIELD_NAME':'surface','FIELD_TYPE':0,'FIELD_LENGTH':0,'FIELD_PRECISION':0,'FORMULA':' round( $area,3) ','OUTPUT':'TEMPORARY_OUTPUT'})
## renommer
project.mapLayersByName('Calculé')[0].setName("Résultat")

layer = QgsProject.instance().mapLayersByName("Résultat")[0]
for entite in layer.getFeatures():
    print("surface de "+entite["libofficie"]+" : "+str(entite["surface"]))
	
# for id, layer in QgsProject.instance().mapLayers().items():
#     if id == calculchamps['OUTPUT']:
#         for entite in layer.getFeatures():
#             print("surface de "+entite["libofficie"]+" : "+entite["surface"]) 

# Extraction de la gare de Part-Dieu
expression = "nom = 'Gare de Lyon Part-Dieu'"
partdieu = processing.runAndLoadResults(
   "native:extractbyexpression",
   {'INPUT':gares_reproject, 
    'EXPRESSION': expression,
    'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']