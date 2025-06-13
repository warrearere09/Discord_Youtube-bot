import discord
import asyncio
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()  # .env 파일 불러오기

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))  # 숫자형으로 변환
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')


intents = discord.Intents.default()
client = discord.Client(intents=intents)
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

last_live_video_id = None
last_upload_video_id = None

async def check_live():
    global last_live_video_id
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if channel is None:
        print("알림 채널을 찾지 못했습니다!")
        return

    while not client.is_closed():
        request = youtube.search().list(
            part='snippet',
            channelId=YOUTUBE_CHANNEL_ID,
            eventType='live',
            type='video',
            maxResults=1
        )
        response = request.execute()
        items = response.get('items', [])

        if items:
            video = items[0]
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            channel_title = video['snippet']['channelTitle']
            video_url = f'https://www.youtube.com/watch?v={video_id}'

            if video_id != last_live_video_id:
                last_live_video_id = video_id
                msg = f'📢 **라이브 방송 시작!**\n유튜버: **{channel_title}**\n제목: {title}\n링크: {video_url}'
                await channel.send(msg)
        else:
            last_live_video_id = None

        await asyncio.sleep(60)

async def check_upload():
    global last_upload_video_id
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    if channel is None:
        print("❌ 디스코드 알림 채널을 찾지 못했습니다!")
        return

    while not client.is_closed():
        print("📡 [업로드 체크] 유튜브 API 요청 중...")

        request = youtube.search().list(
            part='snippet',
            channelId=YOUTUBE_CHANNEL_ID,
            type='video',
            order='date',
            maxResults=1
        )
        response = request.execute()
        items = response.get('items', [])

        print(f"📦 응답 받은 영상 수: {len(items)}")

        if items:
            video = items[0]
            video_id = video['id']['videoId']
            title = video['snippet']['title']
            channel_title = video['snippet']['channelTitle']
            video_url = f'https://www.youtube.com/watch?v={video_id}'

            print("🎞 영상 ID:", video_id)
            print("📌 영상 제목:", title)
            print("📋 채널명:", channel_title)

            if video_id != last_upload_video_id and video_id != last_live_video_id:
                print("✅ 새 영상 감지됨, 알림 전송!")
                last_upload_video_id = video_id
                msg = f'🎬 **새 영상 업로드!**\n유튜버: **{channel_title}**\n제목: {title}\n링크: {video_url}'
                await channel.send(msg)
            else:
                print("🔁 이미 감지된 영상입니다. 건너뜀.")
        else:
            print("🚫 유튜브 API 결과에 영상이 없습니다.")

        await asyncio.sleep(300)


@client.event
async def on_ready():
    print(f'봇 로그인 성공! {client.user}')

async def main():
    async with client:
        client.loop.create_task(check_live())
        client.loop.create_task(check_upload())
        await client.start(DISCORD_TOKEN)

asyncio.run(main())
