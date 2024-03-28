from pathlib import Path

import pytest

from ai21_tokenizer import Tokenizer, PreTrainedTokenizers, JambaInstructTokenizer
from ai21_tokenizer.jurassic_tokenizer import JurassicTokenizer


@pytest.fixture
def resources_path() -> Path:
    return Path(__file__).parent / "resources"


@pytest.fixture(scope="session")
def tokenizer() -> JurassicTokenizer:
    jurassic_tokenizer = Tokenizer.get_tokenizer(tokenizer_name=PreTrainedTokenizers.J2_TOKENIZER)

    if isinstance(jurassic_tokenizer, JurassicTokenizer):
        return jurassic_tokenizer

    raise ValueError("JurassicTokenizer not found")


@pytest.fixture(scope="session")
def jamba_instruct_tokenizer() -> JambaInstructTokenizer:
    jurassic_tokenizer = Tokenizer.get_tokenizer(PreTrainedTokenizers.JAMBA_INSTRUCT_TOKENIZER)

    if isinstance(jurassic_tokenizer, JambaInstructTokenizer):
        return jurassic_tokenizer

    raise ValueError("JambaInstructTokenizer not found")
