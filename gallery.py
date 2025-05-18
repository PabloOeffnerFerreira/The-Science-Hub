import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os, json, shutil, difflib
from tkinterdnd2 import DND_FILES, TkinterDnD

IMAGE_DIRS = ["images", "results"]
META_PATH = "gallery_meta.json"
IMG_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif")

def load_gallery_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_gallery_meta(meta):
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

class GalleryTool:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Gallery")
        self.window.geometry("1000x700")
        self.meta = load_gallery_meta()
        self.images = []
        self.search_var = tk.StringVar()
        self.tag_filter = tk.StringVar()
        self.fav_only = tk.BooleanVar(value=False)
        self.setup_ui()
        self.load_images()

    def setup_ui(self):
        top = tk.Frame(self.window)
        top.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(top, text="Search:").pack(side=tk.LEFT)
        tk.Entry(top, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)
        tk.Label(top, text="Tag:").pack(side=tk.LEFT)
        tk.Entry(top, textvariable=self.tag_filter, width=12).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(top, text="Favorites Only", variable=self.fav_only).pack(side=tk.LEFT, padx=8)
        tk.Button(top, text="Reload", command=self.load_images).pack(side=tk.RIGHT)
        self.search_var.trace_add("write", lambda *_: self.display_images())
        self.tag_filter.trace_add("write", lambda *_: self.display_images())
        self.fav_only.trace_add("write", lambda *_: self.display_images())
        dnd_label = tk.Label(top, text="Drag images here to import", relief="groove", width=22, bg="#ececec")
        dnd_label.pack(side=tk.LEFT, padx=12)

        def handle_drop(event):
            # event.data is a string: '{/path/one.png} {/path/two.jpg}'
            file_list = self.window.tk.splitlist(event.data)
            for fpath in file_list:
                fname = os.path.basename(fpath)
                dest = os.path.join("images", fname)
                if os.path.exists(dest):
                    # Optionally, auto-rename here (append number or use timestamp)
                    name, ext = os.path.splitext(fname)
                    dest = os.path.join("images", f"{name}_imported{ext}")
                shutil.copy(fpath, dest)
            self.load_images()

        dnd_label.drop_target_register(DND_FILES)
        dnd_label.dnd_bind('<<Drop>>', handle_drop)

        # Scrollable area for images
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(frame)
        self.scrollbar = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Correct: nested but at the right level
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<Enter>", lambda e: self.canvas.bind_all("<MouseWheel>", _on_mousewheel))
        self.canvas.bind("<Leave>", lambda e: self.canvas.unbind_all("<MouseWheel>"))
        
        tk.Button(top, text="Import Image", command=self.import_image).pack(side=tk.RIGHT)

    def load_images(self):
        self.images = []
        for folder in IMAGE_DIRS:
            if not os.path.exists(folder): continue
            for fname in os.listdir(folder):
                if fname.lower().endswith(IMG_EXTS):
                    self.images.append((folder, fname))
        self.display_images()

    def import_image(self):
        filetypes = [("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        filepath = filedialog.askopenfilename(title="Select Image", filetypes=filetypes)
        if not filepath:
            return
        fname = os.path.basename(filepath)
        dest = os.path.join("images", fname)
        if os.path.exists(dest):
            name, ext = os.path.splitext(fname)
            dest = os.path.join("images", f"{name}_imported{ext}")
        shutil.copy(filepath, dest)
        self.load_images()

    def display_images(self):
        # Clear current thumbnails
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        query = self.search_var.get().lower()
        tag = self.tag_filter.get().lower()
        fav_only = self.fav_only.get()

        filtered = []
        for folder, fname in self.images:
            meta = self.meta.get(fname, {})
            tags = meta.get("tags", [])
            is_fav = meta.get("favorite", False)
            if query and query not in fname.lower():
                continue
            if tag:
                tag_matches = [t for t in tags if tag in t.lower()]
                # fallback: fuzzy match if substring didn't work
                if not tag_matches and tags:
                    tag_matches = difflib.get_close_matches(tag, [t.lower() for t in tags], n=1, cutoff=0.6)
                if not tag_matches:
                    continue
            if fav_only and not is_fav:
                continue
            filtered.append((folder, fname, meta))

        for folder, fname, meta in filtered:
            try:
                frame = tk.Frame(self.scrollable_frame, relief=tk.RIDGE, bd=2, padx=4, pady=4)
                frame.pack(fill="x", padx=10, pady=6)
                path = os.path.join(folder, fname)
                img = Image.open(path)
                img.thumbnail((120, 120))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=img_tk)
                img_label.image = img_tk
                img_label.pack(side="left")
                info = tk.Frame(frame)
                info.pack(side="left", fill="both", expand=True)
                tk.Label(info, text=fname, font=("Helvetica", 10, "bold")).pack(anchor="w")
                tk.Label(info, text=", ".join(meta.get("tags", [])), fg="gray").pack(anchor="w")
                fav_btn = tk.Button(info, text="★" if meta.get("favorite", False) else "☆",
                                   command=lambda n=fname: self.toggle_favorite(n))
                fav_btn.pack(anchor="e")
                tk.Button(info, text="Rename", command=lambda f=fname, p=path: self.rename_image(f, p)).pack(anchor="e")
                tk.Button(info, text="Delete", command=lambda f=fname, p=path: self.delete_image(f, p)).pack(anchor="e")
                tk.Button(info, text="Tag", command=lambda f=fname: self.edit_tags(f)).pack(anchor="e")
            except Exception as e:
                tk.Label(self.scrollable_frame, text=f"Error: {e}", fg="red").pack()

    def toggle_favorite(self, fname):
        meta = self.meta.setdefault(fname, {})
        meta["favorite"] = not meta.get("favorite", False)
        save_gallery_meta(self.meta)
        self.display_images()

    def rename_image(self, fname, path):
        top = tk.Toplevel(self.window)
        top.title(f"Rename: {fname}")
        new_var = tk.StringVar(value=fname)
        tk.Label(top, text="New name (with extension):").pack(padx=10, pady=(10,0))
        entry = tk.Entry(top, textvariable=new_var, width=40)
        entry.pack(padx=10, pady=5)
        entry.focus_set()
        def do_rename(event=None):
            new_name = new_var.get().strip()
            if not new_name or new_name == fname:
                top.destroy()
                return
            new_path = os.path.join(os.path.dirname(path), new_name)
            try:
                os.rename(path, new_path)
                if fname in self.meta:
                    self.meta[new_name] = self.meta.pop(fname)
                save_gallery_meta(self.meta)
                top.destroy()
                self.load_images()
            except Exception as e:
                messagebox.showerror("Rename failed", f"Could not rename: {e}")
        tk.Button(top, text="Rename", command=do_rename).pack(pady=10)
        entry.bind("<Return>", do_rename)


    def delete_image(self, fname, path):
        # Ellipsize the filename if it's too long for the label
        def ellipsize_filename(name, maxlen=30):
            if len(name) <= maxlen:
                return name
            return name[:14] + "..." + name[-13:]

        def confirm_delete():
            try:
                os.remove(path)
                if fname in self.meta:
                    del self.meta[fname]
                save_gallery_meta(self.meta)
                conf_win.destroy()
                self.load_images()
            except Exception as e:
                conf_win.destroy()
                # Optionally show error inline

        conf_win = tk.Toplevel(self.window)
        conf_win.title("Confirm Delete")
        conf_win.geometry("410x130")
        short_name = ellipsize_filename(fname)
        msg = tk.Label(conf_win, text=f"Delete '{short_name}'?", font=("Helvetica", 11, "bold"))
        msg.pack(pady=(18, 0))

        # Tooltip for full name on hover
        def show_full(event):
            tip = tk.Toplevel(conf_win)
            tip.wm_overrideredirect(True)
            tip.geometry(f"+{event.x_root+12}+{event.y_root+12}")
            tip_label = tk.Label(tip, text=fname, font=("Helvetica", 10), bg="yellow", relief="solid", borderwidth=1)
            tip_label.pack()
            msg.tooltip = tip
        def hide_full(event):
            if hasattr(msg, "tooltip"):
                msg.tooltip.destroy()
                del msg.tooltip

        msg.bind("<Enter>", show_full)
        msg.bind("<Leave>", hide_full)

        btn_row = tk.Frame(conf_win)
        btn_row.pack(pady=20)
        tk.Button(btn_row, text="Delete", command=confirm_delete, fg="red", width=8).pack(side="left", padx=14)
        tk.Button(btn_row, text="Cancel", command=conf_win.destroy, width=8).pack(side="left", padx=14)
        conf_win.transient(self.window)
        conf_win.grab_set()
        conf_win.focus_set()
        conf_win.protocol("WM_DELETE_WINDOW", conf_win.destroy)


    def edit_tags(self, fname):
        top = tk.Toplevel(self.window)
        top.title(f"Edit Tags: {fname}")
        var = tk.StringVar(value=", ".join(self.meta.get(fname, {}).get("tags", [])))
        tk.Entry(top, textvariable=var, width=40).pack(padx=10, pady=10)
        def save_tags():
            tags = [t.strip() for t in var.get().split(",") if t.strip()]
            self.meta.setdefault(fname, {})["tags"] = tags
            save_gallery_meta(self.meta)
            top.destroy()
            self.display_images()
        tk.Button(top, text="Save", command=save_tags).pack(pady=10)

# Hook it up somewhere in your main menu/tool launcher as "Gallery"
