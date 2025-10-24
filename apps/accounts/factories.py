import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for creating Django built-in User objects.
    Used for tests or seeding demo data.
    """
    class Meta:
        model = User

    username = factory.Faker("user_name")
    email = factory.Faker("email")
    password = factory.PostGenerationMethodCall("set_password", "test1234")  # hashed password
