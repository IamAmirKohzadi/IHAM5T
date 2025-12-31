from django.db import migrations, models
from django.db.models.functions import Lower


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0004_post_categories_m2m'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(Lower('name'), name='category_name_ci_unique'),
        ),
    ]
