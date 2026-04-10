from __future__ import annotations

from dataclasses import dataclass

import speech_recognition as sr


@dataclass
class Transcript:
    text: str
    confidence: float


class SpeechToText:
    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()

    def listen_once(self) -> Transcript:
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=12)

        try:
            text = self.recognizer.recognize_google(audio)
            return Transcript(text=text, confidence=0.8)
        except sr.UnknownValueError:
            return Transcript(text="", confidence=0.0)
        except sr.RequestError:
            return Transcript(text="", confidence=0.0)
