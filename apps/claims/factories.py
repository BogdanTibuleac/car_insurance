import random
from datetime import timedelta

import factory
from django.utils import timezone
from faker import Faker

from apps.claims.models import Claim

# --- realistic mock data providers ---
fake = Faker()

PROVIDERS = ["Allianz", "Groupama", "Omniasig", "Generali", "AXA"]

CLAIM_DESCRIPTIONS = [
    "Windshield replacement after small impact",
    "Rear bumper repair following minor collision",
    "Engine diagnostic due to oil leak",
    "Tire puncture replacement",
    "Routine maintenance and oil change",
    "Front-end damage from parking accident",
]


class ClaimFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Claim

    car = factory.SubFactory("apps.cars.factories.CarFactory")
    claim_date = factory.LazyFunction(
        lambda: timezone.now().date() - timedelta(days=random.randint(0, 120))
    )
    description = factory.LazyFunction(lambda: random.choice(CLAIM_DESCRIPTIONS))
    amount = factory.LazyFunction(lambda: round(random.uniform(200, 10000), 2))
