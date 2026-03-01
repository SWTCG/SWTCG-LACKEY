import os
import shutil
from psd_tools import PSDImage

from SWTCG import isUnit

# --- PATHS ---
BASE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "PSDs")
UNIT_DIR = os.path.join(BASE_DIR, "unit")
NONUNIT_DIR = os.path.join(BASE_DIR, "nonunit")

os.makedirs(UNIT_DIR, exist_ok=True)
os.makedirs(NONUNIT_DIR, exist_ok=True)


def get_layer_by_name(layer, name, top_level_only=False):
    if top_level_only:
        for child in layer:
            if child.name == name:
                return child
        return None

    for child in layer.descendants():
        if child.name == name:
            return child
    return None


def get_text_from_type_layer(layer):
    if layer is None:
        return None
    if layer.kind == "type":
        return layer.text
    return None


def is_unit_file(psd):
    card_text = get_layer_by_name(psd, "Card Text", top_level_only=True)

    if card_text:
        typeline_layer = get_layer_by_name(card_text, "Typeline")
        text = get_text_from_type_layer(typeline_layer)

        if text:
            return isUnit(text.strip())

        return False

    subtype_layer = get_layer_by_name(psd, "Subtype (Subordinate)")
    if subtype_layer is not None:
        return True

    return False


for filename in os.listdir(BASE_DIR):
    if not filename.lower().endswith(".psd"):
        continue

    path = os.path.join(SOURCE_DIR, filename)

    try:
        psd = PSDImage.open(path)
        unit = is_unit_file(psd)

        target_dir = UNIT_DIR if unit else NONUNIT_DIR
        shutil.move(path, os.path.join(target_dir, filename))
        print(f"{filename} → {'UNIT' if unit else 'NONUNIT'}")

    except Exception as e:
        print(f"[ERROR] Could not process {filename}: {e}")