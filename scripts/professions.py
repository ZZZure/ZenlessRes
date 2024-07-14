from pathlib import Path

from .utils import ParseTool, dump_file, decode_file

PROFESSION_BASE_CONFIG_FILE = "FileCfg/AvatarProfessionTemplateTb.json"


icon_path = Path("./image/profession/icon")


def parse_profession():
    profession_map: dict[str, ParseTool] = {}
    profession_base = decode_file(PROFESSION_BASE_CONFIG_FILE)
    for i in profession_base:
        parse_tool = ParseTool()
        id_ = str(i["id"])
        parse_tool.set("id", id_)
        parse_tool.set_hash("name", i["name"])
        parse_tool.set_hash("description", i["description"])
        profession_map[id_] = parse_tool
    return profession_map


def generate():
    content = parse_profession()
    dump_file(content, "professions")
