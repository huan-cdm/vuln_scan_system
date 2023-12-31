# Generated by Django 2.1.5 on 2021-08-10 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Leakage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(default='', max_length=256, null=True)),
                ('sha', models.CharField(max_length=40, null=True)),
                ('fragment', models.TextField(default='')),
                ('html_url', models.CharField(max_length=512, null=True)),
                ('last_modified', models.DateTimeField(null=True)),
                ('file_name', models.CharField(max_length=512, null=True)),
                ('repo_name', models.CharField(max_length=512, null=True)),
                ('repo_url', models.CharField(max_length=512, null=True)),
                ('user_avatar', models.CharField(max_length=256, null=True)),
                ('user_name', models.CharField(max_length=256, null=True)),
                ('user_url', models.CharField(max_length=256, null=True)),
                ('status', models.IntegerField(choices=[(0, '未处理'), (1, '已处理'), (2, '白名单')], default=0)),
                ('add_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('add_time',),
                'db_table': 'Leakage',
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='任务名')),
                ('keywords', models.TextField(verbose_name='关键词')),
                ('match_method', models.IntegerField(choices=[(0, '模糊匹配'), (1, '精确匹配'), (2, '单词匹配')], default=0)),
                ('pages', models.IntegerField(default=5, verbose_name='爬取页数')),
                ('interval', models.IntegerField(default=60, verbose_name='爬取间隔(分钟)')),
                ('ignore_org', models.TextField(default='', null=True, verbose_name='忽略指定组织或账号下的代码')),
                ('ignore_repo', models.TextField(default='', null=True, verbose_name='忽略某类仓库下的代码, 如 github.io')),
                ('status', models.IntegerField(choices=[(0, '等待中'), (1, '运行中'), (2, '完成')], default=0)),
                ('start_time', models.DateTimeField(null=True)),
                ('finished_time', models.DateTimeField(null=True)),
                ('mail', models.TextField(default='', null=True, verbose_name='通知邮箱列表')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name='leakage',
            name='task',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='monitor.Task'),
        ),
    ]
