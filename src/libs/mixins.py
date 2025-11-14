from django.core.files.storage import default_storage


class FileHandlingMixin:
    def handle_file_update(self, instance, validated_data, field_name):
        """
        Deletes old file (thumbnail, file, etc.) and updates with new one
        if provided in validated_data.
        """
        if field_name in validated_data:
            old_file = getattr(instance, field_name)
            new_file = validated_data.pop(field_name)

            # Delete old file if it exists
            if old_file and default_storage.exists(old_file.name):
                default_storage.delete(old_file.name)

            # Assign new file
            setattr(instance, field_name, new_file)
