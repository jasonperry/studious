# Studious Reader
A fixed-width scrolling ePub reader.

# Apologia
Most ePub reader applications lay out the book in discrete pages in an
attempt to simulate the experience of reading a physical paper
book. However, they also reflow the whole book any time you resize the
window, changing all the page numbers and negating a primary purpose of
having discrete pages, which is to help orient yourself in the book.

However, layout is a hard problem; so I have instead hacked together a
UI which renders the whole book in one continuous scrolling pane, and
I made the width of the text pane fixed. This way, you can see in the
scrollbar your relative position in the book, and the lines won't "jump
around" when you resize the window. Ta-da!

# Current and Planned Features
Pretty much just opening and scrolling through a book, and a table of
contents on the left.

There is a "notes pane" on the right but for now it doesn't save
anything.

I also need to add font and text customization features. You can
currently use Ctrl-plus and Ctrl-minus to change the text size.

Nonetheless, I already use this myself for reading nonfiction books. The
non-jumpy layout does seem to help me concentrate.

# Building and Running
Download the source, then type `python -m build` in the top
folder. Assuming that succeeds, type `pip install
dist/studious-<ver>-py3-none-any.whl`. This should put the `studious`
command on your PATH.

Issues are welcome, but no PRs please, I'm very possessive :)
