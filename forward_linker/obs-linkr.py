# pip3 install pyperclip pyyaml python-frontmatter
import frontmatter
import pyperclip
import yaml
import sys
import os
import re
unlinkr = __import__('obs-unlinkr')


page_titles = []
page_aliases = {}
generated_aliases = {}
obsidian_home = ''
wikipedia_mode = False
paragraph_mode = False
yaml_mode = False
regenerate_aliases = False
clear_links = False

def link_title(title, txt, current_title=''):
    updated_txt = txt
    # Matches full wiki links: (\[\[([\w\s|#^])+\]\])*

    # find instances of the title where it's not surrounded by [], |, #, /, \ or other letters
    # these are negative look ahead/behinds
    link_start = r'(?<!([(\]\(\))\w\|\\\[/\#]))'
    link_end = r'(?!([\|\]\w\\/\#\^]))'
    # does not match if title is in front of ::
    dataview_field = r'(?!(::))'
    matches = re.finditer(link_start + re.escape(title.lower()) + link_end + dataview_field, txt.lower())
    offset = 0 # track the offset of our matches (start index) due to document modifications
    
    for m in matches:
        # get the original text to link
        txt_to_link = updated_txt[m.start() + offset:m.end() + offset]
        
        # where is the next ]]?
        next_closing_index = updated_txt.find("]]", m.end() + offset)
        # where is the next [[?
        next_opening_index = updated_txt.find("[[", m.end() + offset)   
        
        # only proceed to link if our text is not already enclosed in a link
        # don't link if there's a ]] ahead, but no [[ (can happen with first few links)
        if not (next_opening_index == -1 and next_closing_index > -1):
            # proceed to link if no [[ or ]] ahead (first link) or [[ appears before ]]
            if (next_opening_index == -1 and next_closing_index == -1) or (next_opening_index < next_closing_index):
                updated_title = title
                # handle aliases
                if title in page_aliases: updated_title = page_aliases[title]
                if updated_title == current_title: return txt
                # handle the display text if it doesn't match the page title
                if txt_to_link != updated_title:
                    if txt_to_link.lower() != updated_title.lower():
                        updated_title += '|' + txt_to_link
                    else:
                        updated_title = txt_to_link
                # create the link and update our text
                updated_txt = updated_txt[:m.start() + offset] + '[[' + updated_title + ']]' + updated_txt[m.end() + offset:]
                # change our offset due to modifications to the document
                offset = offset + (len(updated_title) + 4 - len(txt_to_link))  # pairs of double brackets adds 4 chars
                # if wikipedia mode is on, return after first link is created
                if wikipedia_mode: return updated_txt
            
    return updated_txt


def link_content(content, current_title=''):
    # make a copy of our content and lowercase it for search purposes
    content_low = content.lower()

    # iterate through our page titles
    for page_title in page_titles:
        if page_title == "": continue
        # if we have a case-insenitive title match...
        if page_title.lower() in content_low:        
            updated_txt = link_title(page_title, content, current_title=current_title)            
            # we can tell whether we've matched the term if
            # the linking process changed the updated text length
            if len(updated_txt) != len(content):
                content = updated_txt
                print("linked %s" % page_title)

            # lowercase our updated text for the next round of search
            content_low = content.lower()        
    
    return content

