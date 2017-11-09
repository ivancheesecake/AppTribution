import xml.etree.ElementTree as ET

# Add KML Format validation next time

with open("E:/StreetView/Pagbahan_Final.kml","r") as f:
	kml_string = f.read()

root = ET.fromstring(kml_string)
elements= list(root.iter('{http://www.opengis.net/kml/2.2}Placemark'))

features = []


for element in elements:

	feature_id= element[0][0][0].text
	coordinates = element[1][0].text
	coords = coordinates.split(",")
	features.append({"feature_id":feature_id,"lat":coords[1],"long":coords[0]})

print features