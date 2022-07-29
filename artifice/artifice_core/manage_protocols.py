import json
from os import mkdir

def add_protocol(protocol_name, protocol_dir, config):
    art_protocol_path = config['PROTOCOLS_DIR'] / protocol_name
    
    mkdir(art_protocol_path)
    
    protocol_info = {"directory":protocol_dir}
    
    with open(art_protocol_path / 'info.json', 'w') as file:
        json.dump(protocol_info, file)