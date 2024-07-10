import json
from pathlib import Path

from scripts import module_list, logger, init_textmap, init_hashkey

config: dict[str, str] = {
    "data": "download/ZenlessData",
    "image": "download/Sprite",
}

config_path = Path(__file__).parent / "config.json"

if __name__ == "__main__":

    try:
        import PIL as _
    except ImportError:
        logger.error("Pillow is not installed, please install it by running:")
        logger.error("pip install Pillow")
        exit(1)

    if not config_path.exists():
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        logger.warning(f"No config file found, created a new one at {config_path}")
        logger.warning(
            "Please fill in the values in the config file and re-run the script"
        )
        exit(1)

    config = json.loads(config_path.read_text())

    if not config.get("data") or not config.get("image"):
        logger.error("Missing data or image directory in config file")
        logger.error(
            "Please fill in the values in the config file and re-run the script"
        )
        exit(1)

    data_path = Path(config["data"])
    if not data_path.exists():
        logger.error(f"Data directory not exists at {config['data']}")
        logger.error("Please fill in the correct data directory in the config file")
        logger.error(
            "Usually the path of ZenlessData which includes FileCfg and TextMap"
        )
        exit(1)

    image_path = Path(config["image"])
    if not image_path.exists():
        logger.error(f"Image directory not exists at {config['image']}")
        logger.error("Please fill in the correct image directory in the config file")
        logger.error("Usually the path of Sprite which includes images")
        exit(1)

    init_textmap(data_path)
    init_hashkey(data_path)

    for module in module_list:
        module.generate(data_path, image_path)
        logger.info(f"Module {module.__name__} generated")
