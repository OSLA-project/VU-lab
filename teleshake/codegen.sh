#! /bin/bash

TARGET_FOLDER=./src/sila2_driver/thermoscientific/teleshake1536/generated/

XML1=./feature_xml/CancelController-v1_0.sila.xml
XML2=./feature_xml/settings.sila.xml
XML3=./feature_xml/shakecontroller.sila.xml
XML4=./feature_xml/SimulationController-v1_0.sila.xml

echo Generating Sila2 dependencies
echo Target folder: $TARGET_FOLDER

sila2-codegen generate-feature-files -o $TARGET_FOLDER $XML1 $XML2 $XML3 $XML4
