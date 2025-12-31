from django.db import migrations, models


def copy_category_to_categories(apps, schema_editor):
    Post = apps.get_model('blog', 'Post')
    for post in Post.objects.exclude(category__isnull=True):
        post.categories.add(post.category)


class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0003_post_counted_view'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='posts', to='blog.category'),
        ),
        migrations.RunPython(copy_category_to_categories, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='post',
            name='category',
        ),
    ]
