# Combined Layers GeoJSON Script

### Overview

This Python script for QGIS automatically detects all vector layers in the current project and merges them into a single GeoJSON file. It attempts three methods—native merge, in-memory merge with export, and manual feature copying—to ensure compatibility across different layer setups. Once the merge succeeds, the combined layer is added back into the QGIS map canvas.
Features
```
    Automatically finds every vector layer in a QGIS project

    Tries the built-in native:mergevectorlayers tool with layer IDs

    Falls back to an in-memory merge and explicit GeoJSON export

    Falls back again to manual feature copying if earlier methods fail

    Prints status messages at each stage for easy debugging

    Saves the final GeoJSON to the user’s Desktop as combined_layers.geojson

    Adds the merged layer to the project with the name “Combined_All_Layers”
```

### Requirements

    QGIS with Python API (PyQGIS) installed

    Processing plugin enabled in QGIS

    Write permission to the output folder (default: Desktop)

#### Installation

    Clone or download this repository to your local machine.

    Copy the script file into your QGIS scripts folder or any accessible directory.

    Open QGIS and ensure the Processing toolbox is activated.

##### Usage

    Open the QGIS Python Console or set up a Processing script.

    Load your project containing the vector layers you wish to merge.

    Run the script.

    Watch the console output for progress and any error messages.

    Find the merged GeoJSON at ~/Desktop/combined_layers.geojson.

### Script Workflow

    Layer Detection

        Collects all layers in the project

        Filters to only those with vector geometries

    Method 1: Native Merge

        Uses native:mergevectorlayers with layer IDs

        Outputs directly to GeoJSON

    Method 2: In-Memory Merge + Export

        Merges layers in memory

        Exports the temporary layer to GeoJSON via QgsVectorFileWriter

    Method 3: Manual Feature Copying

        Creates a new memory layer with combined field schema

        Iterates through all features in each layer and adds them

        Exports the fully assembled layer to GeoJSON

## Output

The final merged file is saved as:
```
~/Desktop/combined_layers.geojson
```

The script also adds a new layer named Combined_All_Layers to your QGIS canvas.
