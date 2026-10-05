# ==========================================================
# Copyright (c) 2026 ⎯𝐑𝐨𝐱𝐲  ꭙ ᴍᴜsɪᴄ˼ ♪ | ꞋꞋꞌꞋ𝚨ᴘє𝙭 ɴᴇᴛᴡᴏʀᴋ
# All Rights Reserved.
#
# Project      : ⎯𝐑𝐨𝐱𝐲  ꭙ ᴍᴜsɪᴄ˼ ♪ - Telegram Music Bot
# Powered By   : ꞋꞋꞌꞋ𝚨ᴘє𝙭 ɴᴇᴛᴡᴏʀᴋ
#
# Distributed under the MIT License (see LICENSE).
# ==========================================================
import os
import asyncio
import aiohttp
from PIL import (
    Image,
    ImageDraw,
    ImageFilter,
    ImageFont
)
from ArtistMusic import config
from ArtistMusic.helpers import Track

SIZE = (1280, 720)
BRAND_TEXT = "ꞋꞋꞌꞋ𝚨ᴘє𝙭 ɴᴇᴛᴡᴏʀᴋ"
BRAND_X = 40
BRAND_Y = 30
BRAND_COLOR = (255, 255, 255, 255)
GLOW_COLOR = (255, 196, 61, 200)
PILL_COLOR = (0, 0, 0, 110)
DARK_OVERLAY_ALPHA = 90              # extra darkening over the whole thumbnail

_FONT_FILES = [
    "ArtistMusic/helpers/fonts/FreeSerif.ttf",   # covers every brand glyph
    "ArtistMusic/helpers/DejaVuSans-Bold.ttf",
    "ArtistMusic/helpers/Raleway-Bold.ttf",
]


def _load_font(paths, size):
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _load_fonts(paths, size):
    fonts = []
    for p in paths:
        try:
            fonts.append(ImageFont.truetype(p, size))
        except OSError:
            continue
    return fonts or [ImageFont.load_default()]


def _split_runs(fonts, text):
    """FreeSerif (first font) contains every glyph of the brand text."""
    return [(fonts[0], text)]


class Thumbnail:
    def __init__(self):
        self.brand_fonts = _load_fonts(_FONT_FILES, 34)

    async def save_thumb(self, output_path: str, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(output_path, "wb") as f:
                    f.write(await resp.read())
        return output_path

    async def generate(self, song: Track, size=SIZE) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}_ultra.png"
            if os.path.exists(output):
                return output
            await self.save_thumb(temp, song.thumbnail)
            return await asyncio.get_event_loop().run_in_executor(
                None,
                self._generate_sync,
                temp,
                output,
                song,
                size
            )
        except Exception:
            return config.DEFAULT_THUMB

    def _draw_brand(self, bg: Image.Image):
        """Draws the network watermark in the top-left corner of bg (RGBA)."""
        runs = _split_runs(self.brand_fonts, BRAND_TEXT)
        probe = ImageDraw.Draw(bg)
        widths = [probe.textlength(t, font=f) for f, t in runs]
        text_w = int(sum(widths))
        text_h = max(f.getbbox("Ag")[3] for f, _ in runs)

        pad_x, pad_y = 22, 14
        pill_box = (
            BRAND_X - pad_x,
            BRAND_Y - pad_y,
            BRAND_X + text_w + pad_x,
            BRAND_Y + text_h + pad_y,
        )
        pill_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        ImageDraw.Draw(pill_layer).rounded_rectangle(
            pill_box, radius=(text_h + pad_y * 2) // 2, fill=PILL_COLOR)
        bg.alpha_composite(pill_layer)

        def paint(layer, dx, dy, fill):
            d = ImageDraw.Draw(layer)
            cx = BRAND_X + dx
            for (f, t), w in zip(runs, widths):
                d.text((cx, BRAND_Y + dy), t, font=f, fill=fill)
                cx += w

        glow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        paint(glow, 0, 0, GLOW_COLOR)
        bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6)))

        shadow = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        paint(shadow, 2, 2, (0, 0, 0, 190))
        bg.alpha_composite(shadow)

        text_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
        paint(text_layer, 0, 0, BRAND_COLOR)
        bg.alpha_composite(text_layer)
        return bg

    def _generate_sync(
        self,
        temp: str,
        output: str,
        song: Track,
        size=SIZE
    ) -> str:
        try:
            with Image.open(temp) as temp_img:
                src = temp_img.convert("RGBA")
                src_ratio = src.width / src.height
                dst_ratio = size[0] / size[1]
                if src_ratio > dst_ratio:
                    new_h = size[1]
                    new_w = int(new_h * src_ratio)
                else:
                    new_w = size[0]
                    new_h = int(new_w / src_ratio)
                resized = src.resize((new_w, new_h))
                left = (new_w - size[0]) // 2
                top = (new_h - size[1]) // 2
                bg = resized.crop(
                    (left, top, left + size[0], top + size[1])
                ).convert("RGBA")

            overlay = Image.new("RGBA", bg.size, (0, 0, 0, DARK_OVERLAY_ALPHA))
            bg.alpha_composite(overlay)

            bg = self._draw_brand(bg)

            bg.convert("RGB").save(output)
            try:
                os.remove(temp)
            except OSError:
                pass
            return output
        except Exception:
            return config.DEFAULT_THUMB
