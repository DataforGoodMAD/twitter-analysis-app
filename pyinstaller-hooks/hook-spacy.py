# HOOK FILE FOR SPACY
from PyInstaller.utils.hooks import collect_all

# ----------------------------- SPACY -----------------------------
data = collect_all("spacy")

datas = data[0]
binaries = data[1]
hiddenimports = data[2]

# ----------------------------- THINC -----------------------------
data = collect_all("thinc")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- CYMEM -----------------------------
data = collect_all("cymem")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- PRESHED -----------------------------
data = collect_all("preshed")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]

# ----------------------------- BLIS -----------------------------

data = collect_all("blis")

datas += data[0]
binaries += data[1]
hiddenimports += data[2]
# This hook file is a bit of a hack - really, all of the libraries should be in seperate hook files. (Eg hook-blis.py with the blis part of the hook)

hiddenimports = [
    "cymem",
    "cymem.cymem",
    "thinc.linalg",
    "murmurhash",
    "murmurhash.mrmr",
    "cytoolz",
    "cytoolz.utils",
    "cytoolz._signatures",
    "spacy.strings",
    "spacy.morphology",
    "spacy.lexeme",
    "spacy.tokens",
    "spacy.tokens.underscore",
    "spacy.parts_of_speech",
    "dill",
    "spacy.tokens.printers",
    "spacy.tokens._retokenize",
    "spacy.syntax",
    "spacy.syntax.stateclass",
    "spacy.syntax.transition_system",
    "spacy.syntax.nonproj",
    "spacy.syntax.nn_parser",
    "spacy.syntax.arc_eager",
    "thinc.extra.search",
    "spacy.syntax._beam_utils",
    "spacy.syntax.ner",
    "thinc.neural._classes.difference",
    "srsly.msgpack.util",
    "preshed",
    "preshed.maps",
    "thinc.neural",
    "thinc.neural._aligned_alloc",
    "thinc",
    "blis",
    "blis.py",
    "spacy.vocab",
    "spacy.lemmatizer",
    "spacy._align",
    "spacy.util",
    "spacy.lang",
    "spacy.data.en",
    "spacy.syntax._parser_model",
]

