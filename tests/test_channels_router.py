from project_ash.channels.router import ChannelRouter


def test_telegram_normalization() -> None:
    router = ChannelRouter()
    envelope = router.normalize(
        "telegram",
        {
            "message": {
                "text": "open github.com",
                "chat": {"id": 123},
                "from": {"id": 77},
            }
        },
    )

    assert envelope.channel_user_id == "77"
    assert envelope.message_text == "open github.com"
