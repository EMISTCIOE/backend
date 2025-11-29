from django.core.management.base import BaseCommand
from src.appointments.models import AppointmentSlot, AppointmentCategory
from src.user.models import User
from src.user.constants import ADMIN_ROLE


class Command(BaseCommand):
    help = 'Set office identifiers for Assistant Campus Chiefs'

    def handle(self, *args, **options):
        try:
            # Get Assistant Campus Chief category
            asst_category = AppointmentCategory.objects.get(name=AppointmentCategory.ASSISTANT_CAMPUS_CHIEF)
            
            # Get Assistant Campus Chief slots
            asst_slots = AppointmentSlot.objects.filter(category=asst_category)
            
            # Group slots by official
            officials_dict = {}
            for slot in asst_slots:
                if slot.official.id not in officials_dict:
                    officials_dict[slot.official.id] = {
                        'official': slot.official,
                        'slots': []
                    }
                officials_dict[slot.official.id]['slots'].append(slot)
            
            # Assign office identifiers
            office_identifiers = ["Office A", "Office B", "Office C"]
            
            for i, (official_id, data) in enumerate(officials_dict.items()):
                if i < len(office_identifiers):
                    office_id = office_identifiers[i]
                    official = data['official']
                    slots = data['slots']
                    
                    # Update all slots for this official
                    for slot in slots:
                        slot.office_identifier = office_id
                        slot.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {len(slots)} slots for {official.email} with office identifier: {office_id}'
                        )
                    )
                else:
                    # For additional officials, use letters beyond C
                    office_id = f"Office {chr(65 + i)}"
                    official = data['official']
                    slots = data['slots']
                    
                    for slot in slots:
                        slot.office_identifier = office_id
                        slot.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Updated {len(slots)} slots for {official.email} with office identifier: {office_id}'
                        )
                    )
            
            self.stdout.write(
                self.style.SUCCESS('Successfully updated office identifiers for Assistant Campus Chiefs!')
            )
            
        except AppointmentCategory.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Assistant Campus Chief category not found. Run setup_appointments first.')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )