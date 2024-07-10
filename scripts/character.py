from pathlib import Path

from .utils import ParseTool, dump_file, decode_file

CHARACTER_BASE_CONFIG_FILE = "FileCfg/AvatarBaseTemplateTb.json"


icon_path = Path("./icon/character")
preview_path = Path("./image/character_preview")
portrait_path = Path("./image/character_portrait")


def parse_character(data_path: Path, image_path: Path):
    character_map: dict[str, ParseTool] = {}
    character_base = decode_file(data_path / CHARACTER_BASE_CONFIG_FILE)
    for i in character_base:
        parse_tool = ParseTool()
        id_ = str(i["id"])
        parse_tool.set("id", id_)
        parse_tool.set_hash("name", i["name"])
        parse_tool.set_hash("full_name", i["full_name"])
        parse_tool.set("tag", i["tag"])
        character_map[id_] = parse_tool
    return character_map


def generate(data_path: Path, image_path: Path):
    content = parse_character(data_path, image_path)
    dump_file(content, "character")
