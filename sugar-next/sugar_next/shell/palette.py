"""Dominant-color extraction for active-app chrome tinting.

Deliberately simple: average the pixels of an app's icon rather than
pulling in a full palette-extraction library. Falls back to ``None`` when
extraction is inconclusive (icon missing, fully transparent, or the
result is too close to gray to read as a meaningful accent).
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gtk

#: Below this saturation (0-1), the average color is considered "gray"
#: and not distinctive enough to use as an accent.
_MIN_SATURATION = 0.15


def _average_rgb_from_pixbuf(pixbuf):
    if pixbuf.get_has_alpha():
        channels = 4
    else:
        channels = 3
    data = pixbuf.get_pixels()
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    rowstride = pixbuf.get_rowstride()

    total_r = total_g = total_b = 0
    count = 0
    for y in range(height):
        row_start = y * rowstride
        for x in range(width):
            offset = row_start + x * channels
            if channels == 4 and data[offset + 3] < 32:
                continue
            total_r += data[offset]
            total_g += data[offset + 1]
            total_b += data[offset + 2]
            count += 1

    if count == 0:
        return None
    return (total_r // count, total_g // count, total_b // count)


def _saturation(r, g, b):
    mx = max(r, g, b) / 255.0
    mn = min(r, g, b) / 255.0
    if mx == 0:
        return 0.0
    return (mx - mn) / mx


def dominant_color_hex(gicon, size=32, icon_theme=None) -> str | None:
    """Best-effort dominant color for *gicon* as a ``#rrggbb`` string."""
    if gicon is None:
        return None
    icon_theme = icon_theme or Gtk.IconTheme.get_for_display(
        Gdk.Display.get_default()
    )
    try:
        paintable = icon_theme.lookup_by_gicon(
            gicon, size, 1, Gtk.TextDirection.NONE, Gtk.IconLookupFlags.FORCE_REGULAR
        )
        icon_file = paintable.get_file() if paintable is not None else None
        if icon_file is None:
            return None
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            icon_file.get_path(), size, size
        )
    except Exception:
        return None

    rgb = _average_rgb_from_pixbuf(pixbuf)
    if rgb is None:
        return None
    r, g, b = rgb
    if _saturation(r, g, b) < _MIN_SATURATION:
        return None
    return f"#{r:02x}{g:02x}{b:02x}"
