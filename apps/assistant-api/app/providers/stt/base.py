from typing import Protocol

import numpy as np


class BaseSTTProvider(Protocol):
    def transcribe(self, audio: np.ndarray) -> str:
        raise NotImplementedError