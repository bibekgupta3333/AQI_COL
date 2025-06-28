from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_alter_weatherdata_unique_together_and_more"),
    ]

    operations = [
        migrations.DeleteModel(
            name="whole_dataset",
        ),
    ]
