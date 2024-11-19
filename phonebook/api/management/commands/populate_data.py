from django.core.management.base import BaseCommand
from faker import Faker
from api.models import CustomUser, Contact

class Command(BaseCommand):
    help = "Populate the database with random sample data"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Generate sample users
        users = []
        for _ in range(50):  # Number of users to create
            phone_number = fake.unique.numerify(text="##########")  # Generate a 10-digit number
            users.append(CustomUser(
                name=fake.name(),
                phone_number=phone_number,
                email=fake.email(),
                is_active=True
            ))

        CustomUser.objects.bulk_create(users)
        self.stdout.write(self.style.SUCCESS("Successfully created 50 users."))

        # Generate sample contacts
        all_users = CustomUser.objects.all()
        contacts = []
        for user in all_users:
            for _ in range(10):  # Number of contacts per user
                contact_name = fake.name()
                contact_phone = fake.unique.numerify(text="##########")
                contacts.append(Contact(
                    user=user,
                    name=contact_name,
                    phone_number=contact_phone
                ))

        Contact.objects.bulk_create(contacts)
        self.stdout.write(self.style.SUCCESS("Successfully created 500 contacts."))
