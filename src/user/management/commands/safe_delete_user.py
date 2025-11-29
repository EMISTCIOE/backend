from django.core.management.base import BaseCommand
from django.db import transaction
from src.user.models import User


class Command(BaseCommand):
    help = 'Transfer all data ownership from a user to admin@tcioe.edu.np (does not delete the user)'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email of the user to transfer data from')
        parser.add_argument(
            '--admin-email', 
            type=str, 
            default='admin@tcioe.edu.np',
            help='Email of the admin user to transfer data to (default: admin@tcioe.edu.np)'
        )

    def handle(self, *args, **options):
        user_email = options['email']
        admin_email = options['admin_email']
        
        try:
            # Get the user to transfer data from
            source_user = User.objects.get(email=user_email)
            self.stdout.write(f'Found user: {source_user.username} ({source_user.email})')
            
            # Get admin user
            try:
                admin_user = User.objects.get(email=admin_email)
                self.stdout.write(f'Using admin: {admin_user.username} ({admin_user.email})')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Admin user {admin_email} not found!'))
                self.stdout.write('Available admin users:')
                for admin in User.objects.filter(is_superuser=True):
                    self.stdout.write(f'  - {admin.email}')
                return
            
            # Use transaction to ensure all-or-nothing operation
            with transaction.atomic():
                # Transfer ownership of all created data
                models_to_update = []
                
                # Get all models that have created_by field
                from django.apps import apps
                for model in apps.get_models():
                    if hasattr(model, 'created_by'):
                        count = model.objects.filter(created_by=source_user).count()
                        if count > 0:
                            models_to_update.append((model, count))
                
                if not models_to_update:
                    self.stdout.write(self.style.WARNING(f'No data found for user {user_email}'))
                    return
                
                self.stdout.write(f'Found {len(models_to_update)} model types with data from this user:')
                
                total_transferred = 0
                # Update ownership
                for model, count in models_to_update:
                    # Transfer created_by
                    model.objects.filter(created_by=source_user).update(created_by=admin_user)
                    # Transfer updated_by if exists
                    if hasattr(model, 'updated_by'):
                        model.objects.filter(updated_by=source_user).update(updated_by=admin_user)
                    
                    total_transferred += count
                    self.stdout.write(f'  ✅ {model.__name__}: {count} records transferred')
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Successfully transferred {total_transferred} records from {user_email} to {admin_email}'
                    )
                )
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  User {user_email} is still active. You can now safely delete them from the admin panel.'
                    )
                )
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {user_email} not found!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))