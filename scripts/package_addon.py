"""Stage, verify, and archive the Godot-Jieba addon used by GitHub Actions."""

from argparse import ArgumentParser
from configparser import ConfigParser
from json import loads
from pathlib import Path
from shutil import copy2, copytree, ignore_patterns
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "addons/godot_jieba"
EXTENSION = ADDON / "bin/godot_jieba.gdextension"
DICTIONARY_FILES = (
    "jieba.dict.utf8",
    "hmm_model.utf8",
    "user.dict.utf8",
    "idf.utf8",
    "stop_words.utf8",
)
THIRD_PARTY_LICENSES = (
    "godot-cpp-LICENSE.md",
    "cppjieba-LICENSE",
    "limonp-LICENSE",
)


def read_libraries():
    config = ConfigParser(interpolation=None)
    config.read_string(EXTENSION.read_text(encoding="utf-8"))
    return {key: Path(loads(value)) for key, value in config["libraries"].items()}


def library_file(path):
    if path.suffix == ".framework":
        return path / path.stem
    return path


def require_file(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise SystemExit(f"Missing or empty package file: {path}")


def copy_file(source, destination):
    require_file(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy2(source, destination)


def copy_library(source, destination):
    if source.suffix == ".framework":
        require_file(library_file(source))
        destination.parent.mkdir(parents=True, exist_ok=True)
        copytree(source, destination, dirs_exist_ok=True)
        require_file(library_file(destination))
        return
    copy_file(source, destination)


def library_key(platform, arch, target):
    target_name = target.removeprefix("template_")
    if platform == "ios":
        return f"ios.{target_name}"
    if platform == "macos" and arch == "universal":
        return f"macos.{target_name}"
    return f"{platform}.{target_name}.{arch}"


def stage_build(destination, platform, arch, target, include_addon_data):
    libraries = read_libraries()
    key = library_key(platform, arch, target)
    library = libraries.get(key)
    if library is None:
        raise SystemExit(f"No GDExtension library declared for {platform} {arch} {target} ({key})")

    addon_destination = destination / "addons/godot_jieba"
    extension_bin = ADDON / "bin"
    packaged_bin = addon_destination / "bin"
    copy_library(extension_bin / library, packaged_bin / library)

    if include_addon_data:
        copytree(ADDON / "dict", addon_destination / "dict", dirs_exist_ok=True)


def assemble(destination):
    addon_destination = destination / "addons/godot_jieba"
    copytree(
        ADDON,
        addon_destination,
        dirs_exist_ok=True,
        ignore=ignore_patterns("bin", "dict", "*.import", ".godot"),
    )
    copy_file(EXTENSION, addon_destination / "bin/godot_jieba.gdextension")

    for library in read_libraries().values():
        require_file(addon_destination / "bin" / library_file(library))

    for filename in DICTIONARY_FILES:
        require_file(addon_destination / "dict" / filename)
    for filename in THIRD_PARTY_LICENSES:
        require_file(addon_destination / "THIRD-PARTY-LICENSES" / filename)
    for path in (addon_destination / "translations/properties.zh_Hans.po", addon_destination / "translations/documentation.zh_Hans.po"):
        require_file(path)

    copy_file(ROOT / "README.md", destination / "README.md")
    copy_file(ROOT / "LICENSE.txt", destination / "LICENSE.txt")

    print(f"Verified {len(read_libraries())} GDExtension libraries and addon data in {destination}")


def archive(source, destination):
    if not source.is_dir():
        raise SystemExit(f"Missing assembled addon directory: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED, compresslevel=9) as output:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                output.write(path, path.relative_to(source).as_posix())

    with ZipFile(destination) as packaged:
        corrupt_file = packaged.testzip()
        if corrupt_file is not None:
            raise SystemExit(f"Corrupt file in release archive: {corrupt_file}")
    print(f"Created and verified {destination}")


def main():
    parser = ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    stage = commands.add_parser("stage")
    stage.add_argument("destination", type=Path)
    stage.add_argument("platform")
    stage.add_argument("arch")
    stage.add_argument("target", choices=("template_debug", "template_release"))
    stage.add_argument("--include-addon-data", action="store_true")

    assemble_command = commands.add_parser("assemble")
    assemble_command.add_argument("destination", type=Path)

    archive_command = commands.add_parser("archive")
    archive_command.add_argument("source", type=Path)
    archive_command.add_argument("destination", type=Path)

    args = parser.parse_args()
    if args.command == "stage":
        stage_build(args.destination, args.platform, args.arch, args.target, args.include_addon_data)
    elif args.command == "assemble":
        assemble(args.destination)
    else:
        archive(args.source, args.destination)


if __name__ == "__main__":
    main()
