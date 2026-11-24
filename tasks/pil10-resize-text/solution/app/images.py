from PIL import Image, ImageDraw, ImageFont


def thumbnail(image, max_side):
    thumb = image.copy()
    thumb.thumbnail((max_side, max_side), Image.LANCZOS)
    return thumb


def resize_exact(image, width, height):
    return image.resize((width, height), Image.LANCZOS)


def text_size(text):
    left, top, right, bottom = ImageFont.load_default().getbbox(text)
    return right - left, bottom - top


def label(text, padding=4):
    font = ImageFont.load_default()
    width, height = text_size(text)
    image = Image.new("RGB", (width + 2 * padding, height + 2 * padding), "white")
    ImageDraw.Draw(image).text((padding, padding), text, fill="black", font=font)
    return image
