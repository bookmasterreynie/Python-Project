# Minecraft Launcher
Custom Minecraft launcher. Minecraft files not included. (Only Windows supported right now)

These files must be in a folder called "launcher" in this folder: C:\Users\User\AppData\Roaming\.minecraft

Copy this line into your command terminal: "pip install pygame PyOpenGL PyOpenGL_accelerate pillow" (this will only work if you have python installed, and added to your PATH) It only needs to be used once. Once dependencies are installed, to run the launcher, simply double-click the file called Launcher.

The skin renderers load "skin.png" 

I am activly working on updating it beyond a basic launcher.

The runtime launchers should run out of the box without extra installs, but the bare Fabric and launch versions require manual java downloads. Double-check your path in the file.

Current Features in Progress:
  - Skin Loader
  - Skin Preview
  - Online Play (within people with this same launcher)
      - this project is intended to be fully functional with 100% control without having to go through Mojang's servers. So, as a result, this            will only work within a closed community
  - User accounts
  - Skin Customizer
  - Mod Loader/Management
