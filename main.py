import os
import sys
from pathlib import Path
import site

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
VENV_SITE_PACKAGES = next((PROJECT_ROOT / ".venv" / "lib").glob("python*/site-packages"), None)

if VENV_PYTHON.exists() and Path(sys.executable).resolve() != VENV_PYTHON.resolve():
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), *sys.argv])

if VENV_SITE_PACKAGES is not None:
    site.addsitedir(str(VENV_SITE_PACKAGES))

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv():
        return None

from aplicacion.vista.ventana_principal import App

load_dotenv()

if __name__ == "__main__":
    app = App()
    app.mainloop()
