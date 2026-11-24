from PIL import Image as _Image
from PIL import ImageDraw as _ImageDraw
from PIL import ImageFont as _ImageFont


def _box_size(box):
    return box[2] - box[0], box[3] - box[1]


_Image.ANTIALIAS = _Image.LANCZOS
_ImageDraw.ImageDraw.textsize = lambda self, text, font=None, **kw: _box_size(self.textbbox((0, 0), text, font=font))
_ImageFont.FreeTypeFont.getsize = lambda self, text, *args, **kw: _box_size(self.getbbox(text))
