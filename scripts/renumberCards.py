import os
import re
import subprocess
import tempfile
import argparse
import sys
import time


# Path to Photoshop.exe — use a Windows-style path (works from both WSL and native Windows)
DEFAULT_PHOTOSHOP_EXE_PATH = r"D:\Torrents\New folder\Adobe Photoshop 2021\Photoshop.exe"


def is_wsl():
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False


def to_windows_path(path):
    """Convert a path to Windows format for passing to Photoshop/cmd.exe."""
    if is_wsl():
        result = subprocess.run(['wslpath', '-w', path], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    return path  # Already a Windows path on native Windows

POSSIBLE_LAYER_NAMES = ["Card Number", "Number"]
RARITIES_GROUP_NAME = "Rarities"

PSD_SUBFOLDER_NAME = "PSDs"

JSX_TEMPLATE = """
// Function to recursively search for a layer by name(s)
function findLayerByName(root, layerNames) {{
    // Check direct children first
    for (var i = 0; i < root.layers.length; i++) {{
        var layer = root.layers[i];
        
        // Check if the current layer's name matches any name in the list
        for (var j = 0; j < layerNames.length; j++) {{
            if (layer.name === layerNames[j]) {{
                return layer;
            }}
        }}
        
        // If the layer is a LayerSet (group), recursively search inside it
        if (layer.typename === 'LayerSet') {{
            var found = findLayerByName(layer, layerNames);
            if (found !== null) {{
                return found;
            }}
        }}
    }}
    return null;
}}

try {{
    var psdFile = File("{FILE_PATH}");
    var doc = null;

    if (!psdFile.exists) {{
        // Silent fail: File not found
    }} else {{
        doc = app.open(psdFile);
    }}
    
    if (doc) {{
        var layerNamesToTry = {LAYER_NAMES_ARRAY};
        var textLayer = findLayerByName(doc, layerNamesToTry);

        if (textLayer != null && textLayer.kind == LayerKind.TEXT) {{
            textLayer.textItem.contents = "{NEW_NUMBER}" + "/" + {TOTAL_CARDS};
            doc.save();
        }} else {{
            // Silent fail: Layer not found or is not text
        }}
        
        doc.close(SaveOptions.DONOTSAVECHANGES);
    }} else if (psdFile.exists) {{
        // Silent fail: File exists but failed to open
    }}
    
}} catch (e) {{
    // Silent fail: Unhandled error during script execution
    // If you need debugging, re-enable the alert here temporarily: 
    // alert("An unhandled error occurred: " + e.toString());
}}
"""

JSX_RARITY_TEMPLATE = """
function findLayerByName(root, name) {{
    for (var i = 0; i < root.layers.length; i++) {{
        var layer = root.layers[i];
        if (layer.name === name) return layer;
        if (layer.typename === 'LayerSet') {{
            var found = findLayerByName(layer, name);
            if (found !== null) return found;
        }}
    }}
    return null;
}}

try {{
    var psdFile = File("{FILE_PATH}");
    if (!psdFile.exists) {{
        // Silent fail: File not found
    }} else {{
        var doc = app.open(psdFile);
        var raritiesGroup = findLayerByName(doc, "{RARITIES_GROUP}");
        if (raritiesGroup != null) {{
            for (var i = 0; i < raritiesGroup.layers.length; i++) {{
                var child = raritiesGroup.layers[i];
                child.visible = (child.name === "{RARITY}");
            }}
            doc.save();
        }} else {{
            alert("'{RARITIES_GROUP}' group not found in: " + psdFile.name);
        }}
        doc.close(SaveOptions.DONOTSAVECHANGES);
    }}
}} catch (e) {{
    // alert("Error: " + e.toString());
}}
"""


JSX_COPYRIGHT_TEMPLATE = """
function findLayerByName(root, name) {{
    for (var i = 0; i < root.layers.length; i++) {{
        var layer = root.layers[i];
        if (layer.name === name) return layer;
        if (layer.typename === 'LayerSet') {{
            var found = findLayerByName(layer, name);
            if (found !== null) return found;
        }}
    }}
    return null;
}}

try {{
    var psdFile = File("{FILE_PATH}");
    if (!psdFile.exists) {{
        // Silent fail: File not found
    }} else {{
        var doc = app.open(psdFile);
        var copyrightLayer = findLayerByName(doc, "Copyright");
        if (copyrightLayer != null && copyrightLayer.kind == LayerKind.TEXT) {{
            copyrightLayer.textItem.contents = copyrightLayer.textItem.contents.replace(/\d{{4}}/, "{YEAR}");
            doc.save();
        }} else {{
            alert("'Copyright' layer not found in: " + psdFile.name);
        }}
        doc.close(SaveOptions.DONOTSAVECHANGES);
    }}
}} catch (e) {{
    // alert("Error: " + e.toString());
}}
"""


def wsl_to_windows_path(path):
    """Convert a WSL path like /mnt/e/foo to E:/foo. Passes through Windows paths unchanged."""
    if path.startswith('/mnt/') and len(path) > 5:
        drive_letter = path[5].upper()
        return f"{drive_letter}:{path[6:]}"
    return path


def batch_renumber(card_dir, prefix, start_num, end_num, increment, total_cards, photoshop_path):
    print(f"--- Starting Batch Renumber ---")
    print(f"Target directory: {card_dir}")
    print(f"Prefix: {prefix}, Range: {start_num}-{end_num}, Increment: {increment}")
    print(f"---------------------------------")

    pattern = re.compile(
        f"^{re.escape(prefix)}(\d+)(.*\.psd)\s*$", 
        re.IGNORECASE
    )

    # --- Pass 1: Find all files and plan the renames ---
    files_to_process = []
    for filename in os.listdir(card_dir):
        match = pattern.match(filename)
        
        if not match:
            continue

        old_num_str = match.group(1)
        try:
            old_num_int = int(old_num_str)
        except ValueError:
            continue
            
        if start_num <= old_num_int <= end_num:
            new_num_int = old_num_int + increment
            new_num_str = str(new_num_int).zfill(len(old_num_str))

            rest_of_name = match.group(2)
            new_filename = f"{prefix}{new_num_str}{rest_of_name}"
            
            old_path = os.path.join(card_dir, filename)
            new_path = os.path.join(card_dir, new_filename)

            files_to_process.append({
                "old_path": old_path,
                "new_path": new_path,
                "old_num": old_num_int,
                "new_num_str": new_num_str
            })

    if not files_to_process:
        print("No files found in the specified range.")
        return

    # --- Pass 2: Rename files (in reverse order) ---
    print(f"Found {len(files_to_process)} files. Renaming files on disk...")
    files_to_process.sort(key=lambda x: x["old_num"], reverse=True)

    for item in files_to_process:
        if os.path.exists(item["new_path"]):
            # No-op: file already has the target name (increment=0)
            if item["old_path"] == item["new_path"]:
                print(f"  Skipping rename for {os.path.basename(item['old_path'])} (i=0).")
                continue

            # If the paths are different but new_path exists, it's a real collision.
            print(f"  [ERROR] Collision: {item['new_path']} already exists. Aborting.")
            return
        try:
            os.rename(item["old_path"], item["new_path"])
            print(f"  Renamed: {os.path.basename(item['old_path'])} -> {os.path.basename(item['new_path'])}")
        except Exception as e:
            print(f"  [ERROR] Could not rename {item['old_path']}: {e}")
            return

    # --- Pass 3: Edit internal PSD data ---
    print("\nStarting Photoshop to edit internal layer data...")
    layer_names_js_array = str(POSSIBLE_LAYER_NAMES).replace("'", '"')

    photoshop_windows_path = wsl_to_windows_path(photoshop_path)

    for item in files_to_process:
        new_num_str = item["new_num_str"]
        file_path_js = wsl_to_windows_path(item["new_path"])
        jsx_content = JSX_TEMPLATE.format(
            FILE_PATH=file_path_js,
            LAYER_NAMES_ARRAY=layer_names_js_array,
            NEW_NUMBER=str(int(new_num_str)),
            TOTAL_CARDS=str(total_cards)
        )
        run_photoshop_jsx(
            jsx_content, photoshop_windows_path,
            f"{os.path.basename(item['new_path'])} (setting number to {new_num_str})"
        )

    print("\n--- Batch renumber complete! ---")


def run_photoshop_jsx(jsx_content, photoshop_windows_path, label):
    """Write jsx_content to a temp file and launch Photoshop to execute it."""
    temp_script_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix=".jsx", encoding='utf-8'
        ) as f:
            f.write(jsx_content)
            temp_script_path = f.name

        try:
            windows_jsx_path = to_windows_path(temp_script_path)
        except Exception as e:
            print(f"[ERROR] Failed to convert JSX path: {e}")
            return

        print(f"  Processing {label}...")
        subprocess.Popen(['cmd.exe', '/c', 'start', '', photoshop_windows_path, windows_jsx_path])
        time.sleep(3)

    except Exception as e:
        print(f"  [ERROR] Failed to run Photoshop script: {e}")
    finally:
        if temp_script_path and os.path.exists(temp_script_path):
            os.remove(temp_script_path)


