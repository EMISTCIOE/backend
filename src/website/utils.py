def nepali_year_choices(start=2075, end=2090):
    return [(year, str(year)) for year in range(start, end + 1)]


def build_global_gallery_items():
    """Aggregate gallery images from campus, student club, and department events."""
    from src.website.models import CampusEventGallery, StudentClubEventGallery, GlobalGalleryImage
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
        union_name = gallery.event.union.name if getattr(gallery.event, "union", None) else None
        items.append(
            {
                "uuid": str(gallery.uuid),
                "image": _resolve_image_url(gallery.image),
                "caption": gallery.caption or "",
                "source_type": "union_event" if union_name else "campus_event",
                "source_identifier": str(gallery.event.uuid),
                "source_name": gallery.event.title,
                "source_context": union_name or "Campus Event",
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

    collection_gallery_qs = (
        GlobalGalleryImage.objects.filter(
            is_archived=False,
            collection__is_archived=False,
            collection__is_active=True,
        )
        .select_related(
            "collection",
            "collection__campus_event",
            "collection__student_club_event",
            "collection__department_event",
            "collection__union",
            "collection__club",
            "collection__department",
        )
        .only(
            "uuid",
            "image",
            "caption",
            "created_at",
            "collection__uuid",
            "collection__title",
            "collection__description",
            "collection__campus_event__uuid",
            "collection__campus_event__title",
            "collection__campus_event__union__name",
            "collection__student_club_event__uuid",
            "collection__student_club_event__title",
            "collection__department_event__uuid",
            "collection__department_event__title",
            "collection__union__name",
            "collection__club__name",
            "collection__department__name",
        )
    )

    def _resolve_collection_context(collection):
        if collection.campus_event:
            return (
                "campus_event",
                str(collection.campus_event.uuid),
                collection.campus_event.title,
                collection.campus_event.union.name if collection.campus_event.union else "Campus Event",
            )
        if collection.student_club_event:
            return (
                "club_event",
                str(collection.student_club_event.uuid),
                collection.student_club_event.title,
                collection.student_club_event.club.name if collection.student_club_event.club else "Student Club Event",
            )
        if collection.department_event:
            return (
                "department_event",
                str(collection.department_event.uuid),
                collection.department_event.title,
                collection.department_event.department.name if collection.department_event.department else "Department Event",
            )
        if collection.union:
            return ("union_gallery", str(collection.union.uuid), collection.union.name, collection.title or "Union Gallery")
        if collection.club:
            return ("club_gallery", str(collection.club.uuid), collection.club.name, collection.title or "Club Gallery")
        if collection.department:
            return ("department_gallery", str(collection.department.uuid), collection.department.name, collection.title or "Department Gallery")
        return (
            "gallery_collection",
            str(collection.uuid),
            collection.title or "Gallery",
            collection.description or "",
        )

    for gallery in collection_gallery_qs:
        source_type, source_identifier, source_name, source_context = _resolve_collection_context(
            gallery.collection
        )
        items.append(
            {
                "uuid": str(gallery.uuid),
                "image": _resolve_image_url(gallery.image),
                "caption": gallery.caption or "",
                "source_type": source_type,
                "source_identifier": source_identifier,
                "source_name": source_name,
                "source_context": source_context,
                "created_at": gallery.created_at,
            }
        )

    return items
