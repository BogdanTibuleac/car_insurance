import random

import factory
from django.contrib.auth.models import User
from faker import Faker

from apps.cars.models import Car

MAKES_MODELS = {
    "BMW": ["X5", "X3", "320i"],
    "Volkswagen": ["Golf", "Passat", "Tiguan"],
    "Audi": ["A4", "A6", "Q5"],
    "Skoda": ["Octavia", "Fabia", "Superb"],
    "Toyota": ["Corolla", "Yaris", "RAV4"],
}

fake = Faker()

class CarFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Car

    vin = factory.LazyFunction(lambda: fake.unique.lexify(text="?????????????????"))
    make = factory.LazyFunction(lambda: random.choice(list(MAKES_MODELS.keys())))
    model = factory.LazyAttribute(lambda o: random.choice(MAKES_MODELS[o.make]))
    year_of_manufacture = factory.Faker("year")
    owner = factory.SubFactory('apps.accounts.factories.UserFactory')
