import django.dispatch


"""
Provide the parent Job instance as the `sender`
"""
new_artefact = django.dispatch.Signal(providing_args=['file', 'name'])
