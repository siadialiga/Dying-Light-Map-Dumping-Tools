import json
import math

#
#   Script for importing Call of Dury maps into Dying Light, exports to the text format used in my Map2EDS tool
#   Pretty inaccurate but had fun in the terminal on mw3
#
    
def scale_and_convert_json(input_file, output_file, scale_factor):
    # Load JSON data
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Open the output file for writing
    with open(output_file, 'w') as f:
        for item in data:
            pos_x = float(item["PosX"]) * scale_factor
            pos_y = float(item["PosY"]) * scale_factor
            pos_z = float(item["PosZ"]) * scale_factor
            
            
            rot_x = (float(item['RotX'])) * math.pi/180
            rot_y = (float(item['RotY'])) * math.pi/180
            rot_z = (float(item['RotZ'])) * math.pi/180

            rot_x = -(rot_x * 180/math.pi)
            rot_y = -(rot_y * 180/math.pi)
            rot_z = rot_z * 180/math.pi
            
            name = item["Name"] + ".msh"
            
            scale = float(item["Scale"])
            
            # Format and write to output file
            formatted_output = (
                f"Class = ModelObject\n" #generic class for simple objects in DL, anything with scripting is saved in the exp in the normal format
                f"Position = <{pos_x}, {pos_y}, {pos_z}>\n"
                f"Rotation = <{rot_x}, {rot_y}, {rot_z}>\n"
                f"Scale = <{scale}, {scale}, {scale}>\n"
                f"MeshName = {name}\n\n"
            )
            f.write(formatted_output)

# Specify input and output file paths
input_file = 'input.json'
output_file = 'output.txt'

scale_factor = 0.0254

# Run the function
scale_and_convert_json(input_file, output_file, scale_factor)

print(f"Scaling and conversion complete! Check '{output_file}' for the result.")
