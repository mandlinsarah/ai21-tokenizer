from typing import Type

import pytest
from ai21_tokenizer import Tokenizer, BaseTokenizer
from ai21_tokenizer.jamba_instruct_tokenizer import JambaInstructTokenizer
from ai21_tokenizer.jurassic_tokenizer import JurassicTokenizer


@pytest.mark.parametrize(
    ids=[
        "when_tokenizer_name_is_jurassic_tokenizer__should_return_jurassic_tokenizer",
        "when_tokenizer_name_is_jamba_tokenizer__should_return_jamba_tokenizer",
    ],
    argnames=["tokenizer_name", "expected_tokenizer_instance"],
    argvalues=[
        ("j2-tokenizer", JurassicTokenizer),
        pytest.param(
            "jamba-tokenizer",
            JambaInstructTokenizer,
            marks=pytest.mark.skip(reason="JambaInstructTokenizer is not yet Open Source in HuggingFace"),
        ),
    ],
)
def test_tokenizer_factory__get_tokenizer(
    tokenizer_name: str, expected_tokenizer_instance: Type[BaseTokenizer]
) -> None:
    tokenizer = Tokenizer.get_tokenizer(tokenizer_name)

    assert tokenizer is not None
    assert isinstance(tokenizer, expected_tokenizer_instance)


def test_tokenizer__when_tokenizer_name_is_not_supported__should_raise_value_error() -> None:
    with pytest.raises(ValueError):
        Tokenizer.get_tokenizer(tokenizer_name="unsupported")
