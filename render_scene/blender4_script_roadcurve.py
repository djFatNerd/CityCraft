import bpy
from bpy import ops
from bpy.ops import object, curve


# initialize Asphalt node group
def asphalt_node_group(name="myAsphalt"):
    asphalt = bpy.data.node_groups.get(name, None)
    if asphalt is not None:
        return asphalt
    asphalt = bpy.data.node_groups.new(type='ShaderNodeTree', name=name)

    # asphalt interface
    # Socket BSDF
    bsdf_socket = asphalt.interface.new_socket(name="BSDF", in_out='OUTPUT', socket_type='NodeSocketShader')
    bsdf_socket.attribute_domain = 'POINT'

    # Socket tmp_viewer
    tmp_viewer_socket = asphalt.interface.new_socket(name="tmp_viewer", in_out='OUTPUT',
                                                     socket_type='NodeSocketShader')
    tmp_viewer_socket.attribute_domain = 'POINT'

    # Socket middleLine_color
    middleline_color_socket = asphalt.interface.new_socket(name="middleLine_color", in_out='INPUT',
                                                           socket_type='NodeSocketColor')
    middleline_color_socket.attribute_domain = 'POINT'

    # Socket sideLine_color
    sideline_color_socket = asphalt.interface.new_socket(name="sideLine_color", in_out='INPUT',
                                                         socket_type='NodeSocketColor')
    sideline_color_socket.attribute_domain = 'POINT'

    # Socket line_width
    line_width_socket = asphalt.interface.new_socket(name="line_width", in_out='INPUT',
                                                     socket_type='NodeSocketFloat')
    line_width_socket.subtype = 'NONE'
    line_width_socket.default_value = 0.029999999329447746
    line_width_socket.min_value = -10000.0
    line_width_socket.max_value = 10000.0
    line_width_socket.attribute_domain = 'POINT'

    # Socket sideLine_margin
    sideline_margin_socket = asphalt.interface.new_socket(name="sideLine_margin", in_out='INPUT',
                                                          socket_type='NodeSocketFloat')
    sideline_margin_socket.subtype = 'NONE'
    sideline_margin_socket.default_value = 0.5
    sideline_margin_socket.min_value = -10000.0
    sideline_margin_socket.max_value = 10000.0
    sideline_margin_socket.attribute_domain = 'POINT'

    # Socket dashLine_spacing
    dashline_spacing_socket = asphalt.interface.new_socket(name="dashLine_spacing", in_out='INPUT',
                                                           socket_type='NodeSocketFloat')
    dashline_spacing_socket.subtype = 'NONE'
    dashline_spacing_socket.default_value = 0.25
    dashline_spacing_socket.min_value = 0.009999999776482582
    dashline_spacing_socket.max_value = 100.0
    dashline_spacing_socket.attribute_domain = 'POINT'

    # Socket dashLine_length
    dashline_length_socket = asphalt.interface.new_socket(name="dashLine_length", in_out='INPUT',
                                                          socket_type='NodeSocketFloat')
    dashline_length_socket.subtype = 'NONE'
    dashline_length_socket.default_value = 1.0
    dashline_length_socket.min_value = -1000.0
    dashline_length_socket.max_value = 1000.0
    dashline_length_socket.attribute_domain = 'POINT'

    # Socket middleLine
    middleline_socket = asphalt.interface.new_socket(name="middleLine", in_out='INPUT',
                                                     socket_type='NodeSocketFloat')
    middleline_socket.subtype = 'NONE'
    middleline_socket.default_value = 0.019999999552965164
    middleline_socket.min_value = -10000.0
    middleline_socket.max_value = 10000.0
    middleline_socket.attribute_domain = 'POINT'

    # Socket wet
    wet_socket = asphalt.interface.new_socket(name="wet", in_out='INPUT', socket_type='NodeSocketFloat')
    wet_socket.subtype = 'FACTOR'
    wet_socket.default_value = 0.2734806537628174
    wet_socket.min_value = 0.0
    wet_socket.max_value = 1.0
    wet_socket.attribute_domain = 'POINT'

    # Socket is_intersection
    is_intersection_socket = asphalt.interface.new_socket(name="is_intersection", in_out='INPUT',
                                                          socket_type='NodeSocketFloat')
    is_intersection_socket.subtype = 'FACTOR'
    is_intersection_socket.default_value = 0.5
    is_intersection_socket.min_value = 0.0
    is_intersection_socket.max_value = 1.0
    is_intersection_socket.attribute_domain = 'POINT'

    # Socket pedestrian_crossing_color
    pedestrian_crossing_color_socket = asphalt.interface.new_socket(name="pedestrian_crossing_color",
                                                                    in_out='INPUT',
                                                                    socket_type='NodeSocketColor')
    pedestrian_crossing_color_socket.attribute_domain = 'POINT'

    # Socket pedestrian_crossing_dash
    pedestrian_crossing_dash_socket = asphalt.interface.new_socket(name="pedestrian_crossing_dash", in_out='INPUT',
                                                                   socket_type='NodeSocketFloat')
    pedestrian_crossing_dash_socket.subtype = 'NONE'
    pedestrian_crossing_dash_socket.default_value = 0.75
    pedestrian_crossing_dash_socket.min_value = -1000.0
    pedestrian_crossing_dash_socket.max_value = 1000.0
    pedestrian_crossing_dash_socket.attribute_domain = 'POINT'

    # initialize asphalt nodes
    # node Separate XYZ
    separate_xyz = asphalt.nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.name = "Separate XYZ"

    # node Math.002
    math_002 = asphalt.nodes.new("ShaderNodeMath")
    math_002.name = "Math.002"
    math_002.operation = 'ADD'
    math_002.use_clamp = False
    # Value_002
    math_002.inputs[2].default_value = 0.5

    # node Math.005
    math_005 = asphalt.nodes.new("ShaderNodeMath")
    math_005.name = "Math.005"
    math_005.operation = 'MULTIPLY'
    math_005.use_clamp = False
    # Value_001
    math_005.inputs[1].default_value = -1.0
    # Value_002
    math_005.inputs[2].default_value = 0.5

    # node Group Output
    group_output = asphalt.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.is_active_output = True

    # node Bump
    bump = asphalt.nodes.new("ShaderNodeBump")
    bump.name = "Bump"
    bump.invert = False
    # Strength
    bump.inputs[0].default_value = 1.0
    # Distance
    bump.inputs[1].default_value = 1.0
    # Normal
    bump.inputs[3].default_value = (0.0, 0.0, 0.0)

    # node Mix.008
    mix_008 = asphalt.nodes.new("ShaderNodeMix")
    mix_008.name = "Mix.008"
    mix_008.blend_type = 'MIX'
    mix_008.clamp_factor = True
    mix_008.clamp_result = False
    mix_008.data_type = 'RGBA'
    mix_008.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_008.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_008.inputs[2].default_value = 0.0
    # B_Float
    mix_008.inputs[3].default_value = 0.0
    # A_Vector
    mix_008.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_008.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Color
    mix_008.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_008.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_008.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Reroute
    reroute = asphalt.nodes.new("NodeReroute")
    reroute.name = "Reroute"
    # node ColorRamp
    colorramp = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp.name = "ColorRamp"
    colorramp.color_ramp.color_mode = 'RGB'
    colorramp.color_ramp.hue_interpolation = 'NEAR'
    colorramp.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp.color_ramp.elements.remove(colorramp.color_ramp.elements[0])
    colorramp_cre_0 = colorramp.color_ramp.elements[0]
    colorramp_cre_0.position = 0.0
    colorramp_cre_0.alpha = 1.0
    colorramp_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_cre_1 = colorramp.color_ramp.elements.new(1.0)
    colorramp_cre_1.alpha = 1.0
    colorramp_cre_1.color = (0.1850549280643463, 0.1850549280643463, 0.1850549280643463, 1.0)

    # node Reroute.001
    reroute_001 = asphalt.nodes.new("NodeReroute")
    reroute_001.name = "Reroute.001"
    # node Texture Coordinate
    texture_coordinate = asphalt.nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.from_instancer = False
    if "RoadCurve" in bpy.data.objects:
        texture_coordinate.object = bpy.data.objects["RoadCurve"]

    # node Mapping.001
    mapping_001 = asphalt.nodes.new("ShaderNodeMapping")
    mapping_001.name = "Mapping.001"
    mapping_001.vector_type = 'POINT'
    # Location
    mapping_001.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping_001.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Value
    value = asphalt.nodes.new("ShaderNodeValue")
    value.name = "Value"

    value.outputs[0].default_value = 1.0
    # node Texture Coordinate.001
    texture_coordinate_001 = asphalt.nodes.new("ShaderNodeTexCoord")
    texture_coordinate_001.name = "Texture Coordinate.001"
    texture_coordinate_001.from_instancer = False
    if "RoadCurve" in bpy.data.objects:
        texture_coordinate_001.object = bpy.data.objects["RoadCurve"]

    # node Mapping.002
    mapping_002 = asphalt.nodes.new("ShaderNodeMapping")
    mapping_002.name = "Mapping.002"
    mapping_002.vector_type = 'POINT'
    # Location
    mapping_002.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping_002.inputs[2].default_value = (0.0, 0.0, 0.0)

    # node Value.001
    value_001 = asphalt.nodes.new("ShaderNodeValue")
    value_001.name = "Value.001"

    value_001.outputs[0].default_value = 1.0
    # node Noise Texture.002
    noise_texture_002 = asphalt.nodes.new("ShaderNodeTexNoise")
    noise_texture_002.name = "Noise Texture.002"
    noise_texture_002.noise_dimensions = '3D'
    noise_texture_002.normalize = True
    # W
    noise_texture_002.inputs[1].default_value = 0.0
    # Scale
    noise_texture_002.inputs[2].default_value = 0.3000001907348633
    # Detail
    noise_texture_002.inputs[3].default_value = 15.0
    # Roughness
    noise_texture_002.inputs[4].default_value = 0.6436464190483093
    # Lacunarity
    noise_texture_002.inputs[5].default_value = 2.0
    # Distortion
    noise_texture_002.inputs[6].default_value = 0.0

    # node Mix.010
    mix_010 = asphalt.nodes.new("ShaderNodeMix")
    mix_010.name = "Mix.010"
    mix_010.blend_type = 'MIX'
    mix_010.clamp_factor = True
    mix_010.clamp_result = False
    mix_010.data_type = 'FLOAT'
    mix_010.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_010.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_010.inputs[2].default_value = 0.4000000059604645
    # B_Float
    mix_010.inputs[3].default_value = -0.4000000059604645
    # A_Vector
    mix_010.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_010.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Color
    mix_010.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
    # B_Color
    mix_010.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
    # A_Rotation
    mix_010.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_010.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node ColorRamp.004
    colorramp_004 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_004.name = "ColorRamp.004"
    colorramp_004.color_ramp.color_mode = 'RGB'
    colorramp_004.color_ramp.hue_interpolation = 'NEAR'
    colorramp_004.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_004.color_ramp.elements.remove(colorramp_004.color_ramp.elements[0])
    colorramp_004_cre_0 = colorramp_004.color_ramp.elements[0]
    colorramp_004_cre_0.position = 0.32628414034843445
    colorramp_004_cre_0.alpha = 1.0
    colorramp_004_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_004_cre_1 = colorramp_004.color_ramp.elements.new(1.0)
    colorramp_004_cre_1.alpha = 1.0
    colorramp_004_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Math.006
    math_006 = asphalt.nodes.new("ShaderNodeMath")
    math_006.name = "Math.006"
    math_006.operation = 'ADD'
    math_006.use_clamp = False
    # Value_002
    math_006.inputs[2].default_value = 0.5

    # node Math.008
    math_008 = asphalt.nodes.new("ShaderNodeMath")
    math_008.name = "Math.008"
    math_008.operation = 'DIVIDE'
    math_008.use_clamp = False
    # Value_001
    math_008.inputs[1].default_value = 3.0
    # Value_002
    math_008.inputs[2].default_value = 0.5

    # node Combine XYZ
    combine_xyz = asphalt.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz.name = "Combine XYZ"
    # Z
    combine_xyz.inputs[2].default_value = 0.0

    # node Attribute
    attribute = asphalt.nodes.new("ShaderNodeAttribute")
    attribute.name = "Attribute"
    attribute.attribute_name = "Gradient X"
    attribute.attribute_type = 'GEOMETRY'

    # node Attribute.001
    attribute_001 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_001.name = "Attribute.001"
    attribute_001.attribute_name = "Gradient Y"
    attribute_001.attribute_type = 'GEOMETRY'

    # node Mapping
    mapping = asphalt.nodes.new("ShaderNodeMapping")
    mapping.name = "Mapping"
    mapping.vector_type = 'POINT'
    # Location
    mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
    # Rotation
    mapping.inputs[2].default_value = (0.0, 0.0, 1.5707963705062866)
    # Scale
    mapping.inputs[3].default_value = (-0.30000001192092896, 0.0, 1.0)

    # node Math.003
    math_003 = asphalt.nodes.new("ShaderNodeMath")
    math_003.name = "Math.003"
    math_003.operation = 'COMPARE'
    math_003.use_clamp = False

    # node Math.004
    math_004 = asphalt.nodes.new("ShaderNodeMath")
    math_004.name = "Math.004"
    math_004.operation = 'ADD'
    math_004.use_clamp = False
    # Value_001
    math_004.inputs[1].default_value = 0.0
    # Value_002
    math_004.inputs[2].default_value = 0.5

    # node Math
    math = asphalt.nodes.new("ShaderNodeMath")
    math.name = "Math"
    math.operation = 'COMPARE'
    math.use_clamp = False

    # node Math.001
    math_001 = asphalt.nodes.new("ShaderNodeMath")
    math_001.name = "Math.001"
    math_001.operation = 'ADD'
    math_001.use_clamp = False
    # Value_001
    math_001.inputs[1].default_value = 0.0
    # Value_002
    math_001.inputs[2].default_value = 0.5

    # node Mix.003
    mix_003 = asphalt.nodes.new("ShaderNodeMix")
    mix_003.name = "Mix.003"
    mix_003.blend_type = 'SCREEN'
    mix_003.clamp_factor = True
    mix_003.clamp_result = False
    mix_003.data_type = 'RGBA'
    mix_003.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_003.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_003.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_003.inputs[2].default_value = 0.0
    # B_Float
    mix_003.inputs[3].default_value = 0.0
    # A_Vector
    mix_003.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_003.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_003.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_003.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_003.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Brick Texture
    brick_texture = asphalt.nodes.new("ShaderNodeTexBrick")
    brick_texture.name = "Brick Texture"
    brick_texture.offset = 0.5
    brick_texture.offset_frequency = 2
    brick_texture.squash = 1.0
    brick_texture.squash_frequency = 2
    # Color1
    brick_texture.inputs[1].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    # Color2
    brick_texture.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
    # Mortar
    brick_texture.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
    # Mortar Size
    brick_texture.inputs[5].default_value = 0.025000005960464478
    # Mortar Smooth
    brick_texture.inputs[6].default_value = 0.10000000149011612
    # Bias
    brick_texture.inputs[7].default_value = 0.0
    # Brick Width
    brick_texture.inputs[8].default_value = 0.5

    # node Attribute.004
    attribute_004 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_004.name = "Attribute.004"
    attribute_004.attribute_name = "Gradient Y intersection"
    attribute_004.attribute_type = 'GEOMETRY'

    # node Attribute.003
    attribute_003 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_003.name = "Attribute.003"
    attribute_003.attribute_name = "Gradient X"
    attribute_003.attribute_type = 'GEOMETRY'

    # node ColorRamp.006
    colorramp_006 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_006.name = "ColorRamp.006"
    colorramp_006.color_ramp.color_mode = 'RGB'
    colorramp_006.color_ramp.hue_interpolation = 'NEAR'
    colorramp_006.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_006.color_ramp.elements.remove(colorramp_006.color_ramp.elements[0])
    colorramp_006_cre_0 = colorramp_006.color_ramp.elements[0]
    colorramp_006_cre_0.position = 0.0
    colorramp_006_cre_0.alpha = 1.0
    colorramp_006_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_006_cre_1 = colorramp_006.color_ramp.elements.new(0.4622356593608856)
    colorramp_006_cre_1.alpha = 1.0
    colorramp_006_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Mix.011
    mix_011 = asphalt.nodes.new("ShaderNodeMix")
    mix_011.name = "Mix.011"
    mix_011.blend_type = 'OVERLAY'
    mix_011.clamp_factor = True
    mix_011.clamp_result = False
    mix_011.data_type = 'RGBA'
    mix_011.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_011.inputs[0].default_value = 0.30000001192092896
    # Factor_Vector
    mix_011.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_011.inputs[2].default_value = 0.0
    # B_Float
    mix_011.inputs[3].default_value = 0.0
    # A_Vector
    mix_011.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_011.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_011.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_011.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_011.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Brick Texture.001
    brick_texture_001 = asphalt.nodes.new("ShaderNodeTexBrick")
    brick_texture_001.name = "Brick Texture.001"
    brick_texture_001.offset = 0.5
    brick_texture_001.offset_frequency = 2
    brick_texture_001.squash = 1.0
    brick_texture_001.squash_frequency = 2
    # Color1
    brick_texture_001.inputs[1].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    # Color2
    brick_texture_001.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
    # Mortar
    brick_texture_001.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
    # Mortar Size
    brick_texture_001.inputs[5].default_value = 0.0010000000474974513
    # Mortar Smooth
    brick_texture_001.inputs[6].default_value = 0.10000000149011612
    # Bias
    brick_texture_001.inputs[7].default_value = 0.0
    # Brick Width
    brick_texture_001.inputs[8].default_value = 0.5
    # Row Height
    brick_texture_001.inputs[9].default_value = 0.25

    # node Reroute.002
    reroute_002 = asphalt.nodes.new("NodeReroute")
    reroute_002.name = "Reroute.002"
    # node Combine XYZ.001
    combine_xyz_001 = asphalt.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_001.name = "Combine XYZ.001"
    # Z
    combine_xyz_001.inputs[2].default_value = 0.0

    # node Mapping.003
    mapping_003 = asphalt.nodes.new("ShaderNodeMapping")
    mapping_003.name = "Mapping.003"
    mapping_003.vector_type = 'POINT'
    # Location
    mapping_003.inputs[1].default_value = (0.0, 0.19999998807907104, 0.0)
    # Rotation
    mapping_003.inputs[2].default_value = (0.0, 0.0, 0.0)
    # Scale
    mapping_003.inputs[3].default_value = (1.0, 1.0, 1.0)

    # node Brick Texture.002
    brick_texture_002 = asphalt.nodes.new("ShaderNodeTexBrick")
    brick_texture_002.name = "Brick Texture.002"
    brick_texture_002.offset = 0.5765306353569031
    brick_texture_002.offset_frequency = 2
    brick_texture_002.squash = 1.0
    brick_texture_002.squash_frequency = 2
    # Color1
    brick_texture_002.inputs[1].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
    # Color2
    brick_texture_002.inputs[2].default_value = (1.0, 1.0, 1.0, 1.0)
    # Mortar
    brick_texture_002.inputs[3].default_value = (0.0, 0.0, 0.0, 1.0)
    # Mortar Size
    brick_texture_002.inputs[5].default_value = 0.0010000000474974513
    # Mortar Smooth
    brick_texture_002.inputs[6].default_value = 0.10000000149011612
    # Bias
    brick_texture_002.inputs[7].default_value = 0.0
    # Brick Width
    brick_texture_002.inputs[8].default_value = 0.5
    # Row Height
    brick_texture_002.inputs[9].default_value = 0.25

    # node Mix.014
    mix_014 = asphalt.nodes.new("ShaderNodeMix")
    mix_014.name = "Mix.014"
    mix_014.blend_type = 'MIX'
    mix_014.clamp_factor = True
    mix_014.clamp_result = False
    mix_014.data_type = 'RGBA'
    mix_014.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_014.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_014.inputs[2].default_value = 0.0
    # B_Float
    mix_014.inputs[3].default_value = 0.0
    # A_Vector
    mix_014.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_014.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_014.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    # A_Rotation
    mix_014.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_014.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.018
    mix_018 = asphalt.nodes.new("ShaderNodeMix")
    mix_018.name = "Mix.018"
    mix_018.blend_type = 'MIX'
    mix_018.clamp_factor = True
    mix_018.clamp_result = False
    mix_018.data_type = 'RGBA'
    mix_018.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_018.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_018.inputs[2].default_value = 0.0
    # B_Float
    mix_018.inputs[3].default_value = 0.0
    # A_Vector
    mix_018.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_018.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_018.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    # A_Rotation
    mix_018.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_018.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node ColorRamp.007
    colorramp_007 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_007.name = "ColorRamp.007"
    colorramp_007.color_ramp.color_mode = 'RGB'
    colorramp_007.color_ramp.hue_interpolation = 'NEAR'
    colorramp_007.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_007.color_ramp.elements.remove(colorramp_007.color_ramp.elements[0])
    colorramp_007_cre_0 = colorramp_007.color_ramp.elements[0]
    colorramp_007_cre_0.position = 0.3746224045753479
    colorramp_007_cre_0.alpha = 1.0
    colorramp_007_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_007_cre_1 = colorramp_007.color_ramp.elements.new(0.5166164636611938)
    colorramp_007_cre_1.alpha = 1.0
    colorramp_007_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Mix.019
    mix_019 = asphalt.nodes.new("ShaderNodeMix")
    mix_019.name = "Mix.019"
    mix_019.blend_type = 'MULTIPLY'
    mix_019.clamp_factor = True
    mix_019.clamp_result = False
    mix_019.data_type = 'RGBA'
    mix_019.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_019.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_019.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_019.inputs[2].default_value = 0.0
    # B_Float
    mix_019.inputs[3].default_value = 0.0
    # A_Vector
    mix_019.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_019.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_019.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_019.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.020
    mix_020 = asphalt.nodes.new("ShaderNodeMix")
    mix_020.name = "Mix.020"
    mix_020.blend_type = 'SCREEN'
    mix_020.clamp_factor = True
    mix_020.clamp_result = False
    mix_020.data_type = 'RGBA'
    mix_020.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_020.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_020.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_020.inputs[2].default_value = 0.0
    # B_Float
    mix_020.inputs[3].default_value = 0.0
    # A_Vector
    mix_020.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_020.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_020.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_020.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Invert
    invert = asphalt.nodes.new("ShaderNodeInvert")
    invert.name = "Invert"
    # Fac
    invert.inputs[0].default_value = 1.0

    # node Mix.022
    mix_022 = asphalt.nodes.new("ShaderNodeMix")
    mix_022.name = "Mix.022"
    mix_022.blend_type = 'SCREEN'
    mix_022.clamp_factor = True
    mix_022.clamp_result = False
    mix_022.data_type = 'RGBA'
    mix_022.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_022.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_022.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_022.inputs[2].default_value = 0.0
    # B_Float
    mix_022.inputs[3].default_value = 0.0
    # A_Vector
    mix_022.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_022.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_022.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_022.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Attribute.002
    attribute_002 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_002.name = "Attribute.002"
    attribute_002.attribute_name = "roadlane_width"
    attribute_002.attribute_type = 'GEOMETRY'

    # node Attribute.007
    attribute_007 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_007.name = "Attribute.007"
    attribute_007.attribute_name = "sidewalk_width"
    attribute_007.attribute_type = 'GEOMETRY'

    # node Math.011
    math_011 = asphalt.nodes.new("ShaderNodeMath")
    math_011.name = "Math.011"
    math_011.operation = 'ADD'
    math_011.use_clamp = False
    # Value_002
    math_011.inputs[2].default_value = 0.5

    # node Noise Texture
    noise_texture = asphalt.nodes.new("ShaderNodeTexNoise")
    noise_texture.name = "Noise Texture"
    noise_texture.noise_dimensions = '3D'
    noise_texture.normalize = True
    # W
    noise_texture.inputs[1].default_value = 0.0
    # Scale
    noise_texture.inputs[2].default_value = 0.800000011920929
    # Detail
    noise_texture.inputs[3].default_value = 8.09999942779541
    # Roughness
    noise_texture.inputs[4].default_value = 0.8977900147438049
    # Lacunarity
    noise_texture.inputs[5].default_value = 2.0
    # Distortion
    noise_texture.inputs[6].default_value = 0.0

    # node Voronoi Texture
    voronoi_texture = asphalt.nodes.new("ShaderNodeTexVoronoi")
    voronoi_texture.name = "Voronoi Texture"
    voronoi_texture.distance = 'EUCLIDEAN'
    voronoi_texture.feature = 'F1'
    voronoi_texture.normalize = False
    voronoi_texture.voronoi_dimensions = '3D'
    # W
    voronoi_texture.inputs[1].default_value = 0.0
    # Scale
    voronoi_texture.inputs[2].default_value = 40.0
    # Detail
    voronoi_texture.inputs[3].default_value = 0.0
    # Roughness
    voronoi_texture.inputs[4].default_value = 0.5
    # Lacunarity
    voronoi_texture.inputs[5].default_value = 2.0
    # Smoothness
    voronoi_texture.inputs[6].default_value = 1.0
    # Exponent
    voronoi_texture.inputs[7].default_value = 0.5
    # Randomness
    voronoi_texture.inputs[8].default_value = 1.0

    # node Mix.021
    mix_021 = asphalt.nodes.new("ShaderNodeMix")
    mix_021.name = "Mix.021"
    mix_021.blend_type = 'OVERLAY'
    mix_021.clamp_factor = True
    mix_021.clamp_result = False
    mix_021.data_type = 'RGBA'
    mix_021.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_021.inputs[0].default_value = 0.6574585437774658
    # Factor_Vector
    mix_021.inputs[1].default_value = (0.5, 0.5, 0.5)
    # B_Float
    mix_021.inputs[3].default_value = 0.0
    # A_Vector
    mix_021.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_021.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_021.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_021.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Voronoi Texture.001
    voronoi_texture_001 = asphalt.nodes.new("ShaderNodeTexVoronoi")
    voronoi_texture_001.name = "Voronoi Texture.001"
    voronoi_texture_001.distance = 'EUCLIDEAN'
    voronoi_texture_001.feature = 'F1'
    voronoi_texture_001.normalize = False
    voronoi_texture_001.voronoi_dimensions = '3D'
    # W
    voronoi_texture_001.inputs[1].default_value = 0.0
    # Scale
    voronoi_texture_001.inputs[2].default_value = 60.0
    # Detail
    voronoi_texture_001.inputs[3].default_value = 0.0
    # Roughness
    voronoi_texture_001.inputs[4].default_value = 0.5
    # Lacunarity
    voronoi_texture_001.inputs[5].default_value = 2.0
    # Smoothness
    voronoi_texture_001.inputs[6].default_value = 1.0
    # Exponent
    voronoi_texture_001.inputs[7].default_value = 0.5
    # Randomness
    voronoi_texture_001.inputs[8].default_value = 1.0

    # node Reroute.003
    reroute_003 = asphalt.nodes.new("NodeReroute")
    reroute_003.name = "Reroute.003"
    # node ColorRamp.001
    colorramp_001 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_001.name = "ColorRamp.001"
    colorramp_001.color_ramp.color_mode = 'RGB'
    colorramp_001.color_ramp.hue_interpolation = 'NEAR'
    colorramp_001.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_001.color_ramp.elements.remove(colorramp_001.color_ramp.elements[0])
    colorramp_001_cre_0 = colorramp_001.color_ramp.elements[0]
    colorramp_001_cre_0.position = 0.0
    colorramp_001_cre_0.alpha = 1.0
    colorramp_001_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_001_cre_1 = colorramp_001.color_ramp.elements.new(0.027190495282411575)
    colorramp_001_cre_1.alpha = 1.0
    colorramp_001_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Attribute.005
    attribute_005 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_005.name = "Attribute.005"
    attribute_005.attribute_name = "Gradient Y intersection2"
    attribute_005.attribute_type = 'GEOMETRY'

    # node Attribute.006
    attribute_006 = asphalt.nodes.new("ShaderNodeAttribute")
    attribute_006.name = "Attribute.006"
    attribute_006.attribute_name = "Gradient X"
    attribute_006.attribute_type = 'GEOMETRY'

    # node Combine XYZ.002
    combine_xyz_002 = asphalt.nodes.new("ShaderNodeCombineXYZ")
    combine_xyz_002.name = "Combine XYZ.002"
    # Z
    combine_xyz_002.inputs[2].default_value = 0.0

    # node Mix.002
    mix_002 = asphalt.nodes.new("ShaderNodeMix")
    mix_002.name = "Mix.002"
    mix_002.blend_type = 'MULTIPLY'
    mix_002.clamp_factor = True
    mix_002.clamp_result = False
    mix_002.data_type = 'RGBA'
    mix_002.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_002.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_002.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_002.inputs[2].default_value = 0.0
    # B_Float
    mix_002.inputs[3].default_value = 0.0
    # A_Vector
    mix_002.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_002.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_002.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_002.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.005
    mix_005 = asphalt.nodes.new("ShaderNodeMix")
    mix_005.name = "Mix.005"
    mix_005.blend_type = 'MIX'
    mix_005.clamp_factor = True
    mix_005.clamp_result = False
    mix_005.data_type = 'RGBA'
    mix_005.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_005.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_005.inputs[2].default_value = 0.0
    # B_Float
    mix_005.inputs[3].default_value = 0.0
    # A_Vector
    mix_005.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_005.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_005.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_005.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_005.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.007
    mix_007 = asphalt.nodes.new("ShaderNodeMix")
    mix_007.name = "Mix.007"
    mix_007.blend_type = 'OVERLAY'
    mix_007.clamp_factor = True
    mix_007.clamp_result = False
    mix_007.data_type = 'RGBA'
    mix_007.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_007.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_007.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_007.inputs[2].default_value = 0.0
    # B_Float
    mix_007.inputs[3].default_value = 0.0
    # A_Vector
    mix_007.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_007.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_007.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_007.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Math.010
    math_010 = asphalt.nodes.new("ShaderNodeMath")
    math_010.name = "Math.010"
    math_010.operation = 'COMPARE'
    math_010.use_clamp = False

    # node Math.012
    math_012 = asphalt.nodes.new("ShaderNodeMath")
    math_012.name = "Math.012"
    math_012.operation = 'DIVIDE'
    math_012.use_clamp = False
    # Value_001
    math_012.inputs[1].default_value = 3.0
    # Value_002
    math_012.inputs[2].default_value = 0.5

    # node Math.009
    math_009 = asphalt.nodes.new("ShaderNodeMath")
    math_009.name = "Math.009"
    math_009.operation = 'COMPARE'
    math_009.use_clamp = False

    # node Math.007
    math_007 = asphalt.nodes.new("ShaderNodeMath")
    math_007.name = "Math.007"
    math_007.operation = 'COMPARE'
    math_007.use_clamp = False
    # Value_001
    math_007.inputs[1].default_value = 0.0

    # node Mix.023
    mix_023 = asphalt.nodes.new("ShaderNodeMix")
    mix_023.name = "Mix.023"
    mix_023.blend_type = 'MULTIPLY'
    mix_023.clamp_factor = True
    mix_023.clamp_result = False
    mix_023.data_type = 'RGBA'
    mix_023.factor_mode = 'UNIFORM'
    # Factor_Float
    mix_023.inputs[0].default_value = 1.0
    # Factor_Vector
    mix_023.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_023.inputs[2].default_value = 0.0
    # B_Float
    mix_023.inputs[3].default_value = 0.0
    # A_Vector
    mix_023.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_023.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_023.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_023.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.012
    mix_012 = asphalt.nodes.new("ShaderNodeMix")
    mix_012.name = "Mix.012"
    mix_012.blend_type = 'MIX'
    mix_012.clamp_factor = True
    mix_012.clamp_result = False
    mix_012.data_type = 'RGBA'
    mix_012.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_012.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_012.inputs[2].default_value = 0.0
    # B_Float
    mix_012.inputs[3].default_value = 0.0
    # A_Vector
    mix_012.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_012.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Color
    mix_012.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_012.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_012.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.013
    mix_013 = asphalt.nodes.new("ShaderNodeMix")
    mix_013.name = "Mix.013"
    mix_013.blend_type = 'MIX'
    mix_013.clamp_factor = True
    mix_013.clamp_result = False
    mix_013.data_type = 'RGBA'
    mix_013.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_013.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_013.inputs[2].default_value = 0.0
    # B_Float
    mix_013.inputs[3].default_value = 0.0
    # A_Vector
    mix_013.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_013.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_013.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_013.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_013.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node ColorRamp.005
    colorramp_005 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_005.name = "ColorRamp.005"
    colorramp_005.color_ramp.color_mode = 'RGB'
    colorramp_005.color_ramp.hue_interpolation = 'NEAR'
    colorramp_005.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_005.color_ramp.elements.remove(colorramp_005.color_ramp.elements[0])
    colorramp_005_cre_0 = colorramp_005.color_ramp.elements[0]
    colorramp_005_cre_0.position = 0.054380644112825394
    colorramp_005_cre_0.alpha = 1.0
    colorramp_005_cre_0.color = (1.0, 1.0, 1.0, 1.0)

    colorramp_005_cre_1 = colorramp_005.color_ramp.elements.new(0.24471290409564972)
    colorramp_005_cre_1.alpha = 1.0
    colorramp_005_cre_1.color = (0.0, 0.0, 0.0, 1.0)

    # node ColorRamp.002
    colorramp_002 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_002.name = "ColorRamp.002"
    colorramp_002.color_ramp.color_mode = 'RGB'
    colorramp_002.color_ramp.hue_interpolation = 'NEAR'
    colorramp_002.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_002.color_ramp.elements.remove(colorramp_002.color_ramp.elements[0])
    colorramp_002_cre_0 = colorramp_002.color_ramp.elements[0]
    colorramp_002_cre_0.position = 0.3262840211391449
    colorramp_002_cre_0.alpha = 1.0
    colorramp_002_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_002_cre_1 = colorramp_002.color_ramp.elements.new(0.7311179637908936)
    colorramp_002_cre_1.alpha = 1.0
    colorramp_002_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Invert.001
    invert_001 = asphalt.nodes.new("ShaderNodeInvert")
    invert_001.name = "Invert.001"
    # Fac
    invert_001.inputs[0].default_value = 1.0

    # node Mix.009
    mix_009 = asphalt.nodes.new("ShaderNodeMix")
    mix_009.name = "Mix.009"
    mix_009.blend_type = 'MULTIPLY'
    mix_009.clamp_factor = True
    mix_009.clamp_result = False
    mix_009.data_type = 'RGBA'
    mix_009.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_009.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_009.inputs[2].default_value = 0.0
    # B_Float
    mix_009.inputs[3].default_value = 0.0
    # A_Vector
    mix_009.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_009.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_009.inputs[7].default_value = (0.6424741744995117, 0.6424741744995117, 0.6424741744995117, 1.0)
    # A_Rotation
    mix_009.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_009.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.006
    mix_006 = asphalt.nodes.new("ShaderNodeMix")
    mix_006.name = "Mix.006"
    mix_006.blend_type = 'MULTIPLY'
    mix_006.clamp_factor = True
    mix_006.clamp_result = False
    mix_006.data_type = 'RGBA'
    mix_006.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_006.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_006.inputs[2].default_value = 0.0
    # B_Float
    mix_006.inputs[3].default_value = 0.0
    # A_Vector
    mix_006.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_006.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_006.inputs[7].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_006.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_006.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.017
    mix_017 = asphalt.nodes.new("ShaderNodeMix")
    mix_017.name = "Mix.017"
    mix_017.blend_type = 'MIX'
    mix_017.clamp_factor = True
    mix_017.clamp_result = False
    mix_017.data_type = 'RGBA'
    mix_017.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_017.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_017.inputs[2].default_value = 0.0
    # B_Float
    mix_017.inputs[3].default_value = 0.0
    # A_Vector
    mix_017.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_017.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Color
    mix_017.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
    # A_Rotation
    mix_017.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_017.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Noise Texture.001
    noise_texture_001 = asphalt.nodes.new("ShaderNodeTexNoise")
    noise_texture_001.name = "Noise Texture.001"
    noise_texture_001.noise_dimensions = '3D'
    noise_texture_001.normalize = True
    # W
    noise_texture_001.inputs[1].default_value = 0.0
    # Scale
    noise_texture_001.inputs[2].default_value = 0.30000001192092896
    # Detail
    noise_texture_001.inputs[3].default_value = 15.0
    # Roughness
    noise_texture_001.inputs[4].default_value = 0.8867403268814087
    # Lacunarity
    noise_texture_001.inputs[5].default_value = 2.0
    # Distortion
    noise_texture_001.inputs[6].default_value = 0.0

    # node ColorRamp.003
    colorramp_003 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_003.name = "ColorRamp.003"
    colorramp_003.color_ramp.color_mode = 'RGB'
    colorramp_003.color_ramp.hue_interpolation = 'NEAR'
    colorramp_003.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_003.color_ramp.elements.remove(colorramp_003.color_ramp.elements[0])
    colorramp_003_cre_0 = colorramp_003.color_ramp.elements[0]
    colorramp_003_cre_0.position = 0.0
    colorramp_003_cre_0.alpha = 1.0
    colorramp_003_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_003_cre_1 = colorramp_003.color_ramp.elements.new(1.0)
    colorramp_003_cre_1.alpha = 1.0
    colorramp_003_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Mix.015
    mix_015 = asphalt.nodes.new("ShaderNodeMix")
    mix_015.name = "Mix.015"
    mix_015.blend_type = 'MIX'
    mix_015.clamp_factor = True
    mix_015.clamp_result = False
    mix_015.data_type = 'RGBA'
    mix_015.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_015.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_015.inputs[2].default_value = 0.0
    # B_Float
    mix_015.inputs[3].default_value = 0.0
    # A_Vector
    mix_015.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_015.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_015.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_015.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.004
    mix_004 = asphalt.nodes.new("ShaderNodeMix")
    mix_004.name = "Mix.004"
    mix_004.blend_type = 'SCREEN'
    mix_004.clamp_factor = True
    mix_004.clamp_result = False
    mix_004.data_type = 'RGBA'
    mix_004.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_004.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_004.inputs[2].default_value = 0.0
    # B_Float
    mix_004.inputs[3].default_value = 0.0
    # A_Vector
    mix_004.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_004.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_004.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_004.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.001
    mix_001 = asphalt.nodes.new("ShaderNodeMix")
    mix_001.name = "Mix.001"
    mix_001.blend_type = 'SCREEN'
    mix_001.clamp_factor = True
    mix_001.clamp_result = False
    mix_001.data_type = 'RGBA'
    mix_001.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_001.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_001.inputs[2].default_value = 0.0
    # B_Float
    mix_001.inputs[3].default_value = 0.0
    # A_Vector
    mix_001.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_001.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_001.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_001.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.024
    mix_024 = asphalt.nodes.new("ShaderNodeMix")
    mix_024.name = "Mix.024"
    mix_024.blend_type = 'MIX'
    mix_024.clamp_factor = True
    mix_024.clamp_result = False
    mix_024.data_type = 'RGBA'
    mix_024.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_024.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_024.inputs[2].default_value = 0.0
    # B_Float
    mix_024.inputs[3].default_value = 0.0
    # A_Vector
    mix_024.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_024.inputs[5].default_value = (0.0, 0.0, 0.0)
    # B_Color
    mix_024.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    # A_Rotation
    mix_024.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_024.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix.016
    mix_016 = asphalt.nodes.new("ShaderNodeMix")
    mix_016.name = "Mix.016"
    mix_016.blend_type = 'MIX'
    mix_016.clamp_factor = True
    mix_016.clamp_result = False
    mix_016.data_type = 'RGBA'
    mix_016.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix_016.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix_016.inputs[2].default_value = 0.0
    # B_Float
    mix_016.inputs[3].default_value = 0.0
    # A_Vector
    mix_016.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix_016.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix_016.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix_016.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node Mix
    mix = asphalt.nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.blend_type = 'MIX'
    mix.clamp_factor = True
    mix.clamp_result = False
    mix.data_type = 'RGBA'
    mix.factor_mode = 'UNIFORM'
    # Factor_Vector
    mix.inputs[1].default_value = (0.5, 0.5, 0.5)
    # A_Float
    mix.inputs[2].default_value = 0.0
    # B_Float
    mix.inputs[3].default_value = 0.0
    # A_Vector
    mix.inputs[4].default_value = (0.0, 0.0, 0.0)
    # B_Vector
    mix.inputs[5].default_value = (0.0, 0.0, 0.0)
    # A_Rotation
    mix.inputs[8].default_value = (0.0, 0.0, 0.0)
    # B_Rotation
    mix.inputs[9].default_value = (0.0, 0.0, 0.0)

    # node ColorRamp.008
    colorramp_008 = asphalt.nodes.new("ShaderNodeValToRGB")
    colorramp_008.name = "ColorRamp.008"
    colorramp_008.color_ramp.color_mode = 'RGB'
    colorramp_008.color_ramp.hue_interpolation = 'NEAR'
    colorramp_008.color_ramp.interpolation = 'LINEAR'

    # initialize color ramp elements
    colorramp_008.color_ramp.elements.remove(colorramp_008.color_ramp.elements[0])
    colorramp_008_cre_0 = colorramp_008.color_ramp.elements[0]
    colorramp_008_cre_0.position = 0.981873095035553
    colorramp_008_cre_0.alpha = 1.0
    colorramp_008_cre_0.color = (0.0, 0.0, 0.0, 1.0)

    colorramp_008_cre_1 = colorramp_008.color_ramp.elements.new(1.0)
    colorramp_008_cre_1.alpha = 1.0
    colorramp_008_cre_1.color = (1.0, 1.0, 1.0, 1.0)

    # node Principled BSDF
    principled_bsdf = asphalt.nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.distribution = 'GGX'
    principled_bsdf.subsurface_method = 'RANDOM_WALK_SKIN'
    # Metallic
    principled_bsdf.inputs[1].default_value = 0.0
    # IOR
    principled_bsdf.inputs[3].default_value = 1.4500000476837158
    # Alpha
    principled_bsdf.inputs[4].default_value = 1.0
    # Weight
    principled_bsdf.inputs[6].default_value = 0.0
    # Subsurface Weight
    principled_bsdf.inputs[7].default_value = 0.0
    # Subsurface Radius
    principled_bsdf.inputs[8].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
    # Subsurface Scale
    principled_bsdf.inputs[9].default_value = 0.05000000074505806
    # Subsurface IOR
    principled_bsdf.inputs[10].default_value = 1.399999976158142
    # Subsurface Anisotropy
    principled_bsdf.inputs[11].default_value = 0.0
    # Specular IOR Level
    principled_bsdf.inputs[12].default_value = 0.4909365475177765
    # Specular Tint
    principled_bsdf.inputs[13].default_value = (1.0, 1.0, 1.0, 1.0)
    # Anisotropic
    principled_bsdf.inputs[14].default_value = 0.0
    # Anisotropic Rotation
    principled_bsdf.inputs[15].default_value = 0.0
    # Tangent
    principled_bsdf.inputs[16].default_value = (0.0, 0.0, 0.0)
    # Transmission Weight
    principled_bsdf.inputs[17].default_value = 0.0
    # Coat Weight
    principled_bsdf.inputs[18].default_value = 0.0
    # Coat Roughness
    principled_bsdf.inputs[19].default_value = 0.029999999329447746
    # Coat IOR
    principled_bsdf.inputs[20].default_value = 1.5
    # Coat Tint
    principled_bsdf.inputs[21].default_value = (1.0, 1.0, 1.0, 1.0)
    # Coat Normal
    principled_bsdf.inputs[22].default_value = (0.0, 0.0, 0.0)
    # Sheen Weight
    principled_bsdf.inputs[23].default_value = 0.0
    # Sheen Roughness
    principled_bsdf.inputs[24].default_value = 0.5
    # Sheen Tint
    principled_bsdf.inputs[25].default_value = (1.0, 1.0, 1.0, 1.0)
    # Emission Color
    principled_bsdf.inputs[26].default_value = (0.0, 0.0, 0.0, 1.0)
    # Emission Strength
    principled_bsdf.inputs[27].default_value = 1.0

    # node Group Input
    group_input = asphalt.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"

    # Set locations
    separate_xyz.location = (-610.5906372070312, -43.80999755859375)
    math_002.location = (-831.5322875976562, 338.43206787109375)
    math_005.location = (-1051.333251953125, 243.6428680419922)
    group_output.location = (4448.66259765625, -81.33576202392578)
    bump.location = (2201.72119140625, -873.7306518554688)
    mix_008.location = (1994.90087890625, -985.5946655273438)
    reroute.location = (1112.8365478515625, -1134.8450927734375)
    colorramp.location = (537.9763793945312, -758.17041015625)
    reroute_001.location = (-282.6666564941406, -1140.525146484375)
    texture_coordinate.location = (-728.2633666992188, -1208.4346923828125)
    mapping_001.location = (-508.0000305175781, -1135.3055419921875)
    value.location = (-710.6018676757812, -1489.8895263671875)
    texture_coordinate_001.location = (-178.85061645507812, -1544.3670654296875)
    mapping_002.location = (41.41265869140625, -1471.23779296875)
    value_001.location = (-161.18917846679688, -1825.82177734375)
    noise_texture_002.location = (298.9601135253906, -1587.13232421875)
    mix_010.location = (524.2803344726562, -1405.1409912109375)
    colorramp_004.location = (482.49658203125, -1125.8363037109375)
    math_006.location = (863.94921875, -1124.8975830078125)
    math_008.location = (-638.1271362304688, 775.3056640625)
    combine_xyz.location = (-1107.37744140625, -434.6077575683594)
    attribute.location = (-1443.84716796875, -262.7776794433594)
    attribute_001.location = (-1443.82763671875, -442.36859130859375)
    mapping.location = (-378.6065368652344, 668.8909912109375)
    math_003.location = (24.44985008239746, 224.61468505859375)
    math_004.location = (-173.06422424316406, 264.3428039550781)
    math.location = (-179.18055725097656, 3.7655513286590576)
    math_001.location = (-395.8515625, -57.746219635009766)
    mix_003.location = (94.1447982788086, 1.714281678199768)
    brick_texture.location = (54.88431167602539, 689.553466796875)
    attribute_004.location = (-1145.3577880859375, 987.8432006835938)
    attribute_003.location = (-1087.1539306640625, 1322.5537109375)
    colorramp_006.location = (-61.999996185302734, 1529.5443115234375)
    mix_011.location = (1028.6004638671875, -563.0381469726562)
    brick_texture_001.location = (-291.9747009277344, 1570.7979736328125)
    reroute_002.location = (-339.0116882324219, 1165.60986328125)
    combine_xyz_001.location = (-686.3193969726562, 1203.3707275390625)
    mapping_003.location = (-432.74658203125, 2292.950927734375)
    brick_texture_002.location = (-187.64096069335938, 2261.63671875)
    mix_014.location = (257.73028564453125, 1380.9415283203125)
    mix_018.location = (543.411865234375, 2245.515380859375)
    colorramp_007.location = (42.666664123535156, 2305.42529296875)
    mix_019.location = (705.7559814453125, 1935.0048828125)
    mix_020.location = (208.24305725097656, 1847.4925537109375)
    invert.location = (443.270751953125, 1820.6298828125)
    mix_022.location = (925.76123046875, 1652.9552001953125)
    attribute_002.location = (-1137.6427001953125, 610.8038940429688)
    attribute_007.location = (-1136.3758544921875, 783.9475708007812)
    math_011.location = (-792.3843383789062, 905.8748168945312)
    noise_texture.location = (-283.5843811035156, -793.32470703125)
    voronoi_texture.location = (-113.70003509521484, -663.9116821289062)
    mix_021.location = (92.74606323242188, -647.4246215820312)
    voronoi_texture_001.location = (-65.0149154663086, -930.4039916992188)
    reroute_003.location = (331.3333435058594, -694.9793090820312)
    colorramp_001.location = (289.4462585449219, 672.8645629882812)
    attribute_005.location = (-1209.9915771484375, 1648.3448486328125)
    attribute_006.location = (-1151.7877197265625, 1983.0552978515625)
    combine_xyz_002.location = (-880.3764038085938, 1881.7996826171875)
    mix_002.location = (920.8806762695312, -37.63250732421875)
    mix_005.location = (647.3432006835938, 291.4668884277344)
    mix_007.location = (3300.955078125, 107.1525650024414)
    math_010.location = (-249.2455291748047, 1841.8802490234375)
    math_012.location = (-469.5720520019531, 1707.3701171875)
    math_009.location = (-685.6585083007812, 1557.9716796875)
    math_007.location = (-272.1959533691406, 1116.623291015625)
    mix_023.location = (137.23426818847656, 1040.1737060546875)
    mix_012.location = (1365.676513671875, 1022.4329223632812)
    mix_013.location = (1791.3121337890625, 960.72265625)
    colorramp_005.location = (1273.58349609375, -603.0097045898438)
    colorramp_002.location = (344.0083923339844, -448.7078552246094)
    invert_001.location = (637.4072875976562, -216.8331298828125)
    mix_009.location = (3625.150390625, -251.46730041503906)
    mix_006.location = (1342.104736328125, 225.89208984375)
    mix_017.location = (1011.8152465820312, 332.3418273925781)
    noise_texture_001.location = (1053.3974609375, 601.3997802734375)
    colorramp_003.location = (1273.31787109375, 537.5801391601562)
    mix_015.location = (1658.6435546875, -141.20065307617188)
    mix_004.location = (1781.3675537109375, 256.05615234375)
    mix_001.location = (1574.5364990234375, -485.8892517089844)
    mix_024.location = (2217.14599609375, 981.1532592773438)
    mix_016.location = (2195.166015625, 162.6997833251953)
    mix.location = (3070.435546875, 489.9950256347656)
    colorramp_008.location = (2632.806396484375, 808.187744140625)
    principled_bsdf.location = (3878.755615234375, -228.8268280029297)
    group_input.location = (-712.0262451171875, -442.3509826660156)

    # Set dimensions
    separate_xyz.width, separate_xyz.height = 140.0, 100.0
    math_002.width, math_002.height = 140.0, 100.0
    math_005.width, math_005.height = 140.0, 100.0
    group_output.width, group_output.height = 140.0, 100.0
    bump.width, bump.height = 140.0, 100.0
    mix_008.width, mix_008.height = 140.0, 100.0
    reroute.width, reroute.height = 16.0, 100.0
    colorramp.width, colorramp.height = 240.0, 100.0
    reroute_001.width, reroute_001.height = 16.0, 100.0
    texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
    mapping_001.width, mapping_001.height = 140.0, 100.0
    value.width, value.height = 140.0, 100.0
    texture_coordinate_001.width, texture_coordinate_001.height = 140.0, 100.0
    mapping_002.width, mapping_002.height = 140.0, 100.0
    value_001.width, value_001.height = 140.0, 100.0
    noise_texture_002.width, noise_texture_002.height = 140.0, 100.0
    mix_010.width, mix_010.height = 140.0, 100.0
    colorramp_004.width, colorramp_004.height = 240.0, 100.0
    math_006.width, math_006.height = 140.0, 100.0
    math_008.width, math_008.height = 140.0, 100.0
    combine_xyz.width, combine_xyz.height = 140.0, 100.0
    attribute.width, attribute.height = 140.0, 100.0
    attribute_001.width, attribute_001.height = 140.0, 100.0
    mapping.width, mapping.height = 140.0, 100.0
    math_003.width, math_003.height = 140.0, 100.0
    math_004.width, math_004.height = 140.0, 100.0
    math.width, math.height = 140.0, 100.0
    math_001.width, math_001.height = 140.0, 100.0
    mix_003.width, mix_003.height = 140.0, 100.0
    brick_texture.width, brick_texture.height = 150.0, 100.0
    attribute_004.width, attribute_004.height = 207.02792358398438, 100.0
    attribute_003.width, attribute_003.height = 140.0, 100.0
    colorramp_006.width, colorramp_006.height = 240.0, 100.0
    mix_011.width, mix_011.height = 140.0, 100.0
    brick_texture_001.width, brick_texture_001.height = 150.0, 100.0
    reroute_002.width, reroute_002.height = 16.0, 100.0
    combine_xyz_001.width, combine_xyz_001.height = 140.0, 100.0
    mapping_003.width, mapping_003.height = 140.0, 100.0
    brick_texture_002.width, brick_texture_002.height = 150.0, 100.0
    mix_014.width, mix_014.height = 140.0, 100.0
    mix_018.width, mix_018.height = 140.0, 100.0
    colorramp_007.width, colorramp_007.height = 240.0, 100.0
    mix_019.width, mix_019.height = 140.0, 100.0
    mix_020.width, mix_020.height = 140.0, 100.0
    invert.width, invert.height = 140.0, 100.0
    mix_022.width, mix_022.height = 140.0, 100.0
    attribute_002.width, attribute_002.height = 201.9274139404297, 100.0
    attribute_007.width, attribute_007.height = 201.9274139404297, 100.0
    math_011.width, math_011.height = 140.0, 100.0
    noise_texture.width, noise_texture.height = 140.0, 100.0
    voronoi_texture.width, voronoi_texture.height = 140.0, 100.0
    mix_021.width, mix_021.height = 140.0, 100.0
    voronoi_texture_001.width, voronoi_texture_001.height = 100.0, 100.0
    reroute_003.width, reroute_003.height = 16.0, 100.0
    colorramp_001.width, colorramp_001.height = 240.0, 100.0
    attribute_005.width, attribute_005.height = 207.02792358398438, 100.0
    attribute_006.width, attribute_006.height = 140.0, 100.0
    combine_xyz_002.width, combine_xyz_002.height = 140.0, 100.0
    mix_002.width, mix_002.height = 140.0, 100.0
    mix_005.width, mix_005.height = 140.0, 100.0
    mix_007.width, mix_007.height = 140.0, 100.0
    math_010.width, math_010.height = 140.0, 100.0
    math_012.width, math_012.height = 140.0, 100.0
    math_009.width, math_009.height = 140.0, 100.0
    math_007.width, math_007.height = 140.0, 100.0
    mix_023.width, mix_023.height = 140.0, 100.0
    mix_012.width, mix_012.height = 140.0, 100.0
    mix_013.width, mix_013.height = 140.0, 100.0
    colorramp_005.width, colorramp_005.height = 240.0, 100.0
    colorramp_002.width, colorramp_002.height = 240.0, 100.0
    invert_001.width, invert_001.height = 140.0, 100.0
    mix_009.width, mix_009.height = 140.0, 100.0
    mix_006.width, mix_006.height = 140.0, 100.0
    mix_017.width, mix_017.height = 140.0, 100.0
    noise_texture_001.width, noise_texture_001.height = 140.0, 100.0
    colorramp_003.width, colorramp_003.height = 240.0, 100.0
    mix_015.width, mix_015.height = 140.0, 100.0
    mix_004.width, mix_004.height = 140.0, 100.0
    mix_001.width, mix_001.height = 140.0, 100.0
    mix_024.width, mix_024.height = 140.0, 100.0
    mix_016.width, mix_016.height = 140.0, 100.0
    mix.width, mix.height = 140.0, 100.0
    colorramp_008.width, colorramp_008.height = 240.0, 100.0
    principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
    group_input.width, group_input.height = 167.06671142578125, 100.0

    # initialize asphalt links
    # mix_003.Result -> mix_002.A
    asphalt.links.new(mix_003.outputs[2], mix_002.inputs[6])
    # math_002.Value -> math.Value
    asphalt.links.new(math_002.outputs[0], math.inputs[1])
    # brick_texture.Color -> colorramp_001.Fac
    asphalt.links.new(brick_texture.outputs[0], colorramp_001.inputs[0])
    # mix_006.Result -> mix_004.Factor
    asphalt.links.new(mix_006.outputs[2], mix_004.inputs[0])
    # mix_001.Result -> mix_004.A
    asphalt.links.new(mix_001.outputs[2], mix_004.inputs[6])
    # reroute_003.Output -> colorramp.Fac
    asphalt.links.new(reroute_003.outputs[0], colorramp.inputs[0])
    # combine_xyz.Vector -> mapping.Vector
    asphalt.links.new(combine_xyz.outputs[0], mapping.inputs[0])
    # combine_xyz.Vector -> separate_xyz.Vector
    asphalt.links.new(combine_xyz.outputs[0], separate_xyz.inputs[0])
    # math_004.Value -> math_003.Value
    asphalt.links.new(math_004.outputs[0], math_003.inputs[0])
    # math_003.Value -> mix_005.A
    asphalt.links.new(math_003.outputs[0], mix_005.inputs[6])
    # separate_xyz.Y -> math_001.Value
    asphalt.links.new(separate_xyz.outputs[1], math_001.inputs[0])
    # colorramp_001.Color -> mix_005.Factor
    asphalt.links.new(colorramp_001.outputs[0], mix_005.inputs[0])
    # attribute.Fac -> combine_xyz.X
    asphalt.links.new(attribute.outputs[2], combine_xyz.inputs[0])
    # mix_005.Result -> mix_006.A
    asphalt.links.new(mix_005.outputs[2], mix_006.inputs[6])
    # attribute_002.Fac -> math_002.Value
    asphalt.links.new(attribute_002.outputs[2], math_002.inputs[0])
    # invert_001.Color -> mix_002.B
    asphalt.links.new(invert_001.outputs[0], mix_002.inputs[7])
    # mix_009.Result -> principled_bsdf.Base Color
    asphalt.links.new(mix_009.outputs[2], principled_bsdf.inputs[0])
    # separate_xyz.Y -> math_004.Value
    asphalt.links.new(separate_xyz.outputs[1], math_004.inputs[0])
    # math_001.Value -> math.Value
    asphalt.links.new(math_001.outputs[0], math.inputs[0])
    # mix_002.Result -> mix_001.Factor
    asphalt.links.new(mix_002.outputs[2], mix_001.inputs[0])
    # mix_011.Result -> mix_001.A
    asphalt.links.new(mix_011.outputs[2], mix_001.inputs[6])
    # mix_008.Result -> bump.Height
    asphalt.links.new(mix_008.outputs[2], bump.inputs[2])
    # mapping.Vector -> brick_texture.Vector
    asphalt.links.new(mapping.outputs[0], brick_texture.inputs[0])
    # attribute_001.Fac -> combine_xyz.Y
    asphalt.links.new(attribute_001.outputs[2], combine_xyz.inputs[1])
    # bump.Normal -> principled_bsdf.Normal
    asphalt.links.new(bump.outputs[0], principled_bsdf.inputs[5])
    # colorramp_002.Color -> mix_006.Factor
    asphalt.links.new(colorramp_002.outputs[0], mix_006.inputs[0])
    # math.Value -> mix_003.A
    asphalt.links.new(math.outputs[0], mix_003.inputs[6])
    # group_input.line_width -> math.Value
    asphalt.links.new(group_input.outputs[2], math.inputs[2])
    # group_input.line_width -> math_003.Value
    asphalt.links.new(group_input.outputs[2], math_003.inputs[2])
    # math_005.Value -> math_002.Value
    asphalt.links.new(math_005.outputs[0], math_002.inputs[1])
    # principled_bsdf.BSDF -> group_output.BSDF
    asphalt.links.new(principled_bsdf.outputs[0], group_output.inputs[0])
    # group_input.sideLine_margin -> math_005.Value
    asphalt.links.new(group_input.outputs[3], math_005.inputs[0])
    # group_input.middleLine_color -> mix_004.B
    asphalt.links.new(group_input.outputs[0], mix_004.inputs[7])
    # group_input.sideLine_color -> mix_001.B
    asphalt.links.new(group_input.outputs[1], mix_001.inputs[7])
    # group_input.dashLine_spacing -> brick_texture.Row Height
    asphalt.links.new(group_input.outputs[4], brick_texture.inputs[9])
    # group_input.dashLine_length -> brick_texture.Scale
    asphalt.links.new(group_input.outputs[5], brick_texture.inputs[4])
    # colorramp_003.Color -> mix_007.B
    asphalt.links.new(colorramp_003.outputs[0], mix_007.inputs[7])
    # noise_texture_001.Color -> colorramp_003.Fac
    asphalt.links.new(noise_texture_001.outputs[1], colorramp_003.inputs[0])
    # reroute.Output -> principled_bsdf.Roughness
    asphalt.links.new(reroute.outputs[0], principled_bsdf.inputs[2])
    # reroute.Output -> mix_008.Factor
    asphalt.links.new(reroute.outputs[0], mix_008.inputs[0])
    # colorramp.Color -> mix_008.B
    asphalt.links.new(colorramp.outputs[0], mix_008.inputs[7])
    # mix_007.Result -> mix_009.A
    asphalt.links.new(mix_007.outputs[2], mix_009.inputs[6])
    # colorramp_005.Color -> mix_009.Factor
    asphalt.links.new(colorramp_005.outputs[0], mix_009.inputs[0])
    # reroute.Output -> colorramp_005.Fac
    asphalt.links.new(reroute.outputs[0], colorramp_005.inputs[0])
    # colorramp.Color -> mix_011.A
    asphalt.links.new(colorramp.outputs[0], mix_011.inputs[6])
    # group_input.middleLine -> math_003.Value
    asphalt.links.new(group_input.outputs[6], math_003.inputs[1])
    # noise_texture.Color -> voronoi_texture.Vector
    asphalt.links.new(noise_texture.outputs[1], voronoi_texture.inputs[0])
    # reroute_001.Output -> noise_texture_001.Vector
    asphalt.links.new(reroute_001.outputs[0], noise_texture_001.inputs[0])
    # mapping_001.Vector -> reroute_001.Input
    asphalt.links.new(mapping_001.outputs[0], reroute_001.inputs[0])
    # value.Value -> mapping_001.Scale
    asphalt.links.new(value.outputs[0], mapping_001.inputs[3])
    # texture_coordinate.Object -> mapping_001.Vector
    asphalt.links.new(texture_coordinate.outputs[3], mapping_001.inputs[0])
    # combine_xyz_001.Vector -> math_007.Value
    asphalt.links.new(combine_xyz_001.outputs[0], math_007.inputs[0])
    # mix_016.Result -> mix.A
    asphalt.links.new(mix_016.outputs[2], mix.inputs[6])
    # mix_001.Result -> mix.B
    asphalt.links.new(mix_001.outputs[2], mix.inputs[7])
    # texture_coordinate_001.Object -> mapping_002.Vector
    asphalt.links.new(texture_coordinate_001.outputs[3], mapping_002.inputs[0])
    # mix_010.Result -> math_006.Value
    asphalt.links.new(mix_010.outputs[0], math_006.inputs[1])
    # noise_texture_002.Color -> colorramp_004.Fac
    asphalt.links.new(noise_texture_002.outputs[1], colorramp_004.inputs[0])
    # mapping_002.Vector -> noise_texture_002.Vector
    asphalt.links.new(mapping_002.outputs[0], noise_texture_002.inputs[0])
    # colorramp_004.Color -> math_006.Value
    asphalt.links.new(colorramp_004.outputs[0], math_006.inputs[0])
    # value_001.Value -> mapping_002.Scale
    asphalt.links.new(value_001.outputs[0], mapping_002.inputs[3])
    # group_input.wet -> mix_010.Factor
    asphalt.links.new(group_input.outputs[7], mix_010.inputs[0])
    # math_006.Value -> reroute.Input
    asphalt.links.new(math_006.outputs[0], reroute.inputs[0])
    # group_input.is_intersection -> mix_012.Factor
    asphalt.links.new(group_input.outputs[8], mix_012.inputs[0])
    # math_008.Value -> math_007.Value
    asphalt.links.new(math_008.outputs[0], math_007.inputs[2])
    # attribute_002.Fac -> math_008.Value
    asphalt.links.new(attribute_002.outputs[2], math_008.inputs[0])
    # mix_012.Result -> mix_013.A
    asphalt.links.new(mix_012.outputs[2], mix_013.inputs[6])
    # colorramp_001.Color -> mix_013.Factor
    asphalt.links.new(colorramp_001.outputs[0], mix_013.inputs[0])
    # attribute_004.Fac -> combine_xyz_001.Y
    asphalt.links.new(attribute_004.outputs[2], combine_xyz_001.inputs[1])
    # attribute_003.Fac -> combine_xyz_001.X
    asphalt.links.new(attribute_003.outputs[2], combine_xyz_001.inputs[0])
    # attribute_005.Fac -> combine_xyz_002.Y
    asphalt.links.new(attribute_005.outputs[2], combine_xyz_002.inputs[1])
    # attribute_006.Fac -> combine_xyz_002.X
    asphalt.links.new(attribute_006.outputs[2], combine_xyz_002.inputs[0])
    # combine_xyz_002.Vector -> brick_texture_001.Vector
    asphalt.links.new(combine_xyz_002.outputs[0], brick_texture_001.inputs[0])
    # math_007.Value -> mix_014.A
    asphalt.links.new(math_007.outputs[0], mix_014.inputs[6])
    # colorramp_006.Color -> mix_014.Factor
    asphalt.links.new(colorramp_006.outputs[0], mix_014.inputs[0])
    # brick_texture_001.Color -> colorramp_006.Fac
    asphalt.links.new(brick_texture_001.outputs[0], colorramp_006.inputs[0])
    # combine_xyz_002.Vector -> math_009.Value
    asphalt.links.new(combine_xyz_002.outputs[0], math_009.inputs[0])
    # mix_017.Result -> mix_015.Factor
    asphalt.links.new(mix_017.outputs[2], mix_015.inputs[0])
    # mix_004.Result -> mix_016.A
    asphalt.links.new(mix_004.outputs[2], mix_016.inputs[6])
    # group_input.is_intersection -> mix_016.Factor
    asphalt.links.new(group_input.outputs[8], mix_016.inputs[0])
    # group_input.pedestrian_crossing_color -> mix_015.A
    asphalt.links.new(group_input.outputs[9], mix_015.inputs[6])
    # mix.Result -> mix_007.A
    asphalt.links.new(mix.outputs[2], mix_007.inputs[6])
    # mix_001.Result -> mix_015.B
    asphalt.links.new(mix_001.outputs[2], mix_015.inputs[7])
    # mix_015.Result -> mix_016.B
    asphalt.links.new(mix_015.outputs[2], mix_016.inputs[7])
    # mix_023.Result -> mix_017.B
    asphalt.links.new(mix_023.outputs[2], mix_017.inputs[7])
    # combine_xyz_002.Vector -> math_010.Value
    asphalt.links.new(combine_xyz_002.outputs[0], math_010.inputs[0])
    # reroute_002.Output -> brick_texture_001.Scale
    asphalt.links.new(reroute_002.outputs[0], brick_texture_001.inputs[4])
    # group_input.pedestrian_crossing_dash -> reroute_002.Input
    asphalt.links.new(group_input.outputs[10], reroute_002.inputs[0])
    # reroute_002.Output -> brick_texture_002.Scale
    asphalt.links.new(reroute_002.outputs[0], brick_texture_002.inputs[4])
    # mapping_003.Vector -> brick_texture_002.Vector
    asphalt.links.new(mapping_003.outputs[0], brick_texture_002.inputs[0])
    # combine_xyz_001.Vector -> mapping_003.Vector
    asphalt.links.new(combine_xyz_001.outputs[0], mapping_003.inputs[0])
    # math_010.Value -> mix_018.A
    asphalt.links.new(math_010.outputs[0], mix_018.inputs[6])
    # colorramp_007.Color -> mix_018.Factor
    asphalt.links.new(colorramp_007.outputs[0], mix_018.inputs[0])
    # mix_014.Result -> mix_019.A
    asphalt.links.new(mix_014.outputs[2], mix_019.inputs[6])
    # mix_018.Result -> mix_019.B
    asphalt.links.new(mix_018.outputs[2], mix_019.inputs[7])
    # brick_texture_002.Color -> colorramp_007.Fac
    asphalt.links.new(brick_texture_002.outputs[0], colorramp_007.inputs[0])
    # math_010.Value -> mix_020.A
    asphalt.links.new(math_010.outputs[0], mix_020.inputs[6])
    # math_007.Value -> mix_020.B
    asphalt.links.new(math_007.outputs[0], mix_020.inputs[7])
    # mix_020.Result -> invert.Color
    asphalt.links.new(mix_020.outputs[2], invert.inputs[1])
    # mix_019.Result -> mix_022.A
    asphalt.links.new(mix_019.outputs[2], mix_022.inputs[6])
    # invert.Color -> mix_022.B
    asphalt.links.new(invert.outputs[0], mix_022.inputs[7])
    # mix_022.Result -> mix_012.B
    asphalt.links.new(mix_022.outputs[2], mix_012.inputs[7])
    # attribute_007.Fac -> math_011.Value
    asphalt.links.new(attribute_007.outputs[2], math_011.inputs[0])
    # attribute_002.Fac -> math_011.Value
    asphalt.links.new(attribute_002.outputs[2], math_011.inputs[1])
    # math_012.Value -> math_010.Value
    asphalt.links.new(math_012.outputs[0], math_010.inputs[1])
    # math_011.Value -> math_012.Value
    asphalt.links.new(math_011.outputs[0], math_012.inputs[0])
    # colorramp_002.Color -> invert_001.Color
    asphalt.links.new(colorramp_002.outputs[0], invert_001.inputs[1])
    # invert_001.Color -> mix_017.Factor
    asphalt.links.new(invert_001.outputs[0], mix_017.inputs[0])
    # reroute_001.Output -> noise_texture.Vector
    asphalt.links.new(reroute_001.outputs[0], noise_texture.inputs[0])
    # reroute_001.Output -> voronoi_texture_001.Vector
    asphalt.links.new(reroute_001.outputs[0], voronoi_texture_001.inputs[0])
    # voronoi_texture.Distance -> mix_021.A
    asphalt.links.new(voronoi_texture.outputs[0], mix_021.inputs[2])
    # voronoi_texture.Distance -> mix_021.A
    asphalt.links.new(voronoi_texture.outputs[0], mix_021.inputs[6])
    # voronoi_texture_001.Distance -> mix_021.B
    asphalt.links.new(voronoi_texture_001.outputs[0], mix_021.inputs[7])
    # mix_021.Result -> reroute_003.Input
    asphalt.links.new(mix_021.outputs[2], reroute_003.inputs[0])
    # reroute_003.Output -> colorramp_002.Fac
    asphalt.links.new(reroute_003.outputs[0], colorramp_002.inputs[0])
    # math_008.Value -> math_010.Value
    asphalt.links.new(math_008.outputs[0], math_010.inputs[2])
    # math_008.Value -> math_009.Value
    asphalt.links.new(math_008.outputs[0], math_009.inputs[2])
    # math_012.Value -> math_009.Value
    asphalt.links.new(math_012.outputs[0], math_009.inputs[1])
    # colorramp_008.Color -> mix.Factor
    asphalt.links.new(colorramp_008.outputs[0], mix.inputs[0])
    # math_009.Value -> mix_023.A
    asphalt.links.new(math_009.outputs[0], mix_023.inputs[6])
    # math_007.Value -> mix_023.B
    asphalt.links.new(math_007.outputs[0], mix_023.inputs[7])
    # mix_013.Result -> mix_024.A
    asphalt.links.new(mix_013.outputs[2], mix_024.inputs[6])
    # invert_001.Color -> mix_024.Factor
    asphalt.links.new(invert_001.outputs[0], mix_024.inputs[0])
    # principled_bsdf.BSDF -> group_output.tmp_viewer
    asphalt.links.new(principled_bsdf.outputs[0], group_output.inputs[1])
    # mix_024.Result -> colorramp_008.Fac
    asphalt.links.new(mix_024.outputs[2], colorramp_008.inputs[0])
    return asphalt


