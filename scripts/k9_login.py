"""
K9 Telegram Re-authentication — Two-step process.

Step 1: python3 scripts/k9_login.py send-code
        → Sends verification code to your phone

Step 2: python3 scripts/k9_login.py verify 12345
        → Enter the code you received
"""
import asyncio
import sys
from telethon import TelegramClient

SESSION = "/Users/haotianliu/.openclaw/workspace/ystar-company/ystar_telegram_session"
API_ID = 31953230
API_HASH = "85981cc76a909256eff111c544e0c363"
PHONE = "+17033422330"

async def send_code():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    result = await client.send_code_request(PHONE)
    print(f"验证码已发送到 {PHONE}")
    print(f"phone_code_hash: {result.phone_code_hash}")
    # Save hash for step 2
    with open("/tmp/k9_code_hash.txt", "w") as f:
        f.write(result.phone_code_hash)
    await client.disconnect()
    print("请运行: python3 scripts/k9_login.py verify <你收到的验证码>")

async def verify(code):
    with open("/tmp/k9_code_hash.txt") as f:
        phone_code_hash = f.read().strip()
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.connect()
    await client.sign_in(PHONE, code, phone_code_hash=phone_code_hash)
    me = await client.get_me()
    print(f"登录成功！用户: {me.first_name} (ID: {me.id})")
    await client.disconnect()
    print("金金已恢复连接。可以运行: python3 scripts/k9.py \"ping\"")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  Step 1: python3 scripts/k9_login.py send-code")
        print("  Step 2: python3 scripts/k9_login.py verify <验证码>")
    elif sys.argv[1] == "send-code":
        asyncio.run(send_code())
    elif sys.argv[1] == "verify" and len(sys.argv) >= 3:
        asyncio.run(verify(sys.argv[2]))
    else:
        print("无效参数。用法: send-code 或 verify <验证码>")