def find_files_in_range(card_dir, prefix, start_num, end_num):
    """Return list of {path, num} dicts for PSD files matching prefix+number in range, sorted by num."""
    pattern = re.compile(f"^{re.escape(prefix)}(\d+)(.*\.psd)\s*$", re.IGNORECASE)
    files = []
    for filename in os.listdir(card_dir):
        match = pattern.match(filename)
        if not match:
            continue
        try:
            num = int(match.group(1))
        except ValueError:
            continue
        if start_num <= num <= end_num:
            files.append({"path": os.path.join(card_dir, filename), "num": num})
    files.sort(key=lambda x: x["num"])
    return files


def batch_set_rarity(card_dir, prefix, start_num, end_num, rarity, photoshop_path):
    print(f"--- Starting Batch Set Rarity ---")
    print(f"Target directory: {card_dir}")
    print(f"Prefix: {prefix}, Range: {start_num}-{end_num}, Rarity: {rarity}")
    print(f"---------------------------------")

    files_to_process = find_files_in_range(card_dir, prefix, start_num, end_num)
    if not files_to_process:
        print("No files found in the specified range.")
        return

    print(f"Found {len(files_to_process)} files. Launching Photoshop...")
    photoshop_windows_path = wsl_to_windows_path(photoshop_path)

    for item in files_to_process:
        file_path_js = wsl_to_windows_path(item["path"])
        jsx_content = JSX_RARITY_TEMPLATE.format(
            FILE_PATH=file_path_js,
            RARITIES_GROUP=RARITIES_GROUP_NAME,
            RARITY=rarity,
        )
        run_photoshop_jsx(jsx_content, photoshop_windows_path, os.path.basename(item["path"]))

    print("\n--- Batch set rarity complete! ---")


