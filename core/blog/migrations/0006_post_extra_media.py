from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0005_category_name_ci_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image_2',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='post',
            name='image_3',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='post',
            name='extra_content',
            field=models.TextField(blank=True),
        ),
    ]
