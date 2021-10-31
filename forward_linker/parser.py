import os
import re
from sre_constants import FAILURE
import sys
unlinkr = __import__('obs-unlinkr')




def wildemount(path):
    tag_base = "#Exandria"
    def create_sub_note(line, parent_tag, parent_name):
        name, text = line.split(".**_")
        name = name.replace("_**", "")
        name = unlinkr.unlink_text(name)
        location = f"[[{parent_name}]]"
        extra_tags = []
        if " Level)" in line:
            path = "\Adventures in Wildemount\\"
            tag = f"{tag_base}/Adventure"
            extra_tags.append(f"**Level**:: {name.split('(')[1].replace(')', '')}")
            # if "/monsters/" in line:
            #     link_start = 0
            #     link_end = line.find("/monsters/")
            #     if (link_start > -1):
            #         link_start = line[link_start:link_end].find("](")
        else:
            path = f"\Glossary\\"
            tag = f"{parent_tag}/{parent_name}"
        sub_note = open(base_path + path + name + ".md", 'w', encoding="utf-8")
        sub_note.write(f"#### {name}\n")
        sub_note.write("\n".join([f"**Tag**:: {tag}", f"**Location**:: {location}"] + extra_tags))
        sub_note.write("\n\n" + text)
        sub_note.close()
        return name


    def dv_field(name, value, new_line=True):
        name = unlinkr.unlink_text(name)
        return f"**{name}**:: {value}" + ("\n" if new_line else "")
    #build tag
    # base = f'{tag_base}/Faction/Wildemount/'
    # folder = root.replace(working_dir, "").replace("\\", "")
    # tag = base + folder.replace(" ", "")
    # if folder == "":
    #     location = "Wildemount Gazetteer"
    # else:
    #     location = folder
    with open(root + "/" + file, 'r', encoding="utf-8") as f:
        tag = "#Magic/Item"
        new_fields = {'Features': [], 'Actions': [], 'Reactions': [], 'Legendary Actions': []}
        current_section = 'Features'
        existing_fields = {'Tag': 0, 'Location': 0}
        lines = f.readlines()
        for i in range(len(lines)):
            dv = None
            dv = re.match(r"\*\*(.*)\*\*:: (.*)", lines[i])
            if dv != None:
                existing_fields[dv.group(1)] = i
        # Convert image embeds with captions
            if "[](" in lines[i] and not lines[i].startswith("> "):
                if "![](" in lines[i]:
                    lines[i] = f"> {lines[i]}"
                else:
                    lines[i] = f"> !{lines[i]}"
                if i < len(lines) - 2:
                    lines[i+1] = f"> {lines[i+1]}"
                    lines[i+2] = f"> {lines[i+2]}"
        # find person match
            # # m = re.match(r"(_(?P<allignment>((\w+) (\w+))), (?P<gender>\w+) (?P<race>[\w\s]+)_)", lines[i])
            # m = re.match(r"_(\w+ \w+), (\w+) (.*)_", lines[i])
            # if m != None:
            #     lines[i] = dv_field("Allignment", m.group(1))
            #     lines[i] += dv_field("Gender", m.group(2))
            #     lines[i] += dv_field("Race", m.group(3))
            # # create dataview field
            # if ":**" in lines[i]:
            #     lines[i] = lines[i].replace(":**", "**::")
        # find size, type, alignment
            # monster = re.match(r"(\w+) (\w+)(\((.*)\))*\, ([\w\s]+)", lines[i])
            # if monster != None:
            #     lines[i] = dv_field("Size", monster.group(1))
            #     lines[i] += dv_field("Type", monster.group(2))
            #     lines[i] += dv_field("Alignment", monster.group(3))
        # create sub note
            # if ".**_" in lines[i]:
            #     to_end = "".join(lines[i+1:])
            #     text = lines[i]
            #     if ".**_" not in to_end:
            #         text += "\n" + to_end
            #     name = create_sub_note(text, tag, page_title)
            #     lines[i] = ""
            #     if "Level" in name:
            #         lines[i] = f"**Adventures**:: [[{name}]]\n"
            #     lines[i] += f"![[{name}]]"
        # Set section
            if lines[i].strip() in new_fields.keys(): 
                current_section = lines[i].strip()
                lines[i] = "#### " + current_section
        # get race traits
            trait = None
            # trait = re.match(r"_\*\*(.*)\.\*\*_ (.*)", lines[i]) 
            # trait = re.match(r"\_*\*\*([\w\s]*)\.*\*\*\_*(.*)", lines[i])
            trait = re.match(r"[\*\_\.]+([\w\s]+)[\*\_\.]+ (.*)", lines[i])
            # if trait == None:
            #     trait = re.match(r"(.*) = (.*)", lines[i])   
            if trait != None:
                new_fields[current_section].append(trait.group(1))
                lines[i] = dv_field(trait.group(1), trait.group(2))
        # convert magic item line
            weapon = re.match(r"_(\w+) \((.*)\), (([\w\s]+)( \((requires attunement)( by a )*(\w+)*\))*)_", lines[i])
            if weapon != None:
                item_name = weapon.group(1)
                tag += f"/{item_name}"
                item_type = weapon.group(2)
                rarity = re.match(r"_\w+ \(.*\), (([\w\s]+)( \((requires attunement)( by a )*(\w+)*\))*)_", lines[i])
                lines[i] = dv_field("Item", item_name)
                new_fields[current_section].append("Item")
                lines[i] += dv_field("Item Type", item_type)
                new_fields[current_section].append("Item Type")
            else:
                rarity = re.match(r"_Wondrous item, (([\w\s]+)( \((\w+ \w+)(by a)*(\w+)*\))*)_", lines[i])
                if rarity != None:
                    new_fields[current_section].append("Item")
                    item_name = "Wondrous"
                    tag += f"/{item_name}"
                    lines[i] = dv_field("Item", "Wondrous item")
            
            if rarity != None:
                new_fields[current_section].append("Rarity")
                lines[i] += dv_field("Rarity", rarity.group(2))
                if rarity.group(4) != None:
                    new_fields[current_section].append("Requires Attunement")
                    attunement = "True"
                    if rarity.group(6) != None:
                        attunement = rarity.group(6)
                    lines[i] += dv_field("Requires Attunement", attunement) 


    # Beginning metadata
        if len(lines) > 0:
            first_line = lines[0] 
            lines[0] = ""
        else:
            first_line = ""
            lines.append("")
        header = re.match("^#{1,6} (.*)", first_line)
        if header != None: 
            header = header.group(1)
            first_line = ""
        else:
            header = page_title
        
        lines[0] = f"## {header}\n"

        lines[existing_fields['Tag']] += dv_field("Tag", tag)
        lines[existing_fields["Location"]] += dv_field("Location", "[[Magic Items]]")
        for section in new_fields:
            if len(new_fields[section]) > 0:
                lines[0] += "\n" + dv_field(section, new_fields[section])
        lines[0] += first_line

    
    with open(root + "/" + file, 'w', encoding="utf-8") as f:
        f.write("".join(lines))
                
