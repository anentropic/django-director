from django.db import models
from jsonfield import JSONField


class Job(models.Model):
    command = models.CharField(max_length=255)
    command_args = JSONField(default=[])
    command_kwargs = JSONField(default={})

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    stdout = models.TextField(null=True, blank=True)
    stderr = models.TextField(null=True, blank=True)
    exit_code = models.SmallIntegerField(null=True, blank=True)


class Artefact(models.Model):
    job = models.ForeignKey('Job', related_name='artefacts')
    name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField()
