# Generated by Django 2.1.7 on 2019-03-16 17:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('flexchain', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prediction_date', models.DateTimeField(auto_now_add=True)),
                ('prediction', models.BigIntegerField(help_text='Forecasted demand')),
                ('product', models.ForeignKey(db_column='product_sku', on_delete=django.db.models.deletion.CASCADE,
                                              to='flexchain.Product')),
            ],
            options={
                'db_table': 'forecast',
            },
        ),
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
