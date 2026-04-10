from __future__ import annotations

from pathlib import Path

from project_ash.config import load_default_config
from project_ash.models import InputMode, UserInput
from project_ash.orchestrator import AssistantOrchestrator
from project_ash.voice.stt import SpeechToText
from project_ash.voice.tts import TextToSpeech


def _confirm(prompt: str) -> bool:
    value = input(f"{prompt} [y/N]: ").strip().lower()
    return value in {"y", "yes"}


def run_text_loop(orchestrator: AssistantOrchestrator, tts: TextToSpeech) -> None:
    print("Project Ash ready. Type 'exit' to quit.")
    while True:
        text = input("You: ").strip()
        if text.lower() in {"exit", "quit"}:
            print("Ash: Goodbye.")
            break

        user_input = UserInput(mode=InputMode.TEXT, text=text)
        plan = orchestrator.create_plan(user_input)

        print("Ash: Plan")
        for step in plan.steps:
            print(f"  {step.step_id}. {step.action} (risk={step.risk.value})")
            if step.requires_confirmation and not _confirm("Confirm this step?"):
                print("Ash: Cancelled by user.")
                tts.speak("Cancelled by user.")
                break
        else:
            result = orchestrator.execute_plan(plan)
            print(f"Ash: {result.summary}")
            for item in result.step_results:
                print(f"  - {item.message}")
            tts.speak(result.summary)


def run_voice_once(orchestrator: AssistantOrchestrator, tts: TextToSpeech) -> None:
    stt = SpeechToText()
    print("Ash: Listening...")
    transcript = stt.listen_once()
    if transcript.confidence <= 0.0 or not transcript.text:
        print("Ash: I could not understand. Please repeat or use text mode.")
        return

    print(f"You (voice): {transcript.text}")
    user_input = UserInput(mode=InputMode.VOICE, text=transcript.text)
    plan = orchestrator.create_plan(user_input)

    for step in plan.steps:
        print(f"Ash: Step {step.step_id} -> {step.action} (risk={step.risk.value})")
        if step.requires_confirmation and not _confirm("Confirm this step?"):
            print("Ash: Cancelled by user.")
            return

    result = orchestrator.execute_plan(plan)
    print(f"Ash: {result.summary}")
    for item in result.step_results:
        print(f"  - {item.message}")
    tts.speak(result.summary)


def main() -> None:
    cfg = load_default_config()
    log_dir = Path(cfg.log_dir)
    orchestrator = AssistantOrchestrator(log_dir=log_dir, sqlite_db_path=cfg.sqlite_db_path)
    tts = TextToSpeech(enabled=cfg.enable_tts)

    mode = input("Select mode [text/voice]: ").strip().lower() or "text"
    if mode == "voice":
        run_voice_once(orchestrator, tts)
    else:
        run_text_loop(orchestrator, tts)


if __name__ == "__main__":
    main()
