from pathlib import Path

from .utils import ParseTool, dump_file, decode_file

AGENT_BASE_CONFIG_FILE = "FileCfg/AvatarBaseTemplateTb.json"


icon_path = Path("./image/agent/icon")


def parse_agent():
    agent_map: dict[str, ParseTool] = {}
    agent_base = decode_file(AGENT_BASE_CONFIG_FILE)
    for i in agent_base:
        parse_tool = ParseTool()
        id_ = str(i["id"])
        parse_tool.set("id", id_)
        parse_tool.set_hash("name", i["name"])
        parse_tool.set_hash("name_en", i["name_en"])
        parse_tool.set_hash("name_full", i["name_full"])
        parse_tool.set("tag", i["tag"])
        agent_map[id_] = parse_tool
    return agent_map


def generate():
    content = parse_agent()
    dump_file(content, "agents")
