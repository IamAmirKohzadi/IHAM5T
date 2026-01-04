from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import User,Profile
from blog.models import Post,Category
import random
from django.utils import timezone

DEFAULT_CATEGORY_NAMES = [
    'IT',
    'Design',
    'Football',
    'Politics',
    'Nature',
]

class Command(BaseCommand):
    help = 'creating dummy users!'

    def __init__(self, *args, **kwargs):
        # Initialize Faker instance for data generation.
        super(Command, self).__init__(*args, **kwargs)
        self.fake = Faker()

    def handle(self, *args, **options):
        # Create a fake user, profile, and sample posts/categories.
        user = User.objects.create_user(email=self.fake.email(),password='Test@12345')
        profile = Profile.objects.get(user=user)
        profile.first_name = self.fake.first_name()
        profile.last_name = self.fake.last_name()
        profile.description = self.fake.paragraph(nb_sentences=5)
        profile.save()

        categories = list(Category.objects.all())
        if not categories:
            for name in DEFAULT_CATEGORY_NAMES:
                Category.objects.get_or_create(name=name)
            categories = list(Category.objects.all())

        for i in range(5):
            post = Post.objects.create(
                author=profile,
                title=self.fake.sentence(),
                content=self.fake.paragraph(nb_sentences=10),
                extra_content=self.fake.paragraph(nb_sentences=10),
                status=random.choice([True, False]),
                published_date=timezone.now(),
            )
            if categories:
                count = min(len(categories), random.randint(1, 3))
                post.categories.set(random.sample(categories, count))
