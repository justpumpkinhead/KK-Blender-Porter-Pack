'''
IMPORT TEXTURES SCRIPT
- Loads the material templates from the KK shader .blend
- Loads in the textures received from the KKBP Exporter
Usage:
- Click the button and choose the folder that contains the textures

Texture Postfix Legend:

    _MT_CT -> _MainTex_ColorTexture
    _MT_DT -> _MainTex_DarkenedColorTexture
    _MT -> _MainTex
    _AM -> _AlphaMask
    _CM -> _ColorMask
    _DM -> _DetailMask
    _LM -> _LineMask
    _NM -> _NormalMask
    _NMP -> _NormalMap
    _NMPD -> _NormalMapDetail
    _ot1 -> _overtex1
    _ot2 -> _overtex2
    _ot3 -> _overtex3
    _lqdm -> _liquidmask
    _HGLS -> _HairGloss
    _T2 -> _Texture2
    _T3 -> _Texture3
    _T4 -> _Texture4
    _T5 -> _Texture5
    _T6 -> _Texture6
    _T7 -> _Texture7
    _PM1 -> _PatternMask1
    _PM1 -> _PatternMask2
    _PM1 -> _PatternMask3
        
'''

import bpy, os, traceback, json, time, sys
from pathlib import Path
from .. import common as c
from .cleanarmature import get_bone_list
from .darkcolors import create_darktex

#Stop if this is the wrong folder
def wrong_folder_error(self, context):
    self.layout.label(text="The PMX folder was not selected. (Hint: go into the .pmx folder before confirming)")

#Stop if no face mc or body mc files were found
def missing_texture_error(self, context):
    self.layout.label(text="The files cf_m_body_CM.png and cf_m_face_00_CM.png were not found in the folder.\nMake sure to open the exported folder. \nHit undo and try again")

#Stop if lightning boy shader is not installed
def missing_lbs(self, context):
    text = "An error occured when adding a Lightning Boy Shader node. Make sure it's installed."
    c.kklog(text, 'error')
    self.layout.label(text=text)

def get_templates_and_apply(directory, use_fake_user):
    
    #Clean material list
    bpy.ops.object.mode_set(mode='OBJECT')
    armature = bpy.data.objects['Armature']    
    armature.hide = False
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')
    for ob in bpy.context.view_layer.objects:
        if ob.type == 'MESH':
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
    
    armature.hide = True
    bpy.ops.object.material_slot_remove_unused()
    
    #import all material templates
    fileList = Path(directory).glob('*.*')
    files = [file for file in fileList if file.is_file()]
    
    pmx_file_missing = True
    for file in files:
        if '.pmx' in str(file):
            pmx_file_missing = False
    if pmx_file_missing:
        bpy.context.window_manager.popup_menu(wrong_folder_error, title="Error", icon='ERROR')
        return True

    blend_file_missing = True
    for file in files:
        if '.blend' in str(file) and '.blend1' not in str(file) and 'KK Shader' in str(file):
            filepath = str(file)
            blend_file_missing = False
    
    if blend_file_missing:
        #grab it from the plugin directory
        script_dir=Path(__file__).parent
        template_path=(script_dir / '../KK Shader V6.0.blend').resolve()
        filepath = str(template_path)
    
    innerpath = 'Material'
    templateList = [
        'KK Body',
        'KK Outline',
        'KK Body Outline',
        'KK Tears',
        'KK Gag00',
        'KK Gag01',
        'KK Gag02',
        'KK EyeR (hitomi)',
        'KK EyeL (hitomi)',
        'KK Eyebrows (mayuge)',
        'KK Eyeline down',
        'KK Eyeline Kage',
        'KK Eyeline up',
        'KK Eyewhites (sirome)',
        'KK Face',
        'KK General',
        'KK Hair',
        'KK Mixed Metal or Shiny',
        'KK Nose',
        'KK Shadowcast',
        'KK Teeth (tooth)',
        'KK Fangs (tooth.001)',
        'KK Simple'
    ]

    for template in templateList:
        bpy.ops.wm.append(
            filepath=os.path.join(filepath, innerpath, template),
            directory=os.path.join(filepath, innerpath),
            filename=template,
            set_fake=use_fake_user
            )
    
    #import gfn face node group, cycles node groups as well
    for group in ['Raw Shading (face)', 'Cycles', 'Cycles no shadows', 'LBS', 'LBS face normals']:
        bpy.ops.wm.append(
                filepath=os.path.join(filepath, 'NodeTree', group),
                directory=os.path.join(filepath, 'NodeTree'),
                filename=group,
                set_fake=use_fake_user
                )
    
    #Replace all materials on the body with templates
    body = bpy.data.objects['Body']
    def swap_body_material(original, template):
        try:
            body.material_slots[original].material = bpy.data.materials[template]
        except:
            c.kklog('material or template wasn\'t found: ' + original + ' / ' + template, 'warn')
    
    swap_body_material(body['SMR materials']['cf_O_face'],'KK Face')
    swap_body_material(body['SMR materials']['cf_O_mayuge'],'KK Eyebrows (mayuge)')
    swap_body_material(body['SMR materials']['cf_O_noseline'],'KK Nose')
    swap_body_material(body['SMR materials']['cf_O_eyeline'],'KK Eyeline up')
    swap_body_material(body['SMR materials']['cf_O_eyeline_low'],'KK Eyeline down')
    swap_body_material('cf_m_eyeline_kage','KK Eyeline Kage')
    swap_body_material('Eyeline_Over','KK Eyeline Kage')
    swap_body_material(body['SMR materials']['cf_Ohitomi_L'],'KK Eyewhites (sirome)')
    swap_body_material(body['SMR materials']['cf_Ohitomi_R'],'KK Eyewhites (sirome)')
    swap_body_material(body['SMR materials']['cf_Ohitomi_L02'],'KK EyeL (hitomi)')
    swap_body_material(body['SMR materials']['cf_Ohitomi_R02'],'KK EyeR (hitomi)')
    swap_body_material(body['SMR materials']['o_body_a'],'KK Body') #female
    swap_body_material(body['SMR materials']['cf_O_tooth'],'KK Teeth (tooth)')
    swap_body_material(body['SMR materials']['cf_O_tooth'] + '.001','KK Fangs (tooth.001)')
    swap_body_material(body['SMR materials']['o_tang'],'KK General')
    
    #Make the tongue material unique so parts of the General Template aren't overwritten
    tongue_template = bpy.data.materials['KK General'].copy()
    tongue_template.name = 'KK Tongue'
    body.material_slots['KK General'].material = tongue_template
    
    #Make the texture group unique
    newNode = tongue_template.node_tree.nodes['Gentex'].node_tree.copy()
    tongue_template.node_tree.nodes['Gentex'].node_tree = newNode
    newNode.name = 'Tongue Textures'
    
    #Make the shader group unique
    newNode = tongue_template.node_tree.nodes['Shader'].node_tree.copy()
    tongue_template.node_tree.nodes['Shader'].node_tree = newNode
    newNode.name = 'Tongue Shader'
    
    #Make sure the hair object's name is correctly capitalized
    try:
        bpy.data.objects['hair'].name = 'Hair'
    except:
        try:
            bpy.data.objects['HAIR'].name = 'Hair'
        except:
            #The hair object's name was already correctly capitalized
            pass
    
    #Replace all of the Hair materials with hair templates and name accordingly
    hair_objects = [obj for obj in bpy.data.objects if 'Hair Outfit ' in obj.name]
    for hair in hair_objects:
        for original_material in hair.material_slots:
            template = bpy.data.materials['KK Hair'].copy()
            template.name = 'KK ' + original_material.name
            original_material.material = bpy.data.materials[template.name]
    
    outfit_objects = [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and 'Hair Outfit ' not in obj.name]
    #Replace all other materials with the general template and name accordingly
    for ob in outfit_objects:
        for original_material in ob.material_slots:
            template = bpy.data.materials['KK General'].copy()
            template.name = 'KK ' + original_material.name
            original_material.material = bpy.data.materials[template.name]
    
    #give the shadowcast object a template as well
    if bpy.data.objects.get('Shadowcast'):
        shadowcast = bpy.data.objects['Shadowcast']
        template = bpy.data.materials['KK Shadowcast']
        shadowcast.material_slots[0].material = bpy.data.materials[template.name]

    #give the tears a material template
    if bpy.data.objects.get('Tears'):
        tears = bpy.data.objects['Tears']
        template = bpy.data.materials['KK Tears']
        tears.material_slots[0].material = bpy.data.materials[template.name]

    #give the rigged tongue the existing material template
    if bpy.data.objects.get('Tongue (rigged)'):
        tongue = bpy.data.objects['Tongue (rigged)']
        tongue.material_slots[0].material = bpy.data.materials['KK Tongue']

    #give the gag eyes a material template if they exist and have shapekeys setup
    if bpy.data.objects.get('Gag Eyes'):
        gag = bpy.data.objects['Gag Eyes']
        gag.material_slots[body['SMR materials']['cf_O_gag_eye_00']].material = bpy.data.materials['KK Gag00']
        gag.material_slots[body['SMR materials']['cf_O_gag_eye_01']].material = bpy.data.materials['KK Gag01']
        gag.material_slots[body['SMR materials']['cf_O_gag_eye_02']].material = bpy.data.materials['KK Gag02']

    # Get rid of the duplicate node groups cause there's a lot
    #stolen from somewhere
    def eliminate(node):
        node_groups = bpy.data.node_groups

        # Get the node group name as 3-tuple (base, separator, extension)
        (base, sep, ext) = node.node_tree.name.rpartition('.')

        # Replace the numeric duplicate
        if ext.isnumeric():
            if base in node_groups:
                #print("  Replace '%s' with '%s'" % (node.node_tree.name, base))
                node.node_tree.use_fake_user = False
                node.node_tree = node_groups.get(base)

    #--- Search for duplicates in actual node groups
    node_groups = bpy.data.node_groups

    for group in node_groups:
        for node in group.nodes:
            if node.type == 'GROUP':
                eliminate(node)

    #--- Search for duplicates in materials
    mats = list(bpy.data.materials)
    worlds = list(bpy.data.worlds)

    for mat in mats + worlds:
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                if node.type == 'GROUP':
                    eliminate(node)

    

    return False



