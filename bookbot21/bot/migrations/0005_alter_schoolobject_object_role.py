# Generated by Django 4.1 on 2022-08-17 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_schoolobject_object_role_user_bot_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schoolobject',
            name='object_role',
            field=models.ManyToManyField(related_name='school_objects', to='bot.role'),
        ),
    ]
