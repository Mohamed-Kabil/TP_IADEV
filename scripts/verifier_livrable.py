"""Contrôler la release TP4, puis tester la roue hors du dépôt dans un venv neuf.

Implémentation locale du contrat décrit dans le manuel V1.1 ; kit TP4 absent.
Le rapport est ignoré par Git et destiné aux pièces jointes de la release.
"""

import configparser
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import tomllib
import venv
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAPPORT = ROOT / "docs/livrable-tp4.txt"


def main() -> int:
    lignes = ["Vérification TP4 — installation hors des sources",
              f"Date UTC : {datetime.now(timezone.utc).isoformat()}"]
    echecs = []

    def noter(ok: bool, nom: str, detail: str = "") -> bool:
        lignes.append(f"[{'OK' if ok else 'ÉCHEC'}] {nom}" + (f" : {detail}" if detail else ""))
        if not ok:
            echecs.append(nom)
        return ok

    def commande(args: list[str], cwd: Path, env: dict[str, str] | None = None):
        return subprocess.run(args, cwd=cwd, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=300)

    try:
        version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
        nom_roue = f"sentiment_app-{version}-py3-none-any.whl"
        nom_source = f"sentiment_app-{version}.tar.gz"
        roue, source = ROOT / "dist" / nom_roue, ROOT / "dist" / nom_source
        noter(roue.is_file(), "roue présente", nom_roue)
        noter(source.is_file(), "distribution source présente", nom_source)
        noter({p.name for p in (ROOT / "dist").iterdir()} == {nom_roue, nom_source},
              "aucun autre fichier dans dist/")
        git = commande(["git", "rev-parse", "HEAD"], ROOT)
        tag = commande(["git", "rev-parse", f"v{version}^{{commit}}"], ROOT)
        noter(git.returncode == tag.returncode == 0 and git.stdout.strip() == tag.stdout.strip(),
              "étiquette Git sur le dernier commit", f"v{version} ; HEAD={git.stdout.strip()}")
        statut = commande(["git", "status", "--porcelain"], ROOT)
        noter(statut.returncode == 0 and not statut.stdout.strip(), "dépôt propre")
        noter(f"## [{version}]" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"),
              "CHANGELOG.md décrit cette version")
        if roue.is_file() and source.is_file():
            chemin_modele = "sentiment_app/modele/sentiment.joblib"
            modele = (ROOT / "models/sentiment.joblib").read_bytes()
            with zipfile.ZipFile(roue) as archive:
                noms = archive.namelist()
                noter(chemin_modele in noms and archive.read(chemin_modele) == modele,
                      "modèle embarqué identique au modèle entraîné", hashlib.sha256(modele).hexdigest())
                noter(not any(p.startswith("tests/") or "/test_" in p for p in noms), "pas de tests dans la roue")
                entrees = configparser.ConfigParser()
                entrees.read_string(archive.read(f"sentiment_app-{version}.dist-info/entry_points.txt").decode())
                noter(entrees.get("console_scripts", "sentiment", fallback="") == "sentiment_app.cli:main",
                      "commande sentiment déclarée")
                noter(all(name in noms for name in ["sentiment_app/__init__.py", "sentiment_app/predict.py",
                                                    "sentiment_app/cli.py"]), "modules publics présents")
            with tarfile.open(source) as archive:
                membre = archive.extractfile(f"sentiment_app-{version}/src/{chemin_modele}")
                noter(membre is not None and membre.read() == modele, "modèle présent dans la distribution source")
            for fichier in [roue, source]:
                lignes.append(f"SHA256 {fichier.name} : {hashlib.sha256(fichier.read_bytes()).hexdigest()}")
        if not echecs:
            with tempfile.TemporaryDirectory(prefix="verification-sentiment-") as dossier:
                temporaire = Path(dossier).resolve()
                environnement = temporaire / "venv"
                venv.create(environnement, with_pip=True)
                executables = environnement / ("Scripts" if os.name == "nt" else "bin")
                python = executables / ("python.exe" if os.name == "nt" else "python")
                env = {k: v for k, v in os.environ.items() if k not in {"PYTHONPATH", "PYTHONHOME"}}
                env.update(VERIFICATION_LIVRABLE="1", PYTHONUTF8="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
                installation = commande([str(python), "-I", "-m", "pip", "install", f"{roue}[test]"], temporaire, env)
                if noter(installation.returncode == 0, "installation dans un environnement neuf",
                         installation.stdout.splitlines()[-1] if installation.returncode == 0 else installation.stderr[-2000:]):
                    shutil.copy2(ROOT / "tests/test_paquet.py", temporaire / "test_paquet.py")
                    tests = commande([str(python), "-I", "-m", "pytest", "test_paquet.py", "-q", "--import-mode=importlib"], temporaire, env)
                    sortie = tests.stdout + tests.stderr
                    noter(tests.returncode == 0 and "6 passed" in sortie and "skipped" not in sortie,
                          "six tests sur le paquet installé, aucun ignoré", sortie.strip())
                    cli = executables / ("sentiment.exe" if os.name == "nt" else "sentiment")
                    resultat = commande([str(cli), "Produit cassé et service injoignable, à fuir", "--json"], temporaire, env)
                    noter(resultat.returncode == 0 and json.loads(resultat.stdout) == {"label": "negative", "score": .7465},
                          "commande installée hors des sources", resultat.stdout.strip() or resultat.stderr[-1000:])
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, zipfile.BadZipFile, tarfile.TarError) as exc:
        noter(False, "vérification interrompue", str(exc))
    lignes.append("Bilan : " + ("NON CONFORME" if echecs else "CONFORME"))
    RAPPORT.parent.mkdir(parents=True, exist_ok=True)
    RAPPORT.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("\n".join(lignes))
    print(f"Rapport : {RAPPORT}")
    return int(bool(echecs))


if __name__ == "__main__":
    raise SystemExit(main())