def get_road_geometry_nodes(
        width_roadline=6.499999523162842,
        width_sidewalk=3.8199996948242188,
        wet=0.625,
        color_sideline=(0.7364882826805115, 0.7364882826805115, 0.7364882826805115, 1.0),
        color_middleline=(1.0, 0.23297733068466187, 0.0, 1.0),
        color_pedestrial=(0.5028864741325378, 0.5028864741325378, 0.5028864741325378, 1.0),
        color_sidewalk=(0.19120171666145325, 0.13286834955215454, 0.09989873319864273, 1.0),
        brick_scale=1.5899999141693115,
        end_point_intersection=1.0,
):
    bpy.ops.object.select_all(action="DESELECT")

    # initialize main_road_geometry_nodes node group
    def main_road_geometry_nodes_node_group():
        main_road_geometry_nodes = bpy.data.node_groups.new(type='GeometryNodeTree', name="myMainRoadGeometryNodes")

        main_road_geometry_nodes.is_modifier = True

        # initialize main_road_geometry_nodes nodes
        # main_road_geometry_nodes interface
        # Socket Geometry
        geometry_socket = main_road_geometry_nodes.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                                        socket_type='NodeSocketGeometry')
        geometry_socket.attribute_domain = 'POINT'

        # Socket widthRoad
        widthroad_socket = main_road_geometry_nodes.interface.new_socket(name="widthRoad", in_out='OUTPUT',
                                                                         socket_type='NodeSocketFloat')
        widthroad_socket.subtype = 'NONE'
        widthroad_socket.default_value = 0.0
        widthroad_socket.min_value = -3.4028234663852886e+38
        widthroad_socket.max_value = 3.4028234663852886e+38
        widthroad_socket.attribute_domain = 'POINT'

        # Socket widthSidewalk
        widthsidewalk_socket = main_road_geometry_nodes.interface.new_socket(name="widthSidewalk", in_out='OUTPUT',
                                                                             socket_type='NodeSocketFloat')
        widthsidewalk_socket.subtype = 'NONE'
        widthsidewalk_socket.default_value = 0.0
        widthsidewalk_socket.min_value = -3.4028234663852886e+38
        widthsidewalk_socket.max_value = 3.4028234663852886e+38
        widthsidewalk_socket.attribute_domain = 'POINT'

        # Socket wet
        wet_socket = main_road_geometry_nodes.interface.new_socket(name="wet", in_out='OUTPUT',
                                                                   socket_type='NodeSocketFloat')
        wet_socket.subtype = 'NONE'
        wet_socket.default_value = 0.0
        wet_socket.min_value = -3.4028234663852886e+38
        wet_socket.max_value = 3.4028234663852886e+38
        wet_socket.attribute_domain = 'POINT'

        # Socket color_sideline
        color_sideline_socket = main_road_geometry_nodes.interface.new_socket(name="color_sideline", in_out='OUTPUT',
                                                                              socket_type='NodeSocketColor')
        color_sideline_socket.attribute_domain = 'POINT'

        # Socket color_middleline
        color_middleline_socket = main_road_geometry_nodes.interface.new_socket(name="color_middleline",
                                                                                in_out='OUTPUT',
                                                                                socket_type='NodeSocketColor')
        color_middleline_socket.attribute_domain = 'POINT'

        # Socket color_pedestrial
        color_pedestrial_socket = main_road_geometry_nodes.interface.new_socket(name="color_pedestrial",
                                                                                in_out='OUTPUT',
                                                                                socket_type='NodeSocketColor')
        color_pedestrial_socket.attribute_domain = 'POINT'

        # Socket color_sidewalk
        color_sidewalk_socket = main_road_geometry_nodes.interface.new_socket(name="color_sidewalk", in_out='OUTPUT',
                                                                              socket_type='NodeSocketColor')
        color_sidewalk_socket.attribute_domain = 'POINT'

        # Socket brick_scale
        brick_scale_socket = main_road_geometry_nodes.interface.new_socket(name="brick_scale", in_out='OUTPUT',
                                                                           socket_type='NodeSocketFloat')
        brick_scale_socket.subtype = 'NONE'
        brick_scale_socket.default_value = 0.0
        brick_scale_socket.min_value = -3.4028234663852886e+38
        brick_scale_socket.max_value = 3.4028234663852886e+38
        brick_scale_socket.attribute_domain = 'POINT'

        # Socket intersection rotation
        intersection_rotation_socket = main_road_geometry_nodes.interface.new_socket(name="intersection rotation",
                                                                                     in_out='OUTPUT',
                                                                                     socket_type='NodeSocketVector')
        intersection_rotation_socket.subtype = 'EULER'
        intersection_rotation_socket.default_value = (0.0, 0.0, 0.0)
        intersection_rotation_socket.min_value = -3.4028234663852886e+38
        intersection_rotation_socket.max_value = 3.4028234663852886e+38
        intersection_rotation_socket.attribute_domain = 'POINT'

        # Socket curve
        curve_socket = main_road_geometry_nodes.interface.new_socket(name="curve", in_out='INPUT',
                                                                     socket_type='NodeSocketGeometry')
        curve_socket.attribute_domain = 'POINT'

        # Socket width_roadlane
        width_roadlane_socket = main_road_geometry_nodes.interface.new_socket(name="width_roadlane", in_out='INPUT',
                                                                              socket_type='NodeSocketFloat')
        width_roadlane_socket.subtype = 'NONE'
        width_roadlane_socket.default_value = 0.0
        width_roadlane_socket.min_value = -3.4028234663852886e+38
        width_roadlane_socket.max_value = 3.4028234663852886e+38
        width_roadlane_socket.attribute_domain = 'POINT'

        # Socket width_sidewalk
        width_sidewalk_socket = main_road_geometry_nodes.interface.new_socket(name="width_sidewalk", in_out='INPUT',
                                                                              socket_type='NodeSocketFloat')
        width_sidewalk_socket.subtype = 'NONE'
        width_sidewalk_socket.default_value = 0.0
        width_sidewalk_socket.min_value = -3.4028234663852886e+38
        width_sidewalk_socket.max_value = 3.4028234663852886e+38
        width_sidewalk_socket.attribute_domain = 'POINT'

        # Socket wet
        wet_socket_1 = main_road_geometry_nodes.interface.new_socket(name="wet", in_out='INPUT',
                                                                     socket_type='NodeSocketFloat')
        wet_socket_1.subtype = 'FACTOR'
        wet_socket_1.default_value = 0.5
        wet_socket_1.min_value = 0.0
        wet_socket_1.max_value = 1.0
        wet_socket_1.attribute_domain = 'POINT'

        # Socket color_sideline
        color_sideline_socket_1 = main_road_geometry_nodes.interface.new_socket(name="color_sideline", in_out='INPUT',
                                                                                socket_type='NodeSocketColor')
        color_sideline_socket_1.attribute_domain = 'POINT'

        # Socket color_middleline
        color_middleline_socket_1 = main_road_geometry_nodes.interface.new_socket(name="color_middleline",
                                                                                  in_out='INPUT',
                                                                                  socket_type='NodeSocketColor')
        color_middleline_socket_1.attribute_domain = 'POINT'

        # Socket color_pedestrial
        color_pedestrial_socket_1 = main_road_geometry_nodes.interface.new_socket(name="color_pedestrial",
                                                                                  in_out='INPUT',
                                                                                  socket_type='NodeSocketColor')
        color_pedestrial_socket_1.attribute_domain = 'POINT'

        # Socket color_sidewalk
        color_sidewalk_socket_1 = main_road_geometry_nodes.interface.new_socket(name="color_sidewalk", in_out='INPUT',
                                                                                socket_type='NodeSocketColor')
        color_sidewalk_socket_1.attribute_domain = 'POINT'

        # Socket brick_scale
        brick_scale_socket_1 = main_road_geometry_nodes.interface.new_socket(name="brick_scale", in_out='INPUT',
                                                                             socket_type='NodeSocketFloat')
        brick_scale_socket_1.subtype = 'NONE'
        brick_scale_socket_1.default_value = 0.0
        brick_scale_socket_1.min_value = -3.4028234663852886e+38
        brick_scale_socket_1.max_value = 3.4028234663852886e+38
        brick_scale_socket_1.attribute_domain = 'POINT'

        # Socket endpoint intersection
        endpoint_intersection_socket = main_road_geometry_nodes.interface.new_socket(name="endpoint intersection",
                                                                                     in_out='INPUT',
                                                                                     socket_type='NodeSocketFloat')
        endpoint_intersection_socket.subtype = 'FACTOR'
        endpoint_intersection_socket.default_value = 1.0
        endpoint_intersection_socket.min_value = 0.0
        endpoint_intersection_socket.max_value = 1.0
        endpoint_intersection_socket.attribute_domain = 'POINT'

        # node Frame.002
        frame_002 = main_road_geometry_nodes.nodes.new("NodeFrame")
        frame_002.name = "Frame.002"
        frame_002.label_size = 20
        frame_002.shrink = True

        # node Frame
        frame = main_road_geometry_nodes.nodes.new("NodeFrame")
        frame.name = "Frame"
        frame.label_size = 20
        frame.shrink = True

        # node Frame.001
        frame_001 = main_road_geometry_nodes.nodes.new("NodeFrame")
        frame_001.name = "Frame.001"
        frame_001.label_size = 20
        frame_001.shrink = True

        # node Frame.003
        frame_003 = main_road_geometry_nodes.nodes.new("NodeFrame")
        frame_003.name = "Frame.003"
        frame_003.label_size = 20
        frame_003.shrink = True

        # node Set Shade Smooth
        set_shade_smooth = main_road_geometry_nodes.nodes.new("GeometryNodeSetShadeSmooth")
        set_shade_smooth.name = "Set Shade Smooth"
        set_shade_smooth.domain = 'FACE'
        # Selection
        set_shade_smooth.inputs[1].default_value = True
        # Shade Smooth
        set_shade_smooth.inputs[2].default_value = False

        # node Combine XYZ.009
        combine_xyz_009 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_009.name = "Combine XYZ.009"
        # Y
        combine_xyz_009.inputs[1].default_value = 0.0
        # Z
        combine_xyz_009.inputs[2].default_value = 0.0

        # node Join Geometry.004
        join_geometry_004 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_004.name = "Join Geometry.004"

        # node Set Material.004
        set_material_004 = main_road_geometry_nodes.nodes.new("GeometryNodeSetMaterial")
        set_material_004.name = "Set Material.004"
        # Selection
        set_material_004.inputs[1].default_value = True
        if "road" in bpy.data.materials:
            set_material_004.inputs[2].default_value = bpy.data.materials["road"]

        # node Set Material.005
        set_material_005 = main_road_geometry_nodes.nodes.new("GeometryNodeSetMaterial")
        set_material_005.name = "Set Material.005"
        # Selection
        set_material_005.inputs[1].default_value = True
        if "intersection" in bpy.data.materials:
            set_material_005.inputs[2].default_value = bpy.data.materials["intersection"]

        # node Reroute
        reroute = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute.name = "Reroute"
        # node Reroute.004
        reroute_004 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_004.name = "Reroute.004"
        # node Set Shade Smooth.002
        set_shade_smooth_002 = main_road_geometry_nodes.nodes.new("GeometryNodeSetShadeSmooth")
        set_shade_smooth_002.name = "Set Shade Smooth.002"
        set_shade_smooth_002.domain = 'FACE'
        # Selection
        set_shade_smooth_002.inputs[1].default_value = True
        # Shade Smooth
        set_shade_smooth_002.inputs[2].default_value = True

        # node Join Geometry.001
        join_geometry_001 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_001.name = "Join Geometry.001"

        # node Combine XYZ.010
        combine_xyz_010 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_010.name = "Combine XYZ.010"
        # Y
        combine_xyz_010.inputs[1].default_value = 0.0
        # Z
        combine_xyz_010.inputs[2].default_value = 0.0

        # node Combine XYZ.011
        combine_xyz_011 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_011.name = "Combine XYZ.011"
        # X
        combine_xyz_011.inputs[0].default_value = 0.0
        # Y
        combine_xyz_011.inputs[1].default_value = 0.0
        # Z
        combine_xyz_011.inputs[2].default_value = 0.0

        # node Combine XYZ.012
        combine_xyz_012 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_012.name = "Combine XYZ.012"
        # X
        combine_xyz_012.inputs[0].default_value = 0.0
        # Y
        combine_xyz_012.inputs[1].default_value = 0.0
        # Z
        combine_xyz_012.inputs[2].default_value = 0.0

        # node Curve Line.006
        curve_line_006 = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line_006.name = "Curve Line.006"
        curve_line_006.mode = 'POINTS'
        # Direction
        curve_line_006.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line_006.inputs[3].default_value = 1.0

        # node Curve Line.005
        curve_line_005 = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line_005.name = "Curve Line.005"
        curve_line_005.mode = 'POINTS'
        # Direction
        curve_line_005.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line_005.inputs[3].default_value = 1.0

        # node Math.005
        math_005 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_005.name = "Math.005"
        math_005.operation = 'ADD'
        math_005.use_clamp = False
        # Value_002
        math_005.inputs[2].default_value = 0.5

        # node Join Geometry.003
        join_geometry_003 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_003.name = "Join Geometry.003"

        # node Math.004
        math_004 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_004.name = "Math.004"
        math_004.operation = 'ADD'
        math_004.use_clamp = False
        # Value_002
        math_004.inputs[2].default_value = 0.5

        # node Math.003
        math_003 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_003.name = "Math.003"
        math_003.operation = 'MULTIPLY'
        math_003.use_clamp = False
        # Value_001
        math_003.inputs[1].default_value = 1.0
        # Value_002
        math_003.inputs[2].default_value = 0.5

        # node Math.011
        math_011 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_011.name = "Math.011"
        math_011.operation = 'MULTIPLY'
        math_011.use_clamp = False
        # Value_001
        math_011.inputs[1].default_value = 2.0
        # Value_002
        math_011.inputs[2].default_value = 0.5

        # node Combine XYZ.008
        combine_xyz_008 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_008.name = "Combine XYZ.008"
        # Y
        combine_xyz_008.inputs[1].default_value = 0.0
        # Z
        combine_xyz_008.inputs[2].default_value = 0.0

        # node Curve Line.004
        curve_line_004 = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line_004.name = "Curve Line.004"
        curve_line_004.mode = 'POINTS'
        # End
        curve_line_004.inputs[1].default_value = (0.0, 0.0, 0.0)
        # Direction
        curve_line_004.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line_004.inputs[3].default_value = 1.0

        # node Store Named Attribute.004
        store_named_attribute_004 = main_road_geometry_nodes.nodes.new("GeometryNodeStoreNamedAttribute")
        store_named_attribute_004.name = "Store Named Attribute.004"
        store_named_attribute_004.data_type = 'FLOAT'
        store_named_attribute_004.domain = 'POINT'
        # Selection
        store_named_attribute_004.inputs[1].default_value = True
        # Name
        store_named_attribute_004.inputs[2].default_value = "Gradient Y intersection"
        # Value_Vector
        store_named_attribute_004.inputs[3].default_value = (0.0, 0.0, 0.0)
        # Value_Color
        store_named_attribute_004.inputs[5].default_value = (0.0, 0.0, 0.0, 0.0)
        # Value_Bool
        store_named_attribute_004.inputs[6].default_value = False
        # Value_Int
        store_named_attribute_004.inputs[7].default_value = 0
        # Value_Rotation
        store_named_attribute_004.inputs[8].default_value = (0.0, 0.0, 0.0)

        # node Curve to Mesh.002
        curve_to_mesh_002 = main_road_geometry_nodes.nodes.new("GeometryNodeCurveToMesh")
        curve_to_mesh_002.name = "Curve to Mesh.002"
        # Fill Caps
        curve_to_mesh_002.inputs[2].default_value = False

        # node Mix.002
        mix_002 = main_road_geometry_nodes.nodes.new("ShaderNodeMix")
        mix_002.name = "Mix.002"
        mix_002.blend_type = 'MIX'
        mix_002.clamp_factor = True
        mix_002.clamp_result = False
        mix_002.data_type = 'FLOAT'
        mix_002.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_002.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_002.inputs[2].default_value = 0.0
        # B_Float
        mix_002.inputs[3].default_value = 1.0
        # A_Vector
        mix_002.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_002.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_002.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        # B_Color
        mix_002.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        # A_Rotation
        mix_002.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_002.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Curve Tangent
        curve_tangent = main_road_geometry_nodes.nodes.new("GeometryNodeInputTangent")
        curve_tangent.name = "Curve Tangent"

        # node Endpoint Selection
        endpoint_selection = main_road_geometry_nodes.nodes.new("GeometryNodeCurveEndpointSelection")
        endpoint_selection.name = "Endpoint Selection"
        # Start Size
        endpoint_selection.inputs[0].default_value = 0

        # node Reroute.003
        reroute_003 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_003.name = "Reroute.003"
        # node Store Named Attribute
        store_named_attribute = main_road_geometry_nodes.nodes.new("GeometryNodeStoreNamedAttribute")
        store_named_attribute.name = "Store Named Attribute"
        store_named_attribute.data_type = 'FLOAT'
        store_named_attribute.domain = 'POINT'
        # Selection
        store_named_attribute.inputs[1].default_value = True
        # Name
        store_named_attribute.inputs[2].default_value = "Gradient X"
        # Value_Vector
        store_named_attribute.inputs[3].default_value = (0.0, 0.0, 0.0)
        # Value_Color
        store_named_attribute.inputs[5].default_value = (0.0, 0.0, 0.0, 0.0)
        # Value_Bool
        store_named_attribute.inputs[6].default_value = False
        # Value_Int
        store_named_attribute.inputs[7].default_value = 0
        # Value_Rotation
        store_named_attribute.inputs[8].default_value = (0.0, 0.0, 0.0)

        # node Combine XYZ.002
        combine_xyz_002 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_002.name = "Combine XYZ.002"
        # Y
        combine_xyz_002.inputs[1].default_value = 0.0
        # Z
        combine_xyz_002.inputs[2].default_value = 0.0

        # node Curve Line
        curve_line = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line.name = "Curve Line"
        curve_line.mode = 'POINTS'
        # Direction
        curve_line.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line.inputs[3].default_value = 1.0

        # node Combine XYZ
        combine_xyz = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz.name = "Combine XYZ"
        # Y
        combine_xyz.inputs[1].default_value = 0.0
        # Z
        combine_xyz.inputs[2].default_value = 0.0

        # node Combine XYZ.001
        combine_xyz_001 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_001.name = "Combine XYZ.001"
        # X
        combine_xyz_001.inputs[0].default_value = 0.0
        # Y
        combine_xyz_001.inputs[1].default_value = 0.0
        # Z
        combine_xyz_001.inputs[2].default_value = 0.0

        # node Curve Line.003
        curve_line_003 = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line_003.name = "Curve Line.003"
        curve_line_003.mode = 'POINTS'
        # Direction
        curve_line_003.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line_003.inputs[3].default_value = 1.0

        # node Combine XYZ.003
        combine_xyz_003 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_003.name = "Combine XYZ.003"
        # X
        combine_xyz_003.inputs[0].default_value = 0.0
        # Y
        combine_xyz_003.inputs[1].default_value = 0.0
        # Z
        combine_xyz_003.inputs[2].default_value = 0.0

        # node Join Geometry.002
        join_geometry_002 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_002.name = "Join Geometry.002"

        # node Curve to Mesh
        curve_to_mesh = main_road_geometry_nodes.nodes.new("GeometryNodeCurveToMesh")
        curve_to_mesh.name = "Curve to Mesh"
        # Fill Caps
        curve_to_mesh.inputs[2].default_value = False

        # node Math.006
        math_006 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_006.name = "Math.006"
        math_006.operation = 'ADD'
        math_006.use_clamp = False
        # Value_002
        math_006.inputs[2].default_value = 0.5

        # node Math.007
        math_007 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_007.name = "Math.007"
        math_007.operation = 'MULTIPLY'
        math_007.use_clamp = False
        # Value_001
        math_007.inputs[1].default_value = -1.0
        # Value_002
        math_007.inputs[2].default_value = 0.5

        # node Spline Parameter
        spline_parameter = main_road_geometry_nodes.nodes.new("GeometryNodeSplineParameter")
        spline_parameter.name = "Spline Parameter"

        # node Mix
        mix = main_road_geometry_nodes.nodes.new("ShaderNodeMix")
        mix.name = "Mix"
        mix.blend_type = 'MIX'
        mix.clamp_factor = True
        mix.clamp_result = False
        mix.data_type = 'FLOAT'
        mix.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix.inputs[2].default_value = 0.0
        # B_Float
        mix.inputs[3].default_value = 1.0
        # A_Vector
        mix.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        # B_Color
        mix.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        # A_Rotation
        mix.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Curve to Mesh.001
        curve_to_mesh_001 = main_road_geometry_nodes.nodes.new("GeometryNodeCurveToMesh")
        curve_to_mesh_001.name = "Curve to Mesh.001"
        # Fill Caps
        curve_to_mesh_001.inputs[2].default_value = False

        # node Store Named Attribute.003
        store_named_attribute_003 = main_road_geometry_nodes.nodes.new("GeometryNodeStoreNamedAttribute")
        store_named_attribute_003.name = "Store Named Attribute.003"
        store_named_attribute_003.data_type = 'FLOAT'
        store_named_attribute_003.domain = 'POINT'
        # Selection
        store_named_attribute_003.inputs[1].default_value = True
        # Name
        store_named_attribute_003.inputs[2].default_value = "Gradient X2"
        # Value_Vector
        store_named_attribute_003.inputs[3].default_value = (0.0, 0.0, 0.0)
        # Value_Color
        store_named_attribute_003.inputs[5].default_value = (0.0, 0.0, 0.0, 0.0)
        # Value_Bool
        store_named_attribute_003.inputs[6].default_value = False
        # Value_Int
        store_named_attribute_003.inputs[7].default_value = 0
        # Value_Rotation
        store_named_attribute_003.inputs[8].default_value = (0.0, 0.0, 0.0)

        # node Combine XYZ.007
        combine_xyz_007 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_007.name = "Combine XYZ.007"
        # Y
        combine_xyz_007.inputs[1].default_value = 0.0
        # Z
        combine_xyz_007.inputs[2].default_value = 0.0

        # node Spline Parameter.002
        spline_parameter_002 = main_road_geometry_nodes.nodes.new("GeometryNodeSplineParameter")
        spline_parameter_002.name = "Spline Parameter.002"

        # node Combine XYZ.005
        combine_xyz_005 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_005.name = "Combine XYZ.005"
        # Y
        combine_xyz_005.inputs[1].default_value = 0.0
        # Z
        combine_xyz_005.inputs[2].default_value = 0.0

        # node Combine XYZ.006
        combine_xyz_006 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_006.name = "Combine XYZ.006"
        # Y
        combine_xyz_006.inputs[1].default_value = 0.0
        # Z
        combine_xyz_006.inputs[2].default_value = 0.0

        # node Combine XYZ.004
        combine_xyz_004 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_004.name = "Combine XYZ.004"
        # Y
        combine_xyz_004.inputs[1].default_value = 0.0
        # Z
        combine_xyz_004.inputs[2].default_value = 0.0

        # node Spline Parameter.003
        spline_parameter_003 = main_road_geometry_nodes.nodes.new("GeometryNodeSplineParameter")
        spline_parameter_003.name = "Spline Parameter.003"

        # node Curve Line.002
        curve_line_002 = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line_002.name = "Curve Line.002"
        curve_line_002.mode = 'POINTS'
        # Direction
        curve_line_002.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line_002.inputs[3].default_value = 1.0

        # node Curve Line.001
        curve_line_001 = main_road_geometry_nodes.nodes.new("GeometryNodeCurvePrimitiveLine")
        curve_line_001.name = "Curve Line.001"
        curve_line_001.mode = 'POINTS'
        # Direction
        curve_line_001.inputs[2].default_value = (0.0, 0.0, 1.0)
        # Length
        curve_line_001.inputs[3].default_value = 1.0

        # node Join Geometry
        join_geometry = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry.name = "Join Geometry"

        # node Math.002
        math_002 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_002.name = "Math.002"
        math_002.operation = 'MULTIPLY'
        math_002.use_clamp = False
        # Value_001
        math_002.inputs[1].default_value = -1.0
        # Value_002
        math_002.inputs[2].default_value = 0.5

        # node Math.001
        math_001 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_001.name = "Math.001"
        math_001.operation = 'ADD'
        math_001.use_clamp = False
        # Value_002
        math_001.inputs[2].default_value = 0.5

        # node Math
        math = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math.name = "Math"
        math.operation = 'MULTIPLY'
        math.use_clamp = False
        # Value_001
        math.inputs[1].default_value = -1.0
        # Value_002
        math.inputs[2].default_value = 0.5

        # node Join Geometry.006
        join_geometry_006 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_006.name = "Join Geometry.006"

        # node Set Material.002
        set_material_002 = main_road_geometry_nodes.nodes.new("GeometryNodeSetMaterial")
        set_material_002.name = "Set Material.002"
        # Selection
        set_material_002.inputs[1].default_value = True
        if "sidewalk" in bpy.data.materials:
            set_material_002.inputs[2].default_value = bpy.data.materials["sidewalk"]

        # node Store Named Attribute.002
        store_named_attribute_002 = main_road_geometry_nodes.nodes.new("GeometryNodeStoreNamedAttribute")
        store_named_attribute_002.name = "Store Named Attribute.002"
        store_named_attribute_002.data_type = 'FLOAT'
        store_named_attribute_002.domain = 'POINT'
        # Selection
        store_named_attribute_002.inputs[1].default_value = True
        # Name
        store_named_attribute_002.inputs[2].default_value = "Gradient Y2"
        # Value_Vector
        store_named_attribute_002.inputs[3].default_value = (0.0, 0.0, 0.0)
        # Value_Color
        store_named_attribute_002.inputs[5].default_value = (0.0, 0.0, 0.0, 0.0)
        # Value_Bool
        store_named_attribute_002.inputs[6].default_value = False
        # Value_Int
        store_named_attribute_002.inputs[7].default_value = 0
        # Value_Rotation
        store_named_attribute_002.inputs[8].default_value = (0.0, 0.0, 0.0)

        # node Reroute.002
        reroute_002 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_002.name = "Reroute.002"
        # node Reroute.005
        reroute_005 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_005.name = "Reroute.005"
        # node Reroute.011
        reroute_011 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_011.name = "Reroute.011"
        # node Extrude Mesh
        extrude_mesh = main_road_geometry_nodes.nodes.new("GeometryNodeExtrudeMesh")
        extrude_mesh.name = "Extrude Mesh"
        extrude_mesh.mode = 'FACES'
        # Selection
        extrude_mesh.inputs[1].default_value = True
        # Offset
        extrude_mesh.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Offset Scale
        extrude_mesh.inputs[3].default_value = 0.05000000074505806
        # Individual
        extrude_mesh.inputs[4].default_value = True

        # node Realize Instances.001
        realize_instances_001 = main_road_geometry_nodes.nodes.new("GeometryNodeRealizeInstances")
        realize_instances_001.name = "Realize Instances.001"

        # node Realize Instances
        realize_instances = main_road_geometry_nodes.nodes.new("GeometryNodeRealizeInstances")
        realize_instances.name = "Realize Instances"

        # node Realize Instances.002
        realize_instances_002 = main_road_geometry_nodes.nodes.new("GeometryNodeRealizeInstances")
        realize_instances_002.name = "Realize Instances.002"

        # node Spline Parameter.001
        spline_parameter_001 = main_road_geometry_nodes.nodes.new("GeometryNodeSplineParameter")
        spline_parameter_001.name = "Spline Parameter.001"

        # node Store Named Attribute.001
        store_named_attribute_001 = main_road_geometry_nodes.nodes.new("GeometryNodeStoreNamedAttribute")
        store_named_attribute_001.name = "Store Named Attribute.001"
        store_named_attribute_001.data_type = 'FLOAT'
        store_named_attribute_001.domain = 'POINT'
        # Selection
        store_named_attribute_001.inputs[1].default_value = True
        # Name
        store_named_attribute_001.inputs[2].default_value = "Gradient Y"
        # Value_Vector
        store_named_attribute_001.inputs[3].default_value = (0.0, 0.0, 0.0)
        # Value_Color
        store_named_attribute_001.inputs[5].default_value = (0.0, 0.0, 0.0, 0.0)
        # Value_Bool
        store_named_attribute_001.inputs[6].default_value = False
        # Value_Int
        store_named_attribute_001.inputs[7].default_value = 0
        # Value_Rotation
        store_named_attribute_001.inputs[8].default_value = (0.0, 0.0, 0.0)

        # node Reroute.007
        reroute_007 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_007.name = "Reroute.007"
        # node Join Geometry.007
        join_geometry_007 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_007.name = "Join Geometry.007"

        # node Combine XYZ.013
        combine_xyz_013 = main_road_geometry_nodes.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz_013.name = "Combine XYZ.013"
        # Z
        combine_xyz_013.inputs[2].default_value = 0.0

        # node Separate XYZ
        separate_xyz = main_road_geometry_nodes.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz.name = "Separate XYZ"

        # node Compare
        compare = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare.name = "Compare"
        compare.data_type = 'FLOAT'
        compare.mode = 'ELEMENT'
        compare.operation = 'GREATER_THAN'
        # A
        compare.inputs[0].default_value = 0.0
        # A_INT
        compare.inputs[2].default_value = 0
        # B_INT
        compare.inputs[3].default_value = 0
        # A_VEC3
        compare.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare.inputs[8].default_value = ""
        # B_STR
        compare.inputs[9].default_value = ""
        # C
        compare.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare.inputs[12].default_value = 0.0010000000474974513

        # node Instance on Points.001
        instance_on_points_001 = main_road_geometry_nodes.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points_001.name = "Instance on Points.001"
        # Pick Instance
        instance_on_points_001.inputs[3].default_value = False
        # Instance Index
        instance_on_points_001.inputs[4].default_value = 0
        # Rotation
        instance_on_points_001.inputs[5].default_value = (0.0, 0.0, 0.0)
        # Scale
        instance_on_points_001.inputs[6].default_value = (1.0, 1.0, 1.0)

        # node Reroute.006
        reroute_006 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_006.name = "Reroute.006"
        # node Separate XYZ.002
        separate_xyz_002 = main_road_geometry_nodes.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_002.name = "Separate XYZ.002"

        # node Instance on Points.003
        instance_on_points_003 = main_road_geometry_nodes.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points_003.name = "Instance on Points.003"
        # Pick Instance
        instance_on_points_003.inputs[3].default_value = False
        # Instance Index
        instance_on_points_003.inputs[4].default_value = 0
        # Rotation
        instance_on_points_003.inputs[5].default_value = (0.0, 0.0, 3.1415927410125732)
        # Scale
        instance_on_points_003.inputs[6].default_value = (1.0, 1.0, 1.0)

        # node Compare.003
        compare_003 = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare_003.name = "Compare.003"
        compare_003.data_type = 'FLOAT'
        compare_003.mode = 'ELEMENT'
        compare_003.operation = 'LESS_THAN'
        # A_INT
        compare_003.inputs[2].default_value = 0
        # B_INT
        compare_003.inputs[3].default_value = 0
        # A_VEC3
        compare_003.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare_003.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare_003.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare_003.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare_003.inputs[8].default_value = ""
        # B_STR
        compare_003.inputs[9].default_value = ""
        # C
        compare_003.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare_003.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare_003.inputs[12].default_value = 0.0010000000474974513

        # node Compare.002
        compare_002 = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare_002.name = "Compare.002"
        compare_002.data_type = 'FLOAT'
        compare_002.mode = 'ELEMENT'
        compare_002.operation = 'GREATER_THAN'
        # A
        compare_002.inputs[0].default_value = 1.0
        # A_INT
        compare_002.inputs[2].default_value = 0
        # B_INT
        compare_002.inputs[3].default_value = 0
        # A_VEC3
        compare_002.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare_002.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare_002.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare_002.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare_002.inputs[8].default_value = ""
        # B_STR
        compare_002.inputs[9].default_value = ""
        # C
        compare_002.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare_002.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare_002.inputs[12].default_value = 0.0010000000474974513

        # node Math.010
        math_010 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_010.name = "Math.010"
        math_010.operation = 'SUBTRACT'
        math_010.use_clamp = False
        # Value_002
        math_010.inputs[2].default_value = 0.5

        # node Reroute.001
        reroute_001 = main_road_geometry_nodes.nodes.new("NodeReroute")
        reroute_001.name = "Reroute.001"
        # node Compare.004
        compare_004 = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare_004.name = "Compare.004"
        compare_004.data_type = 'FLOAT'
        compare_004.mode = 'ELEMENT'
        compare_004.operation = 'GREATER_THAN'
        # B
        compare_004.inputs[1].default_value = 0.0
        # A_INT
        compare_004.inputs[2].default_value = 0
        # B_INT
        compare_004.inputs[3].default_value = 0
        # A_VEC3
        compare_004.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare_004.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare_004.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare_004.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare_004.inputs[8].default_value = ""
        # B_STR
        compare_004.inputs[9].default_value = ""
        # C
        compare_004.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare_004.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare_004.inputs[12].default_value = 0.0010000000474974513

        # node Compare.005
        compare_005 = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare_005.name = "Compare.005"
        compare_005.data_type = 'FLOAT'
        compare_005.mode = 'ELEMENT'
        compare_005.operation = 'GREATER_THAN'
        # A_INT
        compare_005.inputs[2].default_value = 0
        # B_INT
        compare_005.inputs[3].default_value = 0
        # A_VEC3
        compare_005.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare_005.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare_005.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare_005.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare_005.inputs[8].default_value = ""
        # B_STR
        compare_005.inputs[9].default_value = ""
        # C
        compare_005.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare_005.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare_005.inputs[12].default_value = 0.0010000000474974513

        # node Math.012
        math_012 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_012.name = "Math.012"
        math_012.operation = 'SUBTRACT'
        math_012.use_clamp = False
        # Value_002
        math_012.inputs[2].default_value = 0.5

        # node Separate XYZ.003
        separate_xyz_003 = main_road_geometry_nodes.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_003.name = "Separate XYZ.003"

        # node Math.013
        math_013 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_013.name = "Math.013"
        math_013.operation = 'MULTIPLY'
        math_013.use_clamp = False
        # Value_001
        math_013.inputs[1].default_value = -1.0
        # Value_002
        math_013.inputs[2].default_value = 0.5

        # node Compare.006
        compare_006 = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare_006.name = "Compare.006"
        compare_006.data_type = 'FLOAT'
        compare_006.mode = 'ELEMENT'
        compare_006.operation = 'GREATER_THAN'
        # A_INT
        compare_006.inputs[2].default_value = 0
        # B_INT
        compare_006.inputs[3].default_value = 0
        # A_VEC3
        compare_006.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare_006.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare_006.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare_006.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare_006.inputs[8].default_value = ""
        # B_STR
        compare_006.inputs[9].default_value = ""
        # C
        compare_006.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare_006.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare_006.inputs[12].default_value = 0.0010000000474974513

        # node Math.014
        math_014 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_014.name = "Math.014"
        math_014.operation = 'SUBTRACT'
        math_014.use_clamp = False
        # Value_002
        math_014.inputs[2].default_value = 0.5

        # node Instance on Points.005
        instance_on_points_005 = main_road_geometry_nodes.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points_005.name = "Instance on Points.005"
        # Pick Instance
        instance_on_points_005.inputs[3].default_value = False
        # Instance Index
        instance_on_points_005.inputs[4].default_value = 0
        # Rotation
        instance_on_points_005.inputs[5].default_value = (0.0, 0.0, -1.5707963705062866)
        # Scale
        instance_on_points_005.inputs[6].default_value = (1.0, 1.0, 1.0)

        # node Math.015
        math_015 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_015.name = "Math.015"
        math_015.operation = 'MULTIPLY'
        math_015.use_clamp = False
        # Value_001
        math_015.inputs[1].default_value = -1.0
        # Value_002
        math_015.inputs[2].default_value = 0.5

        # node Compare.007
        compare_007 = main_road_geometry_nodes.nodes.new("FunctionNodeCompare")
        compare_007.name = "Compare.007"
        compare_007.data_type = 'FLOAT'
        compare_007.mode = 'ELEMENT'
        compare_007.operation = 'GREATER_THAN'
        # A_INT
        compare_007.inputs[2].default_value = 0
        # B_INT
        compare_007.inputs[3].default_value = 0
        # A_VEC3
        compare_007.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_VEC3
        compare_007.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_COL
        compare_007.inputs[6].default_value = (0.0, 0.0, 0.0, 0.0)
        # B_COL
        compare_007.inputs[7].default_value = (0.0, 0.0, 0.0, 0.0)
        # A_STR
        compare_007.inputs[8].default_value = ""
        # B_STR
        compare_007.inputs[9].default_value = ""
        # C
        compare_007.inputs[10].default_value = 0.8999999761581421
        # Angle
        compare_007.inputs[11].default_value = 0.08726649731397629
        # Epsilon
        compare_007.inputs[12].default_value = 0.0010000000474974513

        # node Separate XYZ.004
        separate_xyz_004 = main_road_geometry_nodes.nodes.new("ShaderNodeSeparateXYZ")
        separate_xyz_004.name = "Separate XYZ.004"

        # node Position
        position = main_road_geometry_nodes.nodes.new("GeometryNodeInputPosition")
        position.name = "Position"

        # node Math.008
        math_008 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_008.name = "Math.008"
        math_008.operation = 'ADD'
        math_008.use_clamp = False
        # Value_002
        math_008.inputs[2].default_value = 0.5

        # node Instance on Points.004
        instance_on_points_004 = main_road_geometry_nodes.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points_004.name = "Instance on Points.004"
        # Pick Instance
        instance_on_points_004.inputs[3].default_value = False
        # Instance Index
        instance_on_points_004.inputs[4].default_value = 0
        # Rotation
        instance_on_points_004.inputs[5].default_value = (0.0, 0.0, 1.5707963705062866)
        # Scale
        instance_on_points_004.inputs[6].default_value = (1.0, 1.0, 1.0)

        # node Math.009
        math_009 = main_road_geometry_nodes.nodes.new("ShaderNodeMath")
        math_009.name = "Math.009"
        math_009.operation = 'MULTIPLY'
        math_009.use_clamp = True
        # Value_001
        math_009.inputs[1].default_value = 0.75
        # Value_002
        math_009.inputs[2].default_value = 0.5

        # node Mesh to Points
        mesh_to_points = main_road_geometry_nodes.nodes.new("GeometryNodeMeshToPoints")
        mesh_to_points.name = "Mesh to Points"
        mesh_to_points.mode = 'VERTICES'
        # Selection
        mesh_to_points.inputs[1].default_value = True
        # Position
        mesh_to_points.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Radius
        mesh_to_points.inputs[3].default_value = 0.05000000074505806

        # node Set Material.003
        set_material_003 = main_road_geometry_nodes.nodes.new("GeometryNodeSetMaterial")
        set_material_003.name = "Set Material.003"
        # Selection
        set_material_003.inputs[1].default_value = True
        if "sidewalk_corner" in bpy.data.materials:
            set_material_003.inputs[2].default_value = bpy.data.materials["sidewalk_corner"]

        # node Arc
        arc = main_road_geometry_nodes.nodes.new("GeometryNodeCurveArc")
        arc.name = "Arc"
        arc.mode = 'RADIUS'
        # Resolution
        arc.inputs[0].default_value = 16
        # Start
        arc.inputs[1].default_value = (-1.0, 0.0, 0.0)
        # Middle
        arc.inputs[2].default_value = (0.0, 2.0, 0.0)
        # End
        arc.inputs[3].default_value = (1.0, 0.0, 0.0)
        # Start Angle
        arc.inputs[5].default_value = 0.0
        # Sweep Angle
        arc.inputs[6].default_value = 1.5707963705062866
        # Offset Angle
        arc.inputs[7].default_value = 0.0
        # Connect Center
        arc.inputs[8].default_value = True
        # Invert Arc
        arc.inputs[9].default_value = False

        # node Fill Curve
        fill_curve = main_road_geometry_nodes.nodes.new("GeometryNodeFillCurve")
        fill_curve.name = "Fill Curve"
        fill_curve.mode = 'TRIANGLES'

        # node Group Input
        group_input = main_road_geometry_nodes.nodes.new("NodeGroupInput")
        group_input.name = "Group Input"

        # node Join Geometry.005
        join_geometry_005 = main_road_geometry_nodes.nodes.new("GeometryNodeJoinGeometry")
        join_geometry_005.name = "Join Geometry.005"

        # node Instance on Points
        instance_on_points = main_road_geometry_nodes.nodes.new("GeometryNodeInstanceOnPoints")
        instance_on_points.name = "Instance on Points"
        # Pick Instance
        instance_on_points.inputs[3].default_value = False
        # Instance Index
        instance_on_points.inputs[4].default_value = 0
        # Scale
        instance_on_points.inputs[6].default_value = (1.0, 1.0, 1.0)

        # node Store Named Attribute.005
        store_named_attribute_005 = main_road_geometry_nodes.nodes.new("GeometryNodeStoreNamedAttribute")
        store_named_attribute_005.name = "Store Named Attribute.005"
        store_named_attribute_005.data_type = 'FLOAT'
        store_named_attribute_005.domain = 'POINT'
        # Selection
        store_named_attribute_005.inputs[1].default_value = True
        # Name
        store_named_attribute_005.inputs[2].default_value = "Gradient Y intersection2"
        # Value_Vector
        store_named_attribute_005.inputs[3].default_value = (0.0, 0.0, 0.0)
        # Value_Color
        store_named_attribute_005.inputs[5].default_value = (0.0, 0.0, 0.0, 0.0)
        # Value_Bool
        store_named_attribute_005.inputs[6].default_value = False
        # Value_Int
        store_named_attribute_005.inputs[7].default_value = 0
        # Value_Rotation
        store_named_attribute_005.inputs[8].default_value = (0.0, 0.0, 0.0)

        # node Align Euler to Vector
        align_euler_to_vector = main_road_geometry_nodes.nodes.new("FunctionNodeAlignEulerToVector")
        align_euler_to_vector.name = "Align Euler to Vector"
        align_euler_to_vector.axis = 'X'
        align_euler_to_vector.pivot_axis = 'AUTO'
        # Rotation
        align_euler_to_vector.inputs[0].default_value = (0.0, 0.0, 0.0)
        # Factor
        align_euler_to_vector.inputs[1].default_value = 1.0

        # node Group Output
        group_output = main_road_geometry_nodes.nodes.new("NodeGroupOutput")
        group_output.name = "Group Output"
        group_output.is_active_output = True

        # Set parents
        combine_xyz_010.parent = frame_002
        combine_xyz_011.parent = frame_002
        combine_xyz_012.parent = frame_002
        curve_line_006.parent = frame_002
        curve_line_005.parent = frame_002
        math_005.parent = frame_002
        join_geometry_003.parent = frame_002
        math_004.parent = frame_002
        math_003.parent = frame_002
        math_011.parent = frame_002
        combine_xyz_008.parent = frame_002
        curve_line_004.parent = frame_002
        store_named_attribute_004.parent = frame_002
        curve_to_mesh_002.parent = frame_002
        mix_002.parent = frame_002
        curve_tangent.parent = frame_002
        endpoint_selection.parent = frame_002
        reroute_003.parent = frame_002
        store_named_attribute.parent = frame
        combine_xyz_002.parent = frame
        curve_line.parent = frame
        combine_xyz.parent = frame
        combine_xyz_001.parent = frame
        curve_line_003.parent = frame
        combine_xyz_003.parent = frame
        join_geometry_002.parent = frame
        curve_to_mesh.parent = frame
        math_006.parent = frame
        math_007.parent = frame
        spline_parameter.parent = frame
        curve_to_mesh_001.parent = frame_001
        store_named_attribute_003.parent = frame_001
        combine_xyz_007.parent = frame_001
        spline_parameter_002.parent = frame_001
        combine_xyz_005.parent = frame_001
        combine_xyz_006.parent = frame_001
        combine_xyz_004.parent = frame_001
        spline_parameter_003.parent = frame_001
        curve_line_002.parent = frame_001
        curve_line_001.parent = frame_001
        join_geometry.parent = frame_001
        math_002.parent = frame_001
        math_001.parent = frame_001
        math.parent = frame_001
        join_geometry_006.parent = frame_001
        set_material_002.parent = frame_001
        store_named_attribute_002.parent = frame_001
        reroute_005.parent = frame_001
        extrude_mesh.parent = frame_001
        realize_instances_001.parent = frame_001
        spline_parameter_001.parent = frame
        store_named_attribute_001.parent = frame
        reroute_007.parent = frame_003
        join_geometry_007.parent = frame_003
        combine_xyz_013.parent = frame_003
        separate_xyz.parent = frame_003
        compare.parent = frame_003
        instance_on_points_001.parent = frame_003
        reroute_006.parent = frame_003
        separate_xyz_002.parent = frame_003
        instance_on_points_003.parent = frame_003
        compare_003.parent = frame_003
        compare_002.parent = frame_003
        math_010.parent = frame_003
        reroute_001.parent = frame_003
        compare_004.parent = frame_003
        compare_005.parent = frame_003
        math_012.parent = frame_003
        separate_xyz_003.parent = frame_003
        math_013.parent = frame_003
        compare_006.parent = frame_003
        math_014.parent = frame_003
        instance_on_points_005.parent = frame_003
        math_015.parent = frame_003
        compare_007.parent = frame_003
        separate_xyz_004.parent = frame_003
        position.parent = frame_003
        math_008.parent = frame_003
        instance_on_points_004.parent = frame_003
        math_009.parent = frame_003
        mesh_to_points.parent = frame_003
        set_material_003.parent = frame_003
        join_geometry_005.parent = frame_002
        instance_on_points.parent = frame_002
        store_named_attribute_005.parent = frame_002
        align_euler_to_vector.parent = frame_002

        # Set locations
        frame_002.location = (827.736083984375, 285.8310546875)
        frame.location = (937.7244873046875, 821.0020141601562)
        frame_001.location = (1576.0775146484375, -291.9151916503906)
        frame_003.location = (255.36007690429688, -144.0086669921875)
        set_shade_smooth.location = (3180.46630859375, 608.6560668945312)
        combine_xyz_009.location = (801.334228515625, 1077.6002197265625)
        join_geometry_004.location = (2749.3056640625, 1087.47802734375)
        set_material_004.location = (1689.53857421875, 1060.760498046875)
        set_material_005.location = (2529.51220703125, 1614.2626953125)
        reroute.location = (-713.0432739257812, 373.1620178222656)
        reroute_004.location = (-757.8693237304688, 1315.761474609375)
        set_shade_smooth_002.location = (3174.294921875, 1029.6922607421875)
        join_geometry_001.location = (4426.97265625, 981.884033203125)
        combine_xyz_010.location = (-246.1501922607422, 1443.7652587890625)
        combine_xyz_011.location = (-247.7700653076172, 1565.2772216796875)
        combine_xyz_012.location = (-241.1321258544922, 1315.2091064453125)
        curve_line_006.location = (-12.074722290039062, 1357.326416015625)
        curve_line_005.location = (-86.34085845947266, 1580.44921875)
        math_005.location = (-436.90380859375, 1422.154541015625)
        join_geometry_003.location = (95.39913940429688, 1603.0462646484375)
        math_004.location = (-574.0643310546875, 1601.5758056640625)
        math_003.location = (-239.8043670654297, 1938.54638671875)
        math_011.location = (-426.1263732910156, 1792.362548828125)
        combine_xyz_008.location = (-63.174957275390625, 1943.374755859375)
        curve_line_004.location = (116.08712005615234, 1960.88232421875)
        store_named_attribute_004.location = (383.7430725097656, 1701.8739013671875)
        curve_to_mesh_002.location = (666.3407592773438, 2051.384521484375)
        mix_002.location = (-214.62937927246094, 2448.766845703125)
        curve_tangent.location = (-204.2279510498047, 2591.10888671875)
        endpoint_selection.location = (138.87615966796875, 2444.050048828125)
        reroute_003.location = (-422.2627868652344, 1999.6270751953125)
        store_named_attribute.location = (-42.96711730957031, 234.11785888671875)
        combine_xyz_002.location = (-299.9373474121094, -487.634033203125)
        curve_line.location = (-146.76589965820312, -100.88233947753906)
        combine_xyz.location = (-306.57525634765625, -237.56602478027344)
        combine_xyz_001.location = (-308.1950988769531, -116.05439758300781)
        curve_line_003.location = (-140.12799072265625, -350.9503173828125)
        combine_xyz_003.location = (-301.55718994140625, -366.12237548828125)
        join_geometry_002.location = (51.19605255126953, -109.091064453125)
        curve_to_mesh.location = (309.74407958984375, 229.33209228515625)
        math_006.location = (-303.5211181640625, 224.70147705078125)
        math_007.location = (-541.5947875976562, 214.69952392578125)
        spline_parameter.location = (-217.54840087890625, 36.85296630859375)
        mix.location = (1585.7728271484375, 128.04603576660156)
        curve_to_mesh_001.location = (431.7877197265625, 162.30099487304688)
        store_named_attribute_003.location = (-42.96711730957031, 234.11785888671875)
        combine_xyz_007.location = (-403.4272155761719, -705.4803466796875)
        spline_parameter_002.location = (-236.91021728515625, 125.4948501586914)
        combine_xyz_005.location = (-404.2497253417969, -571.596435546875)
        combine_xyz_006.location = (-404.047607421875, -135.6737060546875)
        combine_xyz_004.location = (-404.047607421875, -268.25439453125)
        spline_parameter_003.location = (-74.71415710449219, -279.8134765625)
        curve_line_002.location = (-229.5640869140625, -538.7314453125)
        curve_line_001.location = (-235.24069213867188, -145.12335205078125)
        join_geometry.location = (-36.20172119140625, -148.03094482421875)
        math_002.location = (-587.103271484375, -575.5347290039062)
        math_001.location = (-624.3336791992188, -291.3660888671875)
        math.location = (-750.80859375, 64.54544067382812)
        join_geometry_006.location = (924.033935546875, 100.84170532226562)
        set_material_002.location = (651.6433715820312, 153.2003936767578)
        store_named_attribute_002.location = (136.57278442382812, 5.32244873046875)
        reroute_002.location = (-797.9868774414062, 61.25142288208008)
        reroute_005.location = (-2.252777099609375, -789.1392822265625)
        reroute_011.location = (-935.769775390625, -136.37640380859375)
        extrude_mesh.location = (1364.0306396484375, 203.4251708984375)
        realize_instances_001.location = (1143.9224853515625, 105.78274536132812)
        realize_instances.location = (2969.124755859375, 1040.216552734375)
        realize_instances_002.location = (4646.66650390625, 611.5092163085938)
        spline_parameter_001.location = (107.24891662597656, -311.5553283691406)
        store_named_attribute_001.location = (293.6241455078125, 42.526023864746094)
        reroute_007.location = (1907.2843017578125, -1561.43994140625)
        join_geometry_007.location = (2492.681640625, -1951.9986572265625)
        combine_xyz_013.location = (590.59521484375, -1737.0609130859375)
        separate_xyz.location = (370.8480224609375, -1740.5111083984375)
        compare.location = (810.430419921875, -1740.8931884765625)
        instance_on_points_001.location = (1993.1302490234375, -1598.4063720703125)
        reroute_006.location = (1166.652587890625, -1612.9278564453125)
        separate_xyz_002.location = (347.3112487792969, -2131.917236328125)
        instance_on_points_003.location = (2003.7332763671875, -1977.279296875)
        compare_003.location = (647.3449096679688, -2015.44921875)
        compare_002.location = (648.9578247070312, -2186.519775390625)
        math_010.location = (900.1796875, -2062.3408203125)
        reroute_001.location = (538.7562255859375, -2074.724853515625)
        compare_004.location = (647.3449096679688, -2346.278564453125)
        compare_005.location = (648.9578247070312, -2517.349365234375)
        math_012.location = (900.1796875, -2393.170166015625)
        separate_xyz_003.location = (347.3112487792969, -2462.746826171875)
        math_013.location = (371.2362060546875, -2611.398681640625)
        compare_006.location = (656.95458984375, -2824.626220703125)
        math_014.location = (909.7893676757812, -2871.517822265625)
        instance_on_points_005.location = (2013.3428955078125, -2786.456298828125)
        math_015.location = (380.8459167480469, -3089.746337890625)
        compare_007.location = (658.5675659179688, -2995.697021484375)
        separate_xyz_004.location = (386.667236328125, -2916.843017578125)
        position.location = (32.13954544067383, -2155.297607421875)
        math_008.location = (-124.18570709228516, -1908.677734375)
        instance_on_points_004.location = (2003.7332763671875, -2308.108642578125)
        math_009.location = (38.334712982177734, -1913.2197265625)
        mesh_to_points.location = (1310.06494140625, -1148.3544921875)
        set_material_003.location = (2437.14404296875, -1224.3472900390625)
        arc.location = (826.6900024414062, -1390.77294921875)
        fill_curve.location = (992.3280639648438, -1409.094482421875)
        group_input.location = (-1357.0404052734375, -738.265869140625)
        join_geometry_005.location = (1496.0081787109375, 2127.43505859375)
        instance_on_points.location = (942.407470703125, 2386.101806640625)
        store_named_attribute_005.location = (349.7482604980469, 1978.0751953125)
        align_euler_to_vector.location = (132.82171630859375, 2651.375732421875)
        group_output.location = (4866.67041015625, 98.61441802978516)

        # Set dimensions
        frame_002.width, frame_002.height = 2268.0, 1508.6666259765625
        frame.width, frame.height = 1049.3333740234375, 894.6666870117188
        frame_001.width, frame_001.height = 2312.666748046875, 1110.6666259765625
        frame_003.width, frame_003.height = 2814.66650390625, 2146.000244140625
        set_shade_smooth.width, set_shade_smooth.height = 140.0, 100.0
        combine_xyz_009.width, combine_xyz_009.height = 140.0, 100.0
        join_geometry_004.width, join_geometry_004.height = 140.0, 100.0
        set_material_004.width, set_material_004.height = 140.0, 100.0
        set_material_005.width, set_material_005.height = 140.0, 100.0
        reroute.width, reroute.height = 16.0, 100.0
        reroute_004.width, reroute_004.height = 16.0, 100.0
        set_shade_smooth_002.width, set_shade_smooth_002.height = 140.0, 100.0
        join_geometry_001.width, join_geometry_001.height = 140.0, 100.0
        combine_xyz_010.width, combine_xyz_010.height = 140.0, 100.0
        combine_xyz_011.width, combine_xyz_011.height = 140.0, 100.0
        combine_xyz_012.width, combine_xyz_012.height = 140.0, 100.0
        curve_line_006.width, curve_line_006.height = 140.0, 100.0
        curve_line_005.width, curve_line_005.height = 140.0, 100.0
        math_005.width, math_005.height = 140.0, 100.0
        join_geometry_003.width, join_geometry_003.height = 140.0, 100.0
        math_004.width, math_004.height = 140.0, 100.0
        math_003.width, math_003.height = 140.0, 100.0
        math_011.width, math_011.height = 140.0, 100.0
        combine_xyz_008.width, combine_xyz_008.height = 140.0, 100.0
        curve_line_004.width, curve_line_004.height = 140.0, 100.0
        store_named_attribute_004.width, store_named_attribute_004.height = 262.4270935058594, 100.0
        curve_to_mesh_002.width, curve_to_mesh_002.height = 140.0, 100.0
        mix_002.width, mix_002.height = 140.0, 100.0
        curve_tangent.width, curve_tangent.height = 140.0, 100.0
        endpoint_selection.width, endpoint_selection.height = 140.0, 100.0
        reroute_003.width, reroute_003.height = 16.0, 100.0
        store_named_attribute.width, store_named_attribute.height = 168.5052490234375, 100.0
        combine_xyz_002.width, combine_xyz_002.height = 140.0, 100.0
        curve_line.width, curve_line.height = 140.0, 100.0
        combine_xyz.width, combine_xyz.height = 140.0, 100.0
        combine_xyz_001.width, combine_xyz_001.height = 140.0, 100.0
        curve_line_003.width, curve_line_003.height = 140.0, 100.0
        combine_xyz_003.width, combine_xyz_003.height = 140.0, 100.0
        join_geometry_002.width, join_geometry_002.height = 140.0, 100.0
        curve_to_mesh.width, curve_to_mesh.height = 140.0, 100.0
        math_006.width, math_006.height = 140.0, 100.0
        math_007.width, math_007.height = 140.0, 100.0
        spline_parameter.width, spline_parameter.height = 140.0, 100.0
        mix.width, mix.height = 140.0, 100.0
        curve_to_mesh_001.width, curve_to_mesh_001.height = 140.0, 100.0
        store_named_attribute_003.width, store_named_attribute_003.height = 168.5052490234375, 100.0
        combine_xyz_007.width, combine_xyz_007.height = 140.0, 100.0
        spline_parameter_002.width, spline_parameter_002.height = 140.0, 100.0
        combine_xyz_005.width, combine_xyz_005.height = 140.0, 100.0
        combine_xyz_006.width, combine_xyz_006.height = 140.0, 100.0
        combine_xyz_004.width, combine_xyz_004.height = 140.0, 100.0
        spline_parameter_003.width, spline_parameter_003.height = 140.0, 100.0
        curve_line_002.width, curve_line_002.height = 140.0, 100.0
        curve_line_001.width, curve_line_001.height = 140.0, 100.0
        join_geometry.width, join_geometry.height = 140.0, 100.0
        math_002.width, math_002.height = 140.0, 100.0
        math_001.width, math_001.height = 140.0, 100.0
        math.width, math.height = 140.0, 100.0
        join_geometry_006.width, join_geometry_006.height = 140.0, 100.0
        set_material_002.width, set_material_002.height = 140.0, 100.0
        store_named_attribute_002.width, store_named_attribute_002.height = 176.4276885986328, 100.0
        reroute_002.width, reroute_002.height = 16.0, 100.0
        reroute_005.width, reroute_005.height = 16.0, 100.0
        reroute_011.width, reroute_011.height = 16.0, 100.0
        extrude_mesh.width, extrude_mesh.height = 140.0, 100.0
        realize_instances_001.width, realize_instances_001.height = 140.0, 100.0
        realize_instances.width, realize_instances.height = 140.0, 100.0
        realize_instances_002.width, realize_instances_002.height = 140.0, 100.0
        spline_parameter_001.width, spline_parameter_001.height = 140.0, 100.0
        store_named_attribute_001.width, store_named_attribute_001.height = 140.0, 100.0
        reroute_007.width, reroute_007.height = 16.0, 100.0
        join_geometry_007.width, join_geometry_007.height = 140.0, 100.0
        combine_xyz_013.width, combine_xyz_013.height = 140.0, 100.0
        separate_xyz.width, separate_xyz.height = 140.0, 100.0
        compare.width, compare.height = 140.0, 100.0
        instance_on_points_001.width, instance_on_points_001.height = 160.1581268310547, 100.0
        reroute_006.width, reroute_006.height = 16.0, 100.0
        separate_xyz_002.width, separate_xyz_002.height = 140.0, 100.0
        instance_on_points_003.width, instance_on_points_003.height = 160.1581268310547, 100.0
        compare_003.width, compare_003.height = 140.0, 100.0
        compare_002.width, compare_002.height = 140.0, 100.0
        math_010.width, math_010.height = 140.0, 100.0
        reroute_001.width, reroute_001.height = 16.0, 100.0
        compare_004.width, compare_004.height = 140.0, 100.0
        compare_005.width, compare_005.height = 140.0, 100.0
        math_012.width, math_012.height = 140.0, 100.0
        separate_xyz_003.width, separate_xyz_003.height = 140.0, 100.0
        math_013.width, math_013.height = 140.0, 100.0
        compare_006.width, compare_006.height = 140.0, 100.0
        math_014.width, math_014.height = 140.0, 100.0
        instance_on_points_005.width, instance_on_points_005.height = 160.1581268310547, 100.0
        math_015.width, math_015.height = 140.0, 100.0
        compare_007.width, compare_007.height = 140.0, 100.0
        separate_xyz_004.width, separate_xyz_004.height = 140.0, 100.0
        position.width, position.height = 140.0, 100.0
        math_008.width, math_008.height = 140.0, 100.0
        instance_on_points_004.width, instance_on_points_004.height = 160.1581268310547, 100.0
        math_009.width, math_009.height = 140.0, 100.0
        mesh_to_points.width, mesh_to_points.height = 140.0, 100.0
        set_material_003.width, set_material_003.height = 140.0, 100.0
        arc.width, arc.height = 140.0, 100.0
        fill_curve.width, fill_curve.height = 140.0, 100.0
        group_input.width, group_input.height = 140.0, 100.0
        join_geometry_005.width, join_geometry_005.height = 140.0, 100.0
        instance_on_points.width, instance_on_points.height = 160.1581268310547, 100.0
        store_named_attribute_005.width, store_named_attribute_005.height = 262.4270935058594, 100.0
        align_euler_to_vector.width, align_euler_to_vector.height = 140.0, 100.0
        group_output.width, group_output.height = 140.0, 100.0

        # initialize main_road_geometry_nodes links
        # curve_line_003.Curve -> join_geometry_002.Geometry
        main_road_geometry_nodes.links.new(curve_line_003.outputs[0], join_geometry_002.inputs[0])
        # curve_line.Curve -> join_geometry_002.Geometry
        main_road_geometry_nodes.links.new(curve_line.outputs[0], join_geometry_002.inputs[0])
        # store_named_attribute_003.Geometry -> curve_to_mesh_001.Curve
        main_road_geometry_nodes.links.new(store_named_attribute_003.outputs[0], curve_to_mesh_001.inputs[0])
        # combine_xyz_003.Vector -> curve_line_003.Start
        main_road_geometry_nodes.links.new(combine_xyz_003.outputs[0], curve_line_003.inputs[0])
        # combine_xyz_001.Vector -> curve_line.Start
        main_road_geometry_nodes.links.new(combine_xyz_001.outputs[0], curve_line.inputs[0])
        # reroute_011.Output -> math_001.Value
        main_road_geometry_nodes.links.new(reroute_011.outputs[0], math_001.inputs[1])
        # curve_line_001.Curve -> join_geometry.Geometry
        main_road_geometry_nodes.links.new(curve_line_001.outputs[0], join_geometry.inputs[0])
        # spline_parameter_003.Length -> store_named_attribute_002.Value
        main_road_geometry_nodes.links.new(spline_parameter_003.outputs[1], store_named_attribute_002.inputs[4])
        # reroute.Output -> math.Value
        main_road_geometry_nodes.links.new(reroute.outputs[0], math.inputs[0])
        # spline_parameter_002.Length -> store_named_attribute_003.Value
        main_road_geometry_nodes.links.new(spline_parameter_002.outputs[1], store_named_attribute_003.inputs[4])
        # reroute.Output -> combine_xyz.X
        main_road_geometry_nodes.links.new(reroute.outputs[0], combine_xyz.inputs[0])
        # math.Value -> combine_xyz_002.X
        main_road_geometry_nodes.links.new(math.outputs[0], combine_xyz_002.inputs[0])
        # set_shade_smooth.Geometry -> join_geometry_001.Geometry
        main_road_geometry_nodes.links.new(set_shade_smooth.outputs[0], join_geometry_001.inputs[0])
        # combine_xyz_002.Vector -> curve_line_003.End
        main_road_geometry_nodes.links.new(combine_xyz_002.outputs[0], curve_line_003.inputs[1])
        # realize_instances_001.Geometry -> extrude_mesh.Mesh
        main_road_geometry_nodes.links.new(realize_instances_001.outputs[0], extrude_mesh.inputs[0])
        # store_named_attribute_002.Geometry -> curve_to_mesh_001.Profile Curve
        main_road_geometry_nodes.links.new(store_named_attribute_002.outputs[0], curve_to_mesh_001.inputs[1])
        # spline_parameter.Length -> store_named_attribute.Value
        main_road_geometry_nodes.links.new(spline_parameter.outputs[1], store_named_attribute.inputs[4])
        # combine_xyz.Vector -> curve_line.End
        main_road_geometry_nodes.links.new(combine_xyz.outputs[0], curve_line.inputs[1])
        # store_named_attribute_001.Geometry -> curve_to_mesh.Profile Curve
        main_road_geometry_nodes.links.new(store_named_attribute_001.outputs[0], curve_to_mesh.inputs[1])
        # reroute.Output -> math_001.Value
        main_road_geometry_nodes.links.new(reroute.outputs[0], math_001.inputs[0])
        # spline_parameter_001.Length -> store_named_attribute_001.Value
        main_road_geometry_nodes.links.new(spline_parameter_001.outputs[1], store_named_attribute_001.inputs[4])
        # set_shade_smooth_002.Geometry -> join_geometry_001.Geometry
        main_road_geometry_nodes.links.new(set_shade_smooth_002.outputs[0], join_geometry_001.inputs[0])
        # math_001.Value -> math_002.Value
        main_road_geometry_nodes.links.new(math_001.outputs[0], math_002.inputs[0])
        # group_input.width_roadlane -> reroute.Input
        main_road_geometry_nodes.links.new(group_input.outputs[1], reroute.inputs[0])
        # reroute_002.Output -> store_named_attribute.Geometry
        main_road_geometry_nodes.links.new(reroute_002.outputs[0], store_named_attribute.inputs[0])
        # combine_xyz_004.Vector -> curve_line_001.Start
        main_road_geometry_nodes.links.new(combine_xyz_004.outputs[0], curve_line_001.inputs[0])
        # combine_xyz_006.Vector -> curve_line_001.End
        main_road_geometry_nodes.links.new(combine_xyz_006.outputs[0], curve_line_001.inputs[1])
        # combine_xyz_005.Vector -> curve_line_002.End
        main_road_geometry_nodes.links.new(combine_xyz_005.outputs[0], curve_line_002.inputs[1])
        # combine_xyz_007.Vector -> curve_line_002.Start
        main_road_geometry_nodes.links.new(combine_xyz_007.outputs[0], curve_line_002.inputs[0])
        # curve_line_002.Curve -> join_geometry.Geometry
        main_road_geometry_nodes.links.new(curve_line_002.outputs[0], join_geometry.inputs[0])
        # math_002.Value -> combine_xyz_007.X
        main_road_geometry_nodes.links.new(math_002.outputs[0], combine_xyz_007.inputs[0])
        # math.Value -> combine_xyz_005.X
        main_road_geometry_nodes.links.new(math.outputs[0], combine_xyz_005.inputs[0])
        # math_001.Value -> combine_xyz_006.X
        main_road_geometry_nodes.links.new(math_001.outputs[0], combine_xyz_006.inputs[0])
        # reroute.Output -> combine_xyz_004.X
        main_road_geometry_nodes.links.new(reroute.outputs[0], combine_xyz_004.inputs[0])
        # join_geometry.Geometry -> store_named_attribute_002.Geometry
        main_road_geometry_nodes.links.new(join_geometry.outputs[0], store_named_attribute_002.inputs[0])
        # join_geometry_002.Geometry -> store_named_attribute_001.Geometry
        main_road_geometry_nodes.links.new(join_geometry_002.outputs[0], store_named_attribute_001.inputs[0])
        # store_named_attribute.Geometry -> curve_to_mesh.Curve
        main_road_geometry_nodes.links.new(store_named_attribute.outputs[0], curve_to_mesh.inputs[0])
        # reroute.Output -> group_output.widthRoad
        main_road_geometry_nodes.links.new(reroute.outputs[0], group_output.inputs[1])
        # realize_instances_002.Geometry -> group_output.Geometry
        main_road_geometry_nodes.links.new(realize_instances_002.outputs[0], group_output.inputs[0])
        # mix.Result -> group_output.wet
        main_road_geometry_nodes.links.new(mix.outputs[0], group_output.inputs[3])
        # group_input.wet -> mix.Factor
        main_road_geometry_nodes.links.new(group_input.outputs[3], mix.inputs[0])
        # reroute_002.Output -> store_named_attribute_003.Geometry
        main_road_geometry_nodes.links.new(reroute_002.outputs[0], store_named_attribute_003.inputs[0])
        # endpoint_selection.Selection -> instance_on_points.Selection
        main_road_geometry_nodes.links.new(endpoint_selection.outputs[0], instance_on_points.inputs[1])
        # store_named_attribute_005.Geometry -> curve_to_mesh_002.Curve
        main_road_geometry_nodes.links.new(store_named_attribute_005.outputs[0], curve_to_mesh_002.inputs[0])
        # math_003.Value -> combine_xyz_008.X
        main_road_geometry_nodes.links.new(math_003.outputs[0], combine_xyz_008.inputs[0])
        # align_euler_to_vector.Rotation -> instance_on_points.Rotation
        main_road_geometry_nodes.links.new(align_euler_to_vector.outputs[0], instance_on_points.inputs[5])
        # reroute_003.Output -> instance_on_points.Points
        main_road_geometry_nodes.links.new(reroute_003.outputs[0], instance_on_points.inputs[0])
        # curve_tangent.Tangent -> align_euler_to_vector.Vector
        main_road_geometry_nodes.links.new(curve_tangent.outputs[0], align_euler_to_vector.inputs[2])
        # curve_line_006.Curve -> join_geometry_003.Geometry
        main_road_geometry_nodes.links.new(curve_line_006.outputs[0], join_geometry_003.inputs[0])
        # curve_line_005.Curve -> join_geometry_003.Geometry
        main_road_geometry_nodes.links.new(curve_line_005.outputs[0], join_geometry_003.inputs[0])
        # combine_xyz_012.Vector -> curve_line_006.Start
        main_road_geometry_nodes.links.new(combine_xyz_012.outputs[0], curve_line_006.inputs[0])
        # combine_xyz_011.Vector -> curve_line_005.Start
        main_road_geometry_nodes.links.new(combine_xyz_011.outputs[0], curve_line_005.inputs[0])
        # combine_xyz_009.Vector -> curve_line_006.End
        main_road_geometry_nodes.links.new(combine_xyz_009.outputs[0], curve_line_006.inputs[1])
        # combine_xyz_010.Vector -> curve_line_005.End
        main_road_geometry_nodes.links.new(combine_xyz_010.outputs[0], curve_line_005.inputs[1])
        # store_named_attribute_004.Geometry -> curve_to_mesh_002.Profile Curve
        main_road_geometry_nodes.links.new(store_named_attribute_004.outputs[0], curve_to_mesh_002.inputs[1])
        # math_005.Value -> combine_xyz_010.X
        main_road_geometry_nodes.links.new(math_005.outputs[0], combine_xyz_010.inputs[0])
        # math_006.Value -> combine_xyz_009.X
        main_road_geometry_nodes.links.new(math_006.outputs[0], combine_xyz_009.inputs[0])
        # reroute.Output -> math_005.Value
        main_road_geometry_nodes.links.new(reroute.outputs[0], math_005.inputs[0])
        # math.Value -> math_006.Value
        main_road_geometry_nodes.links.new(math.outputs[0], math_006.inputs[0])
        # reroute_004.Output -> math_005.Value
        main_road_geometry_nodes.links.new(reroute_004.outputs[0], math_005.inputs[1])
        # reroute_011.Output -> reroute_004.Input
        main_road_geometry_nodes.links.new(reroute_011.outputs[0], reroute_004.inputs[0])
        # math_007.Value -> math_006.Value
        main_road_geometry_nodes.links.new(math_007.outputs[0], math_006.inputs[1])
        # reroute_004.Output -> math_007.Value
        main_road_geometry_nodes.links.new(reroute_004.outputs[0], math_007.inputs[0])
        # set_material_005.Geometry -> join_geometry_004.Geometry
        main_road_geometry_nodes.links.new(set_material_005.outputs[0], join_geometry_004.inputs[0])
        # set_material_004.Geometry -> join_geometry_004.Geometry
        main_road_geometry_nodes.links.new(set_material_004.outputs[0], join_geometry_004.inputs[0])
        # curve_to_mesh_002.Mesh -> instance_on_points.Instance
        main_road_geometry_nodes.links.new(curve_to_mesh_002.outputs[0], instance_on_points.inputs[2])
        # combine_xyz_008.Vector -> curve_line_004.Start
        main_road_geometry_nodes.links.new(combine_xyz_008.outputs[0], curve_line_004.inputs[0])
        # spline_parameter.Length -> store_named_attribute_004.Value
        main_road_geometry_nodes.links.new(spline_parameter.outputs[1], store_named_attribute_004.inputs[4])
        # join_geometry_004.Geometry -> realize_instances.Geometry
        main_road_geometry_nodes.links.new(join_geometry_004.outputs[0], realize_instances.inputs[0])
        # reroute_002.Output -> reroute_003.Input
        main_road_geometry_nodes.links.new(reroute_002.outputs[0], reroute_003.inputs[0])
        # math_011.Value -> math_003.Value
        main_road_geometry_nodes.links.new(math_011.outputs[0], math_003.inputs[0])
        # group_input.curve -> reroute_002.Input
        main_road_geometry_nodes.links.new(group_input.outputs[0], reroute_002.inputs[0])
        # mix_002.Result -> endpoint_selection.End Size
        main_road_geometry_nodes.links.new(mix_002.outputs[0], endpoint_selection.inputs[1])
        # group_input.endpoint intersection -> mix_002.Factor
        main_road_geometry_nodes.links.new(group_input.outputs[9], mix_002.inputs[0])
        # join_geometry_003.Geometry -> store_named_attribute_004.Geometry
        main_road_geometry_nodes.links.new(join_geometry_003.outputs[0], store_named_attribute_004.inputs[0])
        # curve_to_mesh.Mesh -> set_material_004.Geometry
        main_road_geometry_nodes.links.new(curve_to_mesh.outputs[0], set_material_004.inputs[0])
        # realize_instances.Geometry -> set_shade_smooth_002.Geometry
        main_road_geometry_nodes.links.new(realize_instances.outputs[0], set_shade_smooth_002.inputs[0])
        # math_004.Value -> math_011.Value
        main_road_geometry_nodes.links.new(math_004.outputs[0], math_011.inputs[0])
        # curve_line_004.Curve -> store_named_attribute_005.Geometry
        main_road_geometry_nodes.links.new(curve_line_004.outputs[0], store_named_attribute_005.inputs[0])
        # spline_parameter.Length -> store_named_attribute_005.Value
        main_road_geometry_nodes.links.new(spline_parameter.outputs[1], store_named_attribute_005.inputs[4])
        # reroute.Output -> math_004.Value
        main_road_geometry_nodes.links.new(reroute.outputs[0], math_004.inputs[0])
        # reroute_011.Output -> math_004.Value
        main_road_geometry_nodes.links.new(reroute_011.outputs[0], math_004.inputs[1])
        # reroute_011.Output -> group_output.widthSidewalk
        main_road_geometry_nodes.links.new(reroute_011.outputs[0], group_output.inputs[2])
        # set_material_002.Geometry -> join_geometry_006.Geometry
        main_road_geometry_nodes.links.new(set_material_002.outputs[0], join_geometry_006.inputs[0])
        # extrude_mesh.Mesh -> set_shade_smooth.Geometry
        main_road_geometry_nodes.links.new(extrude_mesh.outputs[0], set_shade_smooth.inputs[0])
        # curve_to_mesh_001.Mesh -> set_material_002.Geometry
        main_road_geometry_nodes.links.new(curve_to_mesh_001.outputs[0], set_material_002.inputs[0])
        # set_material_003.Geometry -> join_geometry_006.Geometry
        main_road_geometry_nodes.links.new(set_material_003.outputs[0], join_geometry_006.inputs[0])
        # reroute_006.Output -> instance_on_points_001.Instance
        main_road_geometry_nodes.links.new(reroute_006.outputs[0], instance_on_points_001.inputs[2])
        # instance_on_points.Instances -> join_geometry_005.Geometry
        main_road_geometry_nodes.links.new(instance_on_points.outputs[0], join_geometry_005.inputs[0])
        # join_geometry_005.Geometry -> set_material_005.Geometry
        main_road_geometry_nodes.links.new(join_geometry_005.outputs[0], set_material_005.inputs[0])
        # reroute_005.Output -> mesh_to_points.Mesh
        main_road_geometry_nodes.links.new(reroute_005.outputs[0], mesh_to_points.inputs[0])
        # reroute_007.Output -> instance_on_points_001.Points
        main_road_geometry_nodes.links.new(reroute_007.outputs[0], instance_on_points_001.inputs[0])
        # instance_on_points.Instances -> reroute_005.Input
        main_road_geometry_nodes.links.new(instance_on_points.outputs[0], reroute_005.inputs[0])
        # position.Position -> separate_xyz.Vector
        main_road_geometry_nodes.links.new(position.outputs[0], separate_xyz.inputs[0])
        # combine_xyz_013.Vector -> compare.B
        main_road_geometry_nodes.links.new(combine_xyz_013.outputs[0], compare.inputs[1])
        # compare.Result -> instance_on_points_001.Selection
        main_road_geometry_nodes.links.new(compare.outputs[0], instance_on_points_001.inputs[1])
        # separate_xyz.Y -> combine_xyz_013.Y
        main_road_geometry_nodes.links.new(separate_xyz.outputs[1], combine_xyz_013.inputs[1])
        # separate_xyz.X -> combine_xyz_013.X
        main_road_geometry_nodes.links.new(separate_xyz.outputs[0], combine_xyz_013.inputs[0])
        # mesh_to_points.Points -> reroute_007.Input
        main_road_geometry_nodes.links.new(mesh_to_points.outputs[0], reroute_007.inputs[0])
        # group_input.width_sidewalk -> reroute_011.Input
        main_road_geometry_nodes.links.new(group_input.outputs[2], reroute_011.inputs[0])
        # group_input.width_roadlane -> math_008.Value
        main_road_geometry_nodes.links.new(group_input.outputs[1], math_008.inputs[0])
        # group_input.width_sidewalk -> math_008.Value
        main_road_geometry_nodes.links.new(group_input.outputs[2], math_008.inputs[1])
        # math_008.Value -> math_009.Value
        main_road_geometry_nodes.links.new(math_008.outputs[0], math_009.inputs[0])
        # reroute_006.Output -> instance_on_points_003.Instance
        main_road_geometry_nodes.links.new(reroute_006.outputs[0], instance_on_points_003.inputs[2])
        # reroute_007.Output -> instance_on_points_003.Points
        main_road_geometry_nodes.links.new(reroute_007.outputs[0], instance_on_points_003.inputs[0])
        # position.Position -> separate_xyz_002.Vector
        main_road_geometry_nodes.links.new(position.outputs[0], separate_xyz_002.inputs[0])
        # separate_xyz_002.Y -> compare_002.B
        main_road_geometry_nodes.links.new(separate_xyz_002.outputs[1], compare_002.inputs[1])
        # separate_xyz_002.X -> compare_003.B
        main_road_geometry_nodes.links.new(separate_xyz_002.outputs[0], compare_003.inputs[1])
        # instance_on_points_001.Instances -> join_geometry_007.Geometry
        main_road_geometry_nodes.links.new(instance_on_points_001.outputs[0], join_geometry_007.inputs[0])
        # instance_on_points_003.Instances -> join_geometry_007.Geometry
        main_road_geometry_nodes.links.new(instance_on_points_003.outputs[0], join_geometry_007.inputs[0])
        # compare_003.Result -> math_010.Value
        main_road_geometry_nodes.links.new(compare_003.outputs[0], math_010.inputs[0])
        # compare_002.Result -> math_010.Value
        main_road_geometry_nodes.links.new(compare_002.outputs[0], math_010.inputs[1])
        # math_010.Value -> instance_on_points_003.Selection
        main_road_geometry_nodes.links.new(math_010.outputs[0], instance_on_points_003.inputs[1])
        # reroute_001.Output -> compare_003.A
        main_road_geometry_nodes.links.new(reroute_001.outputs[0], compare_003.inputs[0])
        # reroute_006.Output -> instance_on_points_004.Instance
        main_road_geometry_nodes.links.new(reroute_006.outputs[0], instance_on_points_004.inputs[2])
        # reroute_007.Output -> instance_on_points_004.Points
        main_road_geometry_nodes.links.new(reroute_007.outputs[0], instance_on_points_004.inputs[0])
        # position.Position -> separate_xyz_003.Vector
        main_road_geometry_nodes.links.new(position.outputs[0], separate_xyz_003.inputs[0])
        # compare_004.Result -> math_012.Value
        main_road_geometry_nodes.links.new(compare_004.outputs[0], math_012.inputs[0])
        # compare_005.Result -> math_012.Value
        main_road_geometry_nodes.links.new(compare_005.outputs[0], math_012.inputs[1])
        # math_012.Value -> instance_on_points_004.Selection
        main_road_geometry_nodes.links.new(math_012.outputs[0], instance_on_points_004.inputs[1])
        # math_008.Value -> reroute_001.Input
        main_road_geometry_nodes.links.new(math_008.outputs[0], reroute_001.inputs[0])
        # instance_on_points_004.Instances -> join_geometry_007.Geometry
        main_road_geometry_nodes.links.new(instance_on_points_004.outputs[0], join_geometry_007.inputs[0])
        # separate_xyz_003.X -> compare_004.A
        main_road_geometry_nodes.links.new(separate_xyz_003.outputs[0], compare_004.inputs[0])
        # separate_xyz_003.Y -> compare_005.A
        main_road_geometry_nodes.links.new(separate_xyz_003.outputs[1], compare_005.inputs[0])
        # math_013.Value -> compare_005.B
        main_road_geometry_nodes.links.new(math_013.outputs[0], compare_005.inputs[1])
        # math_009.Value -> math_013.Value
        main_road_geometry_nodes.links.new(math_009.outputs[0], math_013.inputs[0])
        # reroute_006.Output -> instance_on_points_005.Instance
        main_road_geometry_nodes.links.new(reroute_006.outputs[0], instance_on_points_005.inputs[2])
        # reroute_007.Output -> instance_on_points_005.Points
        main_road_geometry_nodes.links.new(reroute_007.outputs[0], instance_on_points_005.inputs[0])
        # position.Position -> separate_xyz_004.Vector
        main_road_geometry_nodes.links.new(position.outputs[0], separate_xyz_004.inputs[0])
        # compare_006.Result -> math_014.Value
        main_road_geometry_nodes.links.new(compare_006.outputs[0], math_014.inputs[0])
        # compare_007.Result -> math_014.Value
        main_road_geometry_nodes.links.new(compare_007.outputs[0], math_014.inputs[1])
        # math_014.Value -> instance_on_points_005.Selection
        main_road_geometry_nodes.links.new(math_014.outputs[0], instance_on_points_005.inputs[1])
        # math_009.Value -> math_015.Value
        main_road_geometry_nodes.links.new(math_009.outputs[0], math_015.inputs[0])
        # instance_on_points_005.Instances -> join_geometry_007.Geometry
        main_road_geometry_nodes.links.new(instance_on_points_005.outputs[0], join_geometry_007.inputs[0])
        # separate_xyz_004.Y -> compare_007.B
        main_road_geometry_nodes.links.new(separate_xyz_004.outputs[1], compare_007.inputs[1])
        # separate_xyz_004.X -> compare_006.B
        main_road_geometry_nodes.links.new(separate_xyz_004.outputs[0], compare_006.inputs[1])
        # math_009.Value -> compare_006.A
        main_road_geometry_nodes.links.new(math_009.outputs[0], compare_006.inputs[0])
        # math_009.Value -> compare_007.A
        main_road_geometry_nodes.links.new(math_009.outputs[0], compare_007.inputs[0])
        # join_geometry_006.Geometry -> realize_instances_001.Geometry
        main_road_geometry_nodes.links.new(join_geometry_006.outputs[0], realize_instances_001.inputs[0])
        # group_input.color_middleline -> group_output.color_middleline
        main_road_geometry_nodes.links.new(group_input.outputs[5], group_output.inputs[5])
        # group_input.color_sideline -> group_output.color_sideline
        main_road_geometry_nodes.links.new(group_input.outputs[4], group_output.inputs[4])
        # group_input.color_pedestrial -> group_output.color_pedestrial
        main_road_geometry_nodes.links.new(group_input.outputs[6], group_output.inputs[6])
        # group_input.color_sidewalk -> group_output.color_sidewalk
        main_road_geometry_nodes.links.new(group_input.outputs[7], group_output.inputs[7])
        # group_input.brick_scale -> group_output.brick_scale
        main_road_geometry_nodes.links.new(group_input.outputs[8], group_output.inputs[8])
        # join_geometry_001.Geometry -> realize_instances_002.Geometry
        main_road_geometry_nodes.links.new(join_geometry_001.outputs[0], realize_instances_002.inputs[0])
        # join_geometry_007.Geometry -> set_material_003.Geometry
        main_road_geometry_nodes.links.new(join_geometry_007.outputs[0], set_material_003.inputs[0])
        # arc.Curve -> fill_curve.Curve
        main_road_geometry_nodes.links.new(arc.outputs[0], fill_curve.inputs[0])
        # fill_curve.Mesh -> reroute_006.Input
        main_road_geometry_nodes.links.new(fill_curve.outputs[0], reroute_006.inputs[0])
        # group_input.width_sidewalk -> arc.Radius
        main_road_geometry_nodes.links.new(group_input.outputs[2], arc.inputs[4])
        # align_euler_to_vector.Rotation -> group_output.intersection rotation
        main_road_geometry_nodes.links.new(align_euler_to_vector.outputs[0], group_output.inputs[9])
        return main_road_geometry_nodes

    main_road_geometry_nodes = main_road_geometry_nodes_node_group()

    # initialize road_geometry_nodes node group
    def road_geometry_nodes_node_group():
        road_geometry_nodes = bpy.data.node_groups.new(type='GeometryNodeTree', name="myRoadGeometryNodes")

        road_geometry_nodes.is_modifier = True

        # initialize road_geometry_nodes nodes
        # road_geometry_nodes interface
        # Socket Geometry
        geometry_socket_1 = road_geometry_nodes.interface.new_socket(name="Geometry", in_out='OUTPUT',
                                                                     socket_type='NodeSocketGeometry')
        geometry_socket_1.attribute_domain = 'POINT'

        # Socket widthRoad
        widthroad_socket_1 = road_geometry_nodes.interface.new_socket(name="widthRoad", in_out='OUTPUT',
                                                                      socket_type='NodeSocketFloat')
        widthroad_socket_1.subtype = 'NONE'
        widthroad_socket_1.default_value = 0.0
        widthroad_socket_1.min_value = -3.4028234663852886e+38
        widthroad_socket_1.max_value = 3.4028234663852886e+38
        widthroad_socket_1.attribute_domain = 'POINT'

        # Socket widthSidewalk
        widthsidewalk_socket_1 = road_geometry_nodes.interface.new_socket(name="widthSidewalk", in_out='OUTPUT',
                                                                          socket_type='NodeSocketFloat')
        widthsidewalk_socket_1.subtype = 'NONE'
        widthsidewalk_socket_1.default_value = 0.0
        widthsidewalk_socket_1.min_value = -3.4028234663852886e+38
        widthsidewalk_socket_1.max_value = 3.4028234663852886e+38
        widthsidewalk_socket_1.attribute_domain = 'POINT'

        # Socket wet
        wet_socket_2 = road_geometry_nodes.interface.new_socket(name="wet", in_out='OUTPUT',
                                                                socket_type='NodeSocketFloat')
        wet_socket_2.subtype = 'NONE'
        wet_socket_2.default_value = 0.0
        wet_socket_2.min_value = -3.4028234663852886e+38
        wet_socket_2.max_value = 3.4028234663852886e+38
        wet_socket_2.attribute_domain = 'POINT'

        # Socket color_sideline
        color_sideline_socket_2 = road_geometry_nodes.interface.new_socket(name="color_sideline", in_out='OUTPUT',
                                                                           socket_type='NodeSocketColor')
        color_sideline_socket_2.attribute_domain = 'POINT'

        # Socket color_middleline
        color_middleline_socket_2 = road_geometry_nodes.interface.new_socket(name="color_middleline", in_out='OUTPUT',
                                                                             socket_type='NodeSocketColor')
        color_middleline_socket_2.attribute_domain = 'POINT'

        # Socket color_pedestrial
        color_pedestrial_socket_2 = road_geometry_nodes.interface.new_socket(name="color_pedestrial", in_out='OUTPUT',
                                                                             socket_type='NodeSocketColor')
        color_pedestrial_socket_2.attribute_domain = 'POINT'

        # Socket color_sidewalk
        color_sidewalk_socket_2 = road_geometry_nodes.interface.new_socket(name="color_sidewalk", in_out='OUTPUT',
                                                                           socket_type='NodeSocketColor')
        color_sidewalk_socket_2.attribute_domain = 'POINT'

        # Socket brick_scale
        brick_scale_socket_2 = road_geometry_nodes.interface.new_socket(name="brick_scale", in_out='OUTPUT',
                                                                        socket_type='NodeSocketFloat')
        brick_scale_socket_2.subtype = 'NONE'
        brick_scale_socket_2.default_value = 0.0
        brick_scale_socket_2.min_value = -3.4028234663852886e+38
        brick_scale_socket_2.max_value = 3.4028234663852886e+38
        brick_scale_socket_2.attribute_domain = 'POINT'

        # Socket intersection rotation
        intersection_rotation_socket_1 = road_geometry_nodes.interface.new_socket(name="intersection rotation",
                                                                                  in_out='OUTPUT',
                                                                                  socket_type='NodeSocketVector')
        intersection_rotation_socket_1.subtype = 'EULER'
        intersection_rotation_socket_1.default_value = (0.0, 0.0, 0.0)
        intersection_rotation_socket_1.min_value = -3.4028234663852886e+38
        intersection_rotation_socket_1.max_value = 3.4028234663852886e+38
        intersection_rotation_socket_1.attribute_domain = 'POINT'

        # Socket Geometry
        geometry_socket_2 = road_geometry_nodes.interface.new_socket(name="Geometry", in_out='INPUT',
                                                                     socket_type='NodeSocketGeometry')
        geometry_socket_2.attribute_domain = 'POINT'

        # node Group Input
        group_input_1 = road_geometry_nodes.nodes.new("NodeGroupInput")
        group_input_1.name = "Group Input"

        # node Group Output
        group_output_1 = road_geometry_nodes.nodes.new("NodeGroupOutput")
        group_output_1.name = "Group Output"
        group_output_1.is_active_output = True

        # node Group
        group = road_geometry_nodes.nodes.new("GeometryNodeGroup")
        group.name = "Group"
        group.node_tree = main_road_geometry_nodes

        # Input_0
        group.inputs[1].default_value = width_roadline
        # Input_1
        group.inputs[2].default_value = width_sidewalk
        # Input_7
        group.inputs[3].default_value = wet
        # Input_13
        group.inputs[4].default_value = color_sideline
        # Input_11
        group.inputs[5].default_value = color_middleline
        # Input_25
        group.inputs[6].default_value = color_pedestrial
        # Input_29
        group.inputs[7].default_value = color_sidewalk
        # Input_31
        group.inputs[8].default_value = brick_scale
        # Input_9
        group.inputs[9].default_value = end_point_intersection

        # Set locations
        group_input_1.location = (1436.3380126953125, 291.5166015625)
        group_output_1.location = (1927.3270263671875, 417.6368103027344)
        group.location = (1661.9249267578125, 414.0752868652344)

        # Set dimensions
        group_input_1.width, group_input_1.height = 140.0, 100.0
        group_output_1.width, group_output_1.height = 140.0, 100.0
        group.width, group.height = 248.78103637695312, 100.0

        # initialize road_geometry_nodes links
        # group.Geometry -> group_output_1.Geometry
        road_geometry_nodes.links.new(group.outputs[0], group_output_1.inputs[0])
        # group_input_1.Geometry -> group.curve
        road_geometry_nodes.links.new(group_input_1.outputs[0], group.inputs[0])
        # group.widthRoad -> group_output_1.widthRoad
        road_geometry_nodes.links.new(group.outputs[1], group_output_1.inputs[1])
        # group.wet -> group_output_1.wet
        road_geometry_nodes.links.new(group.outputs[3], group_output_1.inputs[3])
        # group.widthSidewalk -> group_output_1.widthSidewalk
        road_geometry_nodes.links.new(group.outputs[2], group_output_1.inputs[2])
        # group.color_middleline -> group_output_1.color_middleline
        road_geometry_nodes.links.new(group.outputs[5], group_output_1.inputs[5])
        # group.color_sideline -> group_output_1.color_sideline
        road_geometry_nodes.links.new(group.outputs[4], group_output_1.inputs[4])
        # group.color_pedestrial -> group_output_1.color_pedestrial
        road_geometry_nodes.links.new(group.outputs[6], group_output_1.inputs[6])
        # group.color_sidewalk -> group_output_1.color_sidewalk
        road_geometry_nodes.links.new(group.outputs[7], group_output_1.inputs[7])
        # group.brick_scale -> group_output_1.brick_scale
        road_geometry_nodes.links.new(group.outputs[8], group_output_1.inputs[8])
        # group.intersection rotation -> group_output_1.intersection rotation
        road_geometry_nodes.links.new(group.outputs[9], group_output_1.inputs[9])
        return road_geometry_nodes

    road_geometry_nodes = road_geometry_nodes_node_group()
    return road_geometry_nodes


