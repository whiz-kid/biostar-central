from django.apps import AppConfig

class Biostar4(AppConfig):
    name = 'biostar4.forum'
    verbose_name = "Biostar Q&A Forum"

    def ready(self):
        from . import signals

