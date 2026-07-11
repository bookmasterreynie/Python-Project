import json
import os
import subprocess
import zipfile
from pathlib import Path

JAVA = r"C:\Users\bookm\AppData\Roaming\.minecraft\runtime\windows-x64\java-runtime-delta\bin\java.exe"
MC_DIR = Path(os.environ["USERPROFILE"]) / "AppData/Roaming/.minecraft"


# ----------------------------
# USERNAME
# ----------------------------
def load_username():
    try:
        with open("launcher_account.json", "r") as f:
            return json.load(f).get("username", "Player")
    except:
        return "Player"


username = load_username()


# ----------------------------
# LOAD VERSION JSON (WITH INHERITANCE)
# ----------------------------
def load_version_json(version_name):
    path = MC_DIR / "versions" / version_name / f"{version_name}.json"
    data = json.loads(path.read_text())

    if "inheritsFrom" in data:
        parent = load_version_json(data["inheritsFrom"])
        merged = parent.copy()
        merged["libraries"] = parent.get("libraries", []) + data.get("libraries", [])
        merged.update({k: v for k, v in data.items() if k != "libraries"})
        return merged

    return data


# ----------------------------
# FIND REAL MINECRAFT CLIENT JAR
# ----------------------------
def get_client_jar(version_name):
    jar = MC_DIR / "versions" / version_name / f"{version_name}.jar"
    if jar.exists():
        return jar

    raise RuntimeError(f"Missing Minecraft jar: {jar}")


# ----------------------------
# FIND FABRIC LOADER JAR
# ----------------------------
def find_fabric_loader():
    base = MC_DIR / "libraries" / "net" / "fabricmc" / "fabric-loader"
    for version in sorted(base.iterdir(), reverse=True):
        jar = version / f"fabric-loader-{version.name}.jar"
        if jar.exists():
            return jar
    raise RuntimeError("Fabric loader jar not found")


# ----------------------------
# BUILD CLASSPATH (CRITICAL FIX)
# ----------------------------
def build_classpath(libraries, client_jar, fabric_loader):
    cp = []

    for lib in libraries:
        if "name" in lib:
            group, artifact, version = lib["name"].split(":")[:3]
            path = Path(group.replace(".", "/")) / artifact / version
            jar = MC_DIR / "libraries" / path / f"{artifact}-{version}.jar"

            if jar.exists():
                cp.append(str(jar))

    # ORDER MATTERS (YES, REALLY)
    cp.append(str(fabric_loader))   # Fabric loader FIRST
    cp.append(str(client_jar))      # Minecraft jar LAST

    return ";".join(cp)


# ----------------------------
# NATIVES
# ----------------------------
def extract_natives(libraries, natives_dir):
    natives_dir.mkdir(exist_ok=True)

    for lib in libraries:
        if "downloads" in lib and "classifiers" in lib["downloads"]:
            for obj in lib["downloads"]["classifiers"].values():
                jar_path = MC_DIR / "libraries" / obj["path"]
                if jar_path.exists():
                    with zipfile.ZipFile(jar_path) as z:
                        z.extractall(natives_dir)


# ----------------------------
# LAUNCH FABRIC
# ----------------------------
def launch_fabric(version_name):
    data = load_version_json(version_name)

    client_jar = get_client_jar(data["inheritsFrom"])  # CRITICAL FIX
    fabric_loader = find_fabric_loader()

    natives = MC_DIR / "versions" / version_name / "natives"

    print("Building classpath...")
    cp = build_classpath(data.get("libraries", []), client_jar, fabric_loader)

    print("Extracting natives...")
    extract_natives(data.get("libraries", []), natives)

    args = [
        "--gameDir", str(MC_DIR),
        "--assetsDir", str(MC_DIR / "assets"),
        "--assetIndex", data.get("assetIndex", {}).get("id"),
        "--username", username,
        "--uuid", "00000000-0000-0000-0000-000000000000",
        "--accessToken", "0",
        "--versionType", "release"
    ]

    print("Launching Fabric...")
    subprocess.run([
        JAVA,
        "-cp", cp,
        f"-Djava.library.path={natives}",
        "net.fabricmc.loader.impl.launch.knot.KnotClient"
    ] + args)


# ----------------------------
# MAIN
# ----------------------------
def launch_minecraft():
    versions = sorted([v.name for v in (MC_DIR / "versions").iterdir() if v.is_dir()])

    # ONLY KEEP FABRIC
    fabric_versions = [v for v in versions if "fabric-loader" in v.lower()]

    if not fabric_versions:
        print("No Fabric versions found.")
        return

    for i, v in enumerate(fabric_versions):
        print(f"{i}: {v}")

    choice = int(input("Select Fabric version: "))
    version = fabric_versions[choice]

    launch_fabric(version)