def get_mat_sidewalk_corner():
    bpy.ops.object.select_all(action="DESELECT")

    mat = bpy.data.materials.get("sidewalk_corner", None)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name="sidewalk_corner")
    mat.use_nodes = True

    # initialize Sidewalk_corner node group
    def sidewalk_corner_node_group():
        sidewalk_corner = bpy.data.node_groups.new(type='ShaderNodeTree', name="mySidewalkCorner")

        # sidewalk_corner interface
        # Socket BSDF
        bsdf_socket = sidewalk_corner.interface.new_socket(name="BSDF", in_out='OUTPUT', socket_type='NodeSocketShader')
        bsdf_socket.attribute_domain = 'POINT'

        # Socket tmp_viewer
        tmp_viewer_socket = sidewalk_corner.interface.new_socket(name="tmp_viewer", in_out='OUTPUT',
                                                                 socket_type='NodeSocketShader')
        tmp_viewer_socket.attribute_domain = 'POINT'

        # Socket sidewalk_color
        sidewalk_color_socket = sidewalk_corner.interface.new_socket(name="sidewalk_color", in_out='INPUT',
                                                                     socket_type='NodeSocketColor')
        sidewalk_color_socket.attribute_domain = 'POINT'

        # Socket brick_scale
        brick_scale_socket = sidewalk_corner.interface.new_socket(name="brick_scale", in_out='INPUT',
                                                                  socket_type='NodeSocketFloat')
        brick_scale_socket.subtype = 'NONE'
        brick_scale_socket.default_value = 0.75
        brick_scale_socket.min_value = -1000.0
        brick_scale_socket.max_value = 1000.0
        brick_scale_socket.attribute_domain = 'POINT'

        # Socket wet
        wet_socket = sidewalk_corner.interface.new_socket(name="wet", in_out='INPUT', socket_type='NodeSocketFloat')
        wet_socket.subtype = 'FACTOR'
        wet_socket.default_value = 0.5690608024597168
        wet_socket.min_value = 0.0
        wet_socket.max_value = 1.0
        wet_socket.attribute_domain = 'POINT'

        # initialize sidewalk_corner nodes
        # node Group Output
        group_output = sidewalk_corner.nodes.new("NodeGroupOutput")
        group_output.name = "Group Output"
        group_output.is_active_output = True

        # node Noise Texture.001
        noise_texture_001 = sidewalk_corner.nodes.new("ShaderNodeTexNoise")
        noise_texture_001.name = "Noise Texture.001"
        noise_texture_001.noise_dimensions = '3D'
        noise_texture_001.normalize = True
        # W
        noise_texture_001.inputs[1].default_value = 0.0
        # Scale
        noise_texture_001.inputs[2].default_value = 0.7000000476837158
        # Detail
        noise_texture_001.inputs[3].default_value = 15.0
        # Roughness
        noise_texture_001.inputs[4].default_value = 0.8867403268814087
        # Lacunarity
        noise_texture_001.inputs[5].default_value = 2.0
        # Distortion
        noise_texture_001.inputs[6].default_value = 0.0

        # node Mapping
        mapping = sidewalk_corner.nodes.new("ShaderNodeMapping")
        mapping.name = "Mapping"
        mapping.vector_type = 'POINT'
        # Location
        mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
        # Rotation
        mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Scale
        mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

        # node Texture Coordinate
        texture_coordinate = sidewalk_corner.nodes.new("ShaderNodeTexCoord")
        texture_coordinate.name = "Texture Coordinate"
        texture_coordinate.from_instancer = False

        # node Value
        value = sidewalk_corner.nodes.new("ShaderNodeValue")
        value.name = "Value"

        value.outputs[0].default_value = 66.79999542236328
        # node Bump
        bump = sidewalk_corner.nodes.new("ShaderNodeBump")
        bump.name = "Bump"
        bump.invert = False
        # Distance
        bump.inputs[1].default_value = 1.0
        # Normal
        bump.inputs[3].default_value = (0.0, 0.0, 0.0)

        # node Texture Coordinate.001
        texture_coordinate_001 = sidewalk_corner.nodes.new("ShaderNodeTexCoord")
        texture_coordinate_001.name = "Texture Coordinate.001"
        texture_coordinate_001.from_instancer = False

        # node ColorRamp.003
        colorramp_003 = sidewalk_corner.nodes.new("ShaderNodeValToRGB")
        colorramp_003.name = "ColorRamp.003"
        colorramp_003.color_ramp.color_mode = 'RGB'
        colorramp_003.color_ramp.hue_interpolation = 'NEAR'
        colorramp_003.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp_003.color_ramp.elements.remove(colorramp_003.color_ramp.elements[0])
        colorramp_003_cre_0 = colorramp_003.color_ramp.elements[0]
        colorramp_003_cre_0.position = 0.0
        colorramp_003_cre_0.alpha = 1.0
        colorramp_003_cre_0.color = (0.0, 0.0, 0.0, 1.0)

        colorramp_003_cre_1 = colorramp_003.color_ramp.elements.new(1.0)
        colorramp_003_cre_1.alpha = 1.0
        colorramp_003_cre_1.color = (1.0, 1.0, 1.0, 1.0)

        # node Layer Weight
        layer_weight = sidewalk_corner.nodes.new("ShaderNodeLayerWeight")
        layer_weight.name = "Layer Weight"
        # Blend
        layer_weight.inputs[0].default_value = 0.8000000715255737
        # Normal
        layer_weight.inputs[1].default_value = (0.0, 0.0, 0.0)

        # node ColorRamp.005
        colorramp_005 = sidewalk_corner.nodes.new("ShaderNodeValToRGB")
        colorramp_005.name = "ColorRamp.005"
        colorramp_005.color_ramp.color_mode = 'RGB'
        colorramp_005.color_ramp.hue_interpolation = 'NEAR'
        colorramp_005.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp_005.color_ramp.elements.remove(colorramp_005.color_ramp.elements[0])
        colorramp_005_cre_0 = colorramp_005.color_ramp.elements[0]
        colorramp_005_cre_0.position = 0.054380644112825394
        colorramp_005_cre_0.alpha = 1.0
        colorramp_005_cre_0.color = (1.0, 1.0, 1.0, 1.0)

        colorramp_005_cre_1 = colorramp_005.color_ramp.elements.new(0.24471290409564972)
        colorramp_005_cre_1.alpha = 1.0
        colorramp_005_cre_1.color = (0.0, 0.0, 0.0, 1.0)

        # node Mix.007
        mix_007 = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix_007.name = "Mix.007"
        mix_007.blend_type = 'OVERLAY'
        mix_007.clamp_factor = True
        mix_007.clamp_result = False
        mix_007.data_type = 'RGBA'
        mix_007.factor_mode = 'UNIFORM'
        # Factor_Float
        mix_007.inputs[0].default_value = 1.0
        # Factor_Vector
        mix_007.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_007.inputs[2].default_value = 0.0
        # B_Float
        mix_007.inputs[3].default_value = 0.0
        # A_Vector
        mix_007.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_007.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Rotation
        mix_007.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_007.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix.002
        mix_002 = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix_002.name = "Mix.002"
        mix_002.blend_type = 'MIX'
        mix_002.clamp_factor = True
        mix_002.clamp_result = False
        mix_002.data_type = 'FLOAT'
        mix_002.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_002.inputs[1].default_value = (0.5, 0.5, 0.5)
        # B_Float
        mix_002.inputs[3].default_value = 0.0
        # A_Vector
        mix_002.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_002.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_002.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        # B_Color
        mix_002.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        # A_Rotation
        mix_002.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_002.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix.001
        mix_001 = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix_001.name = "Mix.001"
        mix_001.blend_type = 'MIX'
        mix_001.clamp_factor = True
        mix_001.clamp_result = False
        mix_001.data_type = 'RGBA'
        mix_001.factor_mode = 'UNIFORM'
        # Factor_Float
        mix_001.inputs[0].default_value = 0.019999999552965164
        # Factor_Vector
        mix_001.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_001.inputs[2].default_value = 0.0
        # B_Float
        mix_001.inputs[3].default_value = 0.0
        # A_Vector
        mix_001.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_001.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Rotation
        mix_001.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_001.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix.009
        mix_009 = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix_009.name = "Mix.009"
        mix_009.blend_type = 'MULTIPLY'
        mix_009.clamp_factor = True
        mix_009.clamp_result = False
        mix_009.data_type = 'RGBA'
        mix_009.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_009.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_009.inputs[2].default_value = 0.0
        # B_Float
        mix_009.inputs[3].default_value = 0.0
        # A_Vector
        mix_009.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_009.inputs[5].default_value = (0.0, 0.0, 0.0)
        # B_Color
        mix_009.inputs[7].default_value = (0.5585646629333496, 0.5585646629333496, 0.5585646629333496, 1.0)
        # A_Rotation
        mix_009.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_009.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node ColorRamp
        colorramp = sidewalk_corner.nodes.new("ShaderNodeValToRGB")
        colorramp.name = "ColorRamp"
        colorramp.color_ramp.color_mode = 'RGB'
        colorramp.color_ramp.hue_interpolation = 'NEAR'
        colorramp.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp.color_ramp.elements.remove(colorramp.color_ramp.elements[0])
        colorramp_cre_0 = colorramp.color_ramp.elements[0]
        colorramp_cre_0.position = 0.5709963440895081
        colorramp_cre_0.alpha = 1.0
        colorramp_cre_0.color = (0.0, 0.0, 0.0, 1.0)

        colorramp_cre_1 = colorramp.color_ramp.elements.new(0.6253782510757446)
        colorramp_cre_1.alpha = 1.0
        colorramp_cre_1.color = (1.0, 1.0, 1.0, 1.0)

        # node Mix.003
        mix_003 = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix_003.name = "Mix.003"
        mix_003.blend_type = 'MIX'
        mix_003.clamp_factor = True
        mix_003.clamp_result = False
        mix_003.data_type = 'RGBA'
        mix_003.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_003.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_003.inputs[2].default_value = 0.0
        # B_Float
        mix_003.inputs[3].default_value = 0.0
        # A_Vector
        mix_003.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_003.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_003.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
        # A_Rotation
        mix_003.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_003.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix
        mix = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix.name = "Mix"
        mix.blend_type = 'MULTIPLY'
        mix.clamp_factor = True
        mix.clamp_result = False
        mix.data_type = 'RGBA'
        mix.factor_mode = 'UNIFORM'
        # Factor_Float
        mix.inputs[0].default_value = 1.0
        # Factor_Vector
        mix.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix.inputs[2].default_value = 0.0
        # B_Float
        mix.inputs[3].default_value = 0.0
        # A_Vector
        mix.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Rotation
        mix.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Math
        math = sidewalk_corner.nodes.new("ShaderNodeMath")
        math.name = "Math"
        math.operation = 'MULTIPLY'
        math.use_clamp = False
        # Value
        math.inputs[0].default_value = 0.25
        # Value_002
        math.inputs[2].default_value = 0.5

        # node Group Input
        group_input = sidewalk_corner.nodes.new("NodeGroupInput")
        group_input.name = "Group Input"

        # node Math.001
        math_001 = sidewalk_corner.nodes.new("ShaderNodeMath")
        math_001.name = "Math.001"
        math_001.operation = 'MULTIPLY'
        math_001.use_clamp = False
        # Value
        math_001.inputs[0].default_value = 0.5
        # Value_002
        math_001.inputs[2].default_value = 0.5

        # node Math.003
        math_003 = sidewalk_corner.nodes.new("ShaderNodeMath")
        math_003.name = "Math.003"
        math_003.operation = 'MULTIPLY'
        math_003.use_clamp = False
        # Value_001
        math_003.inputs[1].default_value = 0.7900000214576721
        # Value_002
        math_003.inputs[2].default_value = 0.5

        # node Mapping.002
        mapping_002 = sidewalk_corner.nodes.new("ShaderNodeMapping")
        mapping_002.name = "Mapping.002"
        mapping_002.vector_type = 'POINT'
        # Location
        mapping_002.inputs[1].default_value = (0.6200000047683716, -0.15000000596046448, 0.0)
        # Rotation
        mapping_002.inputs[2].default_value = (0.0, 0.0, 0.6544983983039856)
        # Scale
        mapping_002.inputs[3].default_value = (1.0, 1.0, 1.0)

        # node Math.002
        math_002 = sidewalk_corner.nodes.new("ShaderNodeMath")
        math_002.name = "Math.002"
        math_002.operation = 'MULTIPLY'
        math_002.use_clamp = False
        # Value_001
        math_002.inputs[1].default_value = 1.6000001430511475
        # Value_002
        math_002.inputs[2].default_value = 0.5

        # node Mix.010
        mix_010 = sidewalk_corner.nodes.new("ShaderNodeMix")
        mix_010.name = "Mix.010"
        mix_010.blend_type = 'MIX'
        mix_010.clamp_factor = True
        mix_010.clamp_result = False
        mix_010.data_type = 'FLOAT'
        mix_010.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_010.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_010.inputs[2].default_value = 0.4000000059604645
        # B_Float
        mix_010.inputs[3].default_value = -0.4000000059604645
        # A_Vector
        mix_010.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_010.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_010.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        # B_Color
        mix_010.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        # A_Rotation
        mix_010.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_010.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Math.006
        math_006 = sidewalk_corner.nodes.new("ShaderNodeMath")
        math_006.name = "Math.006"
        math_006.operation = 'ADD'
        math_006.use_clamp = False
        # Value_002
        math_006.inputs[2].default_value = 0.5

        # node ColorRamp.004
        colorramp_004 = sidewalk_corner.nodes.new("ShaderNodeValToRGB")
        colorramp_004.name = "ColorRamp.004"
        colorramp_004.color_ramp.color_mode = 'RGB'
        colorramp_004.color_ramp.hue_interpolation = 'NEAR'
        colorramp_004.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp_004.color_ramp.elements.remove(colorramp_004.color_ramp.elements[0])
        colorramp_004_cre_0 = colorramp_004.color_ramp.elements[0]
        colorramp_004_cre_0.position = 0.32628414034843445
        colorramp_004_cre_0.alpha = 1.0
        colorramp_004_cre_0.color = (0.0, 0.0, 0.0, 1.0)

        colorramp_004_cre_1 = colorramp_004.color_ramp.elements.new(1.0)
        colorramp_004_cre_1.alpha = 1.0
        colorramp_004_cre_1.color = (1.0, 1.0, 1.0, 1.0)

        # node Mapping.001
        mapping_001 = sidewalk_corner.nodes.new("ShaderNodeMapping")
        mapping_001.name = "Mapping.001"
        mapping_001.vector_type = 'POINT'
        # Location
        mapping_001.inputs[1].default_value = (0.0, 0.0, 0.0)
        # Rotation
        mapping_001.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Scale
        mapping_001.inputs[3].default_value = (1.0, 1.0, 1.0)

        # node Principled BSDF
        principled_bsdf = sidewalk_corner.nodes.new("ShaderNodeBsdfPrincipled")
        principled_bsdf.name = "Principled BSDF"
        principled_bsdf.distribution = 'GGX'
        principled_bsdf.subsurface_method = 'RANDOM_WALK_SKIN'
        # Metallic
        principled_bsdf.inputs[1].default_value = 0.0
        # IOR
        principled_bsdf.inputs[3].default_value = 1.4500000476837158
        # Alpha
        principled_bsdf.inputs[4].default_value = 1.0
        # Weight
        principled_bsdf.inputs[6].default_value = 0.0
        # Subsurface Weight
        principled_bsdf.inputs[7].default_value = 0.0
        # Subsurface Radius
        principled_bsdf.inputs[8].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
        # Subsurface Scale
        principled_bsdf.inputs[9].default_value = 0.05000000074505806
        # Subsurface IOR
        principled_bsdf.inputs[10].default_value = 1.399999976158142
        # Subsurface Anisotropy
        principled_bsdf.inputs[11].default_value = 0.0
        # Specular IOR Level
        principled_bsdf.inputs[12].default_value = 0.5
        # Specular Tint
        principled_bsdf.inputs[13].default_value = (1.0, 1.0, 1.0, 1.0)
        # Anisotropic
        principled_bsdf.inputs[14].default_value = 0.0
        # Anisotropic Rotation
        principled_bsdf.inputs[15].default_value = 0.0
        # Tangent
        principled_bsdf.inputs[16].default_value = (0.0, 0.0, 0.0)
        # Transmission Weight
        principled_bsdf.inputs[17].default_value = 0.0
        # Coat Weight
        principled_bsdf.inputs[18].default_value = 0.0
        # Coat Roughness
        principled_bsdf.inputs[19].default_value = 0.029999999329447746
        # Coat IOR
        principled_bsdf.inputs[20].default_value = 1.5
        # Coat Tint
        principled_bsdf.inputs[21].default_value = (1.0, 1.0, 1.0, 1.0)
        # Coat Normal
        principled_bsdf.inputs[22].default_value = (0.0, 0.0, 0.0)
        # Sheen Weight
        principled_bsdf.inputs[23].default_value = 0.0
        # Sheen Roughness
        principled_bsdf.inputs[24].default_value = 0.5
        # Sheen Tint
        principled_bsdf.inputs[25].default_value = (1.0, 1.0, 1.0, 1.0)
        # Emission Color
        principled_bsdf.inputs[26].default_value = (0.0, 0.0, 0.0, 1.0)
        # Emission Strength
        principled_bsdf.inputs[27].default_value = 1.0

        # node Brick Texture
        brick_texture = sidewalk_corner.nodes.new("ShaderNodeTexBrick")
        brick_texture.name = "Brick Texture"
        brick_texture.offset = 0.5
        brick_texture.offset_frequency = 2
        brick_texture.squash = 1.0
        brick_texture.squash_frequency = 2
        # Color1
        brick_texture.inputs[1].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        # Color2
        brick_texture.inputs[2].default_value = (0.6261456608772278, 0.6261456608772278, 0.6261456608772278, 1.0)
        # Mortar
        brick_texture.inputs[3].default_value = (0.029793990775942802, 0.029793990775942802, 0.029793990775942802, 1.0)
        # Scale
        brick_texture.inputs[4].default_value = 0.949999988079071
        # Mortar Size
        brick_texture.inputs[5].default_value = 0.003000000026077032
        # Mortar Smooth
        brick_texture.inputs[6].default_value = 0.10000000149011612
        # Bias
        brick_texture.inputs[7].default_value = 0.0

        # node Noise Texture.002
        noise_texture_002 = sidewalk_corner.nodes.new("ShaderNodeTexNoise")
        noise_texture_002.name = "Noise Texture.002"
        noise_texture_002.noise_dimensions = '3D'
        noise_texture_002.normalize = True
        # W
        noise_texture_002.inputs[1].default_value = 0.0
        # Scale
        noise_texture_002.inputs[2].default_value = 0.3000001907348633
        # Detail
        noise_texture_002.inputs[3].default_value = 15.0
        # Roughness
        noise_texture_002.inputs[4].default_value = 0.6436464190483093
        # Lacunarity
        noise_texture_002.inputs[5].default_value = 2.0
        # Distortion
        noise_texture_002.inputs[6].default_value = 0.0

        # node Texture Coordinate.002
        texture_coordinate_002 = sidewalk_corner.nodes.new("ShaderNodeTexCoord")
        texture_coordinate_002.name = "Texture Coordinate.002"
        texture_coordinate_002.from_instancer = False
        if "RoadCurve" in bpy.data.objects:
            texture_coordinate_002.object = bpy.data.objects["RoadCurve"]

        # node Noise Texture
        noise_texture = sidewalk_corner.nodes.new("ShaderNodeTexNoise")
        noise_texture.name = "Noise Texture"
        noise_texture.noise_dimensions = '3D'
        noise_texture.normalize = True
        # W
        noise_texture.inputs[1].default_value = 0.0
        # Scale
        noise_texture.inputs[2].default_value = 70.0
        # Detail
        noise_texture.inputs[3].default_value = 15.0
        # Roughness
        noise_texture.inputs[4].default_value = 0.8038674592971802
        # Lacunarity
        noise_texture.inputs[5].default_value = 2.0
        # Distortion
        noise_texture.inputs[6].default_value = 0.0

        # Set locations
        group_output.location = (1958.61669921875, 0.0)
        noise_texture_001.location = (-98.908447265625, 858.1087646484375)
        mapping.location = (-278.90838623046875, 818.1087646484375)
        texture_coordinate.location = (-458.90838623046875, 818.1087646484375)
        value.location = (105.6595458984375, -246.51251220703125)
        bump.location = (1468.90380859375, -148.63760375976562)
        texture_coordinate_001.location = (-1059.283447265625, -286.9915771484375)
        colorramp_003.location = (86.85302734375, 764.63671875)
        layer_weight.location = (108.672119140625, -351.849365234375)
        colorramp_005.location = (104.0770263671875, -753.173095703125)
        mix_007.location = (990.2105102539062, 485.00152587890625)
        mix_002.location = (603.3797607421875, -296.52593994140625)
        mix_001.location = (1153.450439453125, 51.6619873046875)
        mix_009.location = (1219.4375, 366.79803466796875)
        colorramp.location = (747.6488647460938, 117.48818969726562)
        mix_003.location = (1448.333251953125, 206.23556518554688)
        mix.location = (792.4931030273438, 399.319091796875)
        math.location = (-312.04095458984375, -195.6041259765625)
        group_input.location = (-695.5864868164062, -16.091812133789062)
        math_001.location = (-318.3697204589844, -17.8665771484375)
        math_003.location = (-98.66666412353516, 93.6023178100586)
        mapping_002.location = (-252.0350799560547, 451.3426818847656)
        math_002.location = (118.70381927490234, 4.04912805557251)
        mix_010.location = (-664.6539916992188, -798.0198364257812)
        math_006.location = (-62.85239791870117, -616.2926025390625)
        colorramp_004.location = (-352.9241943359375, -562.4439697265625)
        mapping_001.location = (-827.7791137695312, -268.9647216796875)
        principled_bsdf.location = (1668.61669921875, 415.7908630371094)
        brick_texture.location = (500.5489807128906, 409.293701171875)
        noise_texture_002.location = (-575.1006469726562, -423.4067687988281)
        texture_coordinate_002.location = (-496.0516052246094, 491.1173400878906)
        noise_texture.location = (-78.3873291015625, -68.18378448486328)

        # Set dimensions
        group_output.width, group_output.height = 140.0, 100.0
        noise_texture_001.width, noise_texture_001.height = 140.0, 100.0
        mapping.width, mapping.height = 140.0, 100.0
        texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
        value.width, value.height = 140.0, 100.0
        bump.width, bump.height = 140.0, 100.0
        texture_coordinate_001.width, texture_coordinate_001.height = 140.0, 100.0
        colorramp_003.width, colorramp_003.height = 240.0, 100.0
        layer_weight.width, layer_weight.height = 140.0, 100.0
        colorramp_005.width, colorramp_005.height = 240.0, 100.0
        mix_007.width, mix_007.height = 140.0, 100.0
        mix_002.width, mix_002.height = 140.0, 100.0
        mix_001.width, mix_001.height = 140.0, 100.0
        mix_009.width, mix_009.height = 140.0, 100.0
        colorramp.width, colorramp.height = 240.0, 100.0
        mix_003.width, mix_003.height = 140.0, 100.0
        mix.width, mix.height = 140.0, 100.0
        math.width, math.height = 140.0, 100.0
        group_input.width, group_input.height = 140.0, 100.0
        math_001.width, math_001.height = 140.0, 100.0
        math_003.width, math_003.height = 140.0, 100.0
        mapping_002.width, mapping_002.height = 140.0, 100.0
        math_002.width, math_002.height = 140.0, 100.0
        mix_010.width, mix_010.height = 140.0, 100.0
        math_006.width, math_006.height = 100.0, 100.0
        colorramp_004.width, colorramp_004.height = 240.0, 100.0
        mapping_001.width, mapping_001.height = 140.0, 100.0
        principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
        brick_texture.width, brick_texture.height = 150.0, 100.0
        noise_texture_002.width, noise_texture_002.height = 140.0, 100.0
        texture_coordinate_002.width, texture_coordinate_002.height = 140.0, 100.0
        noise_texture.width, noise_texture.height = 140.0, 100.0

        # initialize sidewalk_corner links
        # texture_coordinate.Object -> mapping.Vector
        sidewalk_corner.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
        # mapping.Vector -> noise_texture_001.Vector
        sidewalk_corner.links.new(mapping.outputs[0], noise_texture_001.inputs[0])
        # colorramp.Color -> mix_001.A
        sidewalk_corner.links.new(colorramp.outputs[0], mix_001.inputs[6])
        # value.Value -> mix_002.A
        sidewalk_corner.links.new(value.outputs[0], mix_002.inputs[2])
        # mix.Result -> mix_007.A
        sidewalk_corner.links.new(mix.outputs[2], mix_007.inputs[6])
        # math_006.Value -> mix_003.B
        sidewalk_corner.links.new(math_006.outputs[0], mix_003.inputs[7])
        # colorramp_005.Color -> mix_009.Factor
        sidewalk_corner.links.new(colorramp_005.outputs[0], mix_009.inputs[0])
        # mix_001.Result -> bump.Height
        sidewalk_corner.links.new(mix_001.outputs[2], bump.inputs[2])
        # noise_texture.Color -> mix_001.B
        sidewalk_corner.links.new(noise_texture.outputs[1], mix_001.inputs[7])
        # mix_003.Result -> principled_bsdf.Roughness
        sidewalk_corner.links.new(mix_003.outputs[2], principled_bsdf.inputs[2])
        # math_006.Value -> colorramp_005.Fac
        sidewalk_corner.links.new(math_006.outputs[0], colorramp_005.inputs[0])
        # colorramp_004.Color -> math_006.Value
        sidewalk_corner.links.new(colorramp_004.outputs[0], math_006.inputs[0])
        # noise_texture_002.Color -> colorramp_004.Fac
        sidewalk_corner.links.new(noise_texture_002.outputs[1], colorramp_004.inputs[0])
        # layer_weight.Facing -> mix_002.Factor
        sidewalk_corner.links.new(layer_weight.outputs[1], mix_002.inputs[0])
        # colorramp.Color -> mix_003.Factor
        sidewalk_corner.links.new(colorramp.outputs[0], mix_003.inputs[0])
        # mix_002.Result -> bump.Strength
        sidewalk_corner.links.new(mix_002.outputs[0], bump.inputs[0])
        # mix_010.Result -> math_006.Value
        sidewalk_corner.links.new(mix_010.outputs[0], math_006.inputs[1])
        # brick_texture.Color -> colorramp.Fac
        sidewalk_corner.links.new(brick_texture.outputs[0], colorramp.inputs[0])
        # mix_007.Result -> mix_009.A
        sidewalk_corner.links.new(mix_007.outputs[2], mix_009.inputs[6])
        # mix_009.Result -> principled_bsdf.Base Color
        sidewalk_corner.links.new(mix_009.outputs[2], principled_bsdf.inputs[0])
        # mapping_001.Vector -> noise_texture.Vector
        sidewalk_corner.links.new(mapping_001.outputs[0], noise_texture.inputs[0])
        # brick_texture.Color -> mix.A
        sidewalk_corner.links.new(brick_texture.outputs[0], mix.inputs[6])
        # noise_texture_001.Color -> colorramp_003.Fac
        sidewalk_corner.links.new(noise_texture_001.outputs[1], colorramp_003.inputs[0])
        # bump.Normal -> principled_bsdf.Normal
        sidewalk_corner.links.new(bump.outputs[0], principled_bsdf.inputs[5])
        # texture_coordinate_001.Object -> mapping_001.Vector
        sidewalk_corner.links.new(texture_coordinate_001.outputs[3], mapping_001.inputs[0])
        # colorramp_003.Color -> mix_007.B
        sidewalk_corner.links.new(colorramp_003.outputs[0], mix_007.inputs[7])
        # group_input.wet -> mix_010.Factor
        sidewalk_corner.links.new(group_input.outputs[2], mix_010.inputs[0])
        # principled_bsdf.BSDF -> group_output.BSDF
        sidewalk_corner.links.new(principled_bsdf.outputs[0], group_output.inputs[0])
        # group_input.sidewalk_color -> mix.B
        sidewalk_corner.links.new(group_input.outputs[0], mix.inputs[7])
        # group_input.brick_scale -> math_001.Value
        sidewalk_corner.links.new(group_input.outputs[1], math_001.inputs[1])
        # group_input.brick_scale -> math.Value
        sidewalk_corner.links.new(group_input.outputs[1], math.inputs[1])
        # math_003.Value -> brick_texture.Brick Width
        sidewalk_corner.links.new(math_003.outputs[0], brick_texture.inputs[8])
        # math_002.Value -> brick_texture.Row Height
        sidewalk_corner.links.new(math_002.outputs[0], brick_texture.inputs[9])
        # math.Value -> math_002.Value
        sidewalk_corner.links.new(math.outputs[0], math_002.inputs[0])
        # math_001.Value -> math_003.Value
        sidewalk_corner.links.new(math_001.outputs[0], math_003.inputs[0])
        # mapping_002.Vector -> brick_texture.Vector
        sidewalk_corner.links.new(mapping_002.outputs[0], brick_texture.inputs[0])
        # mapping_001.Vector -> noise_texture_002.Vector
        sidewalk_corner.links.new(mapping_001.outputs[0], noise_texture_002.inputs[0])
        # principled_bsdf.BSDF -> group_output.tmp_viewer
        sidewalk_corner.links.new(principled_bsdf.outputs[0], group_output.inputs[1])
        # texture_coordinate_002.Object -> mapping_002.Vector
        sidewalk_corner.links.new(texture_coordinate_002.outputs[3], mapping_002.inputs[0])
        return sidewalk_corner

    sidewalk_corner = sidewalk_corner_node_group()

    # initialize sidewalk_corner node group
    def sidewalk_corner_1_node_group():
        sidewalk_corner_1 = mat.node_tree
        # start with a clean node tree
        for node in sidewalk_corner_1.nodes:
            sidewalk_corner_1.nodes.remove(node)
        # sidewalk_corner_1 interface

        # initialize sidewalk_corner_1 nodes
        # node Material Output
        material_output = sidewalk_corner_1.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        # Displacement
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Thickness
        material_output.inputs[3].default_value = 0.0

        # node Attribute.002
        attribute_002 = sidewalk_corner_1.nodes.new("ShaderNodeAttribute")
        attribute_002.name = "Attribute.002"
        attribute_002.attribute_name = "brick_scale"
        attribute_002.attribute_type = 'GEOMETRY'

        # node Attribute
        attribute = sidewalk_corner_1.nodes.new("ShaderNodeAttribute")
        attribute.name = "Attribute"
        attribute.attribute_name = "wet"
        attribute.attribute_type = 'GEOMETRY'

        # node Attribute.001
        attribute_001 = sidewalk_corner_1.nodes.new("ShaderNodeAttribute")
        attribute_001.name = "Attribute.001"
        attribute_001.attribute_name = "color_sidewalk"
        attribute_001.attribute_type = 'GEOMETRY'

        # node Group
        group = sidewalk_corner_1.nodes.new("ShaderNodeGroup")
        group.name = "Group"
        group.node_tree = sidewalk_corner

        # Set locations
        material_output.location = (1671.8262939453125, 210.73316955566406)
        attribute_002.location = (1282.7618408203125, 130.53253173828125)
        attribute.location = (1279.6961669921875, -47.21490478515625)
        attribute_001.location = (1282.9884033203125, 305.7645568847656)
        group.location = (1483.5435791015625, 221.59242248535156)

        # Set dimensions
        material_output.width, material_output.height = 140.0, 100.0
        attribute_002.width, attribute_002.height = 140.0, 100.0
        attribute.width, attribute.height = 140.0, 100.0
        attribute_001.width, attribute_001.height = 140.0, 100.0
        group.width, group.height = 140.0, 100.0

        # initialize sidewalk_corner_1 links
        # attribute.Fac -> group.wet
        sidewalk_corner_1.links.new(attribute.outputs[2], group.inputs[2])
        # attribute_001.Color -> group.sidewalk_color
        sidewalk_corner_1.links.new(attribute_001.outputs[0], group.inputs[0])
        # attribute_002.Fac -> group.brick_scale
        sidewalk_corner_1.links.new(attribute_002.outputs[2], group.inputs[1])
        # group.tmp_viewer -> material_output.Surface
        sidewalk_corner_1.links.new(group.outputs[1], material_output.inputs[0])
        return sidewalk_corner_1

    sidewalk_corner_1 = sidewalk_corner_1_node_group()
    return mat


