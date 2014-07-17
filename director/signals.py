import django.dispatch


"""
Use the job function you're executing as the `sender`
(though we don't use it currently)
"""
new_artefact = django.dispatch.Signal(providing_args=['file', 'name'])
