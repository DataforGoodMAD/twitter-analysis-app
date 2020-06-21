import platform
import subprocess
import os


if platform.system() == "Linux":
    subprocess.call(
        "pyinstaller app.py --name influencia_twitter --onefile --additional-hooks-dir=./pyinstaller-hooks --hidden-import cymem.cymem --hidden-import thinc.linalg --hidden-import murmurhash.mrmr --hidden-import cytoolz.utils --hidden-import cytoolz._signatures --hidden-import spacy.strings --hidden-import spacy.morphology --hidden-import spacy.lexeme --hidden-import spacy.tokens --hidden-import spacy.gold --hidden-import spacy.tokens.underscore --hidden-import spacy.parts_of_speech --hidden-import dill --hidden-import spacy.tokens.printers --hidden-import spacy.tokens._retokenize --hidden-import spacy.syntax --hidden-import spacy.syntax.stateclass --hidden-import spacy.syntax.transition_system --hidden-import spacy.syntax.nonproj --hidden-import spacy.syntax.nn_parser --hidden-import spacy.syntax.arc_eager --hidden-import thinc.extra.search --hidden-import spacy.syntax._beam_utils --hidden-import spacy.syntax.ner --hidden-import thinc.neural._classes.difference --hidden-import pkg_resources.py2_warn --hidden-import srsly.msgpack.util --hidden-import preshed.maps",
        shell=True,
    )

    # --add-data 'twitterdb.db:.'