def get_mat_sidewalk():
    bpy.ops.object.select_all(action="DESELECT")

    mat = bpy.data.materials.get("sidewalk", None)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name="sidewalk")
    mat.use_nodes = True

    # initialize Sidewalk node group
    def sidewalk_node_group():
        sidewalk = bpy.data.node_groups.new(type='ShaderNodeTree', name="mySidewalk")

        # sidewalk interface
        # Socket BSDF
        bsdf_socket = sidewalk.interface.new_socket(name="BSDF", in_out='OUTPUT', socket_type='NodeSocketShader')
        bsdf_socket.attribute_domain = 'POINT'

        # Socket tmp_viewer
        tmp_viewer_socket = sidewalk.interface.new_socket(name="tmp_viewer", in_out='OUTPUT',
                                                          socket_type='NodeSocketShader')
        tmp_viewer_socket.attribute_domain = 'POINT'

        # Socket brick_color
        brick_color_socket = sidewalk.interface.new_socket(name="brick_color", in_out='INPUT',
                                                           socket_type='NodeSocketColor')
        brick_color_socket.attribute_domain = 'POINT'

        # Socket brick_scale
        brick_scale_socket = sidewalk.interface.new_socket(name="brick_scale", in_out='INPUT',
                                                           socket_type='NodeSocketFloat')
        brick_scale_socket.subtype = 'NONE'
        brick_scale_socket.default_value = 0.5
        brick_scale_socket.min_value = -10000.0
        brick_scale_socket.max_value = 10000.0
        brick_scale_socket.attribute_domain = 'POINT'

        # Socket wet
        wet_socket = sidewalk.interface.new_socket(name="wet", in_out='INPUT', socket_type='NodeSocketFloat')
        wet_socket.subtype = 'FACTOR'
        wet_socket.default_value = 0.5690608024597168
        wet_socket.min_value = 0.0
        wet_socket.max_value = 1.0
        wet_socket.attribute_domain = 'POINT'

        # initialize sidewalk nodes
        # node Group Output
        group_output = sidewalk.nodes.new("NodeGroupOutput")
        group_output.name = "Group Output"
        group_output.is_active_output = True

        # node Noise Texture.001
        noise_texture_001 = sidewalk.nodes.new("ShaderNodeTexNoise")
        noise_texture_001.name = "Noise Texture.001"
        noise_texture_001.noise_dimensions = '3D'
        noise_texture_001.normalize = True
        # W
        noise_texture_001.inputs[1].default_value = 0.0
        # Scale
        noise_texture_001.inputs[2].default_value = 0.7000000476837158
        # Detail
        noise_texture_001.inputs[3].default_value = 15.0
        # Roughness
        noise_texture_001.inputs[4].default_value = 0.8867403268814087
        # Lacunarity
        noise_texture_001.inputs[5].default_value = 2.0
        # Distortion
        noise_texture_001.inputs[6].default_value = 0.0

        # node Mapping
        mapping = sidewalk.nodes.new("ShaderNodeMapping")
        mapping.name = "Mapping"
        mapping.vector_type = 'POINT'
        # Location
        mapping.inputs[1].default_value = (0.0, 0.0, 0.0)
        # Rotation
        mapping.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Scale
        mapping.inputs[3].default_value = (1.0, 1.0, 1.0)

        # node Texture Coordinate
        texture_coordinate = sidewalk.nodes.new("ShaderNodeTexCoord")
        texture_coordinate.name = "Texture Coordinate"
        texture_coordinate.from_instancer = False

        # node Value
        value = sidewalk.nodes.new("ShaderNodeValue")
        value.name = "Value"

        value.outputs[0].default_value = 66.79999542236328
        # node Bump
        bump = sidewalk.nodes.new("ShaderNodeBump")
        bump.name = "Bump"
        bump.invert = False
        # Distance
        bump.inputs[1].default_value = 1.0
        # Normal
        bump.inputs[3].default_value = (0.0, 0.0, 0.0)

        # node Texture Coordinate.001
        texture_coordinate_001 = sidewalk.nodes.new("ShaderNodeTexCoord")
        texture_coordinate_001.name = "Texture Coordinate.001"
        texture_coordinate_001.from_instancer = False

        # node Mapping.001
        mapping_001 = sidewalk.nodes.new("ShaderNodeMapping")
        mapping_001.name = "Mapping.001"
        mapping_001.vector_type = 'POINT'
        # Location
        mapping_001.inputs[1].default_value = (0.0, 0.0, 0.0)
        # Rotation
        mapping_001.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Scale
        mapping_001.inputs[3].default_value = (1.0, 1.0, 1.0)

        # node Mix.010
        mix_010 = sidewalk.nodes.new("ShaderNodeMix")
        mix_010.name = "Mix.010"
        mix_010.blend_type = 'MIX'
        mix_010.clamp_factor = True
        mix_010.clamp_result = False
        mix_010.data_type = 'FLOAT'
        mix_010.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_010.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_010.inputs[2].default_value = 0.4000000059604645
        # B_Float
        mix_010.inputs[3].default_value = -0.4000000059604645
        # A_Vector
        mix_010.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_010.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_010.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        # B_Color
        mix_010.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        # A_Rotation
        mix_010.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_010.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node ColorRamp.003
        colorramp_003 = sidewalk.nodes.new("ShaderNodeValToRGB")
        colorramp_003.name = "ColorRamp.003"
        colorramp_003.color_ramp.color_mode = 'RGB'
        colorramp_003.color_ramp.hue_interpolation = 'NEAR'
        colorramp_003.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp_003.color_ramp.elements.remove(colorramp_003.color_ramp.elements[0])
        colorramp_003_cre_0 = colorramp_003.color_ramp.elements[0]
        colorramp_003_cre_0.position = 0.0
        colorramp_003_cre_0.alpha = 1.0
        colorramp_003_cre_0.color = (0.0, 0.0, 0.0, 1.0)

        colorramp_003_cre_1 = colorramp_003.color_ramp.elements.new(1.0)
        colorramp_003_cre_1.alpha = 1.0
        colorramp_003_cre_1.color = (1.0, 1.0, 1.0, 1.0)

        # node Layer Weight
        layer_weight = sidewalk.nodes.new("ShaderNodeLayerWeight")
        layer_weight.name = "Layer Weight"
        # Blend
        layer_weight.inputs[0].default_value = 0.8000000715255737
        # Normal
        layer_weight.inputs[1].default_value = (0.0, 0.0, 0.0)

        # node ColorRamp.005
        colorramp_005 = sidewalk.nodes.new("ShaderNodeValToRGB")
        colorramp_005.name = "ColorRamp.005"
        colorramp_005.color_ramp.color_mode = 'RGB'
        colorramp_005.color_ramp.hue_interpolation = 'NEAR'
        colorramp_005.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp_005.color_ramp.elements.remove(colorramp_005.color_ramp.elements[0])
        colorramp_005_cre_0 = colorramp_005.color_ramp.elements[0]
        colorramp_005_cre_0.position = 0.054380644112825394
        colorramp_005_cre_0.alpha = 1.0
        colorramp_005_cre_0.color = (1.0, 1.0, 1.0, 1.0)

        colorramp_005_cre_1 = colorramp_005.color_ramp.elements.new(0.24471290409564972)
        colorramp_005_cre_1.alpha = 1.0
        colorramp_005_cre_1.color = (0.0, 0.0, 0.0, 1.0)

        # node Math.006
        math_006 = sidewalk.nodes.new("ShaderNodeMath")
        math_006.name = "Math.006"
        math_006.operation = 'ADD'
        math_006.use_clamp = False
        # Value_002
        math_006.inputs[2].default_value = 0.5

        # node ColorRamp.004
        colorramp_004 = sidewalk.nodes.new("ShaderNodeValToRGB")
        colorramp_004.name = "ColorRamp.004"
        colorramp_004.color_ramp.color_mode = 'RGB'
        colorramp_004.color_ramp.hue_interpolation = 'NEAR'
        colorramp_004.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp_004.color_ramp.elements.remove(colorramp_004.color_ramp.elements[0])
        colorramp_004_cre_0 = colorramp_004.color_ramp.elements[0]
        colorramp_004_cre_0.position = 0.32628414034843445
        colorramp_004_cre_0.alpha = 1.0
        colorramp_004_cre_0.color = (0.0, 0.0, 0.0, 1.0)

        colorramp_004_cre_1 = colorramp_004.color_ramp.elements.new(1.0)
        colorramp_004_cre_1.alpha = 1.0
        colorramp_004_cre_1.color = (1.0, 1.0, 1.0, 1.0)

        # node Brick Texture
        brick_texture = sidewalk.nodes.new("ShaderNodeTexBrick")
        brick_texture.name = "Brick Texture"
        brick_texture.offset = 0.5
        brick_texture.offset_frequency = 2
        brick_texture.squash = 1.0
        brick_texture.squash_frequency = 2
        # Color1
        brick_texture.inputs[1].default_value = (0.800000011920929, 0.800000011920929, 0.800000011920929, 1.0)
        # Color2
        brick_texture.inputs[2].default_value = (0.6261456608772278, 0.6261456608772278, 0.6261456608772278, 1.0)
        # Mortar
        brick_texture.inputs[3].default_value = (0.029793990775942802, 0.029793990775942802, 0.029793990775942802, 1.0)
        # Scale
        brick_texture.inputs[4].default_value = -0.5999999046325684
        # Mortar Size
        brick_texture.inputs[5].default_value = 0.0020000000949949026
        # Mortar Smooth
        brick_texture.inputs[6].default_value = 0.10000000149011612
        # Bias
        brick_texture.inputs[7].default_value = 0.0

        # node Mix.007
        mix_007 = sidewalk.nodes.new("ShaderNodeMix")
        mix_007.name = "Mix.007"
        mix_007.blend_type = 'OVERLAY'
        mix_007.clamp_factor = True
        mix_007.clamp_result = False
        mix_007.data_type = 'RGBA'
        mix_007.factor_mode = 'UNIFORM'
        # Factor_Float
        mix_007.inputs[0].default_value = 1.0
        # Factor_Vector
        mix_007.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_007.inputs[2].default_value = 0.0
        # B_Float
        mix_007.inputs[3].default_value = 0.0
        # A_Vector
        mix_007.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_007.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Rotation
        mix_007.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_007.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix.002
        mix_002 = sidewalk.nodes.new("ShaderNodeMix")
        mix_002.name = "Mix.002"
        mix_002.blend_type = 'MIX'
        mix_002.clamp_factor = True
        mix_002.clamp_result = False
        mix_002.data_type = 'FLOAT'
        mix_002.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_002.inputs[1].default_value = (0.5, 0.5, 0.5)
        # B_Float
        mix_002.inputs[3].default_value = 0.0
        # A_Vector
        mix_002.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_002.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_002.inputs[6].default_value = (0.5, 0.5, 0.5, 1.0)
        # B_Color
        mix_002.inputs[7].default_value = (0.5, 0.5, 0.5, 1.0)
        # A_Rotation
        mix_002.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_002.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Noise Texture.002
        noise_texture_002 = sidewalk.nodes.new("ShaderNodeTexNoise")
        noise_texture_002.name = "Noise Texture.002"
        noise_texture_002.noise_dimensions = '3D'
        noise_texture_002.normalize = True
        # W
        noise_texture_002.inputs[1].default_value = 0.0
        # Scale
        noise_texture_002.inputs[2].default_value = 0.3000001907348633
        # Detail
        noise_texture_002.inputs[3].default_value = 15.0
        # Roughness
        noise_texture_002.inputs[4].default_value = 0.6436464190483093
        # Lacunarity
        noise_texture_002.inputs[5].default_value = 2.0
        # Distortion
        noise_texture_002.inputs[6].default_value = 0.0

        # node Noise Texture
        noise_texture = sidewalk.nodes.new("ShaderNodeTexNoise")
        noise_texture.name = "Noise Texture"
        noise_texture.noise_dimensions = '3D'
        noise_texture.normalize = True
        # W
        noise_texture.inputs[1].default_value = 0.0
        # Scale
        noise_texture.inputs[2].default_value = 70.0
        # Detail
        noise_texture.inputs[3].default_value = 15.0
        # Roughness
        noise_texture.inputs[4].default_value = 0.8038674592971802
        # Lacunarity
        noise_texture.inputs[5].default_value = 2.0
        # Distortion
        noise_texture.inputs[6].default_value = 0.0

        # node Mix
        mix = sidewalk.nodes.new("ShaderNodeMix")
        mix.name = "Mix"
        mix.blend_type = 'MULTIPLY'
        mix.clamp_factor = True
        mix.clamp_result = False
        mix.data_type = 'RGBA'
        mix.factor_mode = 'UNIFORM'
        # Factor_Float
        mix.inputs[0].default_value = 1.0
        # Factor_Vector
        mix.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix.inputs[2].default_value = 0.0
        # B_Float
        mix.inputs[3].default_value = 0.0
        # A_Vector
        mix.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Rotation
        mix.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix.009
        mix_009 = sidewalk.nodes.new("ShaderNodeMix")
        mix_009.name = "Mix.009"
        mix_009.blend_type = 'MULTIPLY'
        mix_009.clamp_factor = True
        mix_009.clamp_result = False
        mix_009.data_type = 'RGBA'
        mix_009.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_009.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_009.inputs[2].default_value = 0.0
        # B_Float
        mix_009.inputs[3].default_value = 0.0
        # A_Vector
        mix_009.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_009.inputs[5].default_value = (0.0, 0.0, 0.0)
        # B_Color
        mix_009.inputs[7].default_value = (0.5585646629333496, 0.5585646629333496, 0.5585646629333496, 1.0)
        # A_Rotation
        mix_009.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_009.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Mix.003
        mix_003 = sidewalk.nodes.new("ShaderNodeMix")
        mix_003.name = "Mix.003"
        mix_003.blend_type = 'MIX'
        mix_003.clamp_factor = True
        mix_003.clamp_result = False
        mix_003.data_type = 'RGBA'
        mix_003.factor_mode = 'UNIFORM'
        # Factor_Vector
        mix_003.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_003.inputs[2].default_value = 0.0
        # B_Float
        mix_003.inputs[3].default_value = 0.0
        # A_Vector
        mix_003.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_003.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Color
        mix_003.inputs[6].default_value = (0.0, 0.0, 0.0, 1.0)
        # A_Rotation
        mix_003.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_003.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node ColorRamp
        colorramp = sidewalk.nodes.new("ShaderNodeValToRGB")
        colorramp.name = "ColorRamp"
        colorramp.color_ramp.color_mode = 'RGB'
        colorramp.color_ramp.hue_interpolation = 'NEAR'
        colorramp.color_ramp.interpolation = 'LINEAR'

        # initialize color ramp elements
        colorramp.color_ramp.elements.remove(colorramp.color_ramp.elements[0])
        colorramp_cre_0 = colorramp.color_ramp.elements[0]
        colorramp_cre_0.position = 0.5709963440895081
        colorramp_cre_0.alpha = 1.0
        colorramp_cre_0.color = (0.0, 0.0, 0.0, 1.0)

        colorramp_cre_1 = colorramp.color_ramp.elements.new(0.6253782510757446)
        colorramp_cre_1.alpha = 1.0
        colorramp_cre_1.color = (1.0, 1.0, 1.0, 1.0)

        # node Mix.001
        mix_001 = sidewalk.nodes.new("ShaderNodeMix")
        mix_001.name = "Mix.001"
        mix_001.blend_type = 'MIX'
        mix_001.clamp_factor = True
        mix_001.clamp_result = False
        mix_001.data_type = 'RGBA'
        mix_001.factor_mode = 'UNIFORM'
        # Factor_Float
        mix_001.inputs[0].default_value = 0.019999999552965164
        # Factor_Vector
        mix_001.inputs[1].default_value = (0.5, 0.5, 0.5)
        # A_Float
        mix_001.inputs[2].default_value = 0.0
        # B_Float
        mix_001.inputs[3].default_value = 0.0
        # A_Vector
        mix_001.inputs[4].default_value = (0.0, 0.0, 0.0)
        # B_Vector
        mix_001.inputs[5].default_value = (0.0, 0.0, 0.0)
        # A_Rotation
        mix_001.inputs[8].default_value = (0.0, 0.0, 0.0)
        # B_Rotation
        mix_001.inputs[9].default_value = (0.0, 0.0, 0.0)

        # node Principled BSDF
        principled_bsdf = sidewalk.nodes.new("ShaderNodeBsdfPrincipled")
        principled_bsdf.name = "Principled BSDF"
        principled_bsdf.distribution = 'GGX'
        principled_bsdf.subsurface_method = 'RANDOM_WALK_SKIN'
        # Metallic
        principled_bsdf.inputs[1].default_value = 0.0
        # IOR
        principled_bsdf.inputs[3].default_value = 1.4500000476837158
        # Alpha
        principled_bsdf.inputs[4].default_value = 1.0
        # Weight
        principled_bsdf.inputs[6].default_value = 0.0
        # Subsurface Weight
        principled_bsdf.inputs[7].default_value = 0.0
        # Subsurface Radius
        principled_bsdf.inputs[8].default_value = (1.0, 0.20000000298023224, 0.10000000149011612)
        # Subsurface Scale
        principled_bsdf.inputs[9].default_value = 0.05000000074505806
        # Subsurface IOR
        principled_bsdf.inputs[10].default_value = 1.399999976158142
        # Subsurface Anisotropy
        principled_bsdf.inputs[11].default_value = 0.0
        # Specular IOR Level
        principled_bsdf.inputs[12].default_value = 0.5
        # Specular Tint
        principled_bsdf.inputs[13].default_value = (1.0, 1.0, 1.0, 1.0)
        # Anisotropic
        principled_bsdf.inputs[14].default_value = 0.0
        # Anisotropic Rotation
        principled_bsdf.inputs[15].default_value = 0.0
        # Tangent
        principled_bsdf.inputs[16].default_value = (0.0, 0.0, 0.0)
        # Transmission Weight
        principled_bsdf.inputs[17].default_value = 0.0
        # Coat Weight
        principled_bsdf.inputs[18].default_value = 0.0
        # Coat Roughness
        principled_bsdf.inputs[19].default_value = 0.029999999329447746
        # Coat IOR
        principled_bsdf.inputs[20].default_value = 1.5
        # Coat Tint
        principled_bsdf.inputs[21].default_value = (1.0, 1.0, 1.0, 1.0)
        # Coat Normal
        principled_bsdf.inputs[22].default_value = (0.0, 0.0, 0.0)
        # Sheen Weight
        principled_bsdf.inputs[23].default_value = 0.0
        # Sheen Roughness
        principled_bsdf.inputs[24].default_value = 0.5
        # Sheen Tint
        principled_bsdf.inputs[25].default_value = (1.0, 1.0, 1.0, 1.0)
        # Emission Color
        principled_bsdf.inputs[26].default_value = (0.0, 0.0, 0.0, 1.0)
        # Emission Strength
        principled_bsdf.inputs[27].default_value = 1.0

        # node Math.001
        math_001 = sidewalk.nodes.new("ShaderNodeMath")
        math_001.name = "Math.001"
        math_001.operation = 'MULTIPLY'
        math_001.use_clamp = False
        # Value
        math_001.inputs[0].default_value = 0.5
        # Value_002
        math_001.inputs[2].default_value = 0.5

        # node Math
        math = sidewalk.nodes.new("ShaderNodeMath")
        math.name = "Math"
        math.operation = 'MULTIPLY'
        math.use_clamp = False
        # Value
        math.inputs[0].default_value = 0.25
        # Value_002
        math.inputs[2].default_value = 0.5

        # node Attribute
        attribute = sidewalk.nodes.new("ShaderNodeAttribute")
        attribute.name = "Attribute"
        attribute.attribute_name = "Gradient X2"
        attribute.attribute_type = 'GEOMETRY'

        # node Attribute.001
        attribute_001 = sidewalk.nodes.new("ShaderNodeAttribute")
        attribute_001.name = "Attribute.001"
        attribute_001.attribute_name = "Gradient Y2"
        attribute_001.attribute_type = 'GEOMETRY'

        # node Combine XYZ
        combine_xyz = sidewalk.nodes.new("ShaderNodeCombineXYZ")
        combine_xyz.name = "Combine XYZ"
        # Z
        combine_xyz.inputs[2].default_value = 0.0

        # node Group Input
        group_input = sidewalk.nodes.new("NodeGroupInput")
        group_input.name = "Group Input"

        # Set locations
        group_output.location = (1478.2833251953125, 0.0)
        noise_texture_001.location = (30.091644287109375, 858.1087646484375)
        mapping.location = (-149.9083251953125, 818.1087646484375)
        texture_coordinate.location = (-329.9083251953125, 818.1087646484375)
        value.location = (234.65957641601562, -246.51248168945312)
        bump.location = (988.5704345703125, -148.6375732421875)
        texture_coordinate_001.location = (-930.2833251953125, -286.99151611328125)
        mapping_001.location = (-698.779052734375, -268.96466064453125)
        mix_010.location = (-855.2093505859375, -858.1087646484375)
        colorramp_003.location = (215.8531036376953, 764.63671875)
        layer_weight.location = (237.6721649169922, -351.849365234375)
        colorramp_005.location = (233.07708740234375, -753.1730346679688)
        math_006.location = (-141.65118408203125, -616.2926025390625)
        colorramp_004.location = (-470.6852111816406, -533.8610229492188)
        brick_texture.location = (43.647613525390625, 382.8001708984375)
        mix_007.location = (509.8772277832031, 485.0015563964844)
        mix_002.location = (732.3798217773438, -296.5259094238281)
        noise_texture_002.location = (-385.7583923339844, -268.4761962890625)
        noise_texture.location = (52.650726318359375, -71.24314880371094)
        mix.location = (312.1598815917969, 399.3191223144531)
        mix_009.location = (739.104248046875, 366.7980651855469)
        mix_003.location = (968.0, 206.235595703125)
        colorramp.location = (267.3156433105469, 117.48822021484375)
        mix_001.location = (673.1171264648438, 51.662017822265625)
        principled_bsdf.location = (1188.2833251953125, 415.7908935546875)
        math_001.location = (-176.5416259765625, 8.941184043884277)
        math.location = (-170.2128143310547, -168.79638671875)
        attribute.location = (-562.9019775390625, 473.5196228027344)
        attribute_001.location = (-562.8824462890625, 293.9287109375)
        combine_xyz.location = (-226.43218994140625, 301.6895751953125)
        group_input.location = (-527.9694213867188, 17.883821487426758)

        # Set dimensions
        group_output.width, group_output.height = 140.0, 100.0
        noise_texture_001.width, noise_texture_001.height = 140.0, 100.0
        mapping.width, mapping.height = 140.0, 100.0
        texture_coordinate.width, texture_coordinate.height = 140.0, 100.0
        value.width, value.height = 140.0, 100.0
        bump.width, bump.height = 140.0, 100.0
        texture_coordinate_001.width, texture_coordinate_001.height = 140.0, 100.0
        mapping_001.width, mapping_001.height = 140.0, 100.0
        mix_010.width, mix_010.height = 140.0, 100.0
        colorramp_003.width, colorramp_003.height = 240.0, 100.0
        layer_weight.width, layer_weight.height = 140.0, 100.0
        colorramp_005.width, colorramp_005.height = 240.0, 100.0
        math_006.width, math_006.height = 100.0, 100.0
        colorramp_004.width, colorramp_004.height = 240.0, 100.0
        brick_texture.width, brick_texture.height = 150.0, 100.0
        mix_007.width, mix_007.height = 140.0, 100.0
        mix_002.width, mix_002.height = 140.0, 100.0
        noise_texture_002.width, noise_texture_002.height = 140.0, 100.0
        noise_texture.width, noise_texture.height = 140.0, 100.0
        mix.width, mix.height = 140.0, 100.0
        mix_009.width, mix_009.height = 140.0, 100.0
        mix_003.width, mix_003.height = 140.0, 100.0
        colorramp.width, colorramp.height = 240.0, 100.0
        mix_001.width, mix_001.height = 140.0, 100.0
        principled_bsdf.width, principled_bsdf.height = 240.0, 100.0
        math_001.width, math_001.height = 140.0, 100.0
        math.width, math.height = 140.0, 100.0
        attribute.width, attribute.height = 140.0, 100.0
        attribute_001.width, attribute_001.height = 140.0, 100.0
        combine_xyz.width, combine_xyz.height = 140.0, 100.0
        group_input.width, group_input.height = 140.0, 100.0

        # initialize sidewalk links
        # mix_010.Result -> math_006.Value
        sidewalk.links.new(mix_010.outputs[0], math_006.inputs[1])
        # noise_texture_001.Color -> colorramp_003.Fac
        sidewalk.links.new(noise_texture_001.outputs[1], colorramp_003.inputs[0])
        # attribute_001.Fac -> combine_xyz.Y
        sidewalk.links.new(attribute_001.outputs[2], combine_xyz.inputs[1])
        # mix.Result -> mix_007.A
        sidewalk.links.new(mix.outputs[2], mix_007.inputs[6])
        # colorramp_003.Color -> mix_007.B
        sidewalk.links.new(colorramp_003.outputs[0], mix_007.inputs[7])
        # value.Value -> mix_002.A
        sidewalk.links.new(value.outputs[0], mix_002.inputs[2])
        # texture_coordinate_001.Object -> mapping_001.Vector
        sidewalk.links.new(texture_coordinate_001.outputs[3], mapping_001.inputs[0])
        # noise_texture_002.Color -> colorramp_004.Fac
        sidewalk.links.new(noise_texture_002.outputs[1], colorramp_004.inputs[0])
        # mapping_001.Vector -> noise_texture_002.Vector
        sidewalk.links.new(mapping_001.outputs[0], noise_texture_002.inputs[0])
        # colorramp_004.Color -> math_006.Value
        sidewalk.links.new(colorramp_004.outputs[0], math_006.inputs[0])
        # colorramp.Color -> mix_001.A
        sidewalk.links.new(colorramp.outputs[0], mix_001.inputs[6])
        # mix_009.Result -> principled_bsdf.Base Color
        sidewalk.links.new(mix_009.outputs[2], principled_bsdf.inputs[0])
        # texture_coordinate.Object -> mapping.Vector
        sidewalk.links.new(texture_coordinate.outputs[3], mapping.inputs[0])
        # combine_xyz.Vector -> brick_texture.Vector
        sidewalk.links.new(combine_xyz.outputs[0], brick_texture.inputs[0])
        # colorramp_005.Color -> mix_009.Factor
        sidewalk.links.new(colorramp_005.outputs[0], mix_009.inputs[0])
        # mix_003.Result -> principled_bsdf.Roughness
        sidewalk.links.new(mix_003.outputs[2], principled_bsdf.inputs[2])
        # mix_002.Result -> bump.Strength
        sidewalk.links.new(mix_002.outputs[0], bump.inputs[0])
        # noise_texture.Color -> mix_001.B
        sidewalk.links.new(noise_texture.outputs[1], mix_001.inputs[7])
        # layer_weight.Facing -> mix_002.Factor
        sidewalk.links.new(layer_weight.outputs[1], mix_002.inputs[0])
        # attribute.Fac -> combine_xyz.X
        sidewalk.links.new(attribute.outputs[2], combine_xyz.inputs[0])
        # mix_007.Result -> mix_009.A
        sidewalk.links.new(mix_007.outputs[2], mix_009.inputs[6])
        # math_006.Value -> colorramp_005.Fac
        sidewalk.links.new(math_006.outputs[0], colorramp_005.inputs[0])
        # bump.Normal -> principled_bsdf.Normal
        sidewalk.links.new(bump.outputs[0], principled_bsdf.inputs[5])
        # mapping.Vector -> noise_texture_001.Vector
        sidewalk.links.new(mapping.outputs[0], noise_texture_001.inputs[0])
        # principled_bsdf.BSDF -> group_output.BSDF
        sidewalk.links.new(principled_bsdf.outputs[0], group_output.inputs[0])
        # group_input.wet -> mix_010.Factor
        sidewalk.links.new(group_input.outputs[2], mix_010.inputs[0])
        # group_input.brick_color -> mix.B
        sidewalk.links.new(group_input.outputs[0], mix.inputs[7])
        # math_001.Value -> brick_texture.Brick Width
        sidewalk.links.new(math_001.outputs[0], brick_texture.inputs[8])
        # math.Value -> brick_texture.Row Height
        sidewalk.links.new(math.outputs[0], brick_texture.inputs[9])
        # group_input.brick_scale -> math_001.Value
        sidewalk.links.new(group_input.outputs[1], math_001.inputs[1])
        # group_input.brick_scale -> math.Value
        sidewalk.links.new(group_input.outputs[1], math.inputs[1])
        # brick_texture.Color -> colorramp.Fac
        sidewalk.links.new(brick_texture.outputs[0], colorramp.inputs[0])
        # mix_001.Result -> bump.Height
        sidewalk.links.new(mix_001.outputs[2], bump.inputs[2])
        # mapping_001.Vector -> noise_texture.Vector
        sidewalk.links.new(mapping_001.outputs[0], noise_texture.inputs[0])
        # brick_texture.Color -> mix.A
        sidewalk.links.new(brick_texture.outputs[0], mix.inputs[6])
        # colorramp.Color -> mix_003.Factor
        sidewalk.links.new(colorramp.outputs[0], mix_003.inputs[0])
        # math_006.Value -> mix_003.B
        sidewalk.links.new(math_006.outputs[0], mix_003.inputs[7])
        # principled_bsdf.BSDF -> group_output.tmp_viewer
        sidewalk.links.new(principled_bsdf.outputs[0], group_output.inputs[1])
        return sidewalk

    sidewalk = sidewalk_node_group()

    # initialize sidewalk node group
    def sidewalk_1_node_group():
        sidewalk_1 = mat.node_tree
        # start with a clean node tree
        for node in sidewalk_1.nodes:
            sidewalk_1.nodes.remove(node)
        # sidewalk_1 interface

        # initialize sidewalk_1 nodes
        # node Material Output
        material_output = sidewalk_1.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        # Displacement
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Thickness
        material_output.inputs[3].default_value = 0.0

        # node Attribute.001
        attribute_001_1 = sidewalk_1.nodes.new("ShaderNodeAttribute")
        attribute_001_1.name = "Attribute.001"
        attribute_001_1.attribute_name = "color_sidewalk"
        attribute_001_1.attribute_type = 'GEOMETRY'

        # node Attribute.002
        attribute_002 = sidewalk_1.nodes.new("ShaderNodeAttribute")
        attribute_002.name = "Attribute.002"
        attribute_002.attribute_name = "brick_scale"
        attribute_002.attribute_type = 'GEOMETRY'

        # node Attribute
        attribute_1 = sidewalk_1.nodes.new("ShaderNodeAttribute")
        attribute_1.name = "Attribute"
        attribute_1.attribute_name = "wet"
        attribute_1.attribute_type = 'GEOMETRY'

        # node Group
        group = sidewalk_1.nodes.new("ShaderNodeGroup")
        group.name = "Group"
        group.node_tree = sidewalk

        # Set locations
        material_output.location = (1826.2747802734375, 185.69667053222656)
        attribute_001_1.location = (1419.4169921875, 348.05810546875)
        attribute_002.location = (1426.7799072265625, 166.61277770996094)
        attribute_1.location = (1439.9827880859375, -35.1737060546875)
        group.location = (1638.7568359375, 202.44264221191406)

        # Set dimensions
        material_output.width, material_output.height = 140.0, 100.0
        attribute_001_1.width, attribute_001_1.height = 140.0, 100.0
        attribute_002.width, attribute_002.height = 140.0, 100.0
        attribute_1.width, attribute_1.height = 140.0, 100.0
        group.width, group.height = 140.0, 100.0

        # initialize sidewalk_1 links
        # attribute_1.Fac -> group.wet
        sidewalk_1.links.new(attribute_1.outputs[2], group.inputs[2])
        # group.tmp_viewer -> material_output.Surface
        sidewalk_1.links.new(group.outputs[1], material_output.inputs[0])
        # attribute_001_1.Color -> group.brick_color
        sidewalk_1.links.new(attribute_001_1.outputs[0], group.inputs[0])
        # attribute_002.Fac -> group.brick_scale
        sidewalk_1.links.new(attribute_002.outputs[2], group.inputs[1])
        return sidewalk_1

    sidewalk_1 = sidewalk_1_node_group()
    return mat


