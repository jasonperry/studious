import xml.etree.ElementTree as ETree
# from lxml import etree as ETree # about 0.2 secs for dracula


dracfiles = [ "./testbooks/dracula_extract/epub/text/chapter-"+ str(n) +".xhtml" for n in range(1,28)]

#file1 = "./testbooks/dracula_extract/epub/text/chapter-1.xhtml"
#file2 = "./testbooks/dracula_extract/epub/text/chapter-2.xhtml"

# file1 = "./testbooks/schop-extract/@public@vhost@g@gutenberg@html@files@10715@10715-h@10715-h-0.htm.html"
# file2 = "./testbooks/schop-extract/@public@vhost@g@gutenberg@html@files@10715@10715-h@10715-h-1.htm.html"

ETree.register_namespace('', 'http://www.w3.org/1999/xhtml')

tree = ETree.parse(dracfiles[0])
root = tree.getroot()
print(root.tag)
for child in root:
    print(child.tag, child.attrib)
print("-----------------------------------------")

body = root.find('{http://www.w3.org/1999/xhtml}body')
print(body.tag)
    
print("-----------------------------------------")

for fname in dracfiles[1:]:
    tree2 = ETree.parse(fname)
    root2 = tree2.getroot()
    body2 = root2.find('{http://www.w3.org/1999/xhtml}body')
    for child in body2:
        body.append(child)

print(ETree.tostring(body))
tree.write('dracall.html')

