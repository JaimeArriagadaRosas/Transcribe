from __future__ import annotations

import sys
from pathlib import Path

from app.core.pipeline import process_url


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_url(label: str) -> str:
    value = input(label).strip()
    if not value:
        raise ValueError("La URL no puede estar vacía")
    return value


def _read_transcription_name() -> str:
    while True:
        value = input("Nombre de la transcripción: ").strip()
        if value:
            return value
        print("El nombre no puede estar vacío.")


def _process(provider: str) -> None:
    title = "ZOOM" if provider == "zoom" else "YOUTUBE"
    print(f"\n---------------- {title} ----------------")
    url = _read_url("Pega la URL: ")
    transcription_name = _read_transcription_name()
    try:
        process_url(_root(), provider, url, transcription_name)
    except KeyboardInterrupt:
        print("\nInterrumpido. El trabajo queda guardado para reanudarlo.")
    except Exception as exc:
        print(f"\n[ERROR] {exc}")


def menu() -> int:
    while True:
        print("\n========================================")
        print("            MEDIATRANSCRIBE")
        print("========================================")
        print("1) Zoom")
        print("2) YouTube")
        print("3) Salir")
        choice = input("\nSelecciona una opción (1-3): ").strip()
        if choice == "1":
            _process("zoom")
        elif choice == "2":
            _process("youtube")
        elif choice == "3":
            return 0
        else:
            print("Opción inválida.")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    try:
        return menu()
    except (EOFError, KeyboardInterrupt):
        print()
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
