import json
import gdal
import os
import mpu
import polyline

rasters = ['USGS_NED_13_n39w077_IMG.img','USGS_NED_13_n39w078_IMG.img','USGS_NED_13_n40w077_IMG.img','USGS_NED_13_n40w078_IMG.img']

def get_coord_elevation_meters(lng, lat):
    for elevationfile in rasters:
        result = os.popen('gdallocationinfo -valonly -wgs84 %s %s %s' % (elevationfile, lng, lat)).read()
        try:
            return float(result)
        except ValueError:
            # This coordinate is not in this elevation file, try another
            continue
    # Unable to obtain elevation data for this coordinate
    return -1

#lng = -76.9084866
#lat = 38.8541532
#print(get_coord_elevation_meters(lng, lat))

# gdallocationinfo -wgs84 USGS_NED_13_n39w077_IMG.img [lng] [lat]


with open('streets.geojson', 'r') as f:
    data = json.load(f)


results = []

totalfeatures = 0
for feature in data['features']:
    if feature['geometry']['type'] == "LineString":
        totalfeatures += 1
    
currfeaturenum = 0
for feature in data['features']:
    

    # What a feature looks like:
    # {'type': 'Feature', 'id': 'way/41278036', 'properties': {'area': 'yes', 'highway': 'pedestrian', 'id': 'way/41278036'}, 'geometry': {'type': 'Polygon', 'coordinates': [[[-77.0714409, 38.881617], [-77.0714535, 38.8816418], [-77.0715855, 38.8816026], [-77.071504, 38.8814362], [-77.0713693, 38.8814764], [-77.0713869, 38.8815109], [-77.0713221, 38.8815294], [-77.0713494, 38.8815634], [-77.0713643, 38.8815977], [-77.0713716, 38.881636], [-77.0714409, 38.881617]]]}}
    if feature['geometry']['type'] == "LineString":
        currfeaturenum += 1
        print("Processing feature "+str(currfeaturenum)+" of "+str(totalfeatures)+" features.")
        #if currfeaturenum < 1000 or currfeaturenum > 1005:
        #    continue
        # What a coord_list looks like
        # [[-77.0517825, 38.8370915], [-77.0517141, 38.8370776], [-77.0515477, 38.8370852]]
        coord_list = feature['geometry']['coordinates']
        
        # For each pair of consecutive points in the coord_list, compute
        # the grade of straight-line path between two points. 
        # Also compute the Google Maps encoding of the straight-line path.
        # Append [encoding, grade] to the results array.
        currPointIdx = 1
        prevPointIdx = 0
        while currPointIdx < len(coord_list):
            curr_lng = coord_list[currPointIdx][0]
            curr_lat = coord_list[currPointIdx][1]
            prev_lng = coord_list[prevPointIdx][0]
            prev_lat = coord_list[prevPointIdx][1]
            curr_elev = get_coord_elevation_meters(curr_lng, curr_lat)
            prev_elev = get_coord_elevation_meters(prev_lng, prev_lat)
            # If either elevation is not available, move on to the next pair
            if curr_elev == -1 or prev_elev == -1:
                currPointIdx += 1
                prevPointIdx += 1
                continue
            # Calculate the distance between the two points (in meters)
            dist = mpu.haversine_distance((curr_lat, curr_lng), (prev_lat, prev_lng))*1000
            # Calculate the elevation difference between the two points
            elev_change = abs(curr_elev - prev_elev)
            # Calculate the grade
            grade = 100*(elev_change / dist)
            # Get the GMaps polyline encoding of the line between the two points
            encoding = polyline.encode([(curr_lat,curr_lng),(prev_lat,prev_lng)])
            # Append result
            results.append([encoding, grade])
            currPointIdx += 1
            prevPointIdx += 1
print(results)
with open('slopes.json', 'w') as outfile:
    output = {}
    output['data'] = results
    json.dump(output, outfile)

#with open('streets_with_elevation.geojson', 'w') as f:
#    json.dump(data, f)
#print("Finished processing "+str(featurecount)+" streets features.")
