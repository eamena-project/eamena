from eamena.bulk_uploader import BulkUploadSheet
import json, uuid, re, urllib.request, sys

class GeoarchaeologyBulkUploadSheet(BulkUploadSheet):

	def __prune(self, data):

		if isinstance(data, (list)):
			ret = []
			for item in data:
				newitem = self.__prune(item)
				if isinstance(newitem, (bool)):
					ret[key] = value
				else:
					if len(newitem) > 0:
						if newitem != 'x':
							ret.append(newitem)
			return ret
		if isinstance(data, (dict)):
			ret = {}
			for keyob in data.keys():
				key = str(keyob)
				value = self.__prune(data[key])
				if isinstance(value, (bool)):
					ret[key] = value
				else:
					if len(value) > 0:
						if value != 'x':
							ret[key] = value
			return ret
		return data

	def __parse_condition_assessment(self, index, uniqueid=''):

		exceptions = ['EFFECT_TYPE', 'EFFECT_CERTAINTY']
		if len(self._BulkUploadSheet__data[index]) == 1: # Support the old 'one item per line' style
			exceptions = []

		unparsed = self.pre_parse(index, ['OVERALL_CONDITION_STATE', 'DAMAGE_EXTENT_TYPE', 'DISTURBANCE_CAUSE_CATEGORY_TYPE', 'DISTURBANCE_CAUSE_TYPE', 'DISTURBANCE_CAUSE_CERTAINTY', 'DISTURBANCE_DATE_FROM', 'DISTURBANCE_DATE_TO', 'DISTURBANCE_DATE_OCCURRED_BEFORE', 'DISTURBANCE_DATE_OCCURRED_ON', 'DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME', 'EFFECT_TYPE', 'EFFECT_CERTAINTY', 'THREAT_CATEGORY', 'THREAT_TYPE', 'THREAT_PROBABILITY', 'THREAT_INFERENCE_MAKING_ASSESSOR_NAME', 'INTERVENTION_ACTIVITY_TYPE', 'RECOMMENDATION_TYPE', 'PRIORITY_TYPE', 'RELATED_DETAILED_CONDITION_RESOURCE'], exceptions)
		states = []
		types = []
		disturbances = []
		threats = []
		plans = []
		dcr = []

		for item in unparsed:

			rel_cr = ''
			overall_condition_state = item["OVERALL_CONDITION_STATE"].strip()
			damage_extent_type = item["DAMAGE_EXTENT_TYPE"].strip()
			if 'RELATED_DETAILED_CONDITION_RESOURCE' in item:
				rel_cr = item["RELATED_DETAILED_CONDITION_RESOURCE"].strip()

			if len(overall_condition_state) > 0:
				states.append(overall_condition_state)
			if len(damage_extent_type) > 0:
				types.append({"DAMAGE_EXTENT_TYPE": damage_extent_type})
			if len(rel_cr) > 0:
				dcr.append(rel_cr)

			dc_cat_type = item["DISTURBANCE_CAUSE_CATEGORY_TYPE"].strip()
			dc_type = item["DISTURBANCE_CAUSE_TYPE"].strip()
			dc_certainty = item["DISTURBANCE_CAUSE_CERTAINTY"].strip()
			d_date_from = item["DISTURBANCE_DATE_FROM"].strip()
			d_date_to = item["DISTURBANCE_DATE_TO"].strip()
			d_date_before = item["DISTURBANCE_DATE_OCCURRED_BEFORE"].strip()
			d_date_on = item["DISTURBANCE_DATE_OCCURRED_ON"].strip()
			dd_name = item["DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME"].strip()
			eff_type = item["EFFECT_TYPE"]
			eff_certainty = item["EFFECT_CERTAINTY"]
			t_cat = item["THREAT_CATEGORY"].strip()
			t_type = item["THREAT_TYPE"].strip()
			t_prob = item["THREAT_PROBABILITY"].strip()
			t_name = ''
			int_act_type = ''
			rec_type = ''
			priority = ''
			if 'THREAT_INFERENCE_MAKING_ASSESSOR_NAME' in item:
				t_name = item["THREAT_INFERENCE_MAKING_ASSESSOR_NAME"].strip()
			if 'INTERVENTION_ACTIVITY_TYPE' in item:
				int_act_type = item["INTERVENTION_ACTIVITY_TYPE"].strip()
			if 'RECOMMENDATION_TYPE' in item:
				rec_type = item["RECOMMENDATION_TYPE"].strip()
			if 'PRIORITY_TYPE' in item:
				priority = item["PRIORITY_TYPE"].strip()

			if ((len(eff_type) > 0) & (len(eff_certainty) > 0) & (len(dc_type) > 0) & (len(dc_certainty) > 0)):
				eff_types = eff_type.split('|')
				eff_certs = eff_certainty.split('|')
				if (len(eff_certs) != len(eff_types)):

					self.error(uniqueid, "Cannot map effect types to certainties.", "There should be the same number of each. Please check the Effect Type and Effect Certainty columns for stray pipe (|) characters and leading/trailing spaces.")

				else:

					if ((len(dc_type) > 0) & (len(dc_certainty) == 0)):
						self.error(uniqueid, "Invalid Disturbance Data", "Item contains a Disturbance Cause Type but no Disturbance Cause Type Certainty.")
					if ((len(dc_type) == 0) & (len(dc_certainty) > 0)):
						self.error(uniqueid, "Invalid Disturbance Data", "Item contains a Disturbance Cause Type Certainty but no Disturbance Cause Type.")

					dist = {"EFFECTS": []}

					dist["DISTURBANCE_CAUSE_ASSIGNMENT"] = {}
					dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DAMAGE_OBSERVATION"] = []
					if len(dc_cat_type) > 0:
						dist["DISTURBANCE_CAUSE_CATEGORY_TYPE"] = dc_cat_type
					if len(dc_type) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_CAUSE_TYPE"] = dc_type
					if len(dc_certainty) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_CAUSE_CERTAINTY"] = dc_certainty
					if len(d_date_from) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_DATE_FROM"] = d_date_from
					if len(d_date_to) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_DATE_TO"] = d_date_to
					if len(d_date_before) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_DATE_OCCURRED_BEFORE"] = d_date_before
					if len(d_date_on) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_DATE_OCCURRED_ON"] = d_date_on
					if len(dd_name) > 0:
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DISTURBANCE_CAUSE_ASSIGNMENT_ASSESSOR_NAME"] = dd_name

					for i in range(0, len(eff_types)):
						effect = {"EFFECT_TYPE": eff_types[i], "EFFECT_CERTAINTY": eff_certs[i]}
						dist["DISTURBANCE_CAUSE_ASSIGNMENT"]["DAMAGE_OBSERVATION"].append(effect)

					disturbances.append(dist)

			if ((len(t_type) > 0) & (len(t_prob) == 0)):
				self.error(uniqueid, "Invalid Threat Data", "Item contains a Threat Type '" + t_type + "' but no Threat Type Probability.")
			if ((len(t_type) == 0) & (len(t_prob) > 0)):
				self.error(uniqueid, "Invalid Threat Data", "Item contains a Threat Type Probability '" + t_prob + "' but no Threat Type.")
			if ((len(t_type) > 0) & (len(t_prob) > 0)):
				threat = {"THREAT_TYPE": t_type, "THREAT_PROBABILITY": t_prob}
				if len(t_cat) > 0:
					threat["THREAT_CATEGORY"] = t_cat
				if len(t_name) > 0:
					threat["THREAT_INFERENCE_MAKING_ASSESSOR_NAME"] = t_name
				threats.append(threat)

			rec = {}
			if len(int_act_type) > 0:
				rec["INTERVENTION_ACTIVITY_TYPE"] = int_act_type
			if len(rec_type) > 0:
				rec["RECOMMENDATION_TYPE"] = rec_type
			if len(priority) > 0:
				rec["PRIORITY_TYPE"] = priority
			if len(rec) > 0:
				plans.append(rec)

		return {"OVERALL_CONDITION_STATE": states, "ESTIMATED_DAMAGE_EXTENT": types, "DAMAGE_STATE": {"DISTURBANCE_EVENT": disturbances}, "THREATS": threats, "RECOMMENDATION_PLAN": plans, "RELATED_DETAILED_CONDITION_RESOURCE": dcr}

	def __parse_geoarchaeological_assessment(self, index, uniqueid=''):

		timespace = []
		feature_ass = {"FEATURE_LANDFORM_BELIEF": [], "FEATURE_SEDIMENT_BELIEF": [], "FEATURE_INTERPRETATION_BELIEF": []}
		general_date = {"MARINE_ISOTOPE_STAGES_BELIEF": {}, "QUATERNARY_DIVISIONS_BELIEF": {}}
		evidence = []
		certainty_obs = {}

		exceptions = []
		unparsed = self.pre_parse(index, ['OVERALL_GEOARCHAEOLOGICAL_CERTAINTY_VALUE', 'SOURCE_OF_EVIDENCE_TYPE', 'MARINE_ISOTOPE_STAGES', 'MARINE_ISOTOPE_STAGE_CERTAINTY', 'QUATERNARY_DIVISIONS', 'QUATERNARY_DATE_CERTAINTY', 'DATE_INFERENCE_MAKING_ACTOR', 'ARCHAEOLOGICAL_DATE_FROM', 'ARCHAEOLOGICAL_DATE_TO', 'BP_DATE_FROM', 'BP_DATE_TO', 'AH_DATE_FROM', 'AH_DATE_TO', 'SH_DATE_FROM', 'SH_DATE_TO', 'FEATURE_SEDIMENT_TYPE', 'FEATURE_SEDIMENT_TRANSITION', 'FEATURE_SEDIMENT_TYPE_CERTAINTY', 'FEATURE_LANDFORM_TYPE', 'SITE_LANDFORM_ARRANGEMENT_TYPE', 'SITE_LANDFORM_NUMBER_TYPE', 'FEATURE_LANDFORM_TYPE_CERTAINTY', 'FEATURE_INTERPRETATION_TYPE', 'FEATURE_INTERPRETATION_CERTAINTY', 'RELATED_GEOARCHAEOLOGY_RESOURCE'], exceptions)
		ret = {}
		for item in unparsed:

			if 'MARINE_ISOTOPE_STAGES' in item:
				if item['MARINE_ISOTOPE_STAGES'] != '':
					general_date['MARINE_ISOTOPE_STAGES_BELIEF']['MARINE_ISOTOPE_STAGES'] = item['MARINE_ISOTOPE_STAGES']
			if 'MARINE_ISOTOPE_STAGE_CERTAINTY' in item:
				if item['MARINE_ISOTOPE_STAGE_CERTAINTY'] != '':
					general_date['MARINE_ISOTOPE_STAGES_BELIEF']['MARINE_ISOTOPE_STAGE_CERTAINTY'] = item['MARINE_ISOTOPE_STAGE_CERTAINTY']
			if 'QUATERNARY_DIVISIONS' in item:
				if item['QUATERNARY_DIVISIONS'] != '':
					general_date['QUATERNARY_DIVISIONS_BELIEF']['QUATERNARY_DIVISIONS'] = item['QUATERNARY_DIVISIONS']
			if 'QUATERNARY_DATE_CERTAINTY' in item:
				if item['QUATERNARY_DATE_CERTAINTY'] != '':
					general_date['QUATERNARY_DIVISIONS_BELIEF']['QUATERNARY_DATE_CERTAINTY'] = item['QUATERNARY_DATE_CERTAINTY']

			ts = {"ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS": {}}
			if 'ARCHAEOLOGICAL_DATE_FROM' in item:
				if item['ARCHAEOLOGICAL_DATE_FROM'] != '':
					ts['ARCHAEOLOGICAL_DATE_FROM'] = item['ARCHAEOLOGICAL_DATE_FROM']
			if 'ARCHAEOLOGICAL_DATE_TO' in item:
				if item['ARCHAEOLOGICAL_DATE_TO'] != '':
					ts['ARCHAEOLOGICAL_DATE_TO'] = item['ARCHAEOLOGICAL_DATE_TO']
			if 'AH_DATE_FROM' in item:
				if item['AH_DATE_FROM'] != '':
					ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']['AH_DATE_FROM'] = item['AH_DATE_FROM']
			if 'AH_DATE_TO' in item:
				if item['AH_DATE_TO'] != '':
					ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']['AH_DATE_TO'] = item['AH_DATE_TO']
			if 'BP_DATE_FROM' in item:
				if item['BP_DATE_FROM'] != '':
					ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']['BP_DATE_FROM'] = item['BP_DATE_FROM']
			if 'BP_DATE_TO' in item:
				if item['BP_DATE_TO'] != '':
					ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']['BP_DATE_TO'] = item['BP_DATE_TO']
			if 'SH_DATE_FROM' in item:
				if item['SH_DATE_FROM'] != '':
					ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']['SH_DATE_FROM'] = item['SH_DATE_FROM']
			if 'SH_DATE_TO' in item:
				if item['SH_DATE_TO'] != '':
					ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']['SH_DATE_TO'] = item['SH_DATE_TO']
			if ((len(ts) > 1) or (len(ts['ALTERNATIVE_TEMPORAL_REFERENCE_SYSTEMS']) > 0)):
				timespace.append(ts)

			landform = {}
			if 'FEATURE_LANDFORM_TYPE' in item:
				landform['FEATURE_LANDFORM_TYPE'] = item['FEATURE_LANDFORM_TYPE']
			if 'FEATURE_LANDFORM_TYPE_CERTAINTY' in item:
				landform['FEATURE_LANDFORM_TYPE_CERTAINTY'] = item['FEATURE_LANDFORM_TYPE_CERTAINTY']
			if 'SITE_LANDFORM_ARRANGEMENT_TYPE' in item:
				landform['SITE_LANDFORM_ARRANGEMENT_TYPE'] = item['SITE_LANDFORM_ARRANGEMENT_TYPE']
			if 'SITE_LANDFORM_NUMBER_TYPE' in item:
				landform['SITE_LANDFORM_NUMBER_TYPE'] = item['SITE_LANDFORM_NUMBER_TYPE']
			if len(landform) > 0:
				feature_ass['FEATURE_LANDFORM_BELIEF'].append(landform)

			sediment = {}
			if 'FEATURE_SEDIMENT_TYPE' in item:
				sediment['FEATURE_SEDIMENT_TYPE'] = item['FEATURE_SEDIMENT_TYPE']
			if 'FEATURE_SEDIMENT_TRANSITION' in item:
				sediment['FEATURE_SEDIMENT_TRANSITION'] = item['FEATURE_SEDIMENT_TRANSITION']
			if 'FEATURE_SEDIMENT_TYPE_CERTAINTY' in item:
				sediment['FEATURE_SEDIMENT_TYPE_CERTAINTY'] = item['FEATURE_SEDIMENT_TYPE_CERTAINTY']
			if len(sediment) > 0:
				feature_ass['FEATURE_SEDIMENT_BELIEF'].append(sediment)

			if 'RELATED_GEOARCHAEOLOGY_RESOURCE' in item:
				if item['RELATED_GEOARCHAEOLOGY_RESOURCE'] != '':
					feature_ass['RELATED_GEOARCHAEOLOGY_RESOURCE'] = item['RELATED_GEOARCHAEOLOGY_RESOURCE']

			int_belief = {}
			if 'FEATURE_INTERPRETATION_TYPE' in item:
				int_belief['FEATURE_INTERPRETATION_TYPE'] = item['FEATURE_INTERPRETATION_TYPE']
			if 'FEATURE_INTERPRETATION_CERTAINTY' in item:
				int_belief['FEATURE_INTERPRETATION_CERTAINTY'] = item['FEATURE_INTERPRETATION_CERTAINTY']
			if 'RELATED_HERITAGE_PLACE' in item:
				if item['RELATED_HERITAGE_PLACE'] != '':
					ret['RELATED_HERITAGE_PLACE'] = item['RELATED_HERITAGE_PLACE']
			if len(int_belief) > 0:
				feature_ass["FEATURE_INTERPRETATION_BELIEF"].append(int_belief)

			ev = {}
			if 'SOURCE_OF_EVIDENCE_TYPE' in item:
				ev['SOURCE_OF_EVIDENCE_TYPE'] = item['SOURCE_OF_EVIDENCE_TYPE']
			if 'RELATED_INFORMATION_RESOURCE' in item:
				ev['RELATED_INFORMATION_RESOURCE'] = item['RELATED_INFORMATION_RESOURCE']
			if len(ev) > 0:
				evidence.append(ev)

			if 'OVERALL_GEOARCHAEOLOGICAL_CERTAINTY_VALUE' in item:
				certainty_obs['OVERALL_GEOARCHAEOLOGICAL_CERTAINTY_VALUE'] = item['OVERALL_GEOARCHAEOLOGICAL_CERTAINTY_VALUE']

		ret['GEOARCHAEOLOGY_FEATURE_ASSESSMENT'] = feature_ass
		ret['GENERAL_DATE'] = general_date
		if len(timespace) > 0:
			ret['GEOARCHAEOLOGICAL_TIMESPACE'] = timespace
		if len(evidence) > 0:
			ret['SOURCE_OF_EVIDENCE'] = evidence
		if len(certainty_obs) > 0:
			ret['GEOARCHAEOLOGY_CERTAINTY_OBSERVATION'] = certainty_obs
		return ret

	def __parse_environment_assessment(self, index, uniqueid=''):

		topography_type = []
		land_cover = []
		bedrock_geology = []
		surficial_geology = []
		marine_environment = []
		depth_elevation = []

		unparsed = self.pre_parse(index, ['TOPOGRAPHY_TYPE', 'LAND_COVER_TYPE', 'LAND_COVER_ASSESSMENT_DATE', 'SURFICIAL_GEOLOGY_TYPE', 'DEPOSITIONAL_PROCESS', 'BEDROCK_GEOLOGY', 'FETCH_TYPE', 'WAVE_CLIMATE', 'TIDAL_ENERGY', 'MINIMUM_DEPTH_MAX_ELEVATION_M_', 'MAXIMUM_DEPTH_MIN_ELEVATION_M_', 'DATUM_TYPE', 'DATUM_DESCRIPTION_EPSG_CODE'])

		for item in unparsed:

			top_type = item["TOPOGRAPHY_TYPE"].strip()
			bedrock_geo = item["BEDROCK_GEOLOGY"].strip()

			if len(top_type) > 0:
				topography_type.append(top_type)
			if len(bedrock_geo) > 0:
				bedrock_geology.append({"BEDROCK_GEOLOGY_TYPE": bedrock_geo})

			lc_type = item["LAND_COVER_TYPE"].strip()
			lc_ass_date = item["LAND_COVER_ASSESSMENT_DATE"].strip()
			lc = {}
			if (len(lc_type) > 0):
				lc['LAND_COVER_TYPE'] = lc_type
			if (len(lc_ass_date) > 0):
				lc['LAND_COVER_ASSESSMENT_DATE'] = lc_ass_date
			if len(lc) > 0:
				land_cover.append(lc)

			s_geo_type = item["SURFICIAL_GEOLOGY_TYPE"].strip()
			dep_proc = item["DEPOSITIONAL_PROCESS"].strip()
			s_geo = {}
			if (len(s_geo_type) > 0):
				s_geo['SURFICIAL_GEOLOGY_TYPE'] = s_geo_type
			if (len(dep_proc) > 0):
				s_geo['DEPOSITIONAL_PROCESS'] = dep_proc
			if len(s_geo) > 0:
				surficial_geology.append(s_geo)

			fetch_type = item["FETCH_TYPE"].strip()
			wave_climate = item["WAVE_CLIMATE"].strip()
			tidal_energy = item["TIDAL_ENERGY"].strip()
			marine_env = {}
			if (len(fetch_type) > 0):
				marine_env['FETCH_TYPE'] = fetch_type
			if (len(wave_climate) > 0):
				marine_env['WAVE_CLIMATE'] = wave_climate
			if (len(tidal_energy) > 0):
				marine_env['TIDAL_ENERGY'] = tidal_energy
			if (len(marine_env) > 0):
				marine_environment.append(marine_env)

			min_depth = item["MINIMUM_DEPTH_MAX_ELEVATION_M_"].strip()
			max_depth = item["MAXIMUM_DEPTH_MIN_ELEVATION_M_"].strip()
			datum_type = item["DATUM_TYPE"].strip()
			epsg_code = item["DATUM_DESCRIPTION_EPSG_CODE"].strip()
			depth_elev = {}
			if len(min_depth) > 0:
				depth_elev["MINIMUM_DEPTH_MAX_ELEVATION_M_"] = min_depth
			if len(max_depth) > 0:
				depth_elev["MAXIMUM_DEPTH_MIN_ELEVATION_M_"] = max_depth
			if len(datum_type) > 0:
				depth_elev["DATUM_TYPE"] = datum_type
			if len(epsg_code) > 0:
				depth_elev["DATUM_DESCRIPTION_EPSG_CODE"] = epsg_code
			if len(depth_elev):
				depth_elevation.append(depth_elev)

			topography = []
			for t in topography_type:
				topography.append({"TOPOGRAPHY_TYPE": t})

		return {"TOPOGRAPHY": topography, "LAND_COVER": land_cover, "GEOLOGY": {"BEDROCK_GEOLOGY": bedrock_geology, "SURFICIAL_GEOLOGY": surficial_geology}, "MARINE_ENVIRONMENT": marine_environment, "DEPTH_ELEVATION": depth_elevation}

	def __parse_geography(self, index, uniqueid=''):

		unparsed = self.pre_parse(index, ['SITE_OVERALL_SHAPE_TYPE', 'GRID_ID', 'COUNTRY_TYPE', 'CADASTRAL_REFERENCE', 'RESOURCE_ORIENTATION', 'ADDRESS', 'ADDRESS_TYPE', 'ADMINISTRATIVE_SUBDIVISION', 'ADMINISTRATIVE_SUBDIVISION_TYPE'])
		ret = {}

		address = []
		subdiv = []

		for item in unparsed:

			geog_sost = item["SITE_OVERALL_SHAPE_TYPE"].strip()
			geog_gid = item["GRID_ID"].strip()
			geog_ct = item["COUNTRY_TYPE"].strip()
			geog_cr = item["CADASTRAL_REFERENCE"].strip()
			geog_ro = item["RESOURCE_ORIENTATION"].strip()

			addr = {"ADDRESS": item['ADDRESS'].strip(), "ADDRESS_TYPE": item['ADDRESS_TYPE'].strip()}
			if len(addr['ADDRESS']) > 0:
				address.append(addr)

			sd = {"ADMINISTRATIVE_SUBDIVISION": item['ADMINISTRATIVE_SUBDIVISION'].strip(), "ADMINISTRATIVE_SUBDIVISION_TYPE": item['ADMINISTRATIVE_SUBDIVISION_TYPE'].strip()}
			if len(sd['ADMINISTRATIVE_SUBDIVISION']) > 0:
				subdiv.append(sd)

			if geog_sost != '':
				ret['SITE_OVERALL_SHAPE_TYPE'] = geog_sost
			if geog_gid != '':
				ret['GRID_ID'] = geog_gid
			if geog_ct != '':
				ret['COUNTRY_TYPE'] = geog_ct
			if geog_cr != '':
				ret['CADASTRAL_REFERENCE'] = geog_cr
			if geog_ro != '':
				ret['RESOURCE_ORIENTATION'] = geog_ro

		ret['ADDRESS'] = address
		ret['ADMINISTRATIVE_SUBDIVISION'] = subdiv

		return ret


	def __parse_geometries(self, index, uniqueid=''):

		unparsed = self.pre_parse(index, ['GEOMETRIC_PLACE_EXPRESSION', 'GEOMETRY_QUALIFIER', 'LOCATION_CERTAINTY', 'SITE_LOCATION_CERTAINTY', 'GEOMETRY_EXTENT_CERTAINTY'])
		ret = []

		for item in unparsed:

			if not('SITE_LOCATION_CERTAINTY' in item):
				item['SITE_LOCATION_CERTAINTY'] = ''
			if item["SITE_LOCATION_CERTAINTY"].strip() == '':
				item["SITE_LOCATION_CERTAINTY"] = item["LOCATION_CERTAINTY"]

			if item["GEOMETRIC_PLACE_EXPRESSION"].strip() == '':
				continue
			if item["SITE_LOCATION_CERTAINTY"].strip() == '':
				self.error(uniqueid, "Missing Location Certainty", "Record cannot have a geometry without a location certainty.")
				continue
			if item["GEOMETRY_EXTENT_CERTAINTY"].strip() == '':
				self.error(uniqueid, "Missing Extent Certainty", "Record cannot have a geometry without an extent certainty.")
				continue

			geom = {}
			geom["GEOMETRIC_PLACE_EXPRESSION"] = item["GEOMETRIC_PLACE_EXPRESSION"].strip()
			geom["SITE_LOCATION_CERTAINTY"] = item["SITE_LOCATION_CERTAINTY"].strip()
			geom["GEOMETRY_EXTENT_CERTAINTY"] = item["GEOMETRY_EXTENT_CERTAINTY"].strip()
			if item["GEOMETRY_QUALIFIER"].strip() != '':
				geom["GEOMETRY_QUALIFIER"] = item["GEOMETRY_QUALIFIER"].strip()
			ret.append(geom)

		return ret


	def __parse_resource_summary(self, index, uniqueid=''):

		unparsed = self.pre_parse(index, ['RESOURCE_NAME', 'NAME_TYPE', 'HERITAGE_PLACE_TYPE', 'GENERAL_DESCRIPTION_TYPE', 'GENERAL_DESCRIPTION', 'HERITAGE_PLACE_FUNCTION', 'HERITAGE_PLACE_FUNCTION_CERTAINTY', 'DESIGNATION', 'DESIGNATION_FROM_DATE', 'DESIGNATION_TO_DATE'])

		rs_type = []
		rs_resource_name = []
		rs_resource_desc = []
		rs_resource_class = []
		rs_resource_designation = []

		for item in unparsed:

			type = item["HERITAGE_PLACE_TYPE"].strip()
			name = item["RESOURCE_NAME"].strip()
			desc = item["GENERAL_DESCRIPTION"].strip()
			func = item["HERITAGE_PLACE_FUNCTION"].strip()
			desg = item["DESIGNATION"].strip()

			if len(type) > 0:
				rs_type.append(type)
			if len(name) > 0:
				value = {}
				value["RESOURCE_NAME"] = name
				if len(item["NAME_TYPE"].strip()) > 0:
					value["NAME_TYPE"] = item["NAME_TYPE"]
				rs_resource_name.append(value)
			if len(desc) > 0:
				value = {}
				value["GENERAL_DESCRIPTION"] = desc
				if len(item["GENERAL_DESCRIPTION_TYPE"].strip()) > 0:
					value["GENERAL_DESCRIPTION_TYPE"] = item["GENERAL_DESCRIPTION_TYPE"]
				rs_resource_desc.append(value)
			if len(func) > 0:
				value = {}
				value["HERITAGE_PLACE_FUNCTION"] = func
				if len(item["HERITAGE_PLACE_FUNCTION_CERTAINTY"].strip()) > 0:
					value["HERITAGE_PLACE_FUNCTION_CERTAINTY"] = item["HERITAGE_PLACE_FUNCTION_CERTAINTY"]
				else:
					self.error(uniqueid, "Heritage Place Function Certainty missing", "The entry contains a Heritage Place Function, but not a Heritage Place Function Certainty.")
				rs_resource_class.append(value)
			else:
				if len(item["HERITAGE_PLACE_FUNCTION_CERTAINTY"].strip()) > 0:
					self.error(uniqueid, "Heritage Place Function missing", "The entry contains a Heritage Place Function Certainty, but not a Heritage Place Function.")
			if len(desg) > 0:
				value = {}
				value["DESIGNATION"] = desg
				if len(item["DESIGNATION_FROM_DATE"].strip()) > 0:
					value["DESIGNATION_FROM_DATE"] = item["DESIGNATION_FROM_DATE"]
				if len(item["DESIGNATION_TO_DATE"].strip()) > 0:
					value["DESIGNATION_TO_DATE"] = item["DESIGNATION_TO_DATE"]
				rs_resource_designation.append(value)

		return{"RESOURCE_NAME": rs_resource_name,"HERITAGE_PLACE_TYPE": rs_type,"DESCRIPTION_ASSIGNMENT": rs_resource_desc,"HERITAGE_PLACE_ASSIGNMENT": rs_resource_class,"DESIGNATION": rs_resource_designation}

	def __parse_assessment_summary(self, index, uniqueid=''):

		unparsed = self.pre_parse(index, ['ASSESSMENT_INVESTIGATOR___ACTOR','INVESTIGATOR_ROLE_TYPE','ASSESSMENT_ACTIVITY_TYPE','ASSESSMENT_ACTIVITY_DATE','GE_ASSESSMENT_YES_NO_','GE_IMAGERY_ACQUISITION_DATE','INFORMATION_RESOURCE','INFORMATION_RESOURCE_USED','INFORMATION_RESOURCE_ACQUISITION_DATE'])
		activity_data = []
		activity = {}
		actor = ''
		role = ''
		for item in unparsed:

			if 'ASSESSMENT_INVESTIGATOR___ACTOR' in item:
				if len(item['ASSESSMENT_INVESTIGATOR___ACTOR']) > 0:
					actor = item['ASSESSMENT_INVESTIGATOR___ACTOR']
			if 'INVESTIGATOR_ROLE_TYPE' in item:
				if len(item['INVESTIGATOR_ROLE_TYPE']) > 0:
					role = item['INVESTIGATOR_ROLE_TYPE']

			act_type = item['ASSESSMENT_ACTIVITY_TYPE'].strip()
			act_date = item['ASSESSMENT_ACTIVITY_DATE'].strip()
			act_ge = 'No'
			if 'GE_ASSESSMENT_YES_NO_' in item:
				act_ge = item['GE_ASSESSMENT_YES_NO_'].strip()
			if 'GE_ASSESSMENT_YES_NO' in item:
				act_ge = item['GE_ASSESSMENT_YES_NO'].strip()
			if act_type != '':
				if len(activity) > 0:
					activity_data.append(activity)
				activity = {"GE_IMAGERY_ACQUISITION_DATE": [], "INFORMATION_RESOURCE_USED": []}
			if act_type != '':
				activity["ASSESSMENT_ACTIVITY_TYPE"] = act_type
			if act_date != '':
				activity["ASSESSMENT_ACTIVITY_DATE"] = act_date
			if act_ge != '':
				activity["GE_ASSESSMENT_YES_NO_"] = self.__boolean_cast(act_ge)

			act_ge_date = ''
			if 'GE_IMAGERY_ACQUISITION_DATE' in item:
				act_ge_date = item['GE_IMAGERY_ACQUISITION_DATE'].strip()
			act_infores = ''
			if 'INFORMATION_RESOURCE' in item:
				if item['INFORMATION_RESOURCE'] != '':
					act_infores = item['INFORMATION_RESOURCE'].strip()
			if 'INFORMATION_RESOURCE_USED' in item:
				if item['INFORMATION_RESOURCE_USED'] != '':
					act_infores = item['INFORMATION_RESOURCE_USED'].strip()
			act_infores_date = ''
			if 'INFORMATION_RESOURCE_ACQUISITION_DATE' in item:
				act_infores_date = item['INFORMATION_RESOURCE_ACQUISITION_DATE'].strip()

			if len(act_ge_date) > 0:
				if not('GE_IMAGERY_ACQUISITION_DATE' in activity):
					activity['GE_IMAGERY_ACQUISITION_DATE'] = []
				activity['GE_IMAGERY_ACQUISITION_DATE'].append(act_ge_date)
			if len(act_infores) > 0:
				infores = {"INFORMATION_RESOURCE_USED": act_infores}
				if len(act_infores_date) > 0:
					infores['INFORMATION_RESOURCE_ACQUISITION_DATE'] = act_infores_date
				if not('INFORMATION_RESOURCE_USED' in activity):
					activity['INFORMATION_RESOURCE_USED'] = []
				activity['INFORMATION_RESOURCE_USED'].append(infores)
			if len(actor) > 0:
				activity['ASSESSMENT_INVESTIGATOR___ACTOR'] = actor
			if len(role) > 0:
				activity['INVESTIGATOR_ROLE_TYPE'] = role

		if len(activity) > 0:
			activity_data.append(activity)

		return activity_data

	def __parse_access(self, index, uniqueid=''):

		unparsed = self.pre_parse(index, ['RESTRICTED_ACCESS_RECORD_DESIGNATION'])
		return {"RESTRICTED_ACCESS_RECORD_DESIGNATION": self.__boolean_cast(unparsed[0]["RESTRICTED_ACCESS_RECORD_DESIGNATION"])}

	def __parse_uid(self, index):

		unparsed = self.pre_parse(index, ['UNIQUEID'])
		if len(unparsed) == 0:
			return ''
		if not('UNIQUEID' in unparsed[0]):
			return ''
		return unparsed[0]["UNIQUEID"]

	def data(self, index):

		uid = self.__parse_uid(index)

		assessment_summary = self.__parse_assessment_summary(index, uid)
		resource_summary = self.__parse_resource_summary(index, uid)
		geometries = self.__parse_geometries(index, uid)
		geography = self.__parse_geography(index, uid)
		geo_assessment = self.__parse_geoarchaeological_assessment(index, uid)
		cond_assessment = self.__parse_condition_assessment(index, uid)
		env_assessment = self.__parse_environment_assessment(index, uid)
		access = self.__parse_access(index, uid)

		ret = {}
		ret["_"] = uid
		ret["ASSESSMENT_SUMMARY"] = assessment_summary
		ret["RESOURCE_SUMMARY"] = resource_summary
		ret["GEOMETRIES"] = geometries
		ret["GEOGRAPHY"] = geography
		ret["GEOARCHAEOLOGY_ASSESSMENT"] = geo_assessment
		ret["CONDITION_ASSESSMENT"] = cond_assessment
		ret["ENVIRONMENT_ASSESSMENT"] = env_assessment
		#ret["ACCESS"] = access

		return self.__prune(ret)

	def __boolean_cast(self, text):
		t = str(text).lower()
		if t == 'yes':
			return True
		if t == '1':
			return True
		if t == 'true':
			return True
		if t == 'y':
			return True
		return False

	def __init__(self, filename, uidkey='UNIQUEID'):

		super().__init__(filename, uidkey)
		self.__required_fields = ["UNIQUEID"]
		self.__errors = []
		for i in range(0, len(self._BulkUploadSheet__data)):
			for row in range(0, len(self._BulkUploadSheet__data[i])):
				for field in self.__required_fields:
					if field in self._BulkUploadSheet__data[i][row]:
						continue
					self._BulkUploadSheet__data[i][row][field] = ''
