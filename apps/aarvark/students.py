# C2008 (deprecated-nullboolean-field)
# C2011 (non-unique-primary)
from django.db import models


class StudentPerformance(models.Model):
    stident_id = models.CharField(max_length=100, primary_key=True, unique=False)
    registration_id = models.CharField(max_length=10, db_index=True)
    academic_year = models.IntegerField()
    acronym = models.CharField(max_length=15)
    update_date = models.DateTimeField()
    creation_date = models.DateTimeField()
    authorized = models.BooleanField(default=True)
    courses_registration_validated = models.NullBooleanField(null=True)
