from PIL import Image, ImageFont

from app.images import label, text_size, thumbnail


def _box_size(text):
    left, top, right, bottom = ImageFont.load_default().getbbox(text)
    return right - left, bottom - top


def test_thumbnail_keeps_aspect_ratio():
    image = Image.new("RGB", (100, 50), "red")
    assert thumbnail(image, 40).size == (40, 20)
    assert image.size == (100, 50)


def test_text_size_and_label():
    assert text_size("Hello") == _box_size("Hello")
    width, height = _box_size("Hello")
    assert label("Hello").size == (width + 8, height + 8)
