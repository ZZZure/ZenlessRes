import json
import logging
from typing import Any
from pathlib import Path

textmap: dict[str, dict[str, str]] = {}
hashkey: dict[str, str] = {}

TEXTMAP_FILE_DICT = {
    "chs": "TextMap/TextMapTemplateTb.json",
    "cht": "TextMap/TextMap_CHTTemplateTb.json",
    "en": "TextMap/TextMap_ENTemplateTb.json",
    "de": "TextMap/TextMap_DETemplateTb.json",
    "es": "TextMap/TextMap_ESTemplateTb.json",
    "fr": "TextMap/TextMap_FRTemplateTb.json",
    "id": "TextMap/TextMap_IDTemplateTb.json",
    "ja": "TextMap/TextMap_JATemplateTb.json",
    "ko": "TextMap/TextMap_KOTemplateTb.json",
    "pt": "TextMap/TextMap_PTTemplateTb.json",
    "ru": "TextMap/TextMap_RUTemplateTb.json",
    "th": "TextMap/TextMap_THTemplateTb.json",
    "vi": "TextMap/TextMap_VITemplateTb.json",
}


class ParseTool:
    """
    Tool to manage language text map
    """

    def __init__(self) -> None:
        self.key_list: list[str] = []
        self.hash_map: dict[str, str] = {}
        self.data: dict[str, Any] = {}

    def set(self, key: str, value: Any):
        """
        Set a key to hash mapping
        """
        self.key_list.append(key) if key not in self.key_list else None
        self.data[key] = value

    def set_hash(self, key: str, hash: str):
        """
        Set a key to hash mapping
        """
        self.key_list.append(key) if key not in self.key_list else None
        self.hash_map[key] = hash

    def export(self, language: str):
        """
        Export dict of texts of specific language
        """
        export_data = {}
        for key in self.key_list:
            if key in self.data.keys():
                export_data[key] = self.data[key]
            else:
                global textmap
                export_data[key] = textmap[language].get(self.hash_map[key], "")
        return export_data


def get_language_list():
    """
    Get available language list
    """
    global textmap
    return list(textmap.keys())


def decode_file(file_path: Path):
    """
    Open a JSON file and replace hashed keys with readable text
    """
    raw_text = file_path.read_text()
    for hash in hashkey.keys():
        hash_str = f'"{hash}"'
        key_str = f'"{hashkey[hash]}"'
        raw_text = raw_text.replace(hash_str, key_str)
    data = json.loads(raw_text)
    if "data" not in data.keys():
        logger.warning(f"Data not found in {file_path}")
    return data.get("data")


def dump_file(content: dict[str, ParseTool], stem: str):
    """
    Dump parse result to JSON files by language
    """
    for language in get_language_list():
        file_path = Path("data") / language / f"{stem}.json"
        data = {k: v.export(language) for k, v in content.items()}
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(data, ensure_ascii=False))


def init_textmap(data_path: Path):
    """
    Load textmap files
    """
    global textmap
    for language in TEXTMAP_FILE_DICT.keys():
        textmap_file = data_path / TEXTMAP_FILE_DICT[language]
        try:
            textmap[language] = json.loads(textmap_file.read_text())
        except FileNotFoundError:
            logger.error(f"TextMap file not found: {textmap_file}")


def init_hashkey(data_path: Path):
    """
    Build hashkey
    """
    global hashkey
    character_raw_json = json.loads(
        (data_path / "FileCfg/AvatarBaseTemplateTb.json").read_text()
    )
    data_hash = next(iter(character_raw_json))
    character_raw_keys = list(character_raw_json[data_hash][0].keys())
    hashkey[data_hash] = "data"
    hashkey[character_raw_keys[0]] = "id"
    hashkey[character_raw_keys[2]] = "name"
    hashkey[character_raw_keys[3]] = "full_name"
    hashkey[character_raw_keys[4]] = "tag"


logger = logging.getLogger("ZenlessGenerator")
"""
Logger for Zenless Generator
"""

log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)
