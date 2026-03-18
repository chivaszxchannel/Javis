import discord
from google import genai
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- ส่วนที่ 1: สร้าง "ประตูหลอก" (Dummy Web Server) เพื่อหลอก Google Cloud ---
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"JARVIS is Online!")

def run_dummy_server():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('', port), SimpleHandler)
    print(f"Dummy server started on port {port}")
    server.serve_forever()

# เริ่มรันประตูหลอกในอีกทู้ (Thread) นึงแยกจากบอท
threading.Thread(target=run_dummy_server, daemon=True).start()

# --- ส่วนที่ 2: โค้ด JARVIS ของอา-ไฉตัวเดิม ---
GEN_API_KEY = os.getenv("GEMINI_API_KEY")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

client_gemini = genai.Client(api_key=GEN_API_KEY)
chat = client_gemini.chats.create(
    model="gemini-2.5-flash",
    config={"system_instruction": "คุณคือ JARVIS ผู้ช่วยส่วนตัวของ ป๋าทศ ผู้เชี่ยวชาญด้าน การเขียน code และโปรแกรมเมอร์ และบริการธุรกิจการจัดการวางระบบต่างๆในองกรค์"}
)

intents = discord.Intents.default()
intents.message_content = True
client_discord = discord.Client(intents=intents)

@client_discord.event
async def on_message(message):
    if message.author == client_discord.user: return
    async with message.channel.typing():
        try:
            response = chat.send_message(message.content)
            full_text = response.text
            if len(full_text) <= 2000:
                await message.channel.send(full_text)
            else:
                for i in range(0, len(full_text), 1900):
                    await message.channel.send(full_text[i:i+1900])
        except Exception as e:
            await message.channel.send(f"อา-ไฉครับ เกิดปัญหา: {e}")

client_discord.run(DISCORD_TOKEN)
