from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.route, name='route'),
    path("route", views.route, name='route'),
    path("sensor_update", views.sensor_update, name="arduino_loc_update"),
    # path("delete_selected_hospitals", views.delete_selected_hospitals, name="delete-selected-data"),
    path("delete-hospitals", views.delete_hospitals, name="delete_hospitals"),
    path("sensor",views.Sensor, name='sensor'),
    path("fetch_and_store_hospitals",views.fetch_and_store_hospitals, name='fetch_and_store_hospitals'),
    path("test",views.test, name='test'),
    path("distance", views.distance, name='distance'),
    path("s_data", views.send_coordinates_to_amb82_mini, name='s_data'),
    path("map", views.map, name="map"),
    path("map2", views.map2, name="map2"),
    path("map3", views.map3, name="map3"),
    path("error", views.error, name="error"),
    path("hospital", views.hospital, name="hospital"),
    path('start_task/', views.start_task, name='start_task'),
    path('start_task2/', views.start_task2, name='start_task2'),
    path('get_progress/<str:task_id>/', views.get_progress, name='get_progress'),
]