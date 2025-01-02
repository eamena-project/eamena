import json, os, sys

# Check the command line arguments are OK
if len(sys.argv) != 3:
	sys.stderr.write("Use: " + sys.argv[0] + ' [file_1] [file_2]\n')
	sys.exit(1)

files = [os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])]

# Check that all the passed files exist
for file in files:
	if os.path.exists(file):
		continue
	sys.stderr.write("File " + file + " not found\n")
	sys.exit(1)

store = {}
index = []
i = 0
c = len(files)
for file in files:
	try:
		with open(file, 'r') as fp:
			data = json.load(fp)
	except:
		data = {}
	if not('business_data' in data):
		sys.stderr.write("File " + file + " is not valid Arches JSON\n")
		sys.exit(1)
	if not('resources' in data['business_data']):
		sys.stderr.write("File " + file + " is not valid Arches JSON\n")
		sys.exit(1)

	data = data['business_data']['resources']
	for resource in data:
		id = resource['resourceinstance']['resourceinstanceid']
		if not(id in store):
			store[id] = [0] * c
		store[id][i] = len(resource['tiles'])

	i = i + 1

for idv in store.keys():

	id = str(idv)
	if id in index:
		continue
	l = store[id]
	if all(x == l[0] for x in l):
		continue
	index.append(id)

# Last pass - now we know which resources differ between files, we can generate our final file

ret = []
done = []
for file in files:
	with open(file, 'r') as fp:
		data = json.load(fp)
	data = data['business_data']['resources']
	for resource in data:
		id = resource['resourceinstance']['resourceinstanceid']
		if id in done:
			sys.stderr.write("Resource instance " + id + " exists differently in more than one file.\n")
			sys.exit(1)
		if not(id in index):
			continue
		ret.append(resource)
		done.append(id)

print(json.dumps({'business_data': {'resources': ret}}))
