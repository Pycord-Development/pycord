import importlib.resources
from contextlib import suppress

with (
    suppress(FileNotFoundError),
    importlib.resources.files(__package__).joinpath("ART.txt").open(encoding="utf-8") as f,
):
    print(f.read())
