from PIL import Image, ImageFont

from app.images import label, resize_exact, text_size, thumbnail


def _box_size(text):
    left, top, right, bottom = ImageFont.load_default().getbbox(text)
    return right - left, bottom - top


def _gradient(width, height):
    image = Image.new("RGB", (width, height))
    image.putdata([((x * 7) % 256, (y * 11) % 256, (x + y) % 256) for y in range(height) for x in range(width)])
    return image


def test_tall_and_small_images():
    assert thumbnail(Image.new("L", (30, 90)), 45).size == (15, 45)
    assert thumbnail(Image.new("L", (20, 10)), 50).size == (20, 10)


def test_lanczos_resampling_is_used():
    image = _gradient(40, 30)
    assert resize_exact(image, 7, 5).tobytes() == image.resize((7, 5), Image.LANCZOS).tobytes()
    expected = image.copy()
    expected.thumbnail((16, 16), Image.LANCZOS)
    assert thumbnail(image, 16).tobytes() == expected.tobytes()


def test_label_has_dark_text_and_padding():
    image = label("Total: 42", padding=6)
    width, height = _box_size("Total: 42")
    assert image.size == (width + 12, height + 12)
    assert image.mode == "RGB"
    assert min(image.convert("L").getdata()) < 100
    assert image.getpixel((0, 0)) == (255, 255, 255)


def test_text_size_of_other_text():
    for text in ["x", "Long label with spaces", "123,456.78"]:
        assert text_size(text) == _box_size(text)
