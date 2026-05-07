from typing import Protocol

import numpy as np


class BaseVadService(Protocol):
    def trim_speech(self, audio: np.ndarray) -> np.ndarray:
        raise NotImplementedError