if __name__ == "__main__":
    launch_minecraft()import json
import os
import subprocess
import zipfile
from pathlib import Path

JAVA = r"C:\Program Files\Java\jdk-21.0.11\bin\java.exe"
MC_DIR = Path(os.environ["USERPROFILE"]) / "AppData/Roaming/.minecraft"


# ----------------------------
# USERNAME
# ----------------------------
def load_username():
    try:
        with open("launcher_account.json", "r") as f:
            return json.load(f).get("username", "Player")
    except:
        return "Player"


username = load_username()


# ----------------------------
# LOAD VERSION JSON (WITH INHERITANCE)
# ----------------------------
def load_version_json(version_name):
    path = MC_DIR / "versions" / version_name / f"{version_name}.json"
    data = json.loads(path.read_text())

    if "inheritsFrom" in data:
        parent = load_version_json(data["inheritsFrom"])
        merged = parent.copy()
        merged["libraries"] = parent.get("libraries", []) + data.get("libraries", [])
        merged.update({k: v for k, v in data.items() if k != "libraries"})
        return merged

    return data


# ----------------------------
# FIND REAL MINECRAFT CLIENT JAR
# ----------------------------
def get_client_jar(version_name):
    jar = MC_DIR / "versions" / version_name / f"{version_name}.jar"
    if jar.exists():
        return jar

    raise RuntimeError(f"Missing Minecraft jar: {jar}")


# ----------------------------
# FIND FABRIC LOADER JAR
# ----------------------------
def find_fabric_loader():
    base = MC_DIR / "libraries" / "net" / "fabricmc" / "fabric-loader"
    for version in sorted(base.iterdir(), reverse=True):
        jar = version / f"fabric-loader-{version.name}.jar"
        if jar.exists():
            return jar
    raise RuntimeError("Fabric loader jar not found")


# ----------------------------
# BUILD CLASSPATH (CRITICAL FIX)
# ----------------------------
def build_classpath(libraries, client_jar, fabric_loader):
    cp = []

    for lib in libraries:
        if "name" in lib:
            group, artifact, version = lib["name"].split(":")[:3]
            path = Path(group.replace(".", "/")) / artifact / version
            jar = MC_DIR / "libraries" / path / f"{artifact}-{version}.jar"

            if jar.exists():
                cp.append(str(jar))

    # ORDER MATTERS (YES, REALLY)
    cp.append(str(fabric_loader))   # Fabric loader FIRST
    cp.append(str(client_jar))      # Minecraft jar LAST

    return ";".join(cp)


# ----------------------------
# NATIVES
# ----------------------------
def extract_natives(libraries, natives_dir):
    natives_dir.mkdir(exist_ok=True)

    for lib in libraries:
        if "downloads" in lib and "classifiers" in lib["downloads"]:
            for obj in lib["downloads"]["classifiers"].values():
                jar_path = MC_DIR / "libraries" / obj["path"]
                if jar_path.exists():
                    with zipfile.ZipFile(jar_path) as z:
                        z.extractall(natives_dir)


# ----------------------------
# LAUNCH FABRIC
# ----------------------------
def launch_fabric(version_name):
    data = load_version_json(version_name)

    client_jar = get_client_jar(data["inheritsFrom"])  # CRITICAL FIX
    fabric_loader = find_fabric_loader()

    natives = MC_DIR / "versions" / version_name / "natives"

    print("Building classpath...")
    cp = build_classpath(data.get("libraries", []), client_jar, fabric_loader)

    print("Extracting natives...")
    extract_natives(data.get("libraries", []), natives)

    args = [
        "--gameDir", str(MC_DIR),
        "--assetsDir", str(MC_DIR / "assets"),
        "--assetIndex", data.get("assetIndex", {}).get("id"),
        "--username", username,
        "--uuid", "00000000-0000-0000-0000-000000000000",
        "--accessToken", "0",
        "--versionType", "release"
    ]

    print("Launching Fabric...")
    subprocess.run([
        JAVA,
        "-cp", cp,
        f"-Djava.library.path={natives}",
        "net.fabricmc.loader.impl.launch.knot.KnotClient"
    ] + args)


# ----------------------------
# MAIN
# ----------------------------
def launch_minecraft():
    versions = sorted([v.name for v in (MC_DIR / "versions").iterdir() if v.is_dir()])

    for i, v in enumerate(versions):
        print(f"{i}: {v}")

    choice = int(input("Select Fabric version: "))
    version = versions[choice]

    launch_fabric(version)


if __name__ == "__main__":
    launch_minecraft()
