# Generated by Django 4.1.4 on 2022-12-30 02:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_auction_image_alter_comments_subcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='auction',
            name='closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='auction',
            name='won_auctions',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]