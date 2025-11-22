from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="global_travel_guide")

def add_landmark_marker(map_widget, name, city=None):
    try:
        query = f"{name}, {city}" if city else name
        location = geolocator.geocode(query, timeout=10)
        if location:
            marker = map_widget.set_marker(location.latitude, location.longitude, text=name)
            return marker
    except Exception as e:
        print(f"Marker error for {name}: {e}")

def clear_markers(marker_list):
    for m in marker_list:
        try:
            m.delete()
        except Exception as e:
            print(f"Failed to delete marker: {e}")
    marker_list.clear()