def get_and_load_textures(directory):
    body = bpy.data.objects['Body']
    bpy.ops.object.mode_set(mode='OBJECT')
    if r"C:\Users" in directory:
        print_directory =  directory[directory.find('\\', 10):]
    elif r"/home" == directory[0:4]:
        print_directory =  directory[directory.find('/', 7):]
    else:
        print_directory = directory
    c.kklog('Getting textures from: ' + print_directory)

    #get images for body object
    fileList = Path(directory).glob('*.*')
    files = [file for file in fileList if file.is_file()]

    #get images from outfit directory based on outfit ID numbers
    id_list = []
    for obj in [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and obj.type == 'MESH']:
        if obj['KKBP outfit ID'] not in id_list:
            id_list.append(obj['KKBP outfit ID'])
    for outfit_id in id_list:
        fileList = Path(directory + (r'/Outfit 0' if (sys.platform == 'linux' or sys.platform == 'darwin') else r'\Outfit 0') + str(outfit_id)).glob('*.*')
        files_to_append = [file for file in fileList if file.is_file()]
        for outfit_file in files_to_append:
            files.append(outfit_file)

    #get shadow colors for each material and store the dictionary on the body object
    for file in files:
        if 'KK_MaterialData.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_material_data = json.load(json_file)
            color_dict = {}
            supporting_entries = ['Shader Forge/create_body', 'Shader Forge/create_head', 'Shader Forge/create_eyewhite', 'Shader Forge/create_eye', 'Shader Forge/create_topN']
            for line in json_material_data:
                if line['MaterialName'] in supporting_entries:
                    line['MaterialName'] = line['MaterialName'].replace('create_','').replace('_create','')
                labels = line['ShaderPropNames']
                data = line['ShaderPropTextures']
                data.extend(line['ShaderPropTextureValues'])
                data.extend(line['ShaderPropColorValues'])
                data.extend(line['ShaderPropFloatValues'])
                data = dict(zip(labels, data))
                for entry in data:
                    if '_ShadowColor ' in entry:
                        color_dict[line['MaterialName']] = data[entry]
                        break
                    #default to [.764, .880, 1] if shadow color is not available for the material
                    color_dict[line['MaterialName']] = {"r":0.764,"g":0.880,"b":1,"a":1}
    body['KKBP shadow colors'] = color_dict

    #open all images into blender and create dark variants if the image is a maintex
    for image in files:
        bpy.ops.image.open(filepath=str(image), use_udim_detecting=False)
        try:
            bpy.data.images[image.name].pack()
        except:
            c.kklog('This image was not automatically loaded in because its name exceeds 64 characters: ' + image.name, type = 'error')
        try:
            skip_list = ['cf_m_gageye', 'cf_m_eyeline', 'cf_m_mayuge', 'cf_m_namida_00', 'cf_m_noseline_00', 'cf_m_sirome_00', 'cf_m_tooth', '_cf_Ohitomi_', 'cf_m_emblem']
            convert_this = True
            for item in skip_list:
                if item in image.name:
                    convert_this = False
            if '_MT_CT' in image.name and convert_this:
                #c.kklog(image.name)
                material_name = image.name[:-10]
                shadow_color = [body['KKBP shadow colors'][material_name]['r'], body['KKBP shadow colors'][material_name]['g'], body['KKBP shadow colors'][material_name]['b']]
                darktex = create_darktex(bpy.data.images[image.name], shadow_color) #create the darktex now and load it in later
        except:
            c.kklog('Tried to create a dark version of {} but it was missing a shadow color. Defaulting to shadow color of [.764, .880, 1].'.format(image.name), type='warn')
            skip_list = ['cf_m_gageye', 'cf_m_eyeline', 'cf_m_mayuge', 'cf_m_namida_00', 'cf_m_noseline_00', 'cf_m_sirome_00', 'cf_m_tooth', '_cf_Ohitomi_', 'cf_m_emblem']
            convert_this = True
            for item in skip_list:
                if item in image.name:
                    convert_this = False
            if '_MT_CT' in image.name and convert_this:
                #c.kklog(image.name)
                material_name = image.name[:-10]
                darktex = create_darktex(bpy.data.images[image.name], [.764, .880, 1]) #create the darktex now and load it in later
    
    #Get texture data for offset and scale
    for file in files:
        if 'KK_TextureData.json' in str(file):
            json_file_path = str(file)
            json_file = open(json_file_path)
            json_tex_data = json.load(json_file)
    
    #Add all textures to the correct places in the body template
    def image_load(mat, group, node, image, raw = False):
        if bpy.data.images.get(image):
            current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image]
            if raw:
                current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image.colorspace_settings.name = 'Raw'
            apply_texture_data_to_image(image, mat, group, node)
        elif 'MainCol' in image:
            if bpy.data.images[image[0:len(image)-4] + '.dds']:
                current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].image = bpy.data.images[image[0:len(image)-4] + '.dds']
            c.kklog('.dds and .png files not found, skipping: ' + image[0:len(image)-4] + '.dds')
        else:
            c.kklog('File not found, skipping: ' + image)
    
    def set_uv_type(mat, group, uvnode, uvtype):
        current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[uvnode].uv_map = uvtype

    #Added node2 for the alpha masks
    def apply_texture_data_to_image(image, mat, group, node, node2 = ''):
        for item in json_tex_data:
            if item["textureName"] == str(image):
                #Apply Offset and Scale
                if node2 == '':
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[0] = item["offset"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.translation[1] = item["offset"]["y"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[0] = item["scale"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].texture_mapping.scale[1] = item["scale"]["y"]
                else:
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[0] = item["offset"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.translation[1] = item["offset"]["y"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[0] = item["scale"]["x"]
                    current_obj.material_slots[mat].material.node_tree.nodes[group].node_tree.nodes[node].node_tree.nodes[node2].texture_mapping.scale[1] = item["scale"]["y"]
                break
    
    current_obj = bpy.data.objects['Body']
    image_load('KK Body', 'Gentex', 'BodyMain', body['SMR materials']['o_body_a'] + '_MT_CT.png')
    image_load('KK Body', 'Gentex', 'Darktex', body['SMR materials']['o_body_a'] + '_MT_DT.png')
    #check there's a maintex, if not there fallback to colors
    if not current_obj.material_slots['KK Body'].material.node_tree.nodes['Gentex'].node_tree.nodes['BodyMain'].image:
        current_obj.material_slots['KK Body'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use maintex instead?'].default_value = 0
    #but if it is, make sure the body darktex is being used as default
    else:
        current_obj.material_slots['KK Body'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use maintex instead?'].default_value = 1
    image_load('KK Body', 'Gentex', 'BodyMC', body['SMR materials']['o_body_a'] + '_CM.png')
    image_load('KK Body', 'Gentex', 'BodyMD', body['SMR materials']['o_body_a'] + '_DM.png') #cfm female
    image_load('KK Body', 'Gentex', 'BodyLine', body['SMR materials']['o_body_a'] + '_LM.png')
    image_load('KK Body', 'Gentex', 'BodyNorm', body['SMR materials']['o_body_a'] + '_NMP_CNV.png')
    image_load('KK Body', 'Gentex', 'BodyNormDetail', body['SMR materials']['o_body_a'] + '_NMPD_CNV.png')

    image_load('KK Body', 'Gentex', 'BodyMD', 'cm_m_body_DM.png') #cmm male
    image_load('KK Body', 'Gentex', 'BodyLine', 'cm_m_body_LM.png')
    
    image_load('KK Body', 'NSFWTextures', 'Genital', body['SMR materials']['o_body_a'] + '_MT.png') #chara main texture
    image_load('KK Body', 'NSFWTextures', 'Underhair', body['SMR materials']['o_body_a'] + '_ot2.png') #pubic hair

    image_load('KK Body', 'NSFWTextures', 'NipR', body['SMR materials']['o_body_a'] + '_ot1.png') #cfm female
    image_load('KK Body', 'NSFWTextures', 'NipL', body['SMR materials']['o_body_a'] + '_ot1.png')
    image_load('KK Body', 'NSFWTextures', 'NipR', 'cm_m_body_ot1.png') #cmm male
    image_load('KK Body', 'NSFWTextures', 'NipL', 'cm_m_body_ot1.png')

    image_load('KK Body', 'Gentex', 'overone', body['SMR materials']['o_body_a'] + '_T3.png') #body overlays
    image_load('KK Body', 'Gentex', 'overtwo', body['SMR materials']['o_body_a'] + '_T4.png')
    
    set_uv_type('KK Body', 'NSFWpos', 'nippleuv', 'uv_nipple_and_shine')
    set_uv_type('KK Body', 'NSFWpos', 'underuv', 'uv_underhair')

    #find the appropriate alpha mask
    alpha_mask = None
    if bpy.data.images.get(body['SMR materials']['o_body_a'] + '_AM.png'):
        alpha_mask = bpy.data.images.get(body['SMR materials']['o_body_a'] + '_AM.png')
    elif bpy.data.images.get(body['SMR materials']['o_body_a'] + '_AM_00.png'):
        alpha_mask = bpy.data.images.get(body['SMR materials']['o_body_a'] + '_AM_00.png')
    else:
        #check the other alpha mask numbers
        for image in bpy.data.images:
            if '_m_body_AM_' in image.name and image.name[-6:-4].isnumeric():
                alpha_mask = image
                break
    if alpha_mask:
        current_obj.material_slots['KK Body'].material.node_tree.nodes['Gentex'].node_tree.nodes['Bodyalpha'].image = bpy.data.images[alpha_mask.name] #female
        apply_texture_data_to_image(alpha_mask.name, 'KK Body', 'Gentex', 'Bodyalpha')
    else:
        #disable transparency if no alpha mask is present
        current_obj.material_slots['KK Body'].material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].inputs['Built in transparency toggle'].default_value = 0

    image_load('KK Face', 'Gentex', 'FaceMain', body['SMR materials']['cf_O_face'] + '_MT_CT.png')
    image_load('KK Face', 'Gentex', 'Darktex', body['SMR materials']['cf_O_face'] + '_MT_DT.png')
    #default to colors if there's no face maintex
    if not current_obj.material_slots['KK Face'].material.node_tree.nodes['Gentex'].node_tree.nodes['FaceMain'].image:
        current_obj.material_slots['KK Face'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use maintex instead?'].default_value = 0
    else:
        current_obj.material_slots['KK Face'].material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use maintex instead?'].default_value = 1        
    image_load('KK Face', 'Gentex', 'FaceMC', body['SMR materials']['cf_O_face'] + '_CM.png')
    image_load('KK Face', 'Gentex', 'FaceMD', body['SMR materials']['cf_O_face'] + '_DM.png')
    image_load('KK Face', 'Gentex', 'BlushMask', body['SMR materials']['cf_O_face'] + '_T4.png')
    image_load('KK Face', 'Gentex', 'FaceTongue', body['SMR materials']['cf_O_face'] + '_MT.png') #face main texture
    
    image_load('KK Face', 'Gentex', 'linemask', body['SMR materials']['cf_O_face'] + '_LM.png')
    image_load('KK Face', 'Gentex', 'lowerlip', body['SMR materials']['cf_O_face'] + '_T5.png')

    image_load('KK Face', 'Gentex', 'lipstick', body['SMR materials']['cf_O_face'] + '_ot1.png')
    image_load('KK Face', 'Gentex', 'flush', body['SMR materials']['cf_O_face'] + '_ot2.png')
    image_load('KK Face', 'Gentex', 'overlay1', body['SMR materials']['cf_O_face'] + '_T6.png')
    image_load('KK Face', 'Gentex', 'overlay2', body['SMR materials']['cf_O_face'] + '_T7.png')
    image_load('KK Face', 'Gentex', 'overlay3', body['SMR materials']['cf_O_face'] + '_T8.png')
    image_load('KK Face', 'Gentex', 'EyeshadowMask', body['SMR materials']['cf_O_face'] + '_ot3.png')
    set_uv_type('KK Face', 'Facepos', 'eyeshadowuv', 'uv_eyeshadow')  #face extra texture
    
    image_load('KK Eyebrows (mayuge)', 'Gentex', 'Eyebrow', body['SMR materials']['cf_O_mayuge'] + '_MT_CT.png')
    image_load('KK Nose', 'Gentex', 'Nose', body['SMR materials']['cf_O_noseline'] + '_MT_CT.png')
    image_load('KK Teeth (tooth)', 'Gentex', 'Teeth', body['SMR materials']['cf_O_tooth'] + '_MT_CT.png')
    image_load('KK Eyewhites (sirome)', 'Gentex', 'Eyewhite', body['SMR materials']['cf_Ohitomi_R'] + '_MT_CT.png')
    
    image_load('KK Eyeline up', 'Gentex', 'EyelineUp', body['SMR materials']['cf_O_eyeline'] + '_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineUp.001', body['SMR materials']['cf_O_eyeline'] + '_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineDown', body['SMR materials']['cf_O_eyeline_low'] + '_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineDown.001', body['SMR materials']['cf_O_eyeline_low'] + '_MT_CT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineKage', 'cf_m_eyeline_kage_MT.png')
    image_load('KK Eyeline up', 'Gentex', 'EyelineKage', 'Eyeline_Over_MT_CT.png')
    
    image_load('KK EyeR (hitomi)', 'Gentex', 'eyeAlpha', body['SMR materials']['cf_Ohitomi_R02'] + '_MT_CT.png')
    image_load('KK EyeR (hitomi)', 'Gentex', 'EyeHU', body['SMR materials']['cf_Ohitomi_R02'] + '_ot1.png')
    image_load('KK EyeR (hitomi)', 'Gentex', 'EyeHD', body['SMR materials']['cf_Ohitomi_R02'] + '_ot2.png')
    image_load('KK EyeR (hitomi)', 'Gentex', 'expression0', body['SMR materials']['cf_Ohitomi_R'] + '_cf_t_expression_00_EXPR.png')
    image_load('KK EyeR (hitomi)', 'Gentex', 'expression1', body['SMR materials']['cf_Ohitomi_R'] + '_cf_t_expression_01_EXPR.png')

    image_load('KK EyeL (hitomi)', 'Gentex', 'eyeAlpha', body['SMR materials']['cf_Ohitomi_L02'] + '_MT_CT.png')
    image_load('KK EyeL (hitomi)', 'Gentex', 'EyeHU', body['SMR materials']['cf_Ohitomi_L02'] + '_ot1.png')
    image_load('KK EyeL (hitomi)', 'Gentex', 'EyeHD', body['SMR materials']['cf_Ohitomi_L02'] + '_ot2.png')
    image_load('KK EyeL (hitomi)', 'Gentex', 'expression0', body['SMR materials']['cf_Ohitomi_L02'] + '_cf_t_expression_00_EXPR.png')
    image_load('KK EyeL (hitomi)', 'Gentex', 'expression1', body['SMR materials']['cf_Ohitomi_L02'] + '_cf_t_expression_01_EXPR.png')
    
    image_load('KK Tongue', 'Gentex', 'Maintex', body['SMR materials']['o_tang'] + '_CM.png') #done on purpose
    image_load('KK Tongue', 'Gentex', 'MainCol', body['SMR materials']['o_tang'] + '_CM.png')
    image_load('KK Tongue', 'Gentex', 'MainDet', body['SMR materials']['o_tang'] + '_DM.png')
    image_load('KK Tongue', 'Gentex', 'MainNorm', body['SMR materials']['o_tang'] + '_NMP.png')
    image_load('KK Tongue', 'Gentex', 'MainNormDetail', body['SMR materials']['o_tang'] + '_NMP_CNV.png') #load regular map by default
    image_load('KK Tongue', 'Gentex', 'MainNormDetail', body['SMR materials']['o_tang'] + '_NMPD_CNV.png') #then the detail map if it's there

    #load all gag eyes in if it exists
    if bpy.data.objects.get('Gag Eyes'):
        current_obj = bpy.data.objects['Gag Eyes']
        image_load('KK Gag00', 'Gentex', '00gag00', body['SMR materials']['cf_O_gag_eye_00'] + '_cf_t_gageye_00_MT_CT.png')
        image_load('KK Gag00', 'Gentex', '00gag02', body['SMR materials']['cf_O_gag_eye_00'] + '_cf_t_gageye_02_MT_CT.png')
        image_load('KK Gag00', 'Gentex', '00gag04', body['SMR materials']['cf_O_gag_eye_00'] + '_cf_t_gageye_04_MT_CT.png')
        image_load('KK Gag00', 'Gentex', '00gag05', body['SMR materials']['cf_O_gag_eye_00'] + '_cf_t_gageye_05_MT_CT.png')
        image_load('KK Gag00', 'Gentex', '00gag06', body['SMR materials']['cf_O_gag_eye_00'] + '_cf_t_gageye_06_MT_CT.png')

        image_load('KK Gag01', 'Gentex', '01gag03', body['SMR materials']['cf_O_gag_eye_01'] + '_cf_t_gageye_03_MT_CT.png')
        image_load('KK Gag01', 'Gentex', '01gag01', body['SMR materials']['cf_O_gag_eye_01'] + '_cf_t_gageye_01_MT_CT.png')

        image_load('KK Gag02', 'Gentex', '02gag07', body['SMR materials']['cf_O_gag_eye_02'] + '_cf_t_gageye_07_MT_CT.png')
        image_load('KK Gag02', 'Gentex', '02gag08', body['SMR materials']['cf_O_gag_eye_02'] + '_cf_t_gageye_08_MT_CT.png')
        image_load('KK Gag02', 'Gentex', '02gag09', body['SMR materials']['cf_O_gag_eye_02'] + '_cf_t_gageye_09_MT_CT.png')

    #load the tears texture in
    if bpy.data.objects.get('Tears'):
        current_obj = bpy.data.objects['Tears']
        image_load('KK Tears', 'Gentex', 'Maintex', body['SMR materials']['cf_O_namida_L'] + '_MT_CT.png')

    #for each material slot in each hair object, load in the hair detail mask, colormask
    hair_objects = [obj for obj in bpy.data.objects if 'Hair Outfit ' in obj.name]
    for current_obj  in hair_objects:
        for hairMat in current_obj.material_slots:
            hairType = hairMat.name.replace('KK ','')
            
            #make a copy of the node group, use it to replace the current node group and rename it so each piece of hair has it's own unique hair texture group
            newNode = hairMat.material.node_tree.nodes['Gentex'].node_tree.copy()
            hairMat.material.node_tree.nodes['Gentex'].node_tree = newNode
            newNode.name = hairType + ' Textures'
            
            image_load(hairMat.name, 'Gentex', 'hairMainTex',  hairType+'_MT_CT.png')
            image_load(hairMat.name, 'Gentex', 'hairDetail', hairType+'_DM.png')
            image_load(hairMat.name, 'Gentex', 'hairFade',   hairType+'_CM.png')
            image_load(hairMat.name, 'Gentex', 'hairShine',  hairType+'_HGLS.png')
            image_load(hairMat.name, 'Gentex', 'hairAlpha',  hairType+'_AM.png')
            set_uv_type(hairMat.name, 'Hairpos', 'hairuv', 'uv_nipple_and_shine')

            #If no alpha mask wasn't loaded in disconnect the hair alpha node to make sure this piece of hair is visible
            if hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image == None and hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image == None:
                getOut = hairMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Group Output'].inputs['Hair alpha'].links[0]
                hairMat.material.node_tree.nodes['Gentex'].node_tree.links.remove(getOut)
    
    # Loop through each material in the general object and load the textures, if any, into unique node groups
    # also make unique shader node groups so all materials are unique
    # make a copy of the node group, use it to replace the current node group
    outfit_objects = [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and 'Hair Outfit ' not in obj.name and obj.type == 'MESH']
    for object in outfit_objects:
        current_obj = object
        for genMat in current_obj.material_slots:
            genType = genMat.name.replace('KK ','')
            
            #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique texture group
            newNode = genMat.material.node_tree.nodes['Gentex'].node_tree.copy()
            genMat.material.node_tree.nodes['Gentex'].node_tree = newNode
            newNode.name = genType + ' Textures'

            #make a copy of the node group, use it to replace the current node group and rename it so each mat has a unique position group
            posNode = genMat.material.node_tree.nodes['Genpos'].node_tree.copy()
            genMat.material.node_tree.nodes['Genpos'].node_tree = posNode
            posNode.name = genType + ' Position'

            image_load(genMat.name, 'Gentex', 'Maintexplain', genType+ '_MT.png')
            image_load(genMat.name, 'Gentex', 'Maintex', genType+ '_MT.png')
            image_load(genMat.name, 'Gentex', 'Maintex', genType+'_MT_CT.png')
            image_load(genMat.name, 'Gentex', 'Darktex', genType+'_MT_DT.png')
            image_load(genMat.name, 'Gentex', 'MainCol', genType+'_CM.png')
            image_load(genMat.name, 'Gentex', 'MainDet', genType+'_DM.png')
            image_load(genMat.name, 'Gentex', 'MainNorm', genType+'_NMP.png')
            image_load(genMat.name, 'Gentex', 'MainNormDetail', genType+'_NMPD_CNV.png') #load detail map if it's there
            image_load(genMat.name, 'Gentex', 'Alphamask', genType+'_AM.png')

            # image_load(genMat.name, 'Gentex', 'PatBase', genType+'_PM1.png')
            
            image_load(genMat.name, 'Gentex', 'PatRed', genType+'_PM1.png')
            image_load(genMat.name, 'Gentex', 'PatGreen', genType+'_PM2.png')
            image_load(genMat.name, 'Gentex', 'PatBlue', genType+'_PM3.png')
            
            MainImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
            DarkImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Darktex'].image
            AlphaImage = genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image

            #set dark colors to use the maintex if there was a dark image loaded in
            if DarkImage and 'Template: Pattern Placeholder' not in DarkImage.name:
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use dark maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1

            #Also, make a copy of the General shader node group, as it's unlikely everything using it will be the same color
            newNode = genMat.material.node_tree.nodes['Shader'].node_tree.copy()
            genMat.material.node_tree.nodes['Shader'].node_tree = newNode
            newNode.name = genType + ' Shader'
            
            #If an alpha mask was loaded in, enable the alpha mask toggle in the KK shader
            if  AlphaImage != None:
                toggle = genMat.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['Transparency toggle'].default_value = 1

            #If no main image was loaded in, there's no alpha channel being fed into the KK Shader.
            #Unlink the input node and make the alpha channel pure white
            if  not MainImage:
                getOut = genMat.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].links[0]
                genMat.material.node_tree.nodes['Shader'].node_tree.links.remove(getOut)
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['alphatoggle'].inputs['maintex alpha'].default_value = (1,1,1,1)
            
            #check maintex config
            plainMain = not genMat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintexplain'].image.name == 'Template: Maintex plain placeholder'
            if not MainImage and not plainMain:
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 0

            elif not MainImage and plainMain:
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 0
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

            elif MainImage and not plainMain:
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1

            else: #MainImage and plainMain
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use Maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use colored maintex?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Ignore colormask?'].default_value = 1
                genMat.material.node_tree.nodes['Shader'].node_tree.nodes['colorsDark'].inputs['Use Maintex?'].default_value = 1
    
    #setup face normals
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        armature = bpy.data.objects['Armature']
        armature.hide = False
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        head_location = (armature.data.edit_bones['Head'].tail.x+1, armature.data.edit_bones['Head'].tail.y+1, armature.data.edit_bones['Head'].tail.z+1)
        #c.kklog(head_location)
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.empty_add(type='CUBE', align='WORLD', location=head_location)
        empty = bpy.context.view_layer.objects.active
        empty.location.x -= 1
        empty.location.y -= 1
        empty.location.z -= 1
        empty.scale = (0.15, 0.15, 0.15)
        empty.name = 'GFN Empty'
        #mod = empty.constraints.new(type='CHILD_OF')
        #mod.name = 'GFN Empty'
        #mod.target = armature
        #mod.subtarget = "Head"
        #bpy.ops.constraint.childof_set_inverse(constraint='GFN Empty', owner='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = armature
        empty.select_set(True)
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        armature.data.bones['Head'].select = True
        armature.data.bones.active = armature.data.bones['Head']
        bpy.ops.object.parent_set(type='BONE')
        bpy.ops.pose.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.data.node_groups['Generated Face Normals'].nodes['GFNEmpty'].object = empty
        bpy.context.view_layer.objects.active = empty
        empty.select_set(True)
        bpy.ops.object.move_to_collection(collection_index=1)
        empty.hide = True
        empty.hide_render = True
    except:
        #i don't feel like dealing with any errors related to this
        c.kklog('The GFN empty wasnt setup correctly. Oh well.', 'warn')
        pass
    
    #setup gag eye drivers
    if bpy.data.objects.get('Gag Eyes'):
        gag_keys = [
            'Circle Eyes 1',
            'Circle Eyes 2',
            'Spiral Eyes',
            'Heart Eyes',
            'Fiery Eyes',
            'Cartoony Wink',
            'Vertical Line',
            'Cartoony Closed',
            'Horizontal Line',
            'Cartoony Crying' 
        ]

        body = bpy.data.objects['Body']
        skey_driver = bpy.data.materials['KK Gag00'].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
        skey_driver.driver.type = 'SCRIPTED'
        for key in gag_keys:
            newVar = skey_driver.driver.variables.new()
            newVar.name = key.replace(' ','')
            newVar.type = 'SINGLE_PROP'
            newVar.targets[0].id_type = 'KEY'
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
        skey_driver.driver.expression = '0 if CircleEyes1 else 1 if CircleEyes2 else 2 if CartoonyClosed else 3 if VerticalLine else 4'
        skey_driver = bpy.data.materials['KK Gag00'].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
        skey_driver.driver.type = 'SCRIPTED'
        for key in gag_keys:
            newVar = skey_driver.driver.variables.new()
            newVar.name = key.replace(' ','')
            newVar.type = 'SINGLE_PROP'
            newVar.targets[0].id_type = 'KEY'
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value'
        skey_driver.driver.expression = 'CircleEyes1 or CircleEyes2 or CartoonyClosed or VerticalLine or HorizontalLine'

        skey_driver = bpy.data.materials['KK Gag01'].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
        skey_driver.driver.type = 'SCRIPTED'
        for key in gag_keys:
            newVar = skey_driver.driver.variables.new()
            newVar.name = key.replace(' ','')
            newVar.type = 'SINGLE_PROP'
            newVar.targets[0].id_type = 'KEY'
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
        skey_driver.driver.expression = '0 if HeartEyes else 1'
        skey_driver = bpy.data.materials['KK Gag01'].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
        skey_driver.driver.type = 'SCRIPTED'
        for key in gag_keys:
            newVar = skey_driver.driver.variables.new()
            newVar.name = key.replace(' ','')
            newVar.type = 'SINGLE_PROP'
            newVar.targets[0].id_type = 'KEY'
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
        skey_driver.driver.expression = 'HeartEyes or SpiralEyes'

        skey_driver = bpy.data.materials['KK Gag02'].node_tree.nodes['Parser'].inputs[0].driver_add('default_value')
        skey_driver.driver.type = 'SCRIPTED'
        for key in gag_keys:
            newVar = skey_driver.driver.variables.new()
            newVar.name = key.replace(' ','')
            newVar.type = 'SINGLE_PROP'
            newVar.targets[0].id_type = 'KEY'
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
        skey_driver.driver.expression = '0 if CartoonyCrying else 1 if CartoonyWink else 2'
        skey_driver = bpy.data.materials['KK Gag02'].node_tree.nodes['hider'].inputs[0].driver_add('default_value')
        skey_driver.driver.type = 'SCRIPTED'
        for key in gag_keys:
            newVar = skey_driver.driver.variables.new()
            newVar.name = key.replace(' ','')
            newVar.type = 'SINGLE_PROP'
            newVar.targets[0].id_type = 'KEY'
            newVar.targets[0].id = body.data.shape_keys
            newVar.targets[0].data_path = 'key_blocks["' + key + '"].value' 
        skey_driver.driver.expression = 'CartoonyCrying or CartoonyWink or FieryEyes'

def add_outlines(single_outline_mode):
    #Add face and body outlines, then load in the clothes transparency mask to body outline
    ob = bpy.context.view_layer.objects['Body']
    bpy.context.view_layer.objects.active = ob
    mod = ob.modifiers.new(type='SOLIDIFY', name='Outline Modifier')
    mod.thickness = 0.0005
    mod.offset = 0
    mod.material_offset = len(ob.material_slots)
    mod.use_flip_normals = True
    mod.use_rim = False
    mod.name = 'Outline Modifier'
    mod.show_expanded = False
    
    #face first
    faceOutlineMat = bpy.data.materials['KK Outline'].copy()
    faceOutlineMat.name = 'KK Face Outline'
    ob.data.materials.append(faceOutlineMat)
    faceOutlineMat.blend_method = 'CLIP'

    #body second
    ob.data.materials.append(bpy.data.materials['KK Body Outline'])
    if not bpy.data.materials['KK Body Outline'].node_tree.nodes['Gentex'].node_tree.nodes['Bodyalpha'].image:
        #An alpha mask for the clothing wasn't present in the Textures folder
        bpy.data.materials['KK Body Outline'].node_tree.nodes['Clipping prevention toggle'].inputs[0].default_value = 0            



    #Give each piece of hair with an alphamask on each hair object it's own outline group
    hair_objects = [obj for obj in bpy.data.objects if 'Hair Outfit ' in obj.name]
    if not single_outline_mode:
        for ob in hair_objects:
            bpy.context.view_layer.objects.active = ob
            #Get the length of the material list before starting
            outlineStart = len(ob.material_slots)
            #link all polygons to material name
            mats_to_gons = {}
            for slot in ob.material_slots:
                mats_to_gons[slot.material.name] = []
            for gon in ob.data.polygons:
                    mats_to_gons[ob.material_slots[gon.material_index].material.name].append(gon)
            #find all materials that use an alpha mask or maintex
            alpha_users = []
            for mat in ob.material_slots:
                AlphaImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
                MainImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image
                if AlphaImage or MainImage:
                    alpha_users.append(mat.material.name)
            #reorder material_list to place alpha/maintex users first
            new_mat_list_order = [mat_slot.material.name for mat_slot in ob.material_slots if mat_slot.material.name not in alpha_users]
            new_mat_list_order = alpha_users + new_mat_list_order
            #reorder mat slot list
            for index, mat_slot in enumerate(ob.material_slots):
                mat_slot.material = bpy.data.materials[new_mat_list_order[index]]
            #create empty slots for new alpha user outlines
            for mat in alpha_users:
                ob.data.materials.append(None)
            #fill alpha user outline materials, and fill image node
            for index, mat in enumerate(alpha_users):
                OutlineMat = bpy.data.materials['KK Outline'].copy()
                OutlineMat.name = mat.replace('KK ', 'Outline ')
                AlphaImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['hairAlpha'].image
                MainImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['hairMainTex'].image
                if AlphaImage:
                    OutlineMat.node_tree.nodes['outlinealpha'].image = AlphaImage
                    OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                    OutlineMat.node_tree.nodes['maintexoralpha'].blend_type = 'MULTIPLY'
                elif MainImage:
                    OutlineMat.node_tree.nodes['outlinealpha'].image = MainImage
                    OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                OutlineMat.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
                ob.material_slots[index + outlineStart].material = OutlineMat
            #update polygon material indexes
            for mat in mats_to_gons:
                for gon in mats_to_gons[mat]:
                    gon.material_index = new_mat_list_order.index(mat)

    #Add a general outline that covers the rest of the materials on the hair object that don't need transparency
    for ob in hair_objects:
        bpy.context.view_layer.objects.active = ob
        mod = ob.modifiers.new(
            type='SOLIDIFY',
            name='Outline Modifier')
        mod.thickness = 0.0005
        mod.offset = 1
        mod.material_offset = outlineStart if not single_outline_mode else 200
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.show_expanded = False
        hairOutlineMat = bpy.data.materials['KK Outline'].copy()
        hairOutlineMat.name = 'KK Hair Outline'
        ob.data.materials.append(hairOutlineMat)
        #hide alts
        if ob.name[:12] == 'Hair Outfit ' and ob.name != 'Hair Outfit 00':
            ob.hide = True
            ob.hide_render = True

    #Add a standard outline to all other objects
    outfit_objects = [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and 'Hair Outfit ' not in obj.name and obj.type == 'MESH']
    #keep a dictionary of the material length list for the next loop
    outlineStart = {}
    if not single_outline_mode:
        #If the material has a maintex or alphamask then give it it's own outline, mmdtools style
        for ob in outfit_objects:
            bpy.context.view_layer.objects.active = ob
            
            #Get the length of the material list before starting
            outlineStart[ob.name] = len(ob.material_slots)
            
            #link all polygons to material name
            mats_to_gons = {}
            for slot in ob.material_slots:
                mats_to_gons[slot.material.name] = []
            for gon in ob.data.polygons:
                    mats_to_gons[ob.material_slots[gon.material_index].material.name].append(gon)
            #find all materials that use an alpha mask or maintex
            alpha_users = []
            for mat in ob.material_slots:
                AlphaImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                MainImage = mat.material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                if AlphaImage or MainImage:
                    alpha_users.append(mat.material.name)
            #reorder material_list to place alpha/maintex users first
            new_mat_list_order = [mat_slot.material.name for mat_slot in ob.material_slots if mat_slot.material.name not in alpha_users]
            new_mat_list_order = alpha_users + new_mat_list_order
            #reorder mat slot list
            for index, mat_slot in enumerate(ob.material_slots):
                mat_slot.material = bpy.data.materials[new_mat_list_order[index]]
            #create empty slots for new alpha user outlines
            for mat in alpha_users:
                ob.data.materials.append(None)
            #fill alpha user outline materials, and fill image node
            for index, mat in enumerate(alpha_users):
                OutlineMat = bpy.data.materials['KK Outline'].copy()
                OutlineMat.name = mat.replace('KK ', 'Outline ')
                AlphaImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['Alphamask'].image
                MainImage = ob.material_slots[mat].material.node_tree.nodes['Gentex'].node_tree.nodes['Maintex'].image
                if AlphaImage:
                    OutlineMat.node_tree.nodes['outlinealpha'].image = AlphaImage
                    OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                    OutlineMat.node_tree.nodes['maintexoralpha'].blend_type = 'MULTIPLY'
                elif MainImage:
                    OutlineMat.node_tree.nodes['outlinealpha'].image = MainImage
                    OutlineMat.node_tree.nodes['maintexoralpha'].inputs[0].default_value = 1.0
                OutlineMat.node_tree.nodes['outlinetransparency'].inputs[0].default_value = 1.0
                ob.material_slots[index + outlineStart[ob.name]].material = OutlineMat
            #update polygon material indexes
            for mat in mats_to_gons:
                for gon in mats_to_gons[mat]:
                    gon.material_index = new_mat_list_order.index(mat)

    for ob in outfit_objects:    
        #Add a general outline that covers the rest of the materials on the object that don't need transparency
        bpy.context.view_layer.objects.active = ob
        mod = ob.modifiers.new(
            type='SOLIDIFY',
            name='Outline Modifier')
        mod.thickness = 0.0005
        mod.offset = 1
        mod.material_offset = outlineStart[ob.name] if not single_outline_mode else 200
        mod.use_flip_normals = True
        mod.use_rim = False
        mod.show_expanded = False
        ob.data.materials.append(bpy.data.materials['KK Outline'])
        #hide alts
        if 'Indoor shoes Outfit ' in ob.name or ' shift Outfit ' in ob.name or ' hang Outfit ' in ob.name or (ob.name[:7] == 'Outfit ' and ob.name != 'Outfit 00') or (ob.name[:12] == 'Hair Outfit ' and ob.name != 'Hair Outfit 00'):
            ob.hide = True
            ob.hide_render = True
        
    #hide hair alts
    for obj in [obj for obj in bpy.data.objects if obj.get('KKBP outfit ID') != None and 'Hair Outfit ' in obj.name and obj.name != 'Hair Outfit 00']:
        obj.hide = True



def clean_orphan_data():
    #clean up the oprhaned data
    for block in bpy.data.materials:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.textures.remove(block)
    
    for block in bpy.data.images:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.images.remove(block)
    
    for block in bpy.data.node_groups:
        if block.users == 0 and not block.use_fake_user:
            bpy.data.node_groups.remove(block)

def apply_cycles():
    c.kklog('Applying Cycles adjustments...')
    #taken from https://github.com/FlailingFog/KK-Blender-Porter-Pack/issues/234
    #remove outline modifier
    for o in bpy.context.view_layer.objects:
        for m in o.modifiers:
            if(m.name == "Outline Modifier"):
                m.show_viewport = False
                m.show_render = False
                
    ####fix the eyelash mesh overlap
    # deselect everything and make body active object
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode = 'EDIT')
    # define some stuff
    ops = bpy.ops
    obj = ops.object
    mesh = ops.mesh
    context = bpy.context
    object = context.object
    # edit mode and deselect everything
    obj.mode_set(mode='EDIT')
    mesh.select_all(action='DESELECT')
    # delete eyeline down verts and kage faces
    object.active_material_index = 6
    obj.material_slot_select()
    mesh.delete(type='VERT')
    object.active_material_index = 5
    obj.material_slot_select()
    mesh.delete(type='ONLY_FACE')
    #delete nose if no texture loaded in
    if not bpy.data.node_groups['Nose'].nodes[1].image:
        object.active_material_index = 2
        obj.material_slot_select()
        mesh.delete(type='VERT')
    mesh.select_all(action='DESELECT')

    #add cycles node group
    for tree in [mat.node_tree for mat in bpy.data.materials if 'KK ' in mat.name]:
        nodes = tree.nodes
        links = tree.links
        if nodes.get('Rim') and nodes.get('Shader'):
            nodes['Rim'].node_tree = bpy.data.node_groups['Cycles']
            links.new(nodes['Shader'].outputs['Color out light'], nodes['Rim'].inputs[0])
            links.new(nodes['Shader'].outputs['Color out dark'], nodes['Rim'].inputs[1])
            links.new(nodes['Shader'].outputs[3], nodes['Rim'].inputs[2])
        #disable detail shine color too
        if nodes.get('Shader'):
            if nodes['Shader'].node_tree.nodes.get('colorsLight'):
                if nodes['Shader'].node_tree.nodes['colorsLight'].inputs.get('Detail intensity (shine)'):
                    nodes['Shader'].node_tree.nodes['colorsLight'].inputs['Detail intensity (shine)'].default_value = 0
                    nodes['Shader'].node_tree.nodes['colorsDark']. inputs['Detail intensity (shine)'].default_value = 0
    #remove linemask and blush on face material
    for type in ['colorsLight', 'colorsDark']:
        bpy.data.node_groups['Face Shader'].nodes[type].inputs['Linemask intensity'].default_value = 0
        bpy.data.node_groups['Face Shader'].nodes[type].inputs['Blush intensity'].default_value = 0
    #set eyeline up and eyebrows as shadowless
    for mat in [bpy.data.materials['KK Eyebrows (mayuge)'], bpy.data.materials['KK Eyeline up']]:
        mat.node_tree.nodes['Rim'].node_tree = bpy.data.node_groups['Cycles no shadows']
    
    #put face's color out in a mix shader with the cycles face mask
    #mute shader to rgb nodes for clothing items
    for node in [n for n in bpy.data.node_groups['General overlays'].nodes if 'Shader to RGB' in n.name]:
        node.mute = True

    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.preview_samples = 10
    mesh.select_all(action='DESELECT')
    obj.mode_set(mode='OBJECT')

def apply_lbs():
    c.kklog('Applying Lightning Boy Shader adjustments...')
    #Import lbs node group and replace rim group with the lbs group
    keep_list = ['KK Eyebrows (mayuge)', 'KK EyeL (hitomi)', 'KK EyeR (hitomi)', 'KK Eyeline up']
    for tree in [mat.node_tree for mat in bpy.data.materials if ('KK ' in mat.name and mat.name not in keep_list)]:
        nodes = tree.nodes
        links = tree.links
        if nodes.get('Rim') and nodes.get('Shader'):
            nodes['Rim'].node_tree = bpy.data.node_groups['LBS']
            links.new(nodes['Shader'].outputs['Color out light'], nodes['Rim'].inputs['Color light'])
            links.new(nodes['Shader'].outputs['Color out dark'], nodes['Rim'].inputs['Color dark'])
            links.new(nodes['Shader'].outputs[3], nodes['Rim'].inputs[2])
            #if nodes['Shader'].node_tree.name != 'Body Shader':
            #    links.new(nodes['RawShade'].outputs['Normal passthrough'], nodes['Rim'].inputs[3])
    #construct LBS node group from scratch because it can't be included with the KK shader
    nodes = bpy.data.node_groups['LBS'].nodes
    links = bpy.data.node_groups['LBS'].links
    try:
        LBS = nodes.new('LBSShaderNode')
    except:
        bpy.context.window_manager.popup_menu(missing_lbs, title="Error", icon='ERROR')
        return
    def expand(node):
        node.hide = False
        for sock in node.inputs:
            sock.hide = False
    LBS.initialize_group = ".Lightning Boy Shader"
    LBS.inputs['.transparency'].default_value = 0.001
    LBS.inputs['.transparency'].enabled = False
    LBS.inputs[0].enabled = False
    LBS.layers = 4
    LBS.location = 444.6600, 61.8538
    expand(LBS)
    output = [out for out in nodes if out.type == 'GROUP_OUTPUT'][0]
    output.location = 694.6600, -10.6462
    input =  [out for out in nodes if out.type == 'GROUP_INPUT'][0]
    input.location = -538.7341, 24.3778
    reroute_alpha = nodes.new('NodeReroute')
    reroute_alpha.location = 121.4401, -429.1375
    links.new(input.outputs[2], reroute_alpha.inputs[0])
    links.new(reroute_alpha.outputs[0], LBS.inputs[-3]) #connect alpha through reroute
    reroute_dark = nodes.new('NodeReroute')
    reroute_dark.location = 121.4401, -398.1375
    links.new(input.outputs[1], reroute_dark.inputs[0])
    links.new(reroute_dark.outputs[0], LBS.inputs[-4]) #connect dark
    links.new(LBS.outputs[0], output.inputs[0]) #connect LBS out

    key = nodes.new('LBSBaseNode')
    key.initialize_group = '.Key Light*'
    key.location = 49.4401, -144.1374
    expand(key)
    links.new(input.outputs['Color light'], key.inputs[0])
    links.new(input.outputs['Normal'], key.inputs[5])
    links.new(key.outputs[0], LBS.inputs[-5]) #connect light

    ao = nodes.new('LBSBaseNode')
    ao.initialize_group = '.Ambient Occlusion (SS)'
    ao.location = 49.4401, 109.8626
    expand(ao)
    links.new(input.outputs['Color dark'], ao.inputs[0])
    links.new(ao.outputs[0], LBS.inputs[-6]) #connect light

    rim = nodes.new('LBSBaseNode')
    rim.initialize_group = '.2D Rim Light*'
    rim.location = 49.4401, 423.8625
    expand(rim)
    curves = [out for out in nodes if out.type == 'CURVE_RGB'][0]
    curves.location = -215.5599, 289.3625
    links.new(input.outputs['Color light'], curves.inputs[0])
    links.new(curves.outputs[0], rim.inputs[0])
    links.new(rim.outputs[0], LBS.inputs[-7]) #connect 2d rim

    #turn on ambient occlusion and bloom in render settings
    bpy.context.scene.eevee.use_gtao = True

    #turn on bloom in render settings
    bpy.context.scene.eevee.use_bloom = True

    #face has special normal setup to work with gfn. make a copy and add the normals inside of the copy
    #this group prevents Amb Occ issues around nose, and mouth interior
    face_nodes = bpy.data.node_groups['LBS'].copy()
    face_nodes.use_fake_user = True
    face_nodes.name = 'LBS (Face)'
    nodes = bpy.data.node_groups['LBS (Face)'].nodes
    links = bpy.data.node_groups['LBS (Face)'].links
    face_norms = nodes.new('ShaderNodeGroup')
    face_norms.node_tree = bpy.data.node_groups['LBS face normals']
    face_norms.location = 410, 190
    links.new(face_norms.outputs[0], rim.inputs[-1])
    links.new(face_norms.outputs[0], key.inputs[-1])

    #select entire face and body and reset vectors to prevent Amb Occ seam around the neck 
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode = 'EDIT')
    body.active_material_index = 1
    bpy.ops.object.material_slot_select()
    bpy.ops.mesh.normals_tools(mode='RESET')
    bpy.ops.object.mode_set(mode = 'OBJECT')

def apply_sfw():
    #delete nsfw parts of the mesh
    body = bpy.data.objects['Body']
    bpy.ops.object.select_all(action='DESELECT')
    body.select_set(True)
    bpy.context.view_layer.objects.active=body
    bpy.ops.object.mode_set(mode = 'EDIT')
    def mark_group_as_freestyle(group_list):
        for group in group_list:
            group_found = body.vertex_groups.find(group)      
            if group_found > -1:
                bpy.context.object.active_material_index = group_found
                bpy.ops.object.vertex_group_select()
            else:
                c.kklog('Group wasn\'t found when freestyling vertex groups: ' + group, 'warn')
        bpy.ops.mesh.mark_freestyle_face(clear=False)
    freestyle_list = [
        'cf_j_bnip02_L', 'cf_j_bnip02_R',
        'cf_s_bust03_L', 'cf_s_bust03_R']
    mark_group_as_freestyle(freestyle_list)
    bpy.ops.mesh.select_all(action = 'DESELECT')

    def delete_group_and_bone(group_list):
        #delete vertex groups
        bpy.ops.mesh.select_all(action = 'DESELECT')
        for group in group_list:
            group_found = body.vertex_groups.find(group)      
            if group_found > -1:
                bpy.context.object.vertex_groups.active_index = group_found
                bpy.ops.object.vertex_group_select()
            else:
                c.kklog('Group wasn\'t found when deleting vertex groups: ' + group, 'warn')
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')

    delete_list = ['cf_s_bnip025_L', 'cf_s_bnip025_R',
    'cf_j_kokan', 'cf_j_ana', 'cf_d_ana', 'cf_d_kokan', 'cf_s_ana',
    'Vagina_Root', 'Vagina_B', 'Vagina_F', 'Vagina_001_L', 'Vagina_002_L',
    'Vagina_003_L', 'Vagina_004_L', 'Vagina_005_L',  'Vagina_001_R', 'Vagina_002_R',
    'Vagina_003_R', 'Vagina_004_R', 'Vagina_005_R']
    delete_group_and_bone(delete_list)

    #reload the sfw alpha mask
    body_material = bpy.data.objects['Body'].material_slots['KK Body'].material
    body_material.node_tree.nodes['Gentex'].node_tree.nodes['Bodyalphacustom'].image = bpy.data.images['Template: SFW alpha mask.png']
    bpy.data.node_groups["Body Shader"].nodes["BodyTransp"].inputs[0].default_value = 1 #why do i have to do it this way
    bpy.data.node_groups["Body Shader"].nodes["BodyTransp"].inputs[1].default_value = 1
    body_material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].node_tree.inputs[0].hide_value = True
    body_material.node_tree.nodes['Shader'].node_tree.nodes['BodyTransp'].node_tree.inputs[1].hide_value = True

    #get rid of the nsfw groups on the body
    body_material.node_tree.nodes.remove(body_material.node_tree.nodes['NSFWTextures'])
    body_material.node_tree.nodes.remove(body_material.node_tree.nodes['NSFWpos'])

    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Nipple mask'])
    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Nipple alpha'])
    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Genital mask'])
    body_material.node_tree.nodes['Shader'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.inputs['Underhair mask'])

    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital intensity'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital saturation'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital hue'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair color'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair intensity'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple base'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple base 2'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple shine'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple rim'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple alpha'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Nipple texture'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Genital mask'])
    body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs.remove(body_material.node_tree.nodes['Shader'].node_tree.nodes['colorsLight'].node_tree.inputs['Underhair mask'])

    bpy.data.materials['KK Body'].node_tree.nodes['Gentex'].node_tree.nodes['Bodyalphacustom'].image = bpy.data.images['Template: SFW alpha mask.png']
    bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].default_value = 1
    bpy.data.materials['KK Body Outline'].node_tree.nodes['customToggle'].inputs[0].hide = True

