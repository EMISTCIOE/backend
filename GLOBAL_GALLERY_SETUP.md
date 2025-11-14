# Global Gallery Admin Panel Setup

## Summary

You now have a **Global Gallery** table visible in the Django admin panel that aggregates gallery images from three sources:

- ✅ Campus Events Gallery
- ✅ Student Club Events Gallery
- ✅ Department Events Gallery

## What was added:

### 1. **GlobalGalleryAdmin Class** (`admin.py`)

- Custom admin view that builds the aggregated gallery
- Read-only (no add/delete permissions, view only)
- Features:
  - Filter by source type (Campus Event, Club Event, Department Event)
  - Search by caption, event name, or source context
  - Sorted by creation date (newest first)
  - Thumbnail preview of images
  - Shows all relevant metadata

### 2. **Custom Template** (`templates/website/global_gallery_change_list.html`)

- Beautiful table layout showing all gallery items
- Image thumbnails (100x100px)
- Sortable filter for gallery sources
- Search functionality
- Date formatting
- Responsive design

### 3. **GlobalGalleryProxy Class**

- Proxy model that allows registration in Django admin
- Acts as a fake model with proper metadata

## How to Access

1. Go to Django Admin Panel: `https://your-domain/admin/`
2. Look for **"Global Gallery"** under the **Website** section
3. You'll see all aggregated gallery items in a single view

## Features

- **Filter by Source**: View only Campus Events, Club Events, or Department Events
- **Search**: Search by image caption, event name, or source context
- **View Only**: No direct editing (changes made through individual gallery models)
- **Image Previews**: Thumbnail display of each image
- **Metadata**: Shows event name, source, and creation date for each image

## Files Modified/Created

- ✅ `/backend/src/website/admin.py` - Added GlobalGalleryAdmin
- ✅ `/backend/src/templates/website/global_gallery_change_list.html` - Custom template

## Notes

- The gallery is built dynamically from three models, so it's always up-to-date
- Read-only by design to maintain data integrity
- Changes should be made through the individual gallery model admins if needed
