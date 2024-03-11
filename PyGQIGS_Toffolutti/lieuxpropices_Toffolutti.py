# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterDistance,
                       QgsCoordinateReferenceSystem)
from qgis import processing


class LieuxPropices(QgsProcessingAlgorithm):
    
    
    INPUT_GARES = 'INPUT_GARES'
    INPUT_METRO = 'INPUT_METRO'
    INPUT_ESPACES_VERTS = 'INPUT_ESPACES_VERTS'
    INPUT_PISCINES = 'INPUT_PISCINES'
    DISTANCE_GARES = 'DISTANCE_GARES'
    DISTANCE_METRO = 'DISTANCE_METRO'
    DISTANCE_ESPACES_VERTS = 'DISTANCE_ESPACES_VERTS'
    DISTANCE_PISCINES = 'DISTANCE_PISCINES'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LieuxPropices()

    def name(self):
        return 'LieuxPropices'

    def displayName(self):
        return self.tr('LieuxPropices')

    def group(self):
        return self.tr('Example scripts')

    def groupId(self):
        return 'examplescripts'

    def shortHelpString(self):
        return self.tr("LieuxPropices algorithm")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_GARES,
                self.tr('Gares Layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_METRO,
                self.tr('Metro Layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_ESPACES_VERTS,
                self.tr('Espaces Verts Layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT_PISCINES,
                self.tr('Piscines Layer')
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE_GARES,
                self.tr('Buffer Distance for Gares'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=1000
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE_METRO,
                self.tr('Buffer Distance for Metro'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=300
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE_ESPACES_VERTS,
                self.tr('Buffer Distance for Espaces Verts'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=200
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.DISTANCE_PISCINES,
                self.tr('Buffer Distance for Piscines'),
                type=QgsProcessingParameterNumber.Double,
                defaultValue=500
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Output Layer')
            )
        )

def processAlgorithm(self, parameters, context, model_feedback):

    input_gares = self.parameterAsVectorLayer(parameters, self.INPUT_GARES, context)
    input_metro = self.parameterAsVectorLayer(parameters, self.INPUT_METRO, context)
    input_espaces_verts = self.parameterAsVectorLayer(parameters, self.INPUT_ESPACES_VERTS, context)
    input_piscines = self.parameterAsVectorLayer(parameters, self.INPUT_PISCINES, context)


    distance_gares = self.parameterAsDouble(parameters, self.DISTANCE_GARES, context)
    distance_metro = self.parameterAsDouble(parameters, self.DISTANCE_METRO, context)
    distance_espaces_verts = self.parameterAsDouble(parameters, self.DISTANCE_ESPACES_VERTS, context)
    distance_piscines = self.parameterAsDouble(parameters, self.DISTANCE_PISCINES, context)
    
    outputFile = self.parameterAsOutputLayer(parameters,self.OUTPUT, context)


    buffer_gares = processing.run(
        "native:buffer", 
        {'INPUT': input_gares,
         'DISTANCE': distance_gares,
         'SEGMENTS': 5,
         'END_CAP_STYLE': 0,
         'JOIN_STYLE': 0,
         'MITER_LIMIT': 2,
         'DISSOLVE': False,
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"Buffer Gares: {buffer_gares}")


    buffer_metro = processing.run(
        "native:buffer", 
        {'INPUT': input_metro,
         'DISTANCE': distance_metro,
         'SEGMENTS': 5,
         'END_CAP_STYLE': 0,
         'JOIN_STYLE': 0,
         'MITER_LIMIT': 2,
         'DISSOLVE': False,
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"Buffer m: {buffer_metro}")


    buffer_espaces_verts = processing.run(
        "native:buffer", 
        {'INPUT': input_espaces_verts,
         'DISTANCE': distance_espaces_verts,
         'SEGMENTS': 5,
         'END_CAP_STYLE': 0,
         'JOIN_STYLE': 0,
         'MITER_LIMIT': 2,
         'DISSOLVE': False,
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"Buffer ev: {buffer_espaces_verts}")


    buffer_piscines = processing.run(
        "native:buffer", 
        {'INPUT': input_piscines,
         'DISTANCE': distance_piscines,
         'SEGMENTS': 5,
         'END_CAP_STYLE': 0,
         'JOIN_STYLE': 0,
         'MITER_LIMIT': 2,
         'DISSOLVE': False,
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"Buffer p: {buffer_piscines}")


    intersection_gares_metro = processing.run(
        "native:intersection", 
        {'INPUT': buffer_gares,
         'OVERLAY': buffer_metro,
         'INPUT_FIELDS': [],
         'OVERLAY_FIELDS': [],
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"inter gm: {intersection_gares_metro}")

    intersection_gares_metro_EV = processing.run(
        "native:intersection", 
        {'INPUT': intersection_gares_metro,
         'OVERLAY': buffer_espaces_verts,
         'INPUT_FIELDS': [],
         'OVERLAY_FIELDS': [],
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"inter gmev: {intersection_gares_metro_EV}")

    intersection_gares_metro_EV_piscines = processing.run(
        "native:intersection", 
        {'INPUT': intersection_gares_metro_EV,
         'OVERLAY': buffer_piscines,
         'INPUT_FIELDS': [],
         'OVERLAY_FIELDS': [],
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"inter gmevp: {intersection_gares_metro_EV_piscines}")


    join = processing.runAndLoadResults(
        "native:joinattributesbylocation", 
        {'INPUT': intersection_gares_metro_EV_piscines,
         'JOIN': 'C:/Users/vitto/OneDrive/Documents/ENSG/TSI/PyQGIS/PyQGIS/data_lyon/lyon/arrondissements.shp',
         'PREDICATE': [0],
         'JOIN_FIELDS': [],
         'METHOD': 2,
         'DISCARD_NONMATCHING': False,
         'PREFIX': '',
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']
    print(f"jointure spa: {join}")

    fusion = processing.runAndLoadResults(
        "native:dissolve", 
        {'INPUT': join,
         'FIELD': ['insee'],
         'OUTPUT': 'TEMPORARY_OUTPUT'})['OUTPUT']

    champs = processing.runAndLoadResults(
        "native:fieldcalculator", 
        {'INPUT': fusion,
         'FIELD_NAME': 'surface',
         'FIELD_TYPE': 0,
         'FIELD_LENGTH': 0,
         'FIELD_PRECISION': 0,
         'FORMULA': 'round($area, 3)',
         'OUTPUT':outputFile})['OUTPUT']
    
    # Ajouter la couche résultante au projet QGIS
    QgsProject.instance().addMapLayer(champs)

    # Retourner un dictionnaire avec la couche de sortie
    return {self.OUTPUT: champs}
    
    


    
