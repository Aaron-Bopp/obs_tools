import os
import re
import sys
unlinkr = __import__('obs-unlinkr')


# def sections():
#     notes = {}
#     with os.scandir() as it:
#         for entry in it:
#             if entry.is_file() and entry.name.endswith(".md") and entry.name != 'GDB Notes.md':
#                 with open(entry.path, encoding='utf8') as f:
#                     text = f.read()
#                     notes.setdefault(entry.name, text)

#     sections = {'#Yes': [], '#No': [], '#Sometimes': []}
#     for name in notes:
#         note = notes[name]
#         # for tag in sections:
#         #     sections[tag].append(f"From [[{name.split('.')[0]}]]")
#         i = 0
#         while i < len(note):
#             try:
#                 i = note.index('#', i)
#             except ValueError:
#                 i = len(note)
#                 continue
#             for tag in sections:
#                 if note[i:i+len(tag)] == tag:
#                     sections[tag].append(f"- From [[{name.split('.')[0]}]]\n")
#                     end = note.index('==', i+len(tag)+3)
#                     sections[tag].append(
#                         '    - ' + note[i+len(tag)+3:end] + '\n')
#                     i = end
#                     break
#                 else:
#                     continue
#             i += 1
#     with open("I relate to.md", 'w') as f:
#         for tag in sections:
#             f.write(f"# {tag}\n\n")
#             f.write(''.join(list(dict.fromkeys(list(sections[tag])))))


# def clean():
#     notes = {}
#     with os.scandir() as it:
#         for entry in it:
#             if entry.is_file() and entry.name.endswith(".md") and entry.name != 'GDB Notes.md':
#                 with open(entry.path, encoding='Latin-1') as f:
#                     text = f.readlines()
#                     notes.setdefault(entry.name, text)

#     for key in notes:
#         # new_note = []
#         note = notes[key]
#         for i in range(len(note)):
#             line = note[i]
#             if '![Twitter Logo]' in line:
#                 try:
#                     link = line[3:line.index(')')]
#                     note[i] = f"[{note[i+2]}]({link})"
#                     note[i+2] = ''
#                 except IndexError:
#                     pass
#             elif 'https://genderdysphoria.fyi/images/svg/paragraph.svg' in line:
#                 note[i] = line[: line.index('[![]')]
#         with open(f"{key}", "w", encoding='Latin-1') as f:
#             f.write(''.join(note))
tag_base = "#Exandria"
base_path = "C:\\Users\\s533127\\Desktop\\Obsidian-notes\\D&D\\D&D\\Wildemount"

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

if __name__ == '__main__':
    working_dir = ""
    if len(sys.argv) > 1:
        working_dir = sys.argv[1]
    elif not os.path.isdir(working_dir):
        print('First arg is not a directory, using working_dir')
        working_dir = os.getcwd()
    print(working_dir)
    
    for root, dirs, files in os.walk(working_dir):
        for file in files:
            # ignore any 'dot' folders (.trash, .obsidian, etc.)
            
            if file.endswith('.md') and '\\.' not in root and '/.' not in root:
                page_title = re.sub(r'\.md$', '', file)
                
                #build tag
                base = f'{tag_base}/Locale/Wynandir/'
                folder = root.replace(working_dir, "").replace("\\", "")
                tag = base + folder.replace(" ", "")
                if folder == "":
                    location = "Wildemount Gazetteer"
                else:
                    location = folder
                with open(root + "/" + file, 'r', encoding="utf-8") as f:
                    lines = f.readlines()
                    if len(lines) == 0: continue
                    print(lines)
                    first_line = ""
                    if not lines[0].startswith("#"): 
                        first_line = lines[0]
                        lines[0] = f"## {page_title}\n"
                    lines[0] += f"**Tag**:: {tag}\n**Location**:: [[{location}]]\n{first_line}"
                    for i in range(len(lines)):
                        # create dataview field
                        if ":**" in lines[i]:
                            lines[i] = lines[i].replace(":**", "**::")
                        # create sub note
                        if ".**_" in lines[i]:
                            to_end = "".join(lines[i+1:])
                            text = lines[i]
                            if ".**_" not in to_end:
                                text += "\n" + to_end
                            name = create_sub_note(text, tag, page_title)
                            lines[i] = ""
                            if "Level" in name:
                                lines[i] = f"**Adventures**:: [[{name}]]\n"
                            lines[i] += f"![[{name}]]"
                        if "[](" in lines[i] and not lines[i].startswith("> "):
                            if "![](" in lines[i]:
                                lines[i] = f"> {lines[i]}"
                            else:
                                lines[i] = f"> !{lines[i]}"
                            lines[i+1] = f"> {lines[i+1]}"
                            lines[i+2] = f"> {lines[i+2]}"
                with open(root + "/" + file, 'w', encoding="utf-8") as f:
                    f.write("".join(lines))
                            
                                    
                                
                            
                        
                
                
        