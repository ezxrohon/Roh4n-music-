import asyncio
import time

import pyrogram
from pyrogram import enums, filters, types

from ArtistMusic import tune, app, config, db, lang, logger, queue, tasks, userbot, yt
from ArtistMusic.helpers import buttons


@app.on_message(filters.regex(r"^/") & ~filters.service, group=-1)
async def _maintenance_mode_check(_, m: types.Message):
    """
    Global maintenance mode check - runs before all other handlers.
    Blocks non-sudo users when maintenance mode is enabled.
    Only triggers for bot commands (starting with /)
    """
    if not m.from_user or m.from_user.id in app.sudoers:
        return

