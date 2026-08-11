"""Shared perception tokenizers for the Vector Loom editor."""

from . import interaction_runtime


tokenizers = []


def initialize_tokenizers():
    """Reset the ordered tokenizer registry.

    Tokenizer behavior is deliberately deferred until a bounded interaction
    episode needs it.
    """
    tokenizers.clear()


def register_tokenizer(name, fn):
    """Append one tokenizer that writes current-cycle derived facts."""
    tokenizers.append({"NAME": name, "ACTIVE": True, "DATA": {}, "FN": fn})


def run_tokenizers():
    """Build one shared derived mapping from the current raw snapshot."""
    interaction_runtime.derived.clear()
    for tokenizer in tokenizers:
        if tokenizer["ACTIVE"]:
            tokenizer["FN"](tokenizer)
