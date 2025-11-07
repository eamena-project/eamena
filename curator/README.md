# Arches Curator
Arches Curator is a plugin for [Arches](https://github.com/archesproject/arches/). It allows each user to save the results of searches as datasets which are subsets of the entire database. Unlike traditional saved searches in Arches, the results are saved along with the search, as the results may change if the user repeats the search at a later time. These datasets may then be exported to a number of different external locations. Currently we support IPFS and Zenodo, both of these provide a (theoretically) permanent existance.

Thanks go to Cyrus Hiatt of Farallon Geographics for his [dashboard example](https://github.com/chiatt/dashboard), on which this plugin is based.

## IPFS
IPFS (InterPlanetary File System) is a protocol, hypermedia and file sharing peer-to-peer network for storing and sharing data in a distributed hash table. It uses content addressing, and so long as at least one person on the network has a particular file, it remains available. There are also various web gateways that make the contents of the IPFS network available to ordinary web users without requiring them to install any special software.
## Zenodo
The Zenodo code is a modified version of the EAMENA Citation plugin by [Thomas Huet](https://github.com/zoometh) and [Reuben Osborne](https://github.com/reubenosborne1). Zenodo is a general-purpose open repository developed under the European OpenAIRE program and operated by CERN. This plugin allows the user to easily submit saved searches to Zenodo, automatically generating appropriate metadata. For each submission to Zenodo, a persistent digital object identifier (DOI) is generated, which makes the stored items easily citeable.

## Installing the plugin

* Stop the Arches server (either Ctrl+C from `runserver` or stop Apache or NGINX.)
* From the root of your Arches project (the directory that contains `manage.py`), clone the repository into a subdirectory named `curator`...
```bash
git clone https://github.com/ads04r/arches-curator.git curator
```

* Add `"curator"` to the `INSTALLED_APPS` setting in your Arches project...
```python
INSTALLED_APPS = [
    ...
    "arches",
    "[project_name]"
    "curator",
    ...
]
```

* As this plugin modifies part of the default Arches UI, we also need to make the plugin's templates directory visible. We can do this by modifying the `TEMPLATES` key in `settings.py`...
```python
TEMPLATES = build_templates_config(
    debug=DEBUG,
    app_root=APP_ROOT,
    additional_directories=[os.path.join(os.path.dirname(APP_ROOT), 'curator', 'templates')],
)
```

* Add the plugin `curator` as a dependency in `pyproject.toml`...
```toml
dependencies = [
    "arches>=7.6.0,<8.0.0",
    "curator==0.1.0",
]
```

* Update `urls.py` file in your Arches project...
```python
urlpatterns = [
	...
	path("", include("curator.urls")),
	...
]
```

* Run the migrations to ensure the required database tables are created...
```bash
python manage.py migrate curator
```

* Change into your project directory (one below the directory containing `manage.py`) and from there, making sure the Arches server is running, run `npm` to ensure the plugin is built within Webpack...
```bash
npm run build_development
```

## Configuration

As this point, you should see the Curator icon at the bottom of the navigation margin. Basic functionality (eg saving searches and recalling them) should now work. However, in order to push these searches to Zenodo or IPFS you'll need to add some extra settings into `settings.py`

### IPFS
In order to upload to IPFS, you'll need a node that the Arches project can access (for example, a running instance of [kubo](https://github.com/ipfs/kubo)) and a web-accessible IPFS gateway. If you don't have a gateway, you can use `https://ipfs.io/ipfs/`, although using `http://localhost:8080/` will work for users who have the IPFS desktop application running on their local machine.

```python
IPFS_NODE = ['localhost', 5001] # [host, port]
IPFS_WEB_PROXY = 'https://ipfs.io/ipfs/%CID%'
```

### Zenodo
The Zenodo export is a bit more complicated, because it needs to be configured based on your graph models. It needs to know which fields of your data to map to which metadata values in Zenodo. Shown below is an example that is valid for the EAMENA database. Feel free to use it as a template...
```python
ZENODO_ACCESS_TOKEN = '[zenodo_token]' # Redacted, for obvious reasons
ZENODO_URL = 'https://zenodo.org/api/deposit/depositions'
ZENODO_METADATA = {
	'metadata': {
		'upload_type': 'dataset',
		'license': 'cc-by',
		'subjects': [{"term": "Cultural property", "identifier": "https://id.loc.gov/authorities/subjects/sh97000183.html", "scheme": "url"}],
		'method': 'EAMENA data entry methodology',
		'creators': [{'name': "EAMENA database",
		'affiliation': "University of Oxford, University of Southampton"}]
	},
	'keywords': {
		'static': ['EAMENA', 'MaREA', 'Cultural Heritage'],
		'fields': ["Country Type", "Cultural Period Type"]
	},
	'contributors': {
		'fields': ['Assessment Investigator - Actor', 'Disturbance Cause Assignment Assessor Name - Actor', 'Date Inference Making Actor Name'],
		'layout': {"name": None, "type": "DataCollector"},
		'default': [{'name': "University of Oxford", "type": "DataManager"},{'name': "University of Southampton", "type": "DataManager"}]
	},
	'dates': {
		'fields': ["Assessment Activity Date"]
	}
}
```
See https://developers.zenodo.org/#representation for a detailed description of Zenodo upload metadata. 

