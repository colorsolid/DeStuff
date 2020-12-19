import os
import tkinter.filedialog
import tkinter as tk

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

def config_grids(widget, rows=[1], columns=[1]):
    [widget.rowconfigure(i, weight=w) for i, w in enumerate(rows)]
    [widget.columnconfigure(i, weight=w) for i, w in enumerate(columns)]

from utils import *
from widgets import *


# -------------------------------------------------------------
# -------------------- M A I N W I N D O W --------------------
# -------------------------------------------------------------

class MainWindow(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master

        settings = self.master.settings
        dir, fg, bg, font, btn, btn_grid = self.get_vars()

        self.config(bg=bg)

        self.master.title('DeStuff')

        self.pack(fill=tk.BOTH, expand=True)

        config_grids(self, rows=[0, 0, 1])

        self.restart_flag = False

        self.build_btn_frame()
        self.build_search_frame()
        self.build_lists_frame()

        self.menu_bar = Menubar(self)
        self.master.config(menu=self.menu_bar)

        self.master.geometry(get_geometry(settings))


    def browse_directory(self):
        directory = tk.filedialog.askdirectory(initialdir = BASE_DIR)
        if os.path.isdir(directory):
            self.master.settings['scripts-directory'] = directory
            save_settings(self.master.settings)


    def quit(self):
        self.cont = False
        close_window(self.master)


    def restart(self):
        self.quit()
        self.restart_flag = True


    def open_context_menu(self, master, event):
        self.context_menu = ContextMenu(master, event, tearoff=0)


    def get_vars(self):
        settings = self.master.settings
        dir = settings['scripts-directory']
        fg = settings['colors']['dark']
        bg = settings['colors']['light']
        font = settings['font']
        btn = {'relief': 'groove', 'height': 2}
        btn_grid = {'sticky': 'nsew'}
        return dir, fg, bg, font, btn, btn_grid


    # -------------------------------------------------------
    # -------------------- B U T T O N S --------------------
    # -------------------------------------------------------

    def build_btn_frame(self):
        dir, fg, bg, font, btn, btn_grid = self.get_vars()
        self.btn_frame = tk.Frame(self, bg=bg, padx=10, pady=10)
        self.btn_frame.grid(row=0, column=0, sticky='nsew')
        config_grids(self.btn_frame, rows=[1, 1, 1])

        self.btn_update_global = tk.Button(
            self.btn_frame, text='Update global files',
            command=lambda: update_global(dir), font=font, **btn
        )
        self.btn_update_global.grid(row=0, column=0, **btn_grid)

        self.msg_rebuild = tk.Label(
            self.btn_frame, text='**Rebuild dcx files before updating sdat files**',
            fg=fg, bg=bg, font='Consolas 11 bold'
        )
        self.msg_rebuild.grid(row=1, column=0, sticky='s')

        self.btn_update_sdat = tk.Button(
            self.btn_frame, text='Update sdat files',
            command=lambda: update_sdat(dir), font=font, **btn
        )
        self.btn_update_sdat.grid(row=2, column=0, **btn_grid)


    # -----------------------------------------------------
    # -------------------- S E A R C H --------------------
    # -----------------------------------------------------

    def build_search_frame(self):
        dir, fg, bg, font, btn, btn_grid = self.get_vars()
        btn = {'relief': 'groove'}
        self.search_frame = tk.Frame(self, bg=bg)
        self.search_frame.grid(
            row=1, column=0, sticky='nsew',
            padx=(10, 10), pady=(10, 10)
        )
        config_grids(self.search_frame, rows=[0, 0, 0], columns=[1, 0])

        self.search_term = ''

        self.search_label = tk.Label(
            self.search_frame, text='Search files for references',
            bg=bg, fg=fg, font=font
        )
        self.search_label.grid(row=0, column=0, columnspan=5)

        self.search_bar = tk.Entry(self.search_frame, justify='center')
        self.search_bar.grid(row=1, column=0, columnspan=5, sticky='nsew')

        self.search_bar.bind('<Return>', self.btn_search_click)

        self.btn_search = tk.Button(
            self.search_frame, text='Search',
            command=self.btn_search_click, font=font, **btn
        )
        self.btn_search.grid(row=1, column=1, sticky='nsew')

        self.var_case_sensitive = tk.IntVar()

        self.checkbox_frame = tk.Frame(self.search_frame)
        self.checkbox_frame.grid(row=2, column=0, columnspan=2)

        self.checkbox_case_sensitive = tk.Checkbutton(
            self.checkbox_frame, text='case sensitive',
            variable=self.var_case_sensitive, bg=bg, fg=fg, font=font,
            command=self.checkbox_click
        )

        self.checkbox_case_sensitive.grid(row=0, column=1, sticky='nsew')

        self.var_regex = tk.IntVar()

        self.checkbox_regex = tk.Checkbutton(
            self.checkbox_frame, text='regex',
            variable=self.var_regex, bg=bg, fg=fg, font=font,
            command=self.checkbox_click
        )

        self.checkbox_regex.grid(row=0, column=2, sticky='nsew')


    def checkbox_click(self):
        self.lb_files_found.listbox.clicked = -1
        self.lb_previous_searches.listbox.clicked = -1
        self.previous_search_click()


    def btn_search_click(self, *args):
        self.search_term = self.search_bar.get()
        if not self.search_term:
            return
        settings = self.master.settings
        search_terms = settings['search-terms']
        listbox = self.lb_previous_searches.listbox
        if self.search_term in search_terms:
            search_terms.remove(self.search_term)
            search_terms.append(self.search_term)
            listbox.delete(0, tk.END)
            [listbox.insert(0, term) for term in search_terms]
        else:
            search_terms.append(self.search_term)
            listbox.insert(0, self.search_term)
        listbox.select_clear(0, tk.END)
        listbox.select_set(0)
        settings['search-terms'] = search_terms
        save_settings(settings)
        self.search(self.search_bar.get())
        self.search_bar.delete(0, tk.END)


    def search(self, text):
        self.found = find(
            self.master.settings['scripts-directory'], text,
            self.var_case_sensitive.get(), self.var_regex.get()
        )
        self.found.reverse()
        self.lb_files_found.clear()
        for result in self.found:
            filename, matches = result
            count = len(matches)
            self.lb_files_found.listbox.insert(0, f' {str(count).ljust(6)} {filename}')


    # ---------------------------------------------------------------
    # -------------------- S E A R C H L I S T S --------------------
    # ---------------------------------------------------------------

    def build_lists_frame(self):
        settings = self.master.settings
        dir, fg, bg, font, btn, btn_grid = self.get_vars()

        list_style = {'font': font, 'relief': 'groove'}

        self.found = []

        self.lists_frame = tk.Frame(self, bg=bg)
        self.lists_frame.grid(row=2, column=0, sticky='nsew')

        config_grids(self.lists_frame, rows=[1, 1], columns=[1, 1])

        self.lb_previous_searches = ScrollbarListFrame(
            self.lists_frame, bg=bg, label='Previous search terms',
            list_style=list_style
        )

        self.lb_previous_searches.grid(row=0, column=0, sticky='nsew')
        self.lb_previous_searches.listbox.bind(
            '<<ListboxSelect>>', self.previous_search_click
        )

        self.lb_previous_searches.listbox.bind(
            '<Delete>', lambda event: remove_search(
                self.lb_previous_searches, settings
            )
        )

        for search_term in settings['search-terms']:
            self.lb_previous_searches.listbox.insert(0, search_term)

        self.lb_previous_searches.context_functions = [
            {
                'label': 'Remove',
                'state': 'normal',
                'command': lambda: remove_search(
                    self.lb_previous_searches,
                    self.master.settings
                )
            }
        ]

        self.lb_files_found = ScrollbarListFrame(
            self.lists_frame, bg=bg, label='Files found',
            list_style=list_style
        )
        self.lb_files_found.grid(row=0, column=1, sticky='nsew')
        self.lb_files_found.context_functions = [
            {
                'label': 'Open file',
                'state': 'normal',
                'command': lambda : open_file(
                    dir,
                    self.lb_files_found.listbox.get(
                        self.lb_files_found.listbox.curselection()[0]
                    )
                )
            }
        ]

        self.lb_files_found.listbox.bind(
            '<<ListboxSelect>>', self.update_context
        )

        self.lb_file_context = ScrollbarListFrame(
            self.lists_frame, bg=bg, label='File context',
            list_style=list_style
        )

        self.lb_file_context.grid(
            row=1, column=0, columnspan=2, sticky='nsew'
        )


    def previous_search_click(self, *args):
        try:
            lb = self.lb_previous_searches.listbox
            if lb.clicked != lb.curselection()[0]:
                lb.clicked = lb.curselection()[0]
                index = lb.curselection()[0]
                search_term = lb.get(index)
                self.search(search_term)
                self.lb_files_found.listbox.clicked = -1
                self.lb_file_context.clear()
        except IndexError:
            pass # triggers when any listbox is clicked


    def update_context(self, event):
        lb = self.lb_files_found.listbox
        if lb.clicked != lb.curselection()[0]:
            lb.clicked = lb.curselection()[0]
            filename = lb.get(lb.clicked).split()[1]
            if self.found:
                self.lb_file_context.listbox.delete(0, tk.END)
                for result in self.found:
                    result_filename, matches = result
                    if result_filename == filename:
                        for match in matches:
                            i, context = match
                            text = f'{str(i).ljust(5)} {context}'
                            self.lb_file_context.listbox.insert(0, text)


    # -------------------------------------------------------------------
    # -------------------- C O N F I R M A T I O N S --------------------
    # -------------------------------------------------------------------

    def open_confirmation(
            self, func=None, func_text='ok',
            func2=None, func2_text='func2 text', label=''):
        if func is None:
            func = self.close_confirmation
        if hasattr(self, 'window_confirmation') \
        and self.window_confirmation is not None:
            self.window_confirmation.destroy()
        w = 400
        h = 100
        settings = self.master.settings
        bg = settings['colors']['light']
        fg = settings['colors']['dark']
        self.window_confirmation = tk.Toplevel(self.master, bg=bg)
        self.window_confirmation.title('DeStuff - Confirmation')
        window_settings = self.master.settings['window']
        x = int(self.master.winfo_x() + (self.master.winfo_width() / 2) - (w / 2))
        y = int(self.master.winfo_y() + (self.master.winfo_height() / 2) - (h / 2))
        self.window_confirmation.geometry(f'{w}x{h}+{x}+{y}')
        config_grids(self.window_confirmation, rows=[1, 1], columns=[1, 1])

        self.label = tk.Label(self.window_confirmation, text=f'{label}', bg=bg, fg=fg)
        self.label.grid(row=0, column=0, columnspan=2, sticky='nsew')

        self.func_button = tk.Button(
            self.window_confirmation, text=func_text,
            command=lambda: self.func_plus(func), width=6, bg=bg, fg=fg
        )
        self.func_button.grid(row=1, column=0, sticky='nsew')
        self.func_button.command = lambda: self.func_plus(func)

        if func is not self.close_confirmation:
            self.cancel_button = tk.Button(
                self.window_confirmation, text='Cancel',
                command=self.close_confirmation, bg=bg, fg=fg
            )
            self.cancel_button.grid(row=1, column=1, sticky='nsew')

        if func2 is not None:
            config_grids(self.window_confirmation, rows=[1, 1], columns=[1, 1, 1])
            self.func2_button = tk.Button(
                self.window_confirmation, text='cancel',
                command=self.close_confirmation, bg=bg, fg=fg
            )
            self.cancel_button.grid(row=1, column=2, sticky='nsew')

        if func is self.close_confirmation and func2 is None:
            config_grids(self.window_confirmation, rows=[1, 1])

        self.window_confirmation.protocol('WM_DELETE_WINDOW', self.close_confirmation)


    def func_plus(self, func):
        self.close_confirmation()
        func()


    def close_confirmation(self):
        self.window_confirmation.destroy()
        self.window_confirmation = None


# -----------------------------------------------
# -------------------- R U N --------------------
# -----------------------------------------------

def main():
    root = tk.Tk()
    root.settings = load_settings()
    root.protocol('WM_DELETE_WINDOW', lambda: close_window(root))
    window = MainWindow(root)
    root.mainloop()

    if window.restart_flag:
        os.system(__file__)


if __name__ == '__main__':
    main()
