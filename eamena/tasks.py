from django.core.management import call_command
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from celery import shared_task
import os, json

@shared_task
def import_processed_bulk_upload_and_notify(notify_address=None, upload_path=None):

	# If there is no email address, that's fine, we just don't notify. If there is no file, however, we can't do anything, so exit now.

	if upload_path is None:
		return False
	base_path = os.path.abspath(upload_path)
	if not(os.path.exists(base_path)):
		return False

	import_files_path = os.path.join(upload_path, 'for_import')
	summary_path = os.path.join(upload_path, 'summary')
	if not(os.path.exists(import_files_path)):
		return False
	if not(os.path.exists(summary_path)):
		os.makedirs(summary_path)
	files = []
	summary = []
	for file in os.listdir(import_files_path):
		if file.startswith('.'):
			continue
		if not(file.endswith('.json')):
			continue
		import_file = os.path.join(import_files_path, file)
		if(not(os.path.exists(import_file))):
			continue
		files.append(import_file)

	for file in files:
		import_file = file
		summary_file = file.replace('.json', '.summary.json')

		call_command('packages', operation='import_business_data', source=import_file, overwrite='overwrite')

		with open(summary_file, 'w') as fp:
			call_command('bu', operation='summary', source=import_file, dest_dir=summary_path)

	if notify_address is None:
		return True

	for file in os.listdir(summary_path):
		if file.startswith('.'):
			continue
		if not(file.endswith('.json')):
			continue
		summary_file = os.path.join(summary_path, file)
		if not(os.path.exists(summary_file)):
			continue
		with open(summary_file, 'r') as fp:
			for item in json.loads('\n'.join(fp.readlines())):
				summary.append(item)

	if len(summary) > 0:

		data = []
		for item in summary:
			data.append({"url": "https://database.eamena.org/en/report/" + item['uuid'], "uuid": item['uuid'], "eamenaid": item['eamenaid']})

		email_context = {"greeting": "Your bulk upload was successful.", "closing": "", "resources": data}

		html_content = render_to_string("email/bu_ready_email_notification.htm", email_context)  # ...
		text_content = strip_tags(html_content)  # this strips the html, so people will have the text as well.

		msg = EmailMultiAlternatives("Bulk upload complete", text_content, settings.EMAIL_FROM_ADDRESS, [notify_address])
		msg.attach_alternative(html_content, "text/html")
		msg.send()
