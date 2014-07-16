from django.contrib import admin

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

    def status(self, obj):
        if obj.exit_code is None:
            return 'Processing...'
        elif obj.exit_code == 0:
            return 'Finished successfully'
        else:
            return 'Error'


admin.site.register(Job, JobAdmin)
