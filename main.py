from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import AgentSession, Agent, ModelSettings, RoomInputOptions, stt, mcp
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
        super().__init__(instructions="You are a helpful voice AI assistant. USE THE PROVIDED MCP SERVER TO QUERY INFORMATION ABOUT CURRENT EVENTS, INCLUDING THE DATE. DO NOT RELY ON YOUR SYSTEM DATE, IT IS OUTDATED. PROMPT CONTEXT: SPRINKLE DISFLUENCIES IN YOUR SPEECH OCCASIONALLY IF THE TEXT IS LONG")

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

                try:
                    self.curlang = detect(textcache)
                except:
                    continue
                event.alternatives[0].text = event.alternatives[0].text + f". RESPOND IN THIS LANGUAGE IF THE PRECEDING TEXT IS LONGER THAN 4 WORDS ELSE FIGURE IT OUT: {self.curlang}"
                                                
            yield event

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=sarvam.STT(language="unknown",model="saarika:v2.5",),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(voice_id="2zRM7PkgwBPiau2jvVXc", model="eleven_flash_v2_5"),
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
        mcp_servers=[mcp.MCPServerHTTP("https://playwrightmcp.ice.computer/mcp", timeout=10, client_session_timeout_seconds=10)]
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
