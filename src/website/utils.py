def nepali_year_choices(start=2075, end=2090):
    return [(year, str(year)) for year in range(start, end + 1)]


def build_global_gallery_items():
    """Aggregate gallery images from campus, student club, and department events."""
    from src.website.models import CampusEventGallery, StudentClubEventGallery
    from src.department.models import DepartmentEventGallery

    def _resolve_image_url(image_field):
        if not image_field:
            return ""
        try:
            return image_field.url or ""
        except ValueError:
            return ""

    items = []

    campus_gallery_qs = (
        CampusEventGallery.objects.filter(
            is_archived=False,
            event__is_archived=False,
            event__is_active=True,
        )
        .select_related("event")
        .only("uuid", "image", "caption", "created_at", "event__uuid", "event__title")
    )
    for gallery in campus_gallery_qs:
        items.append(
            {
                "uuid": str(gallery.uuid),
                "image": _resolve_image_url(gallery.image),
                "caption": gallery.caption or "",
                "source_type": "campus_event",
                "source_identifier": str(gallery.event.uuid),
                "source_name": gallery.event.title,
                "source_context": "Campus Event",
                "created_at": gallery.created_at,
            }
        )

    club_gallery_qs = (
        StudentClubEventGallery.objects.filter(
            is_archived=False,
            event__is_archived=False,
            event__is_active=True,
            event__club__is_archived=False,
            event__club__is_active=True,
        )
        .select_related("event", "event__club")
        .only(
            "uuid",
            "image",
            "caption",
            "created_at",
            "event__uuid",
            "event__title",
            "event__club__name",
        )
    )
    for gallery in club_gallery_qs:
        items.append(
            {
                "uuid": str(gallery.uuid),
                "image": _resolve_image_url(gallery.image),
                "caption": gallery.caption or "",
                "source_type": "club_event",
                "source_identifier": str(gallery.event.uuid),
                "source_name": gallery.event.title,
                "source_context": gallery.event.club.name if gallery.event.club else "",
                "created_at": gallery.created_at,
            }
        )

    department_gallery_qs = (
        DepartmentEventGallery.objects.filter(
            is_archived=False,
            event__is_archived=False,
            event__is_active=True,
            event__department__is_archived=False,
            event__department__is_active=True,
        )
        .select_related("event", "event__department")
        .only(
            "uuid",
            "image",
            "caption",
            "created_at",
            "event__uuid",
            "event__title",
            "event__department__name",
        )
    )
    for gallery in department_gallery_qs:
        items.append(
            {
                "uuid": str(gallery.uuid),
                "image": _resolve_image_url(gallery.image),
                "caption": gallery.caption or "",
                "source_type": "department_event",
                "source_identifier": str(gallery.event.uuid),
                "source_name": gallery.event.title,
                "source_context": gallery.event.department.name if gallery.event.department else "",
                "created_at": gallery.created_at,
            }
        )

    return items
