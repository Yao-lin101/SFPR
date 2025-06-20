# Generated by Django 5.1.6 on 2025-06-19 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sfpr", "0002_alter_partner_server_partner_server_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="partner",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "待审核"),
                    ("approved", "已发布"),
                    ("rejected", "已拒绝"),
                ],
                default="approved",
                max_length=20,
                verbose_name="状态",
            ),
        ),
    ]
