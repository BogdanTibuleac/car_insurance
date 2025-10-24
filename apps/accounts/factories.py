import factory
from django.contrib.auth.models import User
from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating realistic Django User objects
    with human-like names and matching emails.
    """
    class Meta:
        model = User

    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    username = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}")
    email = factory.LazyAttribute(lambda o: f"{o.first_name.lower()}.{o.last_name.lower()}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "Test1234!")
