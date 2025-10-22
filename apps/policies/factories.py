import factory
from apps.policies.models import InsurancePolicy
from django.utils import timezone
from datetime import timedelta
import random

PROVIDERS = ["Allianz", "Groupama", "Omniasig", "Generali", "AXA"]

class InsurancePolicyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InsurancePolicy

    car = factory.SubFactory("apps.cars.factories.CarFactory")
    provider = factory.LazyFunction(lambda: random.choice(PROVIDERS))
    start_date = factory.LazyFunction(lambda: timezone.now().date() - timedelta(days=random.randint(30, 180)))
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=365))
