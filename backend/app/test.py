import asyncio
from together import AsyncTogether

async def test_together():
    client = AsyncTogether(api_key="7b2da4d4e07796fad4c99f6e62cb4fa82bf98d843a60a9174be2dc6492809ab0")
    try:
        response = await client.chat.completions.create(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        print("Success:", response.choices[0].message.content)
    except Exception as e:
        print("Error:", e)

asyncio.run(test_together())