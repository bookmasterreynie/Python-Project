import json
import os
import subprocess
import zipfile
from pathlib import Path

JAVA = r"C:\Program Files\Java\jdk-21.0.10\bin\java.exe"
MC_DIR = Path(os.environ["USERPROFILE"]) / "AppData/Roaming/.minecraft"

def load_username():
    with open("launcher_account.json", "r") as f:
        return json.load(f).get("username", "Player")
username = load_username()

def load_version_json(version_name):
    version_path = MC_DIR / "versions" / version_name / f"{version_name}.json"
    data = json.loads(version_path.read_text())
    if "inheritsFrom" in data:
        parent_data = load_version_json(data["inheritsFrom"])
        merged = parent_data.copy()
        merged["libraries"] = parent_data.get("libraries", []) + data.get("libraries", [])
        for key in data:
            if key != "libraries":
                merged[key] = data[key]
        return merged
    return data

def build_classpath(libraries, version_jar):
    classpath = []
    for lib in libraries:
        if "downloads" in lib and "artifact" in lib["downloads"]:
            path = lib["downloads"]["artifact"]["path"]
            jar = MC_DIR / "libraries" / path
            if jar.exists(): classpath.append(str(jar))
        if "downloads" in lib and "classifiers" in lib["downloads"]:
            for cls in lib["downloads"]["classifiers"].values():
                jar_path = MC_DIR / "libraries" / cls["path"]
                if jar_path.exists(): classpath.append(str(jar_path))
    classpath.append(str(version_jar))
    return ";".join(classpath)

def extract_natives(libraries, natives_dir):
    natives_dir.mkdir(exist_ok=True)
    for lib in libraries:
        if "downloads" in lib and "classifiers" in lib["downloads"]:
            for key, obj in lib["downloads"]["classifiers"].items():
                if "natives" in key:
                    jar_path = MC_DIR / "libraries" / obj["path"]
                    if jar_path.exists():
                        with zipfile.ZipFile(jar_path) as z:
                            for f in z.namelist():
                                if not f.startswith("META-INF"):
                                    z.extract(f, natives_dir)

# ---- MAIN LAUNCH FUNCTION ----
def launch_minecraft(version_name: str = None):
    # Auto-prompt if no version provided
    versions = sorted([v.name for v in (MC_DIR / "versions").iterdir() if v.is_dir()])
    if version_name is None:
        for i, v in enumerate(versions): print(f"{i}: {v}")
        choice = int(input("Select version number: "))
        version_name = versions[choice]

    VERSION = version_name
    data = load_version_json(VERSION)
    version_dir = MC_DIR / "versions" / VERSION
    version_jar = version_dir / f"{VERSION}.jar"
    natives_dir = version_dir / "natives"

    print("Building classpath...")
    cp = build_classpath(data.get("libraries", []), version_jar)
    print(f"Classpath entries: {len(cp.split(';'))}")

    print("Extracting natives...")
    extract_natives(data.get("libraries", []), natives_dir)

    main_class = data.get("mainClass", "net.minecraft.client.main.Main")
    if "OptiFine" in VERSION and main_class == "net.minecraft.launchwrapper.Launch":
        main_class = "net.minecraft.client.main.Main"

    # ---- GAME ARGS ----
    game_args = []
    if "arguments" in data and "game" in data["arguments"]:
        for arg in data["arguments"]["game"]:
            if isinstance(arg, str) and arg not in game_args:
                game_args.append(arg)

    offline_uuid = "00000000-0000-0000-0000-000000000000"
    asset_index = data.get("assetIndex", {}).get("id", VERSION)
    controlled_options = {
        "--version": VERSION,
        "--gameDir": str(MC_DIR),
        "--assetsDir": str(MC_DIR / "assets"),
        "--assetIndex": asset_index,
        "--username": username,
        "--uuid": offline_uuid,
        "--accessToken": "0",
        "--versionType": "release"
    }

    # Remove duplicates from JSON args
    filtered_args = []
    skip_next = False
    for i, arg in enumerate(game_args):
        if skip_next:
            skip_next = False
            continue
        if arg in controlled_options:
            skip_next = True
        else:
            filtered_args.append(arg)
    game_args = filtered_args

    # Append controlled options exactly once
    for key, value in controlled_options.items():
        game_args += [key, value]

    # Forge: ensure --launchTarget exists
    if "forge" in VERSION.lower():
        launch_target = data.get("mainClass") or "fmlclient"
        if "--launchTarget" not in game_args:
            game_args = ["--launchTarget", launch_target] + game_args

    # ---- JVM ARGS ----
    jvm_args = [JAVA, "-cp", cp, f"-Djava.library.path={natives_dir}", main_class] + game_args

    print("Launching Minecraft...")
    subprocess.run(jvm_args)

# Optional CLI entry
if __name__ == "__main__":
    launch_minecraft()