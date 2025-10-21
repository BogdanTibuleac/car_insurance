from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"          # this must match your folder path

    def ready(self):
        """
        Called automatically when Django starts.
        Use this hook to start the background scheduler.
        """
        from django.conf import settings

        if getattr(settings, "SCHEDULER_ENABLED", False):
            from core.scheduler import start_scheduler
            start_scheduler()
