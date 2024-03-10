from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeature,
                       QgsGeometry,
                       QgsPointXY,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterFeatureSink,
                       QgsField, QgsFields, QgsWkbTypes)
from qgis.PyQt.QtCore import QVariant
import csv
import requests
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsFeatureSink
from qgis.core import QgsVectorFileWriter

class GeocodeCSVAlgorithm(QgsProcessingAlgorithm):
    INPUT_CSV = 'INPUT_CSV'
    OUTPUT = 'OUTPUT'
    OUTPUT_GPKG = 'OUTPUT_GPKG'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return GeocodeCSVAlgorithm()

    def name(self):
        return 'geocodecsv'

    def displayName(self):
        return self.tr('Geocode CSV and Add API Data')

    def group(self):
        return self.tr('Example scripts')

    def groupId(self):
        return 'examplescripts'

    def shortHelpString(self):
        return self.tr("This algorithm geocodes addresses from a specified CSV file and adds additional information from the API.")

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_CSV,
                self.tr('Input CSV file'),
                behavior=QgsProcessingParameterFile.File,
                fileFilter='CSV files (*.csv)'
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer with API data')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterFile(
                self.OUTPUT_GPKG,
                self.tr('Output GeoPackage'),
                behavior=QgsProcessingParameterFile.File,
                fileFilter='GeoPackage files (*.gpkg)'
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        input_csv = self.parameterAsString(parameters, self.INPUT_CSV, context)

        fields = QgsFields()
        fields.append(QgsField("adresse", QVariant.String))
        fields.append(QgsField("ID", QVariant.String))
        fields.append(QgsField("Longitude", QVariant.Double))
        fields.append(QgsField("Latitude", QVariant.Double))
        fields.append(QgsField("label", QVariant.String))
        fields.append(QgsField("score", QVariant.Double))
        fields.append(QgsField("housenumber", QVariant.String))
        fields.append(QgsField("postcode", QVariant.String))
        fields.append(QgsField("citycode", QVariant.String))
        fields.append(QgsField("city", QVariant.String))
        fields.append(QgsField("context", QVariant.String))
        fields.append(QgsField("type", QVariant.String))
        fields.append(QgsField("street", QVariant.String))

        source = self.parameterAsSource(parameters, self.INPUT_CSV, context)
        
        output_gpkg = self.parameterAsString(parameters, self.OUTPUT_GPKG, context)

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            fields,
            QgsWkbTypes.Point,
            QgsCoordinateReferenceSystem('EPSG:2154')
        )
        
        gpkg_writer = QgsVectorFileWriter(output_gpkg, 'UTF-8', fields, QgsWkbTypes.Point, QgsCoordinateReferenceSystem('EPSG:2154'), 'GPKG')
        if gpkg_writer.hasError() != QgsVectorFileWriter.NoError:
            raise QgsProcessingException(f"Erreur lors de la création du GeoPackage : {gpkg_writer.errorMessage()}")

        with open(input_csv, mode='r', encoding='utf-8-sig') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip the header
            for row in csvreader:
                adresse, id = row
                url = f"https://api-adresse.data.gouv.fr/search/?q={adresse}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    features = data.get('features')
                    if features:
                        for feature in features:
                            geom = feature['geometry']
                            props = feature['properties']
                            coords = geom['coordinates']
                            qgs_feature = QgsFeature(fields)
                            qgs_feature.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(coords[0], coords[1])))
                            # Set feature attributes based on the API response
                            qgs_feature['adresse'] = adresse
                            qgs_feature['ID'] = id
                            qgs_feature['Longitude'] = coords[0]
                            qgs_feature['Latitude'] = coords[1]
                            for field in fields.names():
                                if field in props:
                                    qgs_feature[field] = props[field]
                            sink.addFeature(qgs_feature, QgsFeatureSink.FastInsert)

                            # Ajouter la même entité au GeoPackage
                            gpkg_writer.addFeature(qgs_feature)

                if feedback.isCanceled():
                    break

        # Fermer le GeoPackage Writer
        del gpkg_writer

        return {self.OUTPUT: dest_id}


