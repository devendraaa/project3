# this is updated website
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from home.models import Login
from django.contrib import messages
import numpy as np
import pandas as pd
import json
import xml.etree.ElementTree as ET
from tqdm import tqdm
from home.models import sen_locc
from home.models import hospital_db
from home.models import hospital_name
import folium
from folium.plugins import FastMarkerCluster
# Plotting
from django.http import JsonResponse
import uuid
import threading
from django.http import JsonResponse
import uuid
from tqdm import tqdm  # Import tqdm for progress visualization
import xml.etree.ElementTree as ET  # Import ElementTree for XML parsing
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
import paho.mqtt.publish as publish
from math import radians, sin, cos, sqrt, atan2
from .models import hospital_name
import requests
from geopy.geocoders import Nominatim # Import geocoding library


geolocator = Nominatim(user_agent="Smart Ambulance Route with AI")

R = 6371

task_progress = {}

def deg_to_rad(degrees):
    return degrees*(np.pi/180)


def dist(lat1, lon1, lat2, lon2):
    d_lat = deg_to_rad(lat2-lat1)
    d_lon = deg_to_rad(lon2-lon1)
    a = np.sin(d_lat/2)**2 + np.cos(deg_to_rad(lat1)) * np.cos(deg_to_rad(lat2)) * np.sin(d_lon/2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
    return R * c



def calculate_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad = radians(lat1), radians(lon1)
    lat2_rad, lon2_rad = radians(lat2), radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Radius of the Earth in kilometers
    return distance

def rout_list(route_nodes):    ### keeping every third element in the node list to optimise time
    route_list = []
    for i in range(0, len(route_nodes)):
        if i % 3==1:
            route_list.append(route_nodes[i])
    return route_list

# Create your views here.
def index(request):
    # messages.success(request, "this is test message")

    return render(request, 'route.html')

def test(request):
    # messages.success(request, "this is test message")

    return render(request, 'test.html')

def testing(lati, longi):
    near_di =[]
    hosp_data = hospital_db.objects.all()
    if not hosp_data:
        print("No hospital locations found in the database.")
    else:
        for loc in hosp_data:
            lat = loc.lat
            lon = loc.lon
            distance = dist(lati, longi, lat, lon)
            near_di.append(distance * 1000)  # Convert distance to meters and append to near_dist
            # print(near_di)
            # print(f"Distance from ({latitude}, {longitude}) to ({lat}, {lon}): {distance * 1000} meters")
    return near_di


def geocode_place(place):
    url = f"https://nominatim.openstreetmap.org/search?q={place}&format=json"
    response = requests.get(url)
    data = response.json()
    if data:
        # Extract latitude and longitude from the first result
        latitude = float(data[0]["lat"])
        longitude = float(data[0]["lon"])
        return latitude, longitude
    else:
        print(f"Geocoding failed for '{place}'")
        return None, None


def get_route_distance(o_lat, o_lon, d_lat, d_lon):
    url = f"http://router.project-osrm.org/route/v1/driving/{o_lon},{o_lat};{d_lon},{d_lat}?overview=false"
    response = requests.get(url)
    data = response.json()
    if data.get("code") == "Ok":
        # Extract route distance in meters
        distance = data["routes"][0]["distance"]
        distance_km = distance / 1000  # Convert to kilometers
        return distance_km
    else:
        print("Routing failed")
        return None
    
def distance(request):

    hosp_data = hospital_name.objects.all()

    f_distance_km = []

    if latitude and longitude:
        
        for i in hosp_data:
            destination = geolocator.geocode(i.h_name)
            if destination:
         
                latt = destination.latitude
                lonn = destination.longitude
    
                distance_km = get_route_distance(latitude, longitude, latt, lonn)
                f_distance_km.append(distance_km)
         
        # print(f_distance_km)

        sorted_distances = sorted(enumerate(f_distance_km), key=lambda x: x[1])
        top_5_indices = [idx for idx, _ in sorted_distances[:5]]
        top_5_hospitals = [hosp_data[idx] for idx in top_5_indices]
        top_5_distances = [dist for _, dist in sorted_distances[:5]]

        # print(top_5_hospitals)
        hospital_distance_tuples = zip(top_5_hospitals, top_5_distances)
        # print(top_5_distances)


    return render(request, 'route.html', {'hospital_distance_tuples': hospital_distance_tuples})


def route(request):
    
    global latitude, longitude
    # near_dist = []

    if request.method == 'POST':

        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')


    return render(request, 'route.html')

def error(request):
    return render(request, 'checck.html')


def delete_hospitals(request):
    if request.method == 'POST':
        if 'HTTP_X_REQUESTED_WITH' in request.headers and request.headers['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest':
            selected_ids = request.POST.getlist('selected_ids[]')
            print(selected_ids)
            if selected_ids:
                hospitals_to_delete = hospital_name.objects.filter(pk__in=selected_ids)
                hospitals_to_delete.delete()  # Delete selected hospitals from the database
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'No hospitals selected.'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request.'}, status=400)


def hospital(request):

    if request.method == 'POST':
        h_loc = request.POST.get('h_location')

        if h_loc:
                # for name in hospi:
            hospital_name.objects.get_or_create(h_name=h_loc)
            # hospital = hospital_name(h_name=h_loc)
            # hospital.save()
            print("Hospital data saved")
            # hosp_call()
            return JsonResponse({'message': 'Hospital data saved successfully.'})
        else:
            print("Hospital Address is Invalid")
            return JsonResponse({'error': 'Entered Hospital Location is Invalid'})
    # , {'hospitals': hospitals}
    return render(request, 'hospital.html') 


def fetch_and_store_hospitals(request):
    # Make a request to the Nominatim API to search for hospitals in Mumbai
    # url = 'https://nominatim.openstreetmap.org/search?q=hospital+in+mumbai&format=json'
    # response = requests.get(url)
    # data = response.json()

    # # Extract hospital names from the API response
    # hospi = list({item['display_name'] for item in data})  # Use set to remove duplicates

    # Store unique hospital names in the database
        

    # Fetch hospitals from the database and sort them alphabetically


    hospitals = hospital_name.objects.order_by('h_name')
    

    # Render the template with the sorted list of hospitals
    return render(request, 'hospital.html', {'hospitals': hospitals})

def Sensor(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        if latitude:
            if longitude:
                messages.success(request, "SENSOR COORDINATES SAVED")
                sen_loc = sen_locc(lat=latitude, lon=longitude)
                sen_loc.save()
                print("sensor data saved")
                
            else:
                messages.success(request, "Enter Longitude Coordinate's")
            
        else:
            messages.success(request, "Enter Latitude Coordinate's")
        
    return render(request, 'sensor.html')


def login(request):
    
    # new_coord()
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        login = Login(username = 'username', password = 'password')
        login.save()
        messages.success(request, " your messages has been save")
    return render(request, 'login.html')


def map(request): # Marked All Sensors on a MAP
    

    sens_da = sen_locc.objects.all()
    m = folium.Map(location=[19.045823, 72.848379], zoom_start=15)

    for loc in sens_da:
        coordina = [loc.lat, loc.lon]
        folium.Marker(coordina, popup=coordina).add_to(m)
   
    # latitudes = [sens_dat.lat for sens_dat in sens_da]
    # longitudes = [sens_dat.lon for sens_dat in sens_da]

    # FastMarkerCluster(data=list(zip(latitudes, longitudes))).add_to(m)

    context = {'map': m._repr_html_()}
    return render(request, 'map.html', context)

def map3(request): # Current Routes Map
    try:
    # db_sen = db_sens.objects.all()
        m3 = folium.Map(location=[19.045823, 72.848379], zoom_start=15)

        for loc in coordinates:
            coordina = (loc[0], loc[1])
            folium.Marker(coordina, popup=coordina).add_to(m3)

        context = {'map3': m3._repr_html_()}
        return render(request, 'map3.html', context)
        
    except Exception as e:
        response = JsonResponse({"message": "server error"})

        return redirect("/route")

        # return response


def data_frame():

    df_out = pd.DataFrame({'Node': np.arange(len(coordinates))})
    df_out['coordinates'] = coordinates
    df_out[['lat', 'long']] = pd.DataFrame(df_out['coordinates'].tolist())

# Converting Latitude and Longitude into float
    
    df_out['lat'] = df_out['lat'].astype(float)
    df_out['long'] = df_out['long'].astype(float)

    global final_df
    final_df = df_out

def map2(request):
    # sen_da = col_name()
    # new_coord()
    # db_sen = db_sens.objects.all()
    try:
        m2 = folium.Map(location=[19.045823, 72.848379], zoom_start=15)

        for i in range(len(sen_da)):
            coordina = (sen_da.iloc[i]['lat'], sen_da.iloc[i]['long'])
            folium.Marker(coordina, popup=coordina).add_to(m2)

        context = {'map2': m2._repr_html_()}
        return render(request, 'map2.html', context)

    except Exception as e:
            response = JsonResponse({"message": "server error"})

            return redirect("/route")

def col_name(coor1, coor2, diss):

    df = pd.DataFrame()
    df['lat'] = coor1
    df['long'] = coor2

    column_name = []
    for i in range(len(sensor_coor)):
        column_name.append(sensor_coor[i])

    column_name = list(set(column_name))
    # print(column_name)

    for j in range(len(column_name)):
        df.insert(j, column_name[j],diss[j])
    # for j in range(len(column_name)):
        # pd.concat((df,j))

    sensor_f_data = []
    for i in range(len(sensor_coor)):
        s = df[df[sensor_coor[i]] == df[sensor_coor[i]].min()]
        sensor_f_data.append(s)
    # print(sensor_f_data)
        
    sens_data = pd.DataFrame()
    for i in sensor_f_data:
        sens_data = pd.concat([sens_data, i], axis=0)
    # print(sens_data)

    sens_data2 = sens_data.drop_duplicates()
    
    # return(sens_data)

    global sen_da
    sen_da = sens_data2[['lat', 'long']]
    # print(sen_da)

    data_frame()

    # for i in range(len(sen_data)):

        # db_sen = db_sens(lat = sen_data.iloc[i]['lat'], lon = sen_data.iloc[i]['long'])
        # db_sen.save()
        # print("Data Save Coorectly")


def lat_lon(coordina):

    global sensor_coor
    sensor_coor = []
    final_sens = sen_locc.objects.all()
    for sens in final_sens:
        sensor_coor.append((sens.lat, sens.lon))

    coordinates = coordina 
    diss = [[] for _ in range(len(sensor_coor))]
    coor1 = []
    coor2 = []
    for i in range(len(coordinates)):
        coor1.append(float(coordinates[i][0]))
        coor2.append(float(coordinates[i][1]))

        for j in range(len(sensor_coor)):

            distance = dist(float(coordinates[i][0]), float(coordinates[i][1]), float(sensor_coor[j][0]), float(sensor_coor[j][1]))
            diss[j].append(distance*1000)
            
    # print(diss)

    col_name(coor1=coor1, coor2=coor2, diss=diss)  

import json

def sensor_update(request):
    if request.method == 'POST':
        try:
            # Get latitude and longitude from the POST request
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            
            # Publish the new fixed coordinates to the MQTT topic
            mqtt_broker_ip = "broker.hivemq.com"  # Replace with your MQTT broker IP
            mqtt_topic = "fixed_coordinates"  # MQTT topic for fixed coordinates
            payload = '{{"latitude": {}, "longitude": {}}}'.format(latitude, longitude)
            publish.single(mqtt_topic, payload, hostname=mqtt_broker_ip)
            
            return HttpResponse('Fixed coordinates updated successfully')
        except Exception as e:
            return HttpResponse('Failed to update fixed coordinates: {}'.format(e), status=500)
    else:
        return render(request, 'sensor_update.html')


def send_coordinates_to_amb82_mini(request):
    # Define the chunk size
    chunk_size = 6  # Adjust the chunk size as needed

    # Determine the number of chunks
    num_chunks = (len(lat) + chunk_size - 1) // chunk_size

    total_payload_length = 0  # Initialize total payload length

    try:
        mqtt_broker_ip = "broker.hivemq.com"  # Replace with your MQTT broker IP
        mqtt_topic = "coordinates"  # MQTT topic to publish coordinates

        for i in range(num_chunks):
            # Get the chunk of coordinates
            lat_chunk = lat[i * chunk_size: (i + 1) * chunk_size]
            lon_chunk = lon[i * chunk_size: (i + 1) * chunk_size]

            # Truncate each coordinate to 4 digits after the decimal point
            lat_chunk_truncated = ["{:.4f}".format(lat) for lat in lat_chunk]
            lon_chunk_truncated = ["{:.4f}".format(lon) for lon in lon_chunk]

            # Construct the coordinate data
            coordinates = {"lat": lat_chunk_truncated, "lon": lon_chunk_truncated}

            # Convert coordinate data to JSON format
            json_data = json.dumps(coordinates)

            # Calculate payload length for this batch and add to total
            payload_length = len(json_data)
            total_payload_length += payload_length

            # Publish the coordinate data to the MQTT topic
            publish.single(mqtt_topic, json_data, hostname=mqtt_broker_ip)

        # After all batches are sent, print the total payload length
        print("Coordinates sent successfully to MQTT broker. Total Payload length:", total_payload_length)

        return HttpResponse('Coordinates sent successfully to MQTT broker')
    except Exception as e:
        return HttpResponse('An error occurred: {}'.format(e), status=500)



def new_lat_lon(coordinates):
    global sensor_coor
    sensor_coor = []
    final_sens = sen_locc.objects.all()
    for sens in final_sens:
        sensor_coor.append((sens.lat, sens.lon))

    dis = []
    global lat, lon
    lat = []
    lon = []
    for i in range(len(coordinates)):
        for j in range(len(sensor_coor)):
            di = dist(float(coordinates[i][0]), float(coordinates[i][1]), float(sensor_coor[j][0]), float(sensor_coor[j][1]))
            di = di*1000
            if di < 6:
                dis.append(di)
                lat.append(sensor_coor[j][0])
                lon.append(sensor_coor[j][1])

        else:
            continue

    # se_co = []
    # for i in range(len(lat)):
    #     se_co.append((lat[i], lon[i]))
    # print(se_co)

    global sensor_co
    sensor_co = []
    for i in range(len(lat)):
        lat_str = "{:.15f}".format(lat[i])  # Convert latitude to string with high precision
        lon_str = "{:.15f}".format(lon[i])  # Convert longitude to string with high precision
        lat_truncated = float(lat_str[:lat_str.index('.') + 6])  # Keep only the first 5 digits after the decimal point
        lon_truncated = float(lon_str[:lon_str.index('.') + 6])  # Keep only the first 5 digits after the decimal point
        sensor_co.append((lat_truncated, lon_truncated))

    print("all sensor:", sensor_co)

    global sen_da
    
    sen_da = pd.DataFrame(columns=['lat', 'lon'])
    sen_da['lat'] = lat
    sen_da['long'] = lon
    print(sen_da)


# def new_coord(): # store all sensor coordinations of mumbai in a postgre database
#     coordinate = pd.read_csv("E:\\new_django\Hello\static\output.csv")

#     coordinate.rename(columns = {'19.061042984816705':'latitude', '72.84680396318437':'longitude'}, inplace = True)

#     for i in range(len(coordinate)):
#         sen_loc = sen_locc(lat=coordinate.iloc[i][0], lon=coordinate.iloc[i][1])
#         sen_loc.save()
#         print("New Coordinate Save Successfully to DataBase:")

#     print(coordinate.iloc[0][0])

def long_running_task2(task_id, latitude, longitude, Hospital_loc):
    geolocator = Nominatim(user_agent="Smart Ambulance Route with AI")

    Destination = Hospital_loc

    destination = geolocator.geocode(Destination)

    if destination:
        d_latitude = destination.latitude
        d_longitude = destination.longitude
        print("destination latitude:",d_latitude)
        print("destination longitude:", d_longitude)

    if destination is None:
        print("Destination Address is Invalid")
    else:
        print("Address Verified:")

    start = "{},{}".format(longitude, latitude)
    end = "{},{}".format(d_longitude, d_latitude)
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?alternatives=false&annotations=nodes'.format(start, end)

    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)
    print("Calling API ...:", r.status_code)

    routejson = r.json()
    route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

    # Initialize coordinates list
    global coordinates
    coordinates = []

    # Estimate total number of iterations
    total_iterations = len(route_nodes)

    # Process route nodes
    for i, node in enumerate(route_nodes):
        try:
            headers = {'Content-type': 'application/json'}
            url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
            r = requests.get(url, headers=headers)
            myroot = ET.fromstring(r.text)

            for child in myroot:
                lat, long = child.attrib['lat'], child.attrib['lon']
            coordinates.append((lat, long))
        except:
            continue

        # Calculate progress based on completed iterations
        progress = (i + 1) / total_iterations
        task_progress[task_id] = progress

    # Call function for additional processing
    # print(coordinates)
    
    
    # Simulate completion of the task
    task_progress[task_id] = 1.0  # Set progress to 100% when the task is completed
    new_lat_lon(coordinates=coordinates)
    print("task completedddd:")
    return redirect("/map")


def start_task2(request):
    if request.method == 'POST':
        # Retrieve hospital name from session storage
        hospital_name = request.session.get('hospitalName')
        if hospital_name:
            print("Hospital Location:", hospital_name)
        else:
            print("Hospital Location Not Available")
        
        print("current latitude:",latitude)
        print("current longitude:",longitude)
        

        if not hospital_name:
            return JsonResponse({'error': 'Not Fetching Hospital Data'})
        
        
        task_id = str(uuid.uuid4())  # Generate unique task ID
        task_thread = threading.Thread(target=long_running_task, args=(task_id, latitude, longitude, hospital_name))
        task_thread.start()


        return JsonResponse({'task_id': task_id})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})


