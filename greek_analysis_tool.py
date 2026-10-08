import argparse
from tkinter import *
from tkinter import ttk

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('filepaths', metavar='F', type=str, nargs='+', help='htm files to process')
    args = parser.parse_args()

    # This holds each word in the passage, containing dicts of each entry
    word_list = []
    word_fields_list = ["Book", "Chapter", "Verse", "Strongs Num", "Strongs Translation", "English Translit", "Greek", "Translation", "Grammar", "Grammar (Full)"]
    field_sizes = [100, 60, 60, 100, 150, 150, 150, 150, 100, 450]

    for filename in args.filepaths:
        print(f"Adding {filename}")
        file = open(filename, "r", encoding='utf-8')

        # Read in file
        content = file.read()
        file.close()

        # Separate out chunks of page
        content_body = content.split("<body>")
        body_section = []

        # Find the page chunk with "Interlinear Bible" and split to find start of text
        for body in content_body:
            if "Interlinear Bible" in body:
                body_section = body.split("table class=\"tablefloat\"")

        # Find the book and chapter using this sketchy split chain
        for init_part in body_section[0].split(" "):
            if ("src" in init_part):
                book_chapter_list = init_part.split("%20Interlinear")[0].split("src=\"")[1].split("%20")

        book = ""
        for book_part in book_chapter_list[0:-1]:
            book += f"{book_part} "
        chapter = book_chapter_list[-1]

        # Go word by word and separate out each part into the list of dicts
        # Track current verse by updating this var when reaching each new verse
        cur_verse = 1
        for elements in body_section:
            element_list = elements.split("><")
            element_dict = {}
            element_dict[word_fields_list[0]] = book
            element_dict[word_fields_list[1]] = chapter
            for element in element_list:

                # Updated when verse increments
                if ("&nbsp;&nbsp;&nbsp;" in element):
                    cur_verse = element.split('>')[-1].split("&nbsp;&nbsp;&nbsp;")[0]
                element_dict[word_fields_list[2]] = cur_verse

                if ("Strong's Greek" in element):
                    element_dict[word_fields_list[3]] = element.split('>')[-1].split('<')[0]
                    element_dict[word_fields_list[4]] = element.split('>')[-2].split(' ')[-1].split("\"")[0]
                if (("/greek/" in element) and ("Greek" not in element)):
                    element_dict[word_fields_list[5]] = element.split('>')[-1].split('<')[0]
                if ("class=\"greek" in element):
                    element_dict[word_fields_list[6]] = element.split('>')[-1].split('<')[0]
                if ("class=\"eng" in element):
                    element_dict[word_fields_list[7]] = element.split('>')[-1].split('<')[0].replace("&nbsp;"," ")
                if ("grammar" in element):
                    element_dict[word_fields_list[8]] = element.split('>')[-1].split('<')[0]
                    element_dict[word_fields_list[9]] = element.split('"')[-2]

            if element_dict != {}:
                word_list.append(element_dict)

    # Create a display of the generated info using tkinter
    # https://pythonguides.com/python-tkinter-table-tutorial/
    root = Tk()
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
        background="#0a1b2e", foreground="white")
    style.map("Treeview", background=[("selected", "#306998")])

    # Search bar
    top = ttk.Frame(root, padding=(10, 10, 10, 0))
    top.pack(fill="x")
    ttk.Label(top, text="Search:").pack(side="left")

    # Create search
    search = StringVar()
    ttk.Entry(top, textvariable=search, width=10).pack(side="left")

    ttk.Label(top, text="Search Category:").pack(side="left")

    # Combobox
    search_word_field = StringVar()
    cb = ttk.Combobox(top, textvariable=search_word_field, values=word_fields_list)
    cb.pack(side="left")
    cb.set(word_fields_list[4])

    # Use the generated dict's keys to create the column titles
    columns = (word_fields_list)
    table = ttk.Treeview(root, columns=columns, show="headings", height=20)
    for col, width in zip(columns, field_sizes):
        table.heading(col, text=col.title())
        table.column(col, width=width, anchor="w")

    # Search function
    def refresh(*args):
        table.delete(*table.get_children())
        text = search.get().lower()

        # Currently selected word field from combobox created above
        cur_search_word_field = cb.get()

        # Go word by word, checking the field chosen for the text string.
        for w_i, word_dict in enumerate(word_list):
            try:
                if text in word_dict[cur_search_word_field].lower():
                    word_row = []
                    for word_key in word_dict.keys():
                        word_row.append(word_dict[word_key])
                    table.insert("", "end", values=word_row)
            except:
                print(f"Couldn't find a valid dict entry at list entry {w_i}")

    table.pack(padx=10, pady=10)

    search.trace_add("write", refresh) # run on every key press
    refresh()
    root.mainloop()

    return

if __name__ == "__main__":
    main()