if __name__ == '__main__':
    # main entry point
    # validate obsidian vault location
    if len(sys.argv) > 1:
        obsidian_home = sys.argv[1]
        if not os.path.isdir(obsidian_home):
            print('folder specified is not valid')
            # exit()
        
        # check for additional flags
        if len(sys.argv) > 2:
            for arg_index in range(2, len(sys.argv)):
                flag = sys.argv[arg_index]

                if flag == "-w":
                    wikipedia_mode = True
                elif flag == "-p":
                    wikipedia_mode = True
                    paragraph_mode = True
                elif flag == "-r":
                    regenerate_aliases = True
                elif flag == "-y":
                    yaml_mode = True
                elif flag == "-u":
                    clear_links = True

    else:
        print("usage - python obs-link.py <path to obsidian vault> [-r] [-y] [-w / -p]")
        print("-r = regenerate the aliases.md file using yaml frontmatter inside vault markdown files")
        print("-y = use aliases.yml as aliases file instead of aliases.md")
        print("-w = only the first occurrence of a page title (or alias) in the content will be linked ('wikipedia mode')")
        print("-p = only the first occurrence of a page title (or alias) in each paragraph will be linked ('paragraph mode')")
        print("-u = remove existing links in clipboard text before performing linking")
        # exit()
    if obsidian_home == '': obsidian_home = r'C:\Users\aweso\Documents\GitHub\Obsidian-Notes\SecondBrain'
    aliases_file = obsidian_home + "\\aliases" + (".yml" if yaml_mode else ".md")

    # load the aliases file
    # we pivot (invert) the dict for lookup purposes
    if os.path.isfile(aliases_file):
        with open(aliases_file, 'r', encoding='utf-8') as stream:
            try:
                # this line injects quotes around wikilinks so that yaml parsing won't fail
                # we remove them later, so they are only a temporary measure
                # aliases_txt = stream.read().replace("[[", "\"[[").replace("]]", "]]\"")
                aliases_txt = stream.read().replace("[[", "\"").replace("]]", "\"")
                aliases = yaml.full_load(aliases_txt)
                print(aliases)
                if aliases:
                    for title in aliases:         
                        if aliases[title]:                  
                            for alias in aliases[title]:
                                # strip out wikilinks and quotes from title if present
                                sanitized_title = title.replace("[[", "").replace("]]", "").replace("\"", "")
                                if alias:
                                    page_aliases[alias] = sanitized_title
                                else:
                                    # empty entry will signal to ignore page title in matching
                                    print("Empty alias (will be ignored): " + sanitized_title)
                                    if sanitized_title in page_titles:
                                        page_titles.remove(sanitized_title)
                        #print(page_aliases)
            except yaml.YAMLError as exc:
                print(exc)
                exit()
                
    # get a directory listing of obsidian *.md files
    # use it to build our list of titles and aliases
    for root, dirs, files in os.walk(obsidian_home):
        for file in files:
            # ignore any 'dot' folders (.trash, .obsidian, etc.)
            if file.endswith('.md') and '\\.' not in root and '/.' not in root:
                page_title = re.sub(r'\.md$', '', file)
                #print(page_title)
                page_titles.append(page_title)
                # load yaml frontmatter and parse aliases
                if regenerate_aliases:
                    try:
                        with open(root + "/" + file, encoding="utf-8") as f:
                            #print(file)
                            fm = frontmatter.load(f)
                            
                            if fm and 'aliases' in fm:
                                #print(fm['aliases'])
                                generated_aliases[page_title] = fm['aliases']
                    except yaml.YAMLError as exc:
                        print("Error processing aliases in file: " + file)
                        # exit()

    # if -r passed on command line, regenerate aliases.yml
    # this is only necessary if new aliases are present
    if regenerate_aliases:
        page_titles = sorted(page_titles) 
        with open(aliases_file, "w", encoding="utf-8") as af:
            for title in page_titles:
                af.write(title + ":\n" if yaml_mode else "[[" + title + "]]:\n")
                #print(title)
                if title in aliases:
                    if aliases[title] != None:
                        for alias in aliases[title]:
                            if alias != None:
                                af.write("- " + alias + "\n")
                            # print(alias)
                af.write("\n")
            if not yaml_mode: af.write("aliases:\n- ")


    # append our aliases to the list of titles
    for alias in page_aliases:
        page_titles.append(alias)

    # sort from longest to shortest page titles so that we don't
    # identify scenarios where a page title is a subset of another
    page_titles = sorted(page_titles, key=lambda x: len(x), reverse=True)
    for root, dirs, files in os.walk(obsidian_home):
        for file in files:
            name = file.split('.')[0]
            # ignore any 'dot' folders (.trash, .obsidian, etc.)
            # check that file is in the Evergreens folder
            if file.endswith('.md') and '\\.' not in root and '/.' not in root and 'Evergreens' in root or 'Topics' in root:
            # if file.endswith('.md') and file.contains("Evergreens") or file.contains("Topics") and '\\.' not in root and '/.' not in root and 'aliases' not in file:
                with open(root + "/" + file, 'r', encoding="utf-8") as f:
                    full_text = f.readlines()
                # first_line = metamanager.find_frontmatter_end(full_text)
                # plain_text = full_text[first_line:]
                unlinkable_lines = []
                yaml_lines, code_lines = [], []
                for i in range(len(full_text)):
                    if re.match(r"(---\s*)", full_text[i]) != None:
                        yaml_lines.append(i)
                    
                    if re.match(r"```.*", full_text[i]) != None:
                        code_lines.append(i)

                    if re.match(r"^#{1,6} (.*)", full_text[i]):
                        unlinkable_lines.append(i)

                    if re.match(r".*::.*", full_text[i]):
                        unlinkable_lines.append(i)

                # code_lines.append(len(full_text))
                if len(yaml_lines) > 0:
                    if "".join(full_text[:yaml_lines[0]]).replace('\n', "").strip(" ") == "":
                        unlinkable_lines.extend(range(0, yaml_lines[1]))
                
                if len(code_lines) % 2 == 1 : 
                    last = code_lines.pop()
                else:
                    last = len(full_text)
                if len(code_lines) > 0:
                    i = 0
                    while i < len(code_lines):
                        unlinkable_lines.extend(range(code_lines[i], code_lines[i+1]))
                        i += 2
                unlinkable_lines.extend(range(last, len(full_text)))
                
                plain_text = full_text
                # unlink text prior to processing if enabled
                if (clear_links):
                    full_text = [unlinkr.unlink_text(line) for line in full_text]

                # prepare our linked text output
                linked_txt = ""

                for i in range(len(full_text)):
                    if i in unlinkable_lines: 
                        linked_txt += plain_text[i]
                    else:
                        linked_txt += link_content(full_text[i], current_title=name)
                # linked_txt = linked_txt[:-1] # scrub the last newline
                
                with open(root + "/" + file, 'w', encoding="utf-8") as f:
                    # full_text = "\n".join(plain_text[:first_line-1]) + linked_txt
                    f.write(linked_txt)
    # # get text from clipboard
    # clip_txt = pyperclip.paste()
    # #print('--- clipboard text ---')
    # #print(clip_txt)
    # print('----------------------')

    # # unlink text prior to processing if enabled
    # if (clear_links):
    #     clip_txt = unlinkr.unlink_text(clip_txt)
    #     #print('--- text after scrubbing links ---')
    #     #print(clip_txt)
    #     #print('----------------------')

    # # prepare our linked text output
    # linked_txt = ""

    # if paragraph_mode:
    #     for paragraph in clip_txt.split("\n"):
    #         linked_txt += link_content(paragraph) + "\n"
    #     linked_txt = linked_txt[:-1] # scrub the last newline
    # else:
    #     linked_txt = link_content(clip_txt)

    # # send the linked text to the clipboard
    # pyperclip.copy(linked_txt)
    # #print(clip_txt)
    # print('----------------------')
    # print('linked text copied to clipboard')