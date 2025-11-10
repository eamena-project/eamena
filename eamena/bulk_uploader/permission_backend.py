from arches.app.utils.permission_backend import PermissionBackend as ArchesPermissionBackend

# The whole point of this file is to override the Arches permission model in order to ensure
# all users in the Resource Editor group can see the bulk uploader. There is almost certainly
# a less hacky way of doing this.

class PermissionBackend(ArchesPermissionBackend):

	def has_perm(self, user_obj, perm, obj=None):
		if user_obj.groups.filter(name='Resource Editor').count() > 0:
			if perm == 'view_plugin':
				return True
		return super().has_perm(user_obj, perm, obj)
