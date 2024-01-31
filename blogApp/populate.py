import os
import django
import random
from faker import Faker
from django.contrib.auth.models import User  # Import the User model
from blogApp.models import UserProfile, BlogPost, Comment

# Configuration for Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WriteWise.settings')
django.setup()

# List of featured images paths
featured_images_paths = ['blog/images/image1.png', 'blog/images/image2.png', 'blog/images/image3.png']

# Create an instance of Faker
fake = Faker()

def populate_database(num_of_entries=30):
    for _ in range(num_of_entries):
        # Create a User instance
        user = User.objects.create(
            username=fake.user_name(),
            password=fake.password(),  # You can set a random password here
        )

        # Create a UserProfile instance associated with the User
        profile = UserProfile.objects.create(
            user=user,
            bio=fake.text(),
            website=fake.url()
        )

        # Randomly select a path for featured images
        featured_image_path = random.choice(featured_images_paths)

        blog_post = BlogPost.objects.create(
            title=fake.sentence(),
            content=fake.paragraph(),
            author=user,  # Use the created User instance
            featured_image=featured_image_path
        )

        Comment.objects.create(
            blog_post=blog_post,
            author=user,  # Use the created User instance
            content=fake.text()
        )

if __name__ == "__main__":
    # Number of entries to create
    num_entries = 10
    populate_database(num_entries)
    print(f"Created {num_entries} entries in the database.")
