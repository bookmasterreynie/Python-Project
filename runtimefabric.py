import json
import os
import subprocess
import zipfile
from pathlib import Path

MC_DIR = Path(os.environ["USERPROFILE"]) / "AppData/Roaming/.minecraft"

def get_java_path(data):
    fallback = r"C:\Program Files\Java\jdk-25.0.3\bin\java.exe"

    component = data.get("javaVersion", {}).get("component")

    if not component:
        print("No javaVersion found, using fallback Java")
        return fallback

    java_path = (
        MC_DIR /
        "runtime" /
        "windows-x64" /
        component /
        "bin" /
        "java.exe"
    )

    print("Java runtime:")
    print(java_path)

    if java_path.exists():
        return str(java_path)

    print("Runtime not found, using fallback Java")
    return fallback

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

        libraries = {}

        # parent first
        for lib in parent.get("libraries", []):
            if "name" in lib:
                libraries[lib["name"].split(":")[0] + ":" + lib["name"].split(":")[1]] = lib

        # child overrides parent
        for lib in data.get("libraries", []):
            if "name" in lib:
                libraries[lib["name"].split(":")[0] + ":" + lib["name"].split(":")[1]] = lib

        merged = parent.copy()
        merged["libraries"] = list(libraries.values())

        for key, value in data.items():
            if key != "libraries":
                merged[key] = value

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
def find_fabric_loader(libraries):
    for lib in libraries:
        if lib.get("name", "").startswith("net.fabricmc:fabric-loader:"):
            version = lib["name"].split(":")[2]

            jar = (
                MC_DIR /
                "libraries" /
                "net/fabricmc/fabric-loader" /
                version /
                f"fabric-loader-{version}.jar"
            )

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

    JAVA = get_java_path(data)

    client_jar = get_client_jar(data["inheritsFrom"])  # CRITICAL FIX
    fabric_loader = find_fabric_loader(data.get("libraries", []))

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
    launch_minecraft()