# Generated by Django 3.2.9 on 2021-12-05 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("heroes", "0002_prefix_hashed_key"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hero",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
