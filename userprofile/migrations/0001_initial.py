# Generated by Django 5.1.1 on 2024-10-22 17:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('courseEnroll', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_id', models.CharField(max_length=9)),
                ('Name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone_no', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='DepartmentInfo',
            fields=[
                ('department_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('Department', models.CharField(choices=[('CSE', 'CSE'), ('CE', 'CE'), ('MOT', 'MOT')])),
            ],
        ),
        migrations.CreateModel(
            name='FacultyInfo',
            fields=[
                ('faculty_id', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('Phone_no', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='StudentInfo',
            fields=[
                ('N_id', models.CharField(max_length=9, primary_key=True, serialize=False)),
                ('Name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
                ('Education_Level', models.CharField(choices=[('Undergraduate', 'Undergraduate'), ('Graduate', 'Graduate'), ('PHD', 'PHD')], max_length=50)),
                ('Phone_no', models.CharField(max_length=15)),
                ('School', models.CharField(choices=[('Tandon', 'Tandon'), ('Stern', 'Stern'), ('Tisch', 'Tisch'), ('Gallatin', 'Gallatin')], max_length=50)),
                ('is_ta', models.BooleanField(default=False)),
                ('advisor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='advising_students', to='userprofile.admininfo')),
                ('course_enrolled', models.ManyToManyField(related_name='enrolled_students', to='courseEnroll.courseinfo')),
                ('ta_course', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tas', to='courseEnroll.courseinfo')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courseEnroll.courseinfo')),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='userprofile.facultyinfo')),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='userprofile.studentinfo')),
            ],
            options={
                'unique_together': {('student', 'course')},
            },
        ),
        migrations.AddField(
            model_name='facultyinfo',
            name='ta_students',
            field=models.ManyToManyField(related_name='faculty_tas', through='userprofile.TA', to='userprofile.studentinfo'),
        ),
    ]
