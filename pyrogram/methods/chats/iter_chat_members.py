from string import printable
from typing import Union, AsyncGenerator, Optional

from pyrogram import raw
from pyrogram import types


class Filters:
    ALL = "all"
    BANNED = "banned"
    RESTRICTED = "restricted"
    BOTS = "bots"
    RECENT = "recent"
    ADMINISTRATORS = "administrators"


QUERIES = [""] + list(printable)
QUERYABLE_FILTERS = (Filters.ALL, Filters.BANNED, Filters.RESTRICTED)


class IterChatMembers():
    async def iter_chat_members(
            self,
            chat_id: Union[int, str],
            limit: int = 0,
            query: str = "",
            filter: str = Filters.ALL
    ) -> Optional[AsyncGenerator["types.ChatMember", None]]:
        current = 0
        yielded = set()
        queries = [query] if query else QUERIES
        total = limit or (1 << 31) - 1
        limit = min(200, total)
        resolved_chat_id = await self.resolve_peer(chat_id)

        if filter not in QUERYABLE_FILTERS:
            queries = [""]

        for q in queries:
            offset = 0

            while True:
                chat_members = await self.get_chat_members(
                    chat_id=chat_id,
                    offset=offset,
                    limit=limit,
                    query=q,
                    filter=filter
                )

                if not chat_members:
                    break

                if isinstance(resolved_chat_id, raw.types.InputPeerChat):
                    total = len(chat_members)

                offset += len(chat_members)

                for chat_member in chat_members:
                    user_id = chat_member.user.id

                    if user_id in yielded:
                        continue

                    yield chat_member

                    yielded.add(chat_member.user.id)

                    current += 1

                    if current >= total:
                        return
