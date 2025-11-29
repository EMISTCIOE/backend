def nepali_year_choices(start=2075, end=2090):
    return [(year, str(year)) for year in range(start, end + 1)]


def resolve_gallery_image_source(image):
    if image.global_event:
        return (
            "global_event",
            str(image.global_event.uuid),
            image.global_event.title,
            image.source_context or "Global Event",  # Don't use event description
        )

    if image.union:
        return (
            "union_gallery",
            str(image.union.uuid),
            image.union.name,
            image.source_context or "Union Gallery",
        )

    if image.club:
        return (
            "club_gallery",
            str(image.club.uuid),
            image.club.name,
            image.source_context or "Club Gallery",
        )

    if image.department:
        return (
            "department_gallery",
            str(image.department.uuid),
            image.department.name,
            image.source_context or "Department Gallery",
        )

    if image.unit:
        return (
            "unit_gallery",
            str(image.unit.uuid),
            image.unit.name,
            image.source_context or "Campus Unit Gallery",
        )

    if image.section:
        return (
            "section_gallery",
            str(image.section.uuid),
            image.section.name,
            image.source_context or "Campus Section Gallery",
        )

    return (
        image.source_type or "college",
        "",
        image.source_title or "College",
        image.source_context or "",
    )


def build_global_gallery_items():
    """Aggregate gallery images from global events only."""
    from src.website.models import GlobalGalleryImage

    def _resolve_image_url(image_field):
        if not image_field:
            return ""
        try:
            return image_field.url or ""
        except ValueError:
            return ""

    items = []

    collection_gallery_qs = (
        GlobalGalleryImage.objects.filter(
            is_archived=False,
            is_active=True,
        )
        .select_related(
            "union",
            "club",
            "department",
            "unit",
            "section",
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
            "union__uuid",
            "union__name",
            "club__uuid",
            "club__name",
            "department__uuid",
            "department__name",
            "unit__uuid",
            "unit__name",
            "section__uuid",
            "section__name",
            "global_event__uuid",
            "global_event__title",
        )
    )

    def _resolve_collection_context(collection):
        return resolve_gallery_image_source(collection)

    for gallery in collection_gallery_qs:
        (
            source_type,
            source_identifier,
            source_name,
            source_context,
        ) = _resolve_collection_context(gallery)
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
            },
        )

    return items
