import json
import shutil
import logging
from pathlib import Path
from typing import Any, Union, Optional

from PIL import Image

textmap: dict[str, dict[str, str]] = {}
hashkey: dict[str, str] = {}

data_path: Path = Path("download/ZenlessData")
image_path: Path = Path("download/Sprite")

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
        Set a key to stable value
        """
        self.key_list.append(key) if key not in self.key_list else None
        self.data[key] = value

    def set_hash(self, key: str, hash: str):
        """
        Set a key to hash of text
        """
        self.key_list.append(key) if key not in self.key_list else None
        self.hash_map[key] = hash

    def set_image(
        self,
        key: str,
        image: str,
        folder: Path,
        stem: str,
        *,
        size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ):
        """
        Set a key to sprite image
        """
        global image_path
        image_name = image.split("/")[-1]
        sprite_path = image_path / image_name
        output_path = folder / f"{stem}.png"
        self.key_list.append(key) if key not in self.key_list else None
        if sprite_path.exists():
            folder.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(sprite_path, output_path)
            # resize_image(output_path, size=size, width=width, height=height)
            self.data[key] = output_path.as_posix()
        else:
            self.data[key] = ""

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


def decode_file(file: str):
    """
    Open a JSON file and replace hashed keys with readable text
    """
    global hashkey
    global data_path
    file_path = data_path / file
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


def resize_image(
    path: Union[Path, str],
    *,
    size: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
):
    """
    Resize an image to a specific size

    Args:
        path: Path to the image
        size: Size of the image.
        width: Width of the image.
        height: Height of the image.

    Note:
        If `size` is specified,
            the image will be resized to a square image with the specified size.
        If `width` or `height` is specified,
            the image will be resized to the specified width or height.
        If neither specified,
            the image will be resized to a 128x128 square image.
    """
    if size is None and width is None and height is None:
        size = 128
    image = Image.open(path)
    image_width, image_height = image.size
    if size is not None:
        # make a non-square image square by adding padding
        if image_height == size and image_width == size:
            return
        max_dim = max(image_width, image_height)
        bg = Image.new("RGBA", (max_dim, max_dim), (255, 255, 255, 0))
        bg.paste(image, ((max_dim - image_width) // 2, (max_dim - image_height) // 2))
        img = bg.resize((size, size))
        img.save(path, "png")
        return
    # width is not None or height is not None:
    # resize the image to the specified width and height
    width = (
        width
        if width is not None
        else (image_width * (height or image_height) // image_height)
    )
    height = height if height is not None else (image_height * width // image_width)
    if image_width == width and image_height == height:
        return
    img = image.resize((width, height))
    img.save(path, "png")


def init_path(data: Path, image: Path):
    """
    Initialize path
    """
    global data_path
    global image_path
    data_path = data
    image_path = image


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
    agent_raw_json = json.loads(
        (data_path / "FileCfg/AvatarBaseTemplateTb.json").read_text()
    )
    data_hash = next(iter(agent_raw_json))
    agent_raw_keys = list(agent_raw_json[data_hash][0].keys())
    hashkey[data_hash] = "data"
    hashkey[agent_raw_keys[0]] = "id"
    hashkey[agent_raw_keys[1]] = "name_en"
    hashkey[agent_raw_keys[2]] = "name"
    hashkey[agent_raw_keys[3]] = "name_full"
    hashkey[agent_raw_keys[4]] = "tag"
    profession_raw_json = json.loads(
        (data_path / "FileCfg/AvatarProfessionTemplateTb.json").read_text()
    )
    profession_raw_keys = list(profession_raw_json[data_hash][0].keys())
    hashkey[profession_raw_keys[0]] = "id"
    hashkey[profession_raw_keys[1]] = "name"
    hashkey[profession_raw_keys[2]] = "icon"
    hashkey[profession_raw_keys[3]] = "description"


logger = logging.getLogger("ZenlessGenerator")
"""
Logger for Zenless Generator
"""

log_handler = logging.StreamHandler()
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)
logger.setLevel(logging.DEBUG)