def get_mat_road(asphalt=None):
    bpy.ops.object.select_all(action="DESELECT")

    mat = bpy.data.materials.get("road", None)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name="road")
    mat.use_nodes = True

    asphalt = asphalt if asphalt is not None else asphalt_node_group()

    # initialize road node group
    def road_node_group():
        road = mat.node_tree
        # start with a clean node tree
        for node in road.nodes:
            road.nodes.remove(node)
        # road interface

        # initialize road nodes
        # node Material Output
        material_output = road.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        # Displacement
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Thickness
        material_output.inputs[3].default_value = 0.0

        # node Attribute.001
        attribute_001_1 = road.nodes.new("ShaderNodeAttribute")
        attribute_001_1.name = "Attribute.001"
        attribute_001_1.attribute_name = "color_middle"
        attribute_001_1.attribute_type = 'GEOMETRY'

        # node Attribute.002
        attribute_002_1 = road.nodes.new("ShaderNodeAttribute")
        attribute_002_1.name = "Attribute.002"
        attribute_002_1.attribute_name = "color_sideline"
        attribute_002_1.attribute_type = 'GEOMETRY'

        # node Attribute
        attribute_1 = road.nodes.new("ShaderNodeAttribute")
        attribute_1.name = "Attribute"
        attribute_1.attribute_name = "wet"
        attribute_1.attribute_type = 'GEOMETRY'

        # node Group
        group = road.nodes.new("ShaderNodeGroup")
        group.name = "Group"
        group.node_tree = asphalt
        # Input_0
        group.inputs[2].default_value = 0.03999999910593033
        # Input_2
        group.inputs[3].default_value = 0.7300000190734863
        # Input_5
        group.inputs[4].default_value = 0.41999998688697815
        # Input_6
        group.inputs[5].default_value = 1.2400000095367432
        # Input_8
        group.inputs[6].default_value = 0.019999999552965164
        # Input_22
        group.inputs[8].default_value = 0.0
        # Input_40
        group.inputs[9].default_value = (0.5, 0.5, 0.5, 1.0)
        # Input_41
        group.inputs[10].default_value = 0.5499999523162842

        # Set locations
        material_output.location = (1774.8018798828125, 331.67840576171875)
        attribute_001_1.location = (1219.374267578125, 390.7850036621094)
        attribute_002_1.location = (1215.8192138671875, 216.3223114013672)
        attribute_1.location = (1217.21923828125, 31.11240577697754)
        group.location = (1421.4014892578125, 271.8532409667969)

        # Set dimensions
        material_output.width, material_output.height = 140.0, 100.0
        attribute_001_1.width, attribute_001_1.height = 140.0, 100.0
        attribute_002_1.width, attribute_002_1.height = 140.0, 100.0
        attribute_1.width, attribute_1.height = 140.0, 100.0
        group.width, group.height = 316.26708984375, 100.0

        # initialize road links
        # attribute_1.Fac -> group.wet
        road.links.new(attribute_1.outputs[2], group.inputs[7])
        # group.BSDF -> material_output.Surface
        road.links.new(group.outputs[0], material_output.inputs[0])
        # attribute_001_1.Color -> group.middleLine_color
        road.links.new(attribute_001_1.outputs[0], group.inputs[0])
        # attribute_002_1.Color -> group.sideLine_color
        road.links.new(attribute_002_1.outputs[0], group.inputs[1])
        return road

    road = road_node_group()
    return mat


