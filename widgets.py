import os
import tkinter as tk

from destuff import BASE_DIR, config_grids


# -------------------------------------------------------
# -------------------- M E N U B A R --------------------
# -------------------------------------------------------

class Menubar(tk.Menu):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        scripts_dir = self.master.master.settings['scripts-directory']

        self.file_menu = tk.Menu(self, tearoff=0)
        self.file_menu.add_command(label='Restart', command=self.master.restart)
        self.file_menu.add_command(label='Quit', command=self.master.quit)

        self.prepare_menu = tk.Menu(self, tearoff=0)
        self.prepare_menu.add_command(
            label='Set scripts dir', command=self.master.browse_directory
        )

        self.prepare_menu.add_separator()

        self.prepare_menu.add_command(
            label='Prepare files',
            command=lambda: self.master.open_confirmation(
                func=lambda: prepare_files(scripts_dir),
                func_text='Prepare files',
                label='Prepare files for modding?\n\
(only run once unless you permanently restore,\n\
otherwise restore modifications instead) \n\
Extract dcx files after doing this.'
            )
        )

        self.prepare_menu.add_separator()

        self.prepare_menu.add_command(
            label='Reset permanently',
            command=lambda: self.master.open_confirmation(
                func=lambda: reset_permanently(scripts_dir),
                func_text='Reset permanently',
                label='Reset game files to their original state and\n\
permanently delete all modifications.'
            )
        )

        self.prepare_menu.add_command(
            label='Reset temporarily',
            command=lambda: self.master.open_confirmation(
                func=lambda: reset_temporarily(scripts_dir),
                func_text='Reset temporarily',
                label='Reset game files to their original state.\n\
Modifications can be restored.'
            ))

        self.prepare_menu.add_command(
            label='Restore modifications',
            command=lambda: self.master.open_confirmation(
                func=lambda: restore_modifications(scripts_dir),
                func_text='Restore modifications',
                label='Restore game to previously modified state.'
            ))

        self.debug_menu = tk.Menu(self, tearoff=0)
        self.debug_menu.add_command(
            label='Clear console', command=lambda: os.system('cls')
        )

        self.add_cascade(label='File', menu=self.file_menu)
        self.add_cascade(label='Prepare', menu=self.prepare_menu)
        self.add_cascade(label='Debug', menu=self.debug_menu)


#----------------------------------------------------------------
# -------------------- C O N T E X T M E N U --------------------
#----------------------------------------------------------------

class ContextMenu(tk.Menu):
    def __init__(self, master, event, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.event = event
        event = self.event
        click_index = event.widget.curselection()
        functions = event.widget.master.context_functions
        if click_index != -1:
            event.widget.select_clear(0, tk.END)
            event.widget.activate(click_index)
            event.widget.selection_set(first=click_index)
            event.widget.focus_force()
            selection = event.widget.get(event.widget.curselection())

            if functions:
                [self.add_command(**command) for command in functions]

                self.post(event.x_root, event.y_root)


# -----------------------------------------------------------
# -------------------- L I S T B O X E S --------------------
# -----------------------------------------------------------

class ScrollbarListFrame(tk.Frame):
    def __init__(self, master, label='', *args, list_style={}, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        config_grids(self, rows=[0, 1], columns=[1, 0])

        settings = self.master.master.master.settings
        fg = settings['colors']['dark']
        bg = settings['colors']['light']
        font = settings['font']

        self.label = tk.Label(self, bg=bg, fg=fg, font=font, text=label)
        self.label.grid(row=0, column=0)

        self.scrollbar = tk.Scrollbar(self)
        self.scrollbar.grid(row=1, column=1, sticky='ns')

        self.listbox = tk.Listbox(
            self, yscrollcommand=self.scrollbar.set, **list_style,
            exportselection=0
        )
        self.listbox.grid(row=1, column=0, sticky='nsew')

        self.listbox.clicked = -1

        self.listbox.bind('<Button-1>', self.change_selection)
        self.listbox.bind(
            '<Button-3>',
            lambda event: self.change_selection(
                event,
                callback=lambda event: self.master.master.open_context_menu(self.master, event)
            )
        )

        self.context_functions = {}

        self.scrollbar.config(command=self.listbox.yview)


    def change_selection(self, event, callback=lambda *args: None):
        self.clear_selection()
        click_index = event.widget.nearest(event.y_root-event.widget.winfo_rooty())
        event.widget.select_set(click_index)
        event.widget.event_generate("<<ListboxSelect>>")
        callback(event)


    def clear_selection(self):
        self.listbox.select_clear(0, tk.END)


    def clear(self):
        self.listbox.delete(0, tk.END)


    def populate(self):
        for i in range(100):
            self.listbox.insert(tk.END, f'Item {i}')