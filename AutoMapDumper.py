import os
import subprocess
import sys
import re

def get_default_pak_path():
    """Return the default path where Dying Light's Data2.pak is typically located."""
    return r"C:\Program Files (x86)\Steam\steamapps\common\Dying Light\DW\Data2.pak"

def find_7z():
    """Search for 7z.exe in common installation directories or system PATH."""
    possible_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return "7z" # Fallback to searching the system PATH

def main():
    print("="*50)
    print("Dying Light Auto Map Dumper")
    print("="*50)

    sz_path = find_7z()
    
    pak_path = get_default_pak_path()
    print(f"Default Data2.pak path: {pak_path}")
    user_path = input("Enter a custom Data2.pak path (or press Enter to use the default): ").strip()
    
    if user_path:
        # Clean up quotes if the user copied a path with them
        user_path = user_path.strip('\"\'')
        pak_path = user_path

    if not os.path.exists(pak_path):
        print(f"ERROR: {pak_path} could not be found!")
        print("Please ensure you provide the correct directory where Dying Light is installed.")
        input("Press Enter to exit...")
        return

    print("\nScanning Data2.pak for map files (.sobj)... Please wait.")
    
    try:
        # List all .sobj files within the archive recursively
        result = subprocess.run(
            [sz_path, "l", pak_path, "-r", "*.sobj"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Failed to execute 7-Zip. Is 7-Zip installed?")
        print(e)
        input("Press Enter to exit...")
        return
    except FileNotFoundError:
        print("ERROR: 7z.exe not found. Please install 7-Zip on your system.")
        input("Press Enter to exit...")
        return

    # Extract .sobj file paths from the 7z listing output
    sobj_files = []
    lines = result.stdout.split('\n')
    for line in lines:
        if ".sobj" in line.lower():
            # 7z 'l' output typically looks like: Date Time Attr Size Compressed Name
            # The name is at the end of the line.
            match = re.search(r'\s+\d+\s+\d+\s+(.*\.sobj)$', line, re.IGNORECASE)
            if match:
                map_path = match.group(1).strip()
                if map_path not in sobj_files:
                    sobj_files.append(map_path)
            else:
                # Fallback matching if the compressed size column is missing
                match2 = re.search(r'\s+\d+\s+(.*\.sobj)$', line, re.IGNORECASE)
                if match2:
                    map_path = match2.group(1).strip()
                    if map_path not in sobj_files:
                        sobj_files.append(map_path)

    if not sobj_files:
        print("No .sobj map files were found inside Data2.pak.")
        input("Press Enter to exit...")
        return

    print("\n--- Available Maps ---")
    for i, file_path in enumerate(sobj_files):
        print(f"[{i+1}] {file_path}")
    print("-------------------------")

    choice = input("Enter the number of the map you wish to extract (or 'q' to quit): ").strip()
    if choice.lower() == 'q':
        return

    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(sobj_files):
            print("Invalid selection number!")
            return
    except ValueError:
        print("Invalid input!")
        return

    selected_map = sobj_files[choice_idx]
    map_name = os.path.basename(selected_map)
    map_name_no_ext = os.path.splitext(map_name)[0]

    # Create an output directory for the dumped data
    output_dir = os.path.join(os.getcwd(), "DumpedMaps")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nExtracting selected map: {selected_map}")
    try:
        # Extract the specific .sobj file from the archive
        subprocess.run(
            [sz_path, "e", pak_path, selected_map, f"-o{output_dir}", "-y"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("Failed to extract the map file!")
        return

    map_path = os.path.join(output_dir, map_name)
    txt_path = os.path.join(output_dir, f"{map_name_no_ext}.txt")
    eds_path = os.path.join(output_dir, f"{map_name_no_ext}.eds")

    # Locate the compiled binaries for the tools
    dumper_exe = os.path.join(os.getcwd(), "SoDumper", "bin", "Debug", "net8.0", "SO18_Dumper.exe")
    map2eds_exe = os.path.join(os.getcwd(), "Map2EDS", "bin", "Debug", "net8.0", "Map2EDS.exe")

    if not os.path.exists(dumper_exe):
        print("ERROR: SO18_Dumper.exe not found. Please ensure the project is built (dotnet build MapTools.sln).")
        return
    
    if not os.path.exists(map2eds_exe):
        print("ERROR: Map2EDS.exe not found. Please ensure the project is built.")
        return

    print("\nStep 1: Running SO18_Dumper...")
    try:
        # Execute the dumper and redirect output to a text file
        with open(txt_path, "w") as txt_file:
            subprocess.run([dumper_exe, map_path], stdout=txt_file, check=True)
        print("=> Map data successfully dumped to text format.")
    except Exception as e:
        print("An error occurred while running SO18_Dumper:", e)
        return

    print("\nStep 2: Running Map2EDS...")
    try:
        # Convert the intermediate text file to the final EDS format
        subprocess.run([map2eds_exe, txt_path, eds_path], check=True)
        print("=> Map successfully converted to EDS format.")
    except Exception as e:
        print("An error occurred while running Map2EDS:", e)
        return

    print(f"\nPROCESS COMPLETE!")
    print(f"EDS file ready for use: {eds_path}")
    print("You can now open this .eds file in the Dying Light Developer Tools.")

    # Cleanup intermediate files as requested
    try:
        if os.path.exists(map_path):
            os.remove(map_path)
        if os.path.exists(txt_path):
            os.remove(txt_path)
        print("\nIntermediate files (.sobj and .txt) have been cleaned up.")
    except Exception as e:
        print(f"Warning: Could not delete intermediate files: {e}")

    # Guide text for the final manual steps
    guide_text = """
================================================================================
IMPORTANT: FINAL MANUAL STEPS REQUIRED
================================================================================

Even though the extraction is automated, you must complete these final steps manually:

1. Locate the map folder in the game files:
   - Path: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dying Light\\DW\\Data2.pak\\data\\maps\\
   - Use 7-Zip to open Data2.pak.
   - Copy the folder of the map you just dumped and paste it onto your Desktop.

2. Prepare the map file:
   - Inside the copied folder on your Desktop, change the extension of the .exp file to .map.

3. Install the map for DevTools:
   - Move the modified map folder to:
     C:\\Program Files (x86)\\Steam\\steamapps\\common\\Dying Light\\DevTools\\workshop\\(YOUR PROJECT FOLDER)\\data\\maps

   - Then open your project in the Dying Light Developer Tools and load the map you exported from the core game.

4. Initialize the map in Developer Tools:
   - You will see objects scattered randomly—this is normal.
   - Place any random object in the map.
   - In the Attributes section, set its Matrix coordinates to 0, 0, 0 (x, y, z).
   - Group this object, save the map, and exit.

5. Import the dumped data:
   - Take the .eds file generated by this program.
   - Rename it to match the name of the .eds (the group) you just created in the map.
   - Replace the file in the workshop folder.

6. Final result:
   - Reopen the map in DevTools. All objects should now be properly loaded and positioned.
   - Recommendation: Use 'Destroy Hierarchy' to ungroup objects for easier editing.
================================================================================
"""
    
    # Write guide to README.txt if it doesn't exist
    readme_path = os.path.join(output_dir, "README.txt")
    if not os.path.exists(readme_path):
        try:
            with open(readme_path, "w") as f:
                f.write(guide_text.strip())
        except Exception as e:
            print(f"Warning: Could not create README.txt: {e}")

    # Print guide to terminal
    print(guide_text)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
