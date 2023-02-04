# Generated by Django 2.2 on 2020-08-09 01:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='app',
            fields=[
                ('appid', models.AutoField(primary_key=True, serialize=False)),
                ('appname', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'app',
            },
        ),
        migrations.CreateModel(
            name='commit',
            fields=[
                ('commitpk', models.AutoField(primary_key=True, serialize=False)),
                ('commitid', models.CharField(max_length=45)),
                ('version', models.CharField(max_length=10)),
                ('committername', models.CharField(max_length=50)),
                ('committeremail', models.CharField(max_length=70)),
                ('tree', models.CharField(max_length=40)),
                ('parent', models.CharField(max_length=125)),
                ('message', models.CharField(max_length=400)),
                ('time', models.CharField(max_length=30)),
                ('timezone', models.CharField(max_length=7)),
                ('appid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.app')),
            ],
            options={
                'db_table': 'commit',
            },
        ),
        migrations.CreateModel(
            name='file',
            fields=[
                ('fileid', models.AutoField(primary_key=True, serialize=False)),
                ('filename', models.CharField(max_length=130)),
                ('appid', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainapp.app')),
            ],
            options={
                'db_table': 'file',
            },
        ),
        migrations.CreateModel(
            name='function',
            fields=[
                ('functionid', models.AutoField(primary_key=True, serialize=False)),
                ('functionname', models.CharField(max_length=100)),
                ('fileid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.file')),
            ],
            options={
                'db_table': 'function',
            },
        ),
        migrations.CreateModel(
            name='modifiedfunction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.CharField(max_length=30)),
                ('lines', models.CharField(max_length=400)),
                ('version', models.CharField(max_length=10)),
                ('functionscale', models.CharField(max_length=17)),
                ('functionerror', models.CharField(max_length=200)),
                ('appid', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='mainapp.app')),
                ('commitpk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.commit')),
                ('fileid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.file')),
                ('functionid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.function')),
            ],
            options={
                'db_table': 'modifiedfunction',
            },
        ),
    ]