def batch_set_copyright(card_dir, prefix, start_num, end_num, year, photoshop_path):
    print(f"--- Starting Batch Set Copyright Year ---")
    print(f"Target directory: {card_dir}")
    print(f"Prefix: {prefix}, Range: {start_num}-{end_num}, Year: {year}")
    print(f"-----------------------------------------")

    files_to_process = find_files_in_range(card_dir, prefix, start_num, end_num)
    if not files_to_process:
        print("No files found in the specified range.")
        return

    print(f"Found {len(files_to_process)} files. Launching Photoshop...")
    photoshop_windows_path = wsl_to_windows_path(photoshop_path)

    for item in files_to_process:
        file_path_js = wsl_to_windows_path(item["path"])
        jsx_content = JSX_COPYRIGHT_TEMPLATE.format(
            FILE_PATH=file_path_js,
            YEAR=year,
        )
        run_photoshop_jsx(jsx_content, photoshop_windows_path, os.path.basename(item["path"]))

    print("\n--- Batch set copyright year complete! ---")


def rarity_type(val):
    mapping = {
        'r': 'Rare',     'rare': 'Rare',
        'u': 'Uncommon', 'uncommon': 'Uncommon',
        'c': 'Common',   'common': 'Common',
    }
    result = mapping.get(val.lower())
    if result is None:
        raise argparse.ArgumentTypeError(f"Invalid rarity '{val}'. Use: r/rare, u/uncommon, c/common")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Batch renumber card PSD files, set rarity layers, or update copyright year.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-p', '--prefix', required=True, type=str,
        help="The set prefix for the cards (e.g., 'LEG')")
    parser.add_argument('-s', '--start', required=True, type=int,
        help="The starting number of the range (inclusive)")
    parser.add_argument('-e', '--end', required=True, type=int,
        help="The ending number of the range (inclusive)")
    parser.add_argument('-i', '--inc', type=int, default=None,
        help="Renumber mode: increment amount (can be positive or negative)")
    parser.add_argument('-t', '--total', type=int, default=None,
        help="Renumber mode: total number of cards in the set (e.g., 30)")
    parser.add_argument('-r', '--rarity', type=rarity_type,
        help="Rarity mode: set the visible rarity layer. Accepts: r/rare, u/uncommon, c/common (case-insensitive)")
    parser.add_argument('-y', '--year', type=str,
        help="Copyright mode: replace the 4-digit year in the Copyright layer (e.g. 2026)")
    parser.add_argument('--photoshop', type=str, default=DEFAULT_PHOTOSHOP_EXE_PATH,
        help="Path to Photoshop.exe. WSL paths (/mnt/x/...) and Windows paths (X:\\...) both accepted.")

    args = parser.parse_args()

    # Validate mode
    if args.rarity:
        mode = "rarity"
    elif args.year:
        if not re.fullmatch(r'\d{4}', args.year):
            parser.error("--year must be a 4-digit year (e.g. 2026)")
        mode = "copyright"
    elif args.inc is not None and args.total is not None:
        mode = "renumber"
    else:
        parser.error("Specify --rarity, --year, or both --inc and --total.")

    script_dir = os.path.dirname(os.path.realpath(__file__))
    card_dir = os.path.join(script_dir, PSD_SUBFOLDER_NAME)

    if not os.path.isdir(card_dir):
        print(f"[ERROR] The directory '{card_dir}' does not exist.")
        print(f"Please create it and place your PSDs inside.")
        sys.exit(1)

    if mode == "rarity":
        batch_set_rarity(card_dir, args.prefix, args.start, args.end, args.rarity, args.photoshop)
    elif mode == "copyright":
        batch_set_copyright(card_dir, args.prefix, args.start, args.end, args.year, args.photoshop)
    else:
        batch_renumber(card_dir, args.prefix, args.start, args.end, args.inc, args.total, args.photoshop)


if __name__ == "__main__":
    main()