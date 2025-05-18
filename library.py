import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import shutil
from PIL import Image, ImageTk

LIBRARY_DIR = "library_entries"  # or whatever you're using for the JSONs
IMAGE_DIR = "images"  # relative to your root project folder

import re

def sanitize_filename(name):
    name = name.replace(" ", "_").lower()
    return re.sub(r'[\\/*?:"<>|]', "", name)

class ScienceLibrary:
    def __init__(self, master):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Science Library")
        self.window.geometry("1000x700")
        self.entries = []

        self.search_var = tk.StringVar()
        self.tag_filter = tk.StringVar()
        self.sort_mode = tk.StringVar(value="A-Z")
        self.favorites_only = tk.BooleanVar(value=False)

        self.setup_ui()
        self.load_entries()

        self.window.lift()
        self.window.attributes("-topmost", True)
        self.window.after(100, lambda: self.window.attributes("-topmost", False))

    def pick_from_gallery(self, image_path_var):
                win = tk.Toplevel(self.window)
                win.title("Select Image from Gallery")
                win.geometry("560x410")

                search_var = tk.StringVar()
                tk.Label(win, text="Search:").pack(anchor="w", padx=12, pady=(10, 0))
                search_entry = tk.Entry(win, textvariable=search_var, width=28)
                search_entry.pack(anchor="w", padx=12, pady=(0, 10))

                frame = tk.Frame(win)
                frame.pack(fill="both", expand=True)
                canvas = tk.Canvas(frame)
                scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
                grid = tk.Frame(canvas)

                grid.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                canvas.create_window((0, 0), window=grid, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                def load_images():
                    # Load images from both images and results
                    files = []
                    for folder in ["images", "results"]:
                        if os.path.exists(folder):
                            for fname in os.listdir(folder):
                                if fname.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                                    files.append((folder, fname))
                    # Filter by search
                    q = search_var.get().strip().lower()
                    if q:
                        files = [f for f in files if q in f[1].lower()]
                    # Clear grid
                    for w in grid.winfo_children():
                        w.destroy()
                    # Show thumbnails in grid
                    row, col = 0, 0
                    for folder, fname in files:
                        try:
                            path = os.path.join(folder, fname)
                            img = Image.open(path)
                            img.thumbnail((72, 72))
                            img_tk = ImageTk.PhotoImage(img)
                            btn = tk.Button(grid, image=img_tk, width=76, height=76,
                                            command=lambda f=fname, d=folder: select_image(d, f))
                            btn.image = img_tk
                            btn.grid(row=row, column=col, padx=4, pady=4)
                            # Optional: tooltip for filename
                            btn.bind("<Enter>", lambda e, fn=fname: win.title(fn))
                            btn.bind("<Leave>", lambda e: win.title("Select Image from Gallery"))
                            col += 1
                            if col >= 6:
                                col = 0
                                row += 1
                        except Exception as e:
                            continue

                def select_image(folder, fname):
                    # Use relative path if from images/, otherwise include results/
                    if folder == "images":
                        image_path_var.set(fname)
                    else:
                        image_path_var.set(os.path.join(folder, fname))
                    win.destroy()

                search_var.trace_add("write", lambda *args: load_images())
                load_images()


    def setup_ui(self):
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(top_frame, text="Search:").pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)
        tk.Label(top_frame, text="Tag:").pack(side=tk.LEFT)
        tk.Entry(top_frame, textvariable=self.tag_filter, width=20).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(top_frame, text="Favorites Only", variable=self.favorites_only).pack(side=tk.LEFT, padx=10)

        tk.Label(top_frame, text="Sort by:").pack(side=tk.LEFT, padx=(10, 0))

        sort_options = ["A-Z", "Z-A", "Recent", "Favorites"]
        sort_dropdown = ttk.Combobox(top_frame, textvariable=self.sort_mode, values=sort_options, width=12, state="readonly")
        sort_dropdown.pack(side=tk.LEFT)
        sort_dropdown.bind("<<ComboboxSelected>>", lambda e: self.display_entries())

        tk.Button(top_frame, text="Add Entry", command=self.add_entry).pack(side=tk.RIGHT)
        tk.Button(top_frame, text="Import Set", command=self.import_multiple_entries).pack(side=tk.RIGHT, padx=5)
        tk.Button(top_frame, text="Export All", command=self.export_all_entries).pack(side=tk.RIGHT, padx=5)

        self.search_var.trace_add("write", lambda *args: self.display_entries())
        self.tag_filter.trace_add("write", lambda *args: self.display_entries())
        self.favorites_only.trace_add("write", lambda *args: self.display_entries())
        # Scrollable canvas setup
        canvas_frame = tk.Frame(self.window)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: (
                canvas.configure(scrollregion=canvas.bbox("all")),
                canvas.itemconfig("entry_frame", width=canvas.winfo_width())
            )
        )


        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", tags="entry_frame")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.recent_frame = tk.Frame(self.window)
        self.recent_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        self.entry_list_frame = scrollable_frame

        # FIXED: Mousewheel handler inside setup_ui
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))


    def display_recent_entries(self):
        for widget in self.recent_frame.winfo_children():
            widget.destroy()

        if not hasattr(self, "recent_entries") or not self.recent_entries:
            return

        tk.Label(self.recent_frame, text="Recently Viewed:", font=("Helvetica", 10, "bold")).pack(anchor="w")

        for title in self.recent_entries:
            btn = tk.Button(self.recent_frame, text=title, relief=tk.FLAT, fg="blue", cursor="hand2")
            btn.pack(side="left", padx=4)
            btn.bind("<Button-1>", lambda e, t=title: self.reopen_recent_entry(t))
    def reopen_recent_entry(self, title):
        entry = self.find_entry_by_title(title)
        if entry:
            self.view_entry(entry)

    def load_entries(self):
        self.entries = []
        for widget in self.entry_list_frame.winfo_children():
            widget.destroy()

        if not os.path.exists(LIBRARY_DIR):
            os.makedirs(LIBRARY_DIR)

        files = [f for f in os.listdir(LIBRARY_DIR) if f.endswith(".json")]
        for file in files:
            with open(os.path.join(LIBRARY_DIR, file), "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    self.entries.append(data)
                except Exception as e:
                    print(f"Error reading {file}: {e}")

        self.display_entries()
        self.display_recent_entries()

    def view_entry(self, entry):
        viewer = tk.Toplevel(self.window)
        self.track_recent_entry(entry.get("title", ""))
        viewer.title(entry.get("title", "Untitled"))
        viewer.geometry("600x850")

        tk.Label(viewer, text=entry.get("title", ""), font=("Helvetica", 14, "bold")).pack(pady=10)
        tk.Label(viewer, text="Formula: " + entry.get("formula", ""), font=("Helvetica", 11)).pack(pady=5)
        tk.Label(viewer, text="Tags: " + ", ".join(entry.get("tags", [])), fg="gray").pack()

        if entry.get("favorite"):
            tk.Label(viewer, text="★ Favorite", fg="gold").pack(pady=5)

        desc = entry.get("description", "")
        tk.Label(viewer, text="Description:", font=("Helvetica", 10, "bold")).pack(anchor="w", padx=10, pady=(10, 0))
        desc_frame = tk.Frame(viewer)
        desc_frame.pack(padx=10, pady=(5, 10), fill="both", expand=True)

        desc_box = tk.Text(desc_frame, wrap="word", font=("Helvetica", 10))
        desc_box.insert("1.0", desc)
        desc_box.config(state="disabled")
        desc_box.pack(fill="both", expand=True)


        img_file = entry.get("image", "").strip()
        if img_file:
            full_path = os.path.join(IMAGE_DIR, img_file)
            if img_file:
                full_path = os.path.join(IMAGE_DIR, img_file)
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(full_path)
                    img.thumbnail((400, 300))
                    img_tk = ImageTk.PhotoImage(img)
                    img_label = tk.Label(viewer, image=img_tk)
                    img_label.image = img_tk
                    img_label.pack(pady=10)
                except Exception as e:
                    tk.Label(viewer, text=f"Error loading image: {e}", fg="red").pack()


        btn_frame = tk.Frame(viewer)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Edit", command=lambda: (viewer.destroy(), self.edit_entry(entry))).pack(side="left", padx=10)

        def delete():
            confirm = messagebox.askyesno("Delete Entry", f"Delete entry '{entry['title']}'?")
            if not confirm:
                return
            try:
                filename = entry['title'].replace(" ", "_").lower() + ".json"
                os.remove(os.path.join(LIBRARY_DIR, filename))
                messagebox.showinfo("Deleted", "Entry deleted.")
                self.window.lift()
                self.window.attributes("-topmost", True)
                self.window.after(100, lambda: self.window.attributes("-topmost", False))

                viewer.destroy()
                self.load_entries()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete: {e}")

        tk.Button(btn_frame, text="Delete", command=delete).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Duplicate", command=lambda: (viewer.destroy(), self.duplicate_entry(entry))).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Export PDF", command=lambda: self.export_entry_as_pdf(entry)).pack(side="left", padx=10)

    def add_entry(self):
        self.edit_entry(None)

    def edit_entry(self, entry):
        editor = tk.Toplevel(self.window)
        editor.title("Edit Entry" if entry else "Add Entry")
        editor.geometry("600x600")

        # Fields
        title_var = tk.StringVar(value=entry.get("title", "") if entry else "")
        formula_var = tk.StringVar(value=entry.get("formula", "") if entry else "")
        tags_var = tk.StringVar(value=", ".join(entry.get("tags", [])) if entry else "")
        favorite_var = tk.BooleanVar(value=entry.get("favorite", False) if entry else False)
        description_text = tk.Text(editor, height=6, wrap="word")
        image_path_var = tk.StringVar(value=entry.get("image", "") if entry else "")

        if entry:
            description_text.insert("1.0", entry.get("description", ""))

        # Layout
        tk.Label(editor, text="Title:").pack(anchor="w", padx=10)
        tk.Entry(editor, textvariable=title_var, width=50).pack(padx=10)

        tk.Label(editor, text="Formula:").pack(anchor="w", padx=10, pady=(10,0))
        tk.Entry(editor, textvariable=formula_var, width=50).pack(padx=10)

        tk.Label(editor, text="Tags (comma-separated):").pack(anchor="w", padx=10, pady=(10,0))
        tag_entry = tk.Entry(editor, textvariable=tags_var, width=50)
        tag_entry.pack(padx=10)

        def autocomplete_tags(event):
            typed = tags_var.get().split(",")[-1].strip().lower()
            if not typed:
                return
            matches = [t for t in self.get_all_tags() if t.startswith(typed)]
            if matches:
                tag_entry.delete(0, tk.END)
                existing = ", ".join([t.strip() for t in tags_var.get().split(",")[:-1]])
                combined = (existing + ", " if existing else "") + matches[0]
                tag_entry.insert(0, combined)

        tag_entry.bind("<Tab>", autocomplete_tags)


        tk.Checkbutton(editor, text="Favorite", variable=favorite_var).pack(anchor="w", padx=10, pady=(10,0))

        tk.Label(editor, text="Description:").pack(anchor="w", padx=10, pady=(10,0))
        description_text.pack(padx=10, fill=tk.X)

        img_field = tk.Frame(editor)
        img_field.pack(anchor="w", padx=10, pady=(10,0), fill="x")
        tk.Label(img_field, text="Image Filename (relative to /images):").pack(side="left")
        img_entry = tk.Entry(img_field, textvariable=image_path_var, width=36)
        img_entry.pack(side="left", padx=(8, 0))

        pick_btn = tk.Button(img_field, text="Pick from Gallery", command=lambda: self.pick_from_gallery(image_path_var))
        pick_btn.pack(side="left", padx=8)


        def save():
            new_entry = {
                "title": title_var.get().strip(),
                "formula": formula_var.get().strip(),
                "tags": [t.strip() for t in tags_var.get().split(",") if t.strip()],
                "favorite": favorite_var.get(),
                "description": description_text.get("1.0", "end").strip(),
                "image": image_path_var.get().strip()
            }

            if not new_entry["title"]:
                messagebox.showwarning("Missing Title", "Title is required.")
                return

            filename = new_entry["title"].replace(" ", "_").lower() + ".json"
            filepath = os.path.join(LIBRARY_DIR, filename)

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(new_entry, f, indent=2)
                editor.destroy()
                self.load_entries()
                self.window.lift()
                self.window.attributes("-topmost", True)
                self.window.after(100, lambda: self.window.attributes("-topmost", False))

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save entry:\n{e}")

        tk.Button(editor, text="Save Entry", command=save).pack(pady=20)

    def import_multiple_entries(self):
        filepath = filedialog.askopenfilename(
            title="Import Entry Set",
            filetypes=[("JSON Files", "*.json")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                messagebox.showwarning("Invalid Format", "This file does not contain a list of entries.")
                return

            for entry in data:
                title = entry.get("title", "").strip()
                if not title:
                    continue  # Skip invalid ones

                filename = title.replace(" ", "_").lower() + ".json"
                out_path = os.path.join(LIBRARY_DIR, filename)

                with open(out_path, "w", encoding="utf-8") as out_file:
                    json.dump(entry, out_file, indent=2)

            messagebox.showinfo("Import Complete", f"{len(data)} entries imported.")
            self.load_entries()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import entries:\n{e}")
    def export_all_entries(self):
        filepath = filedialog.asksaveasfilename(
            title="Export All Entries",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, indent=2)
            messagebox.showinfo("Export Complete", f"{len(self.entries)} entries exported to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not save export:\n{e}")
    def save_single_entry(self, entry):
        title = entry.get("title", "").strip()
        if not title:
            return
        filename = title.replace(" ", "_").lower() + ".json"
        filepath = os.path.join(LIBRARY_DIR, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(entry, f, indent=2)
        except Exception as e:
            print(f"Failed to save entry '{title}': {e}")

    def display_entries(self):
        for widget in self.entry_list_frame.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        tag = self.tag_filter.get().lower()
        fav_only = self.favorites_only.get()

        filtered = []
        for entry in self.entries:
            try:
                title = entry.get("title", "")
                tags = [t.lower() for t in entry.get("tags", [])]
                is_fav = entry.get("favorite", False)

                if query and query not in title.lower():
                    continue
                if tag and not any(tag in t for t in tags):
                    continue
                if fav_only and not is_fav:
                    continue

                filtered.append(entry)
            except Exception as e:
                print(f"Error filtering entry: {e}")


        filtered = self.apply_sorting(filtered)


        for entry in filtered:
            try:
                frame = tk.Frame(self.entry_list_frame, relief=tk.RIDGE, bd=2, padx=5, pady=5)
                frame.pack(fill="x", expand=True, padx=10, pady=4)

                top_row = tk.Frame(frame)
                top_row.pack(fill="x")

                tk.Button(top_row, text="View Compact", command=lambda e=entry: self.view_entry_compact(e)).pack(side="right")

                label = tk.Label(top_row, text=entry.get("title", ""), font=("Helvetica", 12, "bold"), fg="blue", cursor="hand2")
                label.pack(side="left", anchor="w")
                label.bind("<Button-1>", lambda e, data=entry: self.view_entry(data))

                def toggle_fav(e=entry):
                    e["favorite"] = not e.get("favorite", False)
                    self.save_single_entry(e)
                    self.load_entries()

                fav_btn = tk.Button(top_row, text="★" if entry.get("favorite", False) else "☆", width=2, command=toggle_fav)
                fav_btn.pack(side="right")

                tk.Label(frame, text=", ".join(entry.get("tags", [])), fg="gray").pack(anchor="w")
            except Exception as e:
                print(f"Error displaying entry: {e}")

    # This script defines a collection of method stubs and full implementations for
    # enhancing the ScienceLibrary class with features like duplication, tag autocomplete, sorting, etc.
    # Each function assumes it will be added inside the ScienceLibrary class.

    # You can append this entire block inside the ScienceLibrary class definition.
    # 1. Duplicate Entry
    def duplicate_entry(self, entry):
        new_entry = entry.copy()
        new_entry["title"] = entry["title"] + " Copy"
        self.edit_entry(new_entry)

    # 2. Tag Autocomplete helper - used inside edit_entry
    def get_all_tags(self):
        tag_set = set()
        for entry in self.entries:
            for tag in entry.get("tags", []):
                tag_set.add(tag.lower())
        return sorted(tag_set)

    # 3. Sorting options
    def apply_sorting(self, entries):
        mode = self.sort_mode.get()
        if mode == "A-Z":
            return sorted(entries, key=lambda e: e.get("title", "").lower())
        elif mode == "Z-A":
            return sorted(entries, key=lambda e: e.get("title", "").lower(), reverse=True)
        elif mode == "Recent":
            return sorted(entries, key=lambda e: e.get("modified", ""), reverse=True)
        elif mode == "Favorites":
            return sorted(entries, key=lambda e: not e.get("favorite", False))
        return entries

    # 4. Recent entries tracking
    def track_recent_entry(self, title):
        if not hasattr(self, 'recent_entries'):
            self.recent_entries = []
        if title in self.recent_entries:
            self.recent_entries.remove(title)
        self.recent_entries.insert(0, title)
        self.recent_entries = self.recent_entries[:5]

    # 5. Internal link resolution (basic version)
    def find_entry_by_title(self, title):
        for entry in self.entries:
            if entry.get("title", "").lower() == title.lower():
                return entry
        return None

    # 6. Open image with picker
    def pick_image_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        if filepath:
            dest = os.path.join(IMAGE_DIR, os.path.basename(filepath))
            try:
                shutil.copy(filepath, dest)
                return os.path.basename(dest)
            except Exception as e:
                print(f"Failed to copy image: {e}")
        return ""

    # 7. Multi-image support placeholder (not yet in UI)
    def get_entry_images(self, entry):
        imgs = entry.get("images", [])
        if isinstance(imgs, str):
            return [imgs]
        return imgs

    # 8. Export to PDF (basic placeholder using reportlab if wanted)
    def export_entry_as_pdf(self, entry):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4

            filename = entry.get("title", "entry").replace(" ", "_") + ".pdf"
            filepath = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile=filename)
            if not filepath:
                return

            c = canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica", 14)
            c.drawString(50, height - 50, entry.get("title", "Untitled"))
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 80, f"Formula: {entry.get('formula', '')}")
            c.drawString(50, height - 100, f"Tags: {', '.join(entry.get('tags', []))}")
            c.drawString(50, height - 120, "Description:")
            text = c.beginText(50, height - 140)
            text.setFont("Helvetica", 10)
            for line in entry.get("description", "").split("\n"):
                text.textLine(line)
            c.drawText(text)
            c.save()
            print(f"Exported to {filepath}")
        except ImportError:
            print("reportlab module not found. Install with pip install reportlab")

    # 9. Viewer compact mode
    def view_entry_compact(self, entry):
        viewer = tk.Toplevel(self.window)
        viewer.title(entry.get("title", "Untitled"))
        viewer.geometry("400x400")
        tk.Label(viewer, text=entry.get("title", ""), font=("Helvetica", 12, "bold")).pack(pady=5)
        tk.Label(viewer, text=entry.get("formula", ""), font=("Courier", 10)).pack()
        tk.Label(viewer, text=", ".join(entry.get("tags", [])), fg="gray").pack()
        desc = entry.get("description", "")
        desc_box = tk.Text(viewer, height=15, wrap="word", font=("Helvetica", 9))
        desc_box.insert("1.0", desc)
        desc_box.config(state="disabled")
        desc_box.pack(fill="both", expand=True, padx=10)
        tk.Button(viewer, text="Close", command=viewer.destroy).pack(pady=10)

