# ==========================================================
# Copyright (c) 2026 ⎯𝐑𝐨𝐱𝐲  ꭙ ᴍᴜsɪᴄ˼ ♪ | ꞋꞋꞌꞋ𝚨ᴘє𝙭 ɴᴇᴛᴡᴏʀᴋ
# All Rights Reserved.
#
# Project      : ⎯𝐑𝐨𝐱𝐲  ꭙ ᴍᴜsɪᴄ˼ ♪ - Telegram Music Bot
# Powered By   : ꞋꞋꞌꞋ𝚨ᴘє𝙭 ɴᴇᴛᴡᴏʀᴋ
#
# Distributed under the MIT License (see LICENSE).
# ==========================================================
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import Message

from ArtistMusic import app, config, db


@app.on_message(filters.command(["channelplay"]) & filters.group & ~app.bl_users)
async def channelplay_command(_, m: Message):
    """Enable or disable channel play mode."""
    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass
    
    # Check if from_user exists (not sent by channel/anonymous admin)
    if not m.from_user:
        return await m.reply_text("❌ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴɴᴏᴛ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴄʜᴀɴɴᴇʟꜱ ᴏʀ ᴀɴᴏɴʏᴍᴏᴜꜱ ᴀᴅᴍɪɴꜱ.")
    
    # Check if user is admin
    member = await app.get_chat_member(m.chat.id, m.from_user.id)
    if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
        return await m.reply_text("❌ ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")

    if len(m.command) < 2:
