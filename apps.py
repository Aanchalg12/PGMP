from django.apps import AppConfig


class SolarEstimatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solar_estimator'

    def ready(self):
        import solar_estimator.signals

class SolarEsimatorConfig(AppConfig):
    name = 'your_app_name'

    def ready(self):
        import solar_estimator.signals