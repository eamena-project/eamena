from django.shortcuts import redirect

def index(request):
	# to redirect the GeoServer
	return redirect('http://54.155.109.226:8080/geoserver/ows?version=1.3.0')
