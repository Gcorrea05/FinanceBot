from telegram import Bot


class TelegramNotifier:
    def __init__(
        self,
        token: str,
    ):
        resolved = token.strip()

        if not resolved:
            raise ValueError(
                "TELEGRAM_TOKEN nao configurado."
            )

        self.bot = Bot(
            token=resolved
        )

    async def send(
        self,
        *,
        chat_id: str,
        message: str,
    ) -> None:
        await self.bot.send_message(
            chat_id=chat_id,
            text=message,
        )
