from PIL import Image, ImageDraw, ImageFont


def thumbnail(image, max_side):
    thumb = image.copy()
    thumb.thumbnail((max_side, max_side), Image.ANTIALIAS)
    return thumb


def resize_exact(image, width, height):
    return image.resize((width, height), Image.ANTIALIAS)


def text_size(text):
    return ImageFont.load_default().getsize(text)


def label(text, padding=4):
    font = ImageFont.load_default()
    width, height = ImageDraw.Draw(Image.new("RGB", (1, 1))).textsize(text, font=font)
    image = Image.new("RGB", (width + 2 * padding, height + 2 * padding), "white")
    ImageDraw.Draw(image).text((padding, padding), text, fill="black", font=font)
    return image
