from arches.app.models import models

def find_bad_recommendation_plans():

	rec_plan_id = '34cfe9d4-c2c0-11ea-9026-02e7594ce0a0'
	pks = []
	for tile in models.TileModel.objects.filter(nodegroup_id=rec_plan_id):
		if models.TileModel.objects.filter(parenttile=tile).count() > 0:
			continue
		pks.append(tile.pk)
	return models.TileModel.objects.filter(pk__in=pks)

def fix_recommendation_plan(plan_tile):

	int_act_type_id = '34cfea0a-c2c0-11ea-9026-02e7594ce0a0'
	rec_type_id = '34cfea64-c2c0-11ea-9026-02e7594ce0a0'
	pri_ass_id = '34cfe9d7-c2c0-11ea-9026-02e7594ce0a0'
	pri_type_id = '34cfea84-c2c0-11ea-9026-02e7594ce0a0'

	if models.TileModel.objects.filter(parenttile=plan_tile).count() > 0:
		return None # The tile already has sub-tiles

	data = plan_tile.data
	if len(data) == 0:
		return None # The tile has no bad data associated with it

	check_list = [int_act_type_id, rec_type_id, pri_type_id]
	for kk in data.keys():
		k = str(kk)
		if k not in check_list:
			return None # The tile's data contains extra data with which we don't know what to do.

	if pri_type_id in data:
		new_tile = models.TileModel(resourceinstance=plan_tile.resourceinstance, nodegroup_id=pri_ass_id, parenttile=plan_tile)
		new_data = {pri_type_id: data[pri_type_id]}
		new_tile.data = new_data
		new_tile.save()
	if int_act_type_id in data:
		new_tile = models.TileModel(resourceinstance=plan_tile.resourceinstance, nodegroup_id=int_act_type_id, parenttile=plan_tile)
		new_data = {int_act_type_id: data[int_act_type_id]}
		if rec_type_id in data:
			new_data[rec_type_id] = data[rec_type_id]
		new_tile.data = new_data
		new_tile.save()

	return plan_tile