class import_everything(bpy.types.Operator):
    bl_idname = "kkbp.importeverything"
    bl_label = "Finish separating objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            last_step = time.time()
            directory = context.scene.kkbp.import_dir
            
            c.kklog('\nApplying material templates and textures...')

            scene = context.scene.kkbp
            use_fake_user = scene.templates_bool
            single_outline_mode = scene.texture_outline_bool
            modify_armature = scene.armature_dropdown in ['A', 'B']

            #these methods will return true if an error was encountered to make sure the error popup shows
            template_error = get_templates_and_apply(directory, use_fake_user)
            if template_error:
                return {'FINISHED'}
            
            #redraw the UI after each operation to let the user know the plugin is actually doing something
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

            texture_error = get_and_load_textures(directory)
            if texture_error:
                return {'FINISHED'}
            
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            add_outlines(single_outline_mode)
            if modify_armature and bpy.data.objects['Armature'].pose.bones["Spine"].custom_shape == None:
                #c.kklog(str(time.time() - last_step))
                c.kklog('Adding bone widgets...')
                apply_bone_widgets()
            hide_widgets()

            if bpy.context.scene.kkbp.sfw_mode:
                apply_sfw()
            if bpy.context.scene.kkbp.shader_dropdown == 'B':
                apply_cycles()
            elif bpy.context.scene.kkbp.shader_dropdown == 'C':
                apply_lbs()

            #unhide first found outfit if outfit 00 is not present
            #find the appropriate outfit
            outfit = None
            if bpy.data.objects.get('Outfit 00'):
                outfit = bpy.data.objects.get('Outfit 00')
            else:
                #check the other outfit numbers
                for ob in bpy.data.objects:
                    if ob.name[0:8] == 'Outfit 0' and 'Outfit 00' not in ob.name:
                        outfit = ob
                        break
            if outfit:
                outfit.hide = False
                for child in outfit.children:
                    child.hide = True
                    if 'Hair Outfit 0' in child.name:
                        child.hide = False

            bpy.data.objects['Armature'].hide = False
            bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
            
            #clean data
            clean_orphan_data()

            #set to face select mode for easy material switching
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
            
            if context.scene.kkbp.categorize_dropdown in ['A', 'B', 'C']:
                c.set_viewport_shading('MATERIAL')

            c.kklog('Finished in ' + str(time.time() - last_step)[0:4] + 's')
            return {'FINISHED'}

        except:
            c.kklog('Unknown python error occurred', type = 'error')
            c.kklog(traceback.format_exc())
            self.report({'ERROR'}, traceback.format_exc())
            return {"CANCELLED"}
    
if __name__ == "__main__":
    bpy.utils.register_class(import_everything)

    # test call
    print((bpy.ops.kkbp.importeverything('INVOKE_DEFAULT')))
