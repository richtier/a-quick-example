# C2002 (redundant-default-args)
# C2003 (field-null-not-blank)
# C2004 (brittle-unique-for)
# C2005 (missing-related-name)

from django.db import models


class Group(models.Model):
    title = models.CharField(blank=False, max_length=255)


class PlatformUser(models.Model):
    group = models.OneToOneField(Group)
    changed = models.DateTimeField(null=True)
    slug = models.SlugField(_('slug'), unique_for_date='changed')
