import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'icecream_project.settings')
django.setup()

from django.contrib.auth.models import User

def reset_admin_password():
    try:
        admin = User.objects.get(username='admin')
        admin.set_password('2026@Admin')
        admin.save()
        print("Admin password changed successfully to: 2026@Admin")
    except User.DoesNotExist:
        print("User 'admin' does not exist. Creating it...")
        User.objects.create_superuser('admin', 'admin@example.com', '2026@Admin')
        print("Superuser 'admin' created successfully with password: 2026@Admin")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    reset_admin_password()
