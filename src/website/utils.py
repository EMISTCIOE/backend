def nepali_year_choices(start=2075, end=2090):
    return [(year, str(year)) for year in range(start, end + 1)]


def resolve_gallery_image_source(image):
    if image.campus_event:
        union_name = getattr(image.campus_event.union, "name", None)
        if union_name:
            return (
                "union_event",
                str(image.campus_event.uuid),
                image.campus_event.title,
                union_name,
            )
        return (
            "campus_event",
            str(image.campus_event.uuid),
            image.campus_event.title,
            "Campus Event",
        )

    if image.student_club_event:
        return (
            "club_event",
            str(image.student_club_event.uuid),
            image.student_club_event.title,
            image.student_club_event.club.name if image.student_club_event.club else "",
        )

    if image.department_event:
        return (
            "department_event",
            str(image.department_event.uuid),
            image.department_event.title,
            image.department_event.department.name if image.department_event.department else "",
        )

    if image.global_event:
        return (
            "global_event",
            str(image.global_event.uuid),
            image.global_event.title,
            image.global_event.description or "Global Event",
        )

    if image.union:
        return (
            "union_gallery",
            str(image.union.uuid),
            image.union.name,
            image.source_title or "Union Gallery",
        )

    if image.club:
        return (
            "club_gallery",
            str(image.club.uuid),
            image.club.name,
            image.source_title or "Club Gallery",
        )

    if image.department:
        return (
            "department_gallery",
            str(image.department.uuid),
            image.department.name,
            image.source_title or "Department Gallery",
        )

    return (
        image.source_type or "college",
        "",
        image.source_title or "College",
        image.source_context or "",
    )


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
            is_active=True,
        )
        .select_related(
            "campus_event",
            "campus_event__union",
            "student_club_event",
            "student_club_event__club",
            "department_event",
            "department_event__department",
            "union",
            "club",
            "department",
            "global_event",
        )
        .only(
            "uuid",
            "image",
            "caption",
            "created_at",
            "source_title",
            "source_context",
            "source_type",
            "campus_event__uuid",
            "campus_event__title",
            "campus_event__union__name",
            "student_club_event__uuid",
            "student_club_event__title",
            "student_club_event__club__name",
            "department_event__uuid",
            "department_event__title",
            "department_event__department__name",
            "union__uuid",
            "union__name",
            "club__uuid",
            "club__name",
            "department__uuid",
            "department__name",
            "global_event__uuid",
            "global_event__title",
        )
    )

    def _resolve_collection_context(collection):
        return resolve_gallery_image_source(collection)

    for gallery in collection_gallery_qs:
        source_type, source_identifier, source_name, source_context = _resolve_collection_context(
            gallery
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
