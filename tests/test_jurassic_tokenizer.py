import json
from pathlib import Path
from typing import Union, List, BinaryIO, Optional

import pytest

from ai21_tokenizer.jurassic_tokenizer import JurassicTokenizer
from ai21_tokenizer.utils import PathLike

_LOCAL_RESOURCES_PATH = Path(__file__).parents[1] / "ai21_tokenizer" / "resources" / "j2-tokenizer"


def test_tokenizer_encode_decode(tokenizer: JurassicTokenizer):
    text = "Hello world!"
    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text


def test_tokenizer_encode_set(tokenizer: JurassicTokenizer, resources_path: Path):
    tokenized_docs_path = resources_path / "200_tokenized_C4_val_docs.jsonl"
    with tokenized_docs_path.open("r") as tokenized_docs_file:
        for i, tokenized_doc_line in enumerate(tokenized_docs_file.readlines()):
            tokenized_doc = json.loads(tokenized_doc_line)

            assert tokenized_doc["token_ids_start_true"] == tokenizer.encode(
                tokenized_doc["doc_text"]
            ), f"Not equal at doc {i}"


def test_tokenizer_encode_set_when_is_start_false(tokenizer: JurassicTokenizer, resources_path: Path):
    tokenized_docs_path = resources_path / "200_tokenized_C4_val_docs.jsonl"
    with tokenized_docs_path.open("r") as tokenized_docs_file:
        for i, tokenized_doc_line in enumerate(tokenized_docs_file.readlines()):
            tokenized_doc = json.loads(tokenized_doc_line)

            assert tokenized_doc["token_ids_start_false"] == tokenizer.encode(
                tokenized_doc["doc_text"], is_start=False
            ), f"Not equal at doc {i}"


def test_tokenizer_decode_set_with_offsets(tokenizer: JurassicTokenizer, resources_path: Path):
    tokenized_docs_path = resources_path / "200_tokenized_C4_val_docs.jsonl"
    with tokenized_docs_path.open("r") as tokenized_docs_file:
        for i, tokenized_doc_line in enumerate(tokenized_docs_file.readlines()):
            tokenized_doc = json.loads(tokenized_doc_line)

            tokens = tokenized_doc["token_ids_start_true"]
            decoded_text, offsets = tokenizer.decode_with_offsets(tokens)
            assert tokenized_doc["decoded_text_from_start_true"] == decoded_text, f"Not equal at doc {i}"
            assert [
                tuple(x) for x in tokenized_doc["decoded_offsets_from_start_true"]
            ] == offsets, f"Not equal at doc {i}"


@pytest.mark.parametrize(
    ids=[
        "when_single_int__should_return_single_str",
        "when_list_of_int__should_return_list_of_str",
    ],
    argnames=["ids", "expected_tokens"],
    argvalues=[
        (30671, "▁hello"),
        ([7463, 1754], ["▁Hello", "▁world"]),
    ],
)
def test_tokenizer__convert_ids_to_tokens(
    ids: Union[int, List[int]], expected_tokens: Union[str, List[str]], tokenizer: JurassicTokenizer
):
    actual_tokens = tokenizer.convert_ids_to_tokens(ids)

    assert actual_tokens == expected_tokens


@pytest.mark.parametrize(
    ids=[
        "when_single_str__should_return_single_int",
        "when_list_of_str__should_return_list_of_ints",
    ],
    argnames=["tokens", "expected_ids"],
    argvalues=[
        ("▁hello", 30671),
        (["▁Hello", "▁world"], [7463, 1754]),
    ],
)
def test_tokenizer__convert_tokens_to_ids(
    tokens: Union[str, List[str]], expected_ids: Union[int, List[int]], tokenizer: JurassicTokenizer
):
    actual_ids = tokenizer.convert_tokens_to_ids(tokens)

    assert actual_ids == expected_ids


@pytest.mark.parametrize(
    ids=[
        "when_start_of_line__should_return_no_leading_whitespace",
        "when_not_start_of_line__should_return_leading_whitespace",
    ],
    argnames=["tokens", "start_of_line", "expected_text"],
    argvalues=[
        ([30671], True, "hello"),
        ([30671], False, " hello"),
    ],
)
def test_tokenizer__decode_with_start_of_line(
    tokens: List[int], start_of_line: bool, expected_text: str, tokenizer: JurassicTokenizer
):
    actual_text = tokenizer.decode(tokens, start_of_line=start_of_line)

    assert actual_text == expected_text


def test_tokenizer__from_file_handle():
    text = "Hello world!"
    model_config = {
        "vocab_size": 262144,
        "pad_id": 0,
        "bos_id": 1,
        "eos_id": 2,
        "unk_id": 3,
        "add_dummy_prefix": False,
        "newline_piece": "<|newline|>",
        "number_mode": "right_keep",
        "space_mode": "left",
    }

    with (_LOCAL_RESOURCES_PATH / "j2-tokenizer.model").open("rb") as tokenizer_file:
        tokenizer = JurassicTokenizer.from_file_handle(model_file_handle=tokenizer_file, config=model_config)

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text


def test_tokenizer__from_file_path():
    text = "Hello world!"
    model_config = {
        "vocab_size": 262144,
        "pad_id": 0,
        "bos_id": 1,
        "eos_id": 2,
        "unk_id": 3,
        "add_dummy_prefix": False,
        "newline_piece": "<|newline|>",
        "number_mode": "right_keep",
        "space_mode": "left",
    }

    tokenizer = JurassicTokenizer.from_file_path(
        model_path=(_LOCAL_RESOURCES_PATH / "j2-tokenizer.model"), config=model_config
    )

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text


@pytest.mark.parametrize(
    ids=[
        "when_model_path_and_file_handle_are_none__should_raise_value_error",
        "when_model_path_and_file_handle_are_not_none__should_raise_value_error",
    ],
    argnames=["model_path", "model_file_handle", "expected_error_message"],
    argvalues=[
        (None, None, "Must provide exactly one of model_path or model_file_handle. Got none."),
        (
            Path("some_path"),
            "some_file_handle",
            "Must provide exactly one of model_path or model_file_handle. Got both.",
        ),
    ],
)
def test_tokenizer__(
    model_path: Optional[PathLike], model_file_handle: Optional[BinaryIO], expected_error_message: str
):
    with pytest.raises(ValueError) as error:
        JurassicTokenizer(model_file_handle=model_file_handle, model_path=model_path, config={})

    assert error.value.args[0] == expected_error_message


def test_init__when_model_path_is_a_file__should_support_backwards_compatability():
    text = "Hello world!"
    tokenizer = JurassicTokenizer(model_path=_LOCAL_RESOURCES_PATH / "j2-tokenizer.model")

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text