def get_mat_intersection(asphalt=None):
    bpy.ops.object.select_all(action="DESELECT")

    mat = bpy.data.materials.get("intersection", None)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name="intersection")
    mat.use_nodes = True

    asphalt = asphalt if asphalt is not None else asphalt_node_group()

    # initialize intersection node group
    def intersection_node_group():
        intersection = mat.node_tree
        # start with a clean node tree
        for node in intersection.nodes:
            intersection.nodes.remove(node)
        # intersection interface
        # Socket BSDF
        bsdf_socket_1 = intersection.interface.new_socket(name="BSDF", in_out='OUTPUT', socket_type='NodeSocketShader')
        bsdf_socket_1.attribute_domain = 'POINT'

        # initialize intersection nodes
        # node Attribute
        attribute_1 = intersection.nodes.new("ShaderNodeAttribute")
        attribute_1.name = "Attribute"
        attribute_1.attribute_name = "wet"
        attribute_1.attribute_type = 'GEOMETRY'

        # node Attribute.001
        attribute_001_1 = intersection.nodes.new("ShaderNodeAttribute")
        attribute_001_1.name = "Attribute.001"
        attribute_001_1.attribute_name = "color_pedestrial"
        attribute_001_1.attribute_type = 'GEOMETRY'

        # node Material Output
        material_output = intersection.nodes.new("ShaderNodeOutputMaterial")
        material_output.name = "Material Output"
        material_output.is_active_output = True
        material_output.target = 'ALL'
        # Displacement
        material_output.inputs[2].default_value = (0.0, 0.0, 0.0)
        # Thickness
        material_output.inputs[3].default_value = 0.0

        # node Group
        group = intersection.nodes.new("ShaderNodeGroup")
        group.name = "Group"
        group.node_tree = asphalt
        # Input_3
        group.inputs[0].default_value = (1.0, 0.36103564500808716, 0.0, 1.0)
        # Input_4
        group.inputs[1].default_value = (0.5248628854751587, 0.5248628854751587, 0.5248628854751587, 1.0)
        # Input_0
        group.inputs[2].default_value = 0.029999999329447746
        # Input_2
        group.inputs[3].default_value = 0.5099999904632568
        # Input_5
        group.inputs[4].default_value = 0.23999999463558197
        # Input_6
        group.inputs[5].default_value = 1.0199999809265137
        # Input_8
        group.inputs[6].default_value = 0.019999999552965164
        # Input_22
        group.inputs[8].default_value = 1.0
        # Input_41
        group.inputs[10].default_value = 0.75

        # Set locations
        attribute_1.location = (1133.96630859375, 324.9007263183594)
        attribute_001_1.location = (1137.2152099609375, 138.07640075683594)
        material_output.location = (1575.2303466796875, 236.6826171875)
        group.location = (1331.0787353515625, 318.8813171386719)

        # Set dimensions
        attribute_1.width, attribute_1.height = 140.0, 100.0
        attribute_001_1.width, attribute_001_1.height = 140.0, 100.0
        material_output.width, material_output.height = 140.0, 100.0
        group.width, group.height = 203.67724609375, 100.0

        # initialize intersection links
        # attribute_1.Fac -> group.wet
        intersection.links.new(attribute_1.outputs[2], group.inputs[7])
        # group.tmp_viewer -> material_output.Surface
        intersection.links.new(group.outputs[1], material_output.inputs[0])
        # attribute_001_1.Color -> group.pedestrian_crossing_color
        intersection.links.new(attribute_001_1.outputs[0], group.inputs[9])
        return intersection

    intersection = intersection_node_group()
    return mat


