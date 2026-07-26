# re-export common entry points so users can `from loadin import postgres, spotify, setlistfm`
from . import postgres, spotify, setlistfm

# # Optional: a friendly version getter without importing submodules
# try:
#     from importlib.metadata import version, PackageNotFoundError
#     try:
#         __version__ = version("loadin")
#     except PackageNotFoundError:
#         __version__ = "0.0.0"
# except Exception:
#     __version__ = "0.0.0"