from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    forward = "INSERT INTO plugins (pluginid, name, icon, component, componentname, config, slug, sortorder) VALUES ('9bb5db91-9527-49fb-9299-9621eea2742d', '{\"en\": \"Curator\"}', 'fa fa-pencil', 'views/components/plugins/curator', 'curator', '{\"show\": true, \"is_workflow\": false, \"description\": \"\"}', 'curator', '1' );"

    reverse = "DELETE FROM plugins where pluginid = '9bb5db91-9527-49fb-9299-9621eea2742d';"

    operations = [
        migrations.RunSQL(forward, reverse),
    ]
