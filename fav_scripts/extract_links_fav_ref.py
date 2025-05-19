import xml.etree.ElementTree as ET

# Input XML file
xml_file = 'danbooru_ref_fav.xml'

# Output files
list_output_file = 'danbooru_post_links_list.txt'
array_output_file = 'danbooru_post_links_array.txt'

# Parse the XML
tree = ET.parse(xml_file)
root = tree.getroot()

# Use the Atom namespace
ns = {'atom': 'http://www.w3.org/2005/Atom'}

# Collect all 'alternate' links (post URLs)
post_links = []
for entry in root.findall('atom:entry', ns):
    for link in entry.findall('atom:link', ns):
        if link.get('rel') == 'alternate':
            post_links.append(link.get('href'))

# Write to plain list output file
with open(list_output_file, 'w', encoding='utf-8') as f:
    for url in post_links:
        f.write(f"{url}\n")

# Write to array-style output file
with open(array_output_file, 'w', encoding='utf-8') as f:
    f.write("[\n")
    for url in post_links:
        f.write(f'    "{url}",\n')
    f.write("]\n")

print(f"Exported {len(post_links)} post links to both text files.")