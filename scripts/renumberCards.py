import os
import re
import subprocess
import tempfile
import argparse
import sys
import time


# Path to Photoshop.exe as seen from WSL (e.g. /mnt/c/Program Files/Adobe/.../Photoshop.exe)
DEFAULT_PHOTOSHOP_EXE_PATH_WSL = r"/mnt/d/Torrents/New folder/Adobe Photoshop 2021/Photoshop.exe"

POSSIBLE_LAYER_NAMES = ["Card Number", "Number"]

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

def wsl_to_windows_path(wsl_path):
    """Convert a WSL path like /mnt/e/foo to E:/foo."""
    if wsl_path.startswith('/mnt/') and len(wsl_path) > 5:
        drive_letter = wsl_path[5].upper()
        return f"{drive_letter}:{wsl_path[6:]}"
    return wsl_path


def batch_renumber(card_dir, prefix, start_num, end_num, increment, total_cards, photoshop_wsl_path):
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

    photoshop_windows_path = wsl_to_windows_path(photoshop_wsl_path)

    for item in files_to_process:
        new_path_wsl = item["new_path"]
        new_num_str = item["new_num_str"]

        file_path_js = wsl_to_windows_path(new_path_wsl)

        jsx_content = JSX_TEMPLATE.format(
            FILE_PATH=file_path_js,
            LAYER_NAMES_ARRAY=layer_names_js_array,
            NEW_NUMBER=str(int(new_num_str)),
            TOTAL_CARDS=str(total_cards)
        )

        try:
            with tempfile.NamedTemporaryFile(
                mode='w',
                delete=False,
                suffix=".jsx",
                encoding='utf-8',
            ) as f:
                f.write(jsx_content)
                temp_script_path = f.name

            try:
                result = subprocess.run(
                    ['wslpath', '-w', temp_script_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                windows_jsx_path = result.stdout.strip()
            except Exception as e:
                print(f"[ERROR] Failed to convert JSX path: {e}")
                continue

            print(f"  Processing {os.path.basename(item['new_path'])} (setting number to {new_num_str})...")
            command_list = [
                'cmd.exe',
                '/c',
                'start',
                '""',
                photoshop_windows_path,
                windows_jsx_path
            ]

            # Launch without waiting; Photoshop saves and closes via the JSX script
            subprocess.Popen(command_list, shell=False)

            time.sleep(3)

        except Exception as e:
            print(f"  [ERROR] Failed to run Photoshop script: {e}")
        finally:
            if os.path.exists(temp_script_path):
                os.remove(temp_script_path)

    print("\n--- Batch renumber complete! ---")


def main():
    parser = argparse.ArgumentParser(
        description="Batch renumber card PSD files and their internal text layers.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        '-p', '--prefix', 
        required=True, 
        type=str,
        help="The set prefix for the cards (e.g., 'LEG')"
    )
    parser.add_argument(
        '-s', '--start', 
        required=True, 
        type=int,
        help="The starting number of the range to renumber (inclusive)"
    )
    parser.add_argument(
        '-e', '--end', 
        required=True, 
        type=int,
        help="The ending number of the range to renumber (inclusive)"
    )
    parser.add_argument(
        '-i', '--inc', 
        required=True, 
        type=int,
        help="The increment amount (can be positive or negative)"
    )
    parser.add_argument(
        '-t', '--total',
        required=True,
        type=int,
        help="The total number of cards in the set (e.g., 300)"
    )
    parser.add_argument(
        '--photoshop',
        type=str,
        default=DEFAULT_PHOTOSHOP_EXE_PATH_WSL,
        help="WSL path to Photoshop.exe (default: value of DEFAULT_PHOTOSHOP_EXE_PATH_WSL)"
    )

    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.realpath(__file__))
    card_dir = os.path.join(script_dir, PSD_SUBFOLDER_NAME)

    if not os.path.isdir(card_dir):
        print(f"[ERROR] The directory '{card_dir}' does not exist.")
        print(f"Please create it and place your PSDs inside.")
        sys.exit(1)

    batch_renumber(card_dir, args.prefix, args.start, args.end, args.inc, args.total, args.photoshop)


if __name__ == "__main__":
    main()