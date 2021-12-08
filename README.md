# KK Blender Porter Pack
Plugin pack for exporting and setting up Koikatsu characters in Blender.  

The ```KKBP exporter for Koikatsu``` is used to export the character's mesh, armature and color data. The exported data is then processed by the ```KKBP plugin for Blender``` and the [CATS addon](https://github.com/GiveMeAllYourCats/cats-blender-plugin). Once characters are setup in Blender, they can also be saved as FBX files for use in other programs.   
The changelog for the pack [can be found here.](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/master/Changelog.md)
The pack [also has a barebones wiki here.](https://github.com/FlailingFog/KK-Blender-Shader-Pack/wiki)

# Usage Instructions for V5
### Video instructions (with shading instructions)
Almost finished. For now, [V4's guide is here](https://www.youtube.com/watch?v=xe5A8bOh2Mk&list=PLhiuav2SCuvd5eAOb3Ct1eovFAlgv-iwe)


### Text instructions (without shading instructions)

Prerequisites:
* Install [HF Patch v3.13 or later](https://github.com/ManlyMarco/KK-HF_Patch) for Koikatsu.
* Download [CATS blender plugin](https://github.com/GiveMeAllYourCats/cats-blender-plugin) for Blender

1. Download this repository ZIP using the green CODE button on the top right of the page
2. Open the repository zip > go to the plugins folder > get the KKBP_Exporter.DLL file from KKBP_Exporter.zip
3. Go to your Koikatsu install directory > go to the BepInEx > go to the plugins folder > Place the KKBP_Exporter.DLL file into this folder
4. Start the game, go to the character creator and load your character
5. Click the "Export Model for KKBP" button on the top of the screen
6. Wait for the character to export
7. Copy the entire folder generated by the plugin to your desktop. This folder is located in "Export_PMX" in your koikatsu install directory. The format of this folder is ######_CharacterName. 
8. Open blender and install the CATS addon and the full zip repository zip file (KK-Blender-Shader-Pack-5-merger.zip)
9. Click the Import Model button in CATS and import the .pmx file from the export folder.  
![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/catsimport.png)
9. Click the Finalize PMX file button. This may take a few minutes depending on your hardware. If blender crashes, disable the "Fix eyewhites" toggle before running it  
![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/kkpanel1.png)
10. When that finishes you should be in edit mode (light green box) with some of your hair selected. Enter face select mode on the top left (red box). You can hide the armature in the outliner by clicking the eye on the top right (dark green box). Shift + Click any face on any hair that isn't highlighted. This will highlight the face and also highlight the material the face is using on the material panel. In the screenshot, I have just shift + clicked the cf_m_hair_f_31_00 material, so it is highlighted. Once the face is highlighted, click the Select button on the material panel (yellow box). Continue this until all hair is selected. Do not select any hair accessories like hair bands or hair ties. You can undo a selection using ctrl + Z or by using the Deselect button on the material panel. ![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/hairselection.png)
11. When all hair is selected, press the P key to separate the hair by selection  
![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/hairseparate.png)
12. Rename the separated hair object in the outliner to "Hair"  
![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/rename.png)
13. (Optional) Separate and rename any other objects if you want (accessories, underwear, etc). 
14. Click the Import KK Shader and textures button. Choose the folder that contains the .pmx file. Your character should look black and yellow like this  
![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/importtemplates.png)
16. Click the Convert and Apply colors button. Choose the folder that contains the .pmx file again. Your character should have the correct colors now.  
![ ](https://github.com/FlailingFog/KK-Blender-Shader-Pack/blob/assets/readme/importcolors.png)
18. Edit the armature if you need to
19. Edit the shaders to get the exact look you want. This includes editing the detail mask intensities, hair highlights, eye scaling, dark colors etc

Exporting:
1. Click the "prep things for export button"
2. 

