import glob
import os
from collections import OrderedDict
from typing import Dict, List, Union

from .c2i import C2I
from .w2i import W2I


def create_w2i_dict(corpus_path: Union[str, List[str]]) -> Dict[str, int]:
    if isinstance(corpus_path, str):
        corpus_path = glob.glob(corpus_path)

    assert len(corpus_path) != 0, f"No vocab files are found at the provided location!"

    corpus_tokens: OrderedDict = OrderedDict()
    for path in corpus_path:
        with open(os.path.expanduser(path), encoding="ISO-8859-1") as cf:
            # Note that the first corpus column is considered to be the sentence here
            corpus_tokens.update(
                (w.strip(), None)
                for l in cf.readlines()
                for w in l.split("\t")[0].split(" ")
            )

    w2i = {w: i for i, w in enumerate(corpus_tokens)}

    return w2i


def create_vocab(corpus_path: Union[str, List[str]], notify_unk: bool = False) -> W2I:
    return W2I(create_w2i_dict(corpus_path), notify_unk=notify_unk)


def create_char_vocab(corpus_path: Union[str, List[str]]) -> C2I:
    return C2I(create_w2i_dict(corpus_path))
