# --- START OF SCRIPT ---
# This script automatically detects all layers and combines them into a single GeoJSON file
import processing
from qgis.core import QgsProject, QgsVectorFileWriter
import os

print("Starting layer detection and combination script...")

# 1. Automatically detect ALL vector layers in the project
project = QgsProject.instance()
all_layers = project.mapLayers().values()

# Filter to get only vector layers (excluding raster layers)
vector_layers = [layer for layer in all_layers if hasattr(layer, 'geometryType')]

if not vector_layers:
    raise Exception("No vector layers found in the project!")

print(f"Found {len(vector_layers)} vector layers:")
for layer in vector_layers:
    print(f"  - {layer.name()} ({layer.featureCount()} features)")

# 2. Define output path for the GeoJSON file
output_path = os.path.join(os.path.expanduser("~"), "Desktop", "combined_layers.geojson")
print(f"Output will be saved to: {output_path}")

try:
    # 3. Method 1: Use native:mergevectorlayers with proper layer IDs
    layer_ids = [layer.id() for layer in vector_layers]
    
    params = {
        'LAYERS': layer_ids,  # Use layer IDs instead of layer objects
        'CRS': None,  # Use CRS from first layer
        'OUTPUT': output_path  # Direct output to GeoJSON file
    }
    
    print("Attempting to merge layers...")
    result = processing.run("native:mergevectorlayers", params)
    
    print(f"SUCCESS! Combined GeoJSON file created at: {output_path}")
    
    # Also add the result to the map canvas
    if 'OUTPUT' in result:
        output_layer = result['OUTPUT']
        if hasattr(output_layer, 'setName'):
            output_layer.setName('Combined_All_Layers')
            QgsProject.instance().addMapLayer(output_layer)
            print(f"Added combined layer to map with {output_layer.featureCount()} total features")
    
except Exception as e:
    print(f"Method 1 failed: {str(e)}")
    print("\nTrying alternative method...")
    
    try:
        # Method 2: Create temporary merged layer first, then export
        temp_params = {
            'LAYERS': vector_layers,  # Try with layer objects directly
            'CRS': None,
            'OUTPUT': 'memory:temp_combined'
        }
        
        temp_result = processing.run("native:mergevectorlayers", temp_params)
        temp_layer = temp_result['OUTPUT']
        
        # Export the temporary layer to GeoJSON
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GeoJSON"
        options.fileEncoding = "UTF-8"
        
        error = QgsVectorFileWriter.writeAsVectorFormatV3(
            temp_layer,
            output_path,
            QgsProject.instance().transformContext(),
            options
        )
        
        if error[0] == QgsVectorFileWriter.NoError:
            print(f"SUCCESS with Method 2! GeoJSON file created at: {output_path}")
            
            # Add to map
            temp_layer.setName('Combined_All_Layers')
            QgsProject.instance().addMapLayer(temp_layer)
            print(f"Added combined layer to map with {temp_layer.featureCount()} total features")
        else:
            raise Exception(f"Failed to write GeoJSON: {error}")
            
    except Exception as e2:
        print(f"Method 2 also failed: {str(e2)}")
        print("\nTrying Method 3 - Manual feature copying...")
        
        try:
            # Method 3: Manual approach - copy all features to a new layer
            from qgis.core import QgsVectorLayer, QgsFeature, QgsGeometry
            
            # Create a new memory layer with generic geometry type
            combined_layer = QgsVectorLayer("GeometryCollection?crs=EPSG:4326", "Combined_All_Layers", "memory")
            
            # Get all unique field names from all layers
            all_fields = set()
            for layer in vector_layers:
                for field in layer.fields():
                    all_fields.add(field.name())
            
            # Add fields to the combined layer
            from qgis.core import QgsField
            from PyQt5.QtCore import QVariant
            
            combined_layer.startEditing()
            for field_name in all_fields:
                combined_layer.addAttribute(QgsField(field_name, QVariant.String))
            combined_layer.commitChanges()
            
            # Copy all features from all layers
            total_features = 0
            combined_layer.startEditing()
            
            for layer in vector_layers:
                print(f"Copying features from {layer.name()}...")
                for feature in layer.getFeatures():
                    new_feature = QgsFeature(combined_layer.fields())
                    new_feature.setGeometry(feature.geometry())
                    
                    # Copy attributes
                    for field in feature.fields():
                        if field.name() in [f.name() for f in combined_layer.fields()]:
                            new_feature[field.name()] = feature[field.name()]
                    
                    combined_layer.addFeature(new_feature)
                    total_features += 1
            
            combined_layer.commitChanges()
            
            # Export to GeoJSON
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GeoJSON"
            options.fileEncoding = "UTF-8"
            
            error = QgsVectorFileWriter.writeAsVectorFormatV3(
                combined_layer,
                output_path,
                QgsProject.instance().transformContext(),
                options
            )
            
            if error[0] == QgsVectorFileWriter.NoError:
                print(f"SUCCESS with Method 3! GeoJSON file created at: {output_path}")
                print(f"Total features copied: {total_features}")
                
                # Add to map
                QgsProject.instance().addMapLayer(combined_layer)
            else:
                raise Exception(f"Failed to write GeoJSON: {error}")
                
        except Exception as e3:
            print(f"All methods failed. Final error: {str(e3)}")
            print("Please check that your layers contain valid geometries and try again.")

print("Script completed!")
# --- END OF SCRIPT ---