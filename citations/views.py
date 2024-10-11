from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.test import RequestFactory

from eamena.utils import local_api_call

from .zip_file import save_zip
from .zenodo_publish import zenodo_publish
from .zenodo_calculate import zenodo_contributors, zenodo_keywords, zenodo_dates
from .forms import CitationForm

import re, os

def text_to_filename(text):
	# Replace spaces with underscores
	filename = text.replace(' ', '_').lower()
	# Remove any punctuation using regular expressions
	filename = re.sub(r'[^\w\s]', '', filename)
	return filename

def citation_generator(request):
	if request.method == 'POST':
		form = CitationForm(request.POST)
		if form.is_valid():
			rf = RequestFactory()
			geojson_url = form.cleaned_data['geojson_url']
			title = form.cleaned_data['title']
			description = form.cleaned_data['description']
			filename=text_to_filename(title)

			data = local_api_call(geojson_url, request.user)
			zip_filename = save_zip(data, filename)
			try:
				zd = zenodo_dates(data)
			except:
				zd = []
			zenodo_calculated_fields = zenodo_contributors(data), zenodo_keywords(data, additional=[]), zd
			r = zenodo_publish(title, zip_filename, description, zenodo_calculated_fields)
			os.remove(zip_filename)
			return redirect(str(r))  # Redirect to the uploaded document
	else:
		form = CitationForm()
	return render(request, "citation_form.html", {'form':form})
