from django.core.management.base import BaseCommand
from apps.accounts.factories import UserFactory
from apps.cars.factories import CarFactory
from apps.policies.factories import InsurancePolicyFactory
from apps.claims.factories import ClaimFactory
import random

class Command(BaseCommand):
    help = "Seed database with mock data using factory_boy + Faker"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("🌱 Seeding data..."))

        users = UserFactory.create_batch(5)
        cars = [CarFactory(owner=random.choice(users)) for _ in range(10)]
        policies = [InsurancePolicyFactory(car=random.choice(cars)) for _ in range(15)]
        claims = [ClaimFactory(car=random.choice(cars)) for _ in range(10)]

        self.stdout.write(self.style.SUCCESS("✅ Successfully seeded mock data."))