# Function simulating a long-running task with additional processing
def long_running_task(task_id, p_lat, p_lon, h_loc):
    geolocator = Nominatim(user_agent="Smart Ambulance Route with AI")

    print(p_lat, p_lon, h_loc)
    P_lat = p_lat
    P_lon = p_lon

    Destination = h_loc

    destination = geolocator.geocode(Destination)
    print(destination)

    if destination is None:
        print("Destination Address is Invalid")
    else:
        print("Address Verified:")

    start = "{},{}".format(P_lon, P_lat)
    end = "{},{}".format(destination.longitude, destination.latitude)
    url = 'http://router.project-osrm.org/route/v1/driving/{};{}?alternatives=false&annotations=nodes'.format(start, end)

    headers = {'Content-type': 'application/json'}
    r = requests.get(url, headers=headers)
    print("Calling API ...:", r.status_code)

    routejson = r.json()
    route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

    # Initialize coordinates list
    global coordinates
    coordinates = []

    # Estimate total number of iterations
    total_iterations = len(route_nodes)

    # Process route nodes
    for i, node in enumerate(route_nodes):
        try:
            headers = {'Content-type': 'application/json'}
            url = 'https://api.openstreetmap.org/api/0.6/node/' + str(node)
            r = requests.get(url, headers=headers)
            myroot = ET.fromstring(r.text)

            for child in myroot:
                lat, long = child.attrib['lat'], child.attrib['lon']
            coordinates.append((lat, long))
        except:
            continue

        # Calculate progress based on completed iterations
        progress = (i + 1) / total_iterations
        task_progress[task_id] = progress

    # Call function for additional processing
    # print(coordinates)
    
    
    # Simulate completion of the task
    task_progress[task_id] = 1.0  # Set progress to 100% when the task is completed
    new_lat_lon(coordinates=coordinates)
    print("task completedddd:")
    return redirect("/map")
   

def start_task(request):
    # new_coord()
    if request.method == 'POST':
        global p_lat, p_lon
        p_lat = request.POST.get('P_latitude')
        p_lon = request.POST.get('P_longitude')
        h_loc = request.POST.get('h_location')
        print(p_lat)
        print(p_lon)
        print(h_loc)

        if not h_loc:
            return JsonResponse({'error': 'Enter Hospital Location'})
        
        
        task_id = str(uuid.uuid4())  # Generate unique task ID
        task_thread = threading.Thread(target=long_running_task, args=(task_id, p_lat, p_lon, h_loc))
        task_thread.start()


        return JsonResponse({'task_id': task_id})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    

def get_progress(request, task_id):
    # Your logic to retrieve progress for the given task_id
    # progress = get_progress_from_database(task_id)  # Example function
    progress = task_progress.get(task_id, 0.0)

    if progress is not None:
        return JsonResponse({'progress': progress})
    else:
        # Handle the case when progress is not available
        # return JsonResponse({'error': 'Progress not found'}, status=404)
        print("error")