def set_output_attribute(geometry_modifier):
    geometry_modifier["Socket_1_attribute_name"] = "roadlane_width"
    geometry_modifier["Socket_2_attribute_name"] = "sidewalk_width"
    geometry_modifier["Socket_3_attribute_name"] = "wet"
    geometry_modifier["Socket_4_attribute_name"] = "color_sideline"
    geometry_modifier["Socket_5_attribute_name"] = "color_middle"
    geometry_modifier["Socket_6_attribute_name"] = "color_pedestrial"
    geometry_modifier["Socket_7_attribute_name"] = "color_sidewalk"
    geometry_modifier["Socket_8_attribute_name"] = "brick_scale"
    geometry_modifier["Socket_9_attribute_name"] = "inter_rotate"


def set_road_materials(
        road_object,
        material_sidewalk_corner,
        material_road,
        material_intersection,
        material_sidewalk
):
    road_object.data.materials.append(material_sidewalk_corner)
    road_object.data.materials.append(material_road)
    road_object.data.materials.append(material_intersection)
    road_object.data.materials.append(material_sidewalk)


def _create_one_road(
        coords_list: list,
        road_name: str = "testRoad0",
        curve_type: str = "NURBS",  # POLY / BEZIER / NURBS
        collection_name: str = "geometry_road",
):
    if len(coords_list) < 2:
        raise ValueError("Road should have at least 2 points.")

    # create the Curve Datablock
    curveData = bpy.data.curves.new(road_name, type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 5

    # map coords to spline
    polyline = curveData.splines.new(curve_type)
    match curve_type:
        case "BEZIER":
            line_points = polyline.bezier_points
            # will add point(0,0,0) by default, so we need add(len(coords_list) - 1)
            line_points.add(len(coords_list) - 1)
            for i, coord in enumerate(coords_list):
                x, y, z = coord
                line_points[i].co = (x, y, z)
                line_points[i].handle_left_type = "AUTO"
                line_points[i].handle_right_type = "AUTO"

            # one more point to form a loop
            line_points.add(1)
            x, y, z = coords_list[0]
            line_points[-1].co = (x, y, z)
            line_points[-1].handle_left_type = "AUTO"
            line_points[-1].handle_right_type = "AUTO"

        case "POLY" | "NURBS":
            line_points = polyline.points
            # will add point(0,0,0) by default, so we need add(len(coords_list) - 1)
            line_points.add(len(coords_list) - 1)
            for i, coord in enumerate(coords_list):
                x, y, z = coord
                line_points[i].co = (x, y, z, 1)

            # one more point to form a loop
            line_points.add(1)
            x, y, z = coords_list[0]
            line_points[-1].co = (x, y, z, 1)

            if curve_type == "NURBS":
                polyline.use_endpoint_u = True
                polyline.use_endpoint_v = True

        case _:
            raise ValueError(f"Error!!! Found unsupported curve type: {curve_type}")

    # create Object
    curveOB = bpy.data.objects.new(road_name, curveData)

    # add to collection
    col = _add_collection(collection_name)
    col.objects.link(curveOB)
    bpy.ops.object.select_all(action="DESELECT")
    return curveOB


def _add_collection(col_name: str) -> bpy.types.Collection:
    col = bpy.data.collections.get(col_name, None)
    if col is None:
        # Create a new collection with a given name
        col = bpy.data.collections.new(col_name)
        # Link the new collection to the scene collection
        bpy.context.scene.collection.children.link(col)
    return col


def add_road_side_line(
        coords_list: list = None,
        road_name: str = "testRoad0",
        width_roadline=0.3,
        width_sidewalk=0.2,
        wet=0.4,
        color_sideline=(0.7364882826805115, 0.7364882826805115, 0.7364882826805115, 1.0),
        color_middleline=(1.0, 0.23297733068466187, 0.0, 1.0),
        color_pedestrial=(0.5028864741325378, 0.5028864741325378, 0.5028864741325378, 1.0),
        color_sidewalk=(0.19120171666145325, 0.13286834955215454, 0.09989873319864273, 1.0),
        brick_scale=1.5899999141693115,
        end_point_intersection=0,
):
    if coords_list is None:  # example data
        coords_list = [(10, 0, 1), (20, 1, 0), (30, 0, 1), (40, 1, 0), (50, 0, 1), (60, 1, 0), ]
    # add curve object
    obj = _create_one_road(coords_list, road_name, "NURBS")

    # set the road material
    asphalt = asphalt_node_group()
    mat_road = get_mat_road(asphalt)
    mat_intersection = get_mat_intersection(asphalt)
    mat_sidewalk = get_mat_sidewalk()
    mat_sidewalk_corner = get_mat_sidewalk_corner()

    # set the road geometry nodes
    gnmod = obj.modifiers.new("GeometryNodes", "NODES")
    gnmod.node_group = get_road_geometry_nodes(width_roadline, width_sidewalk, wet,
                                               color_sideline, color_middleline, color_pedestrial, color_sidewalk,
                                               brick_scale, end_point_intersection)  # set the node group
    set_output_attribute(gnmod)
    set_road_materials(obj, mat_sidewalk_corner, mat_road, mat_intersection, mat_sidewalk)


if __name__ == '__main__':
    add_road_side_line()
