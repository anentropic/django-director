from functools import wraps

from django.contrib import admin
from django.shortcuts import render_to_response

from .job import run_job
from .models import Job, Artefact


class ArtefactInline(admin.TabularInline):
    model = Artefact


class JobAdmin(admin.ModelAdmin):
    class Meta:
        model = Job

    inlines = [
        ArtefactInline,
    ]

    list_display = ('command', 'command_args', 'command_kwargs', 'status')


admin.site.register(Job, JobAdmin)


def action_factory(action):
    """
    Converts your existing admin action into a Director background action

    Example:

        background_action = action_factory(download_as_csv)
        admin.site.add_action(background_action, 'download_as_csv')
    """
    @wraps(action)
    def proxy_action(*args, **kwargs):
        job = run_job(f=action, *args, **kwargs)
        return render_to_response(
            'director/admin_job_action.html',
            {
                'job': job,
                'opts': job._meta,
            }
        )
    return proxy_action
