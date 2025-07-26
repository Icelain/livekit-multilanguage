from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, ModelSettings, RoomInputOptions, stt
from typing import AsyncIterable, Optional
from langdetect import detect
from livekit.plugins import (
    openai,
    elevenlabs,
    noise_cancellation,
    silero,
    sarvam
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

        self.curlang = "en"

    async def stt_node(
    self, audio: AsyncIterable[rtc.AudioFrame], model_settings: ModelSettings
) -> Optional[AsyncIterable[stt.SpeechEvent]]:

        textcache = ""
        
        async def filtered_audio():
            async for frame in audio:
                yield frame
    
        async for event in Agent.default.stt_node(self, filtered_audio(), model_settings):
            if len(event.alternatives) > 0:
                textcache = event.alternatives[0].text
                self.curlang = detect(textcache)

                event.alternatives[0].text = event.alternatives[0].text + f". Respond in this language: {self.curlang}"
                                                
            yield event

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=sarvam.STT(language="unknown",model="saarika:v2.5",),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(voice_id="2zRM7PkgwBPiau2jvVXc", model="eleven_flash_v2_5"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
           noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )



if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