def motw_classes(filename, base_path):
    path = f"{base_path}\\{filename}.md"
    with open(path, 'r', encoding='utf-8') as f:
        text = f.readlines()    
    with open(path, 'w', encoding='utf-8') as f:
        f.write("")
    
    in_moves = False
    write_file = open(path, 'a', encoding='utf-8')
    for line in text:
        not_allowed_in_file = r'[\\\/\:\"\*\?\<\>\|\]\[\]]'
        m = re.match(r"^ ? ?\- ([^\:]*)\:(.*)", line)
        if m:
            name = m.group(1)
            name = re.sub(not_allowed_in_file, "", name)
            text = m.group(2)
            write_file.close()
            with open(path, 'a', encoding='utf-8') as mainf:
                mainf.write(f"- ![[{name.strip()}]]\n")
            write_file = open(r'C:\Users\aweso\Documents\GitHub\Obsidian-notes\D&D\D&D\MOTW'+f"\\Weapon Properties\\{name.strip()}.md", 'a', encoding='utf-8')
            line = f"---\nbase class: [[{filename}]]\n---\n{text}"
        m = re.match(r"^\*\*([\w\s\[\]]*)\*\*\s*$", line)
        if m:
            write_file.close()
            write_file = open(path, 'a', encoding='utf-8')
            section = m.group(1)
            write_file.write(f"## {section}\n")
        m = re.match(r"^\#+ .*", line)
        if m:
            in_moves = False
            write_file.close()
            write_file = open(path, 'a', encoding='utf-8')
        m = re.match(r"\[\[MOVES\]\]|\#\# \*\*\[\[MOVES\]\]\*\*|\#\# Moves", line)
        if m:
            in_moves = True
        write_file.write(line)
    write_file.close()

if __name__ == '__main__':
    working_dir = r"C:\Users\aweso\Documents\GitHub\Obsidian-notes\D&D\D&D\MOTW\MOTW Sections"
    
    flags = {'-f': False, '-d':False}
    if len(sys.argv) > 1:
        working_dir = sys.argv[1]
        args = sys.argv
        for i in range(1, len(sys.argv)):
            try:
                if args[i] == '-f' and os.path.isfile(args[i+1]):
                    flags['-f'] = args[i+1]
                if args[i] == '-d' and os.path.isfile(args[i+1]):
                    flags['-d'] = args[i+1]
                    working_dir = args[i+1]
            except IndexError:
                print("You must provide a valid arg for that flag")
    elif not os.path.isdir(working_dir):
        print('First arg is not a directory, or -d is not a valid dir, using current working directory')
        working_dir = os.getcwd()
    print(working_dir)
    # motw = open(r"C:\Users\s533127\Desktop\Obsidian-notes\D&D\D&D\MOTW", 'r', 'utf-8')
    for root, dirs, files in os.walk(working_dir):
        for file in files:
            # ignore any 'dot' folders (.trash, .obsidian, etc.)
            
            if file.endswith('.md') and '\\.' not in root and '/.' not in root:
                page_title = re.sub(r'\.md$', '', file)
                
                