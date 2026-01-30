import tkinter as tk
from tkinter import messagebox
import json
import os

SPECIMEN_FILE = "specimens.csv"
SPECIES_JSON = "species.json"

# ---------- Utilities ----------
def to_float(value):
    try:
        return float(value)
    except:
        return None

def fmt(x):
    return f"{x:.2f}"

def calc_ratios(D,H,W,U):
    return {
        "H/D": H/D if D else 0,
        "W/D": W/D if D else 0,
        "U/D": U/D if D else 0,
        "W/H": W/H if H else 0
    }

# ---------- Load species JSON ----------
def load_species_json():
    """
    Load species JSON file.
    Auto-update missing ratios if necessary.
    """
    if not os.path.exists(SPECIES_JSON):
        return []

    with open(SPECIES_JSON,"r") as f:
        species_data = json.load(f)

    updated_count = 0
    for sp in species_data:
        if "ratios" not in sp:
            D = sp.get("D", 0)
            H = sp.get("H", 0)
            W = sp.get("W", 0)
            U = sp.get("U", 0)
            if D > 0 and H > 0 and W > 0:
                sp["ratios"] = {
                    "H/D": H/D if D else 0,
                    "W/D": W/D if D else 0,
                    "U/D": U/D if D else 0,
                    "W/H": W/H if H else 0
                }
            else:
                sp["ratios"] = {"H/D":0,"W/D":0,"U/D":0,"W/H":0}
            updated_count += 1

    if updated_count > 0:
        with open(SPECIES_JSON,"w") as f:
            json.dump(species_data,f,indent=2)
        print(f"Updated {updated_count} species with missing ratios.")

    return species_data

# ---------- Specimen Section ----------
def update_specimen_ratios(*args):
    D = to_float(sp_D.get())
    H = to_float(sp_H.get())
    W = to_float(sp_W.get())
    U = to_float(sp_U.get())

    sp_Hr.config(text=f"H/D {fmt(H/D)}" if D and H else "")
    sp_Wr.config(text=f"W/D {fmt(W/D)}" if D and W else "")
    sp_Ur.config(text=f"U/D {fmt(U/D)}" if D and U else "")
    sp_WH.config(text=f"W/H {fmt(W/H)}" if H and W else "")

    suggest_species(D,H,W,U)

def copy_specimen():
    name = sp_name.get().strip()
    D = to_float(sp_D.get())
    H = to_float(sp_H.get())
    W = to_float(sp_W.get())
    U = to_float(sp_U.get())
    suggestion = sp_suggest.get()

    if not name or not all([D,H,W,U]):
        messagebox.showerror("Error","Fill all specimen fields.")
        return

    text = (
        f"{name} — D={D} mm; H={H} mm ({fmt(H/D)}); "
        f"W={W} mm ({fmt(W/D)}); U={U} mm ({fmt(U/D)}); W/H={fmt(W/H)}"
        f" — Suggested species: {suggestion}"
    )
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()
    messagebox.showinfo("Copied","Specimen copied to clipboard.")

def save_specimen():
    D = to_float(sp_D.get())
    H = to_float(sp_H.get())
    W = to_float(sp_W.get())
    U = to_float(sp_U.get())

    if not sp_name.get().strip() or not all([D,H,W,U]):
        messagebox.showerror("Error","Fill all specimen fields.")
        return

    import csv
    new_file = not os.path.exists(SPECIMEN_FILE)
    with open(SPECIMEN_FILE,"a",newline="") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["Specimen","D","H","W","U","H/D","W/D","U/D","W/H"])
        writer.writerow([
            sp_name.get().strip(), D,H,W,U,
            fmt(H/D), fmt(W/D), fmt(U/D), fmt(W/H)
        ])
    messagebox.showinfo("Saved","Specimen saved.")

# ---------- Species Section ----------
def update_species_ratios(*args):
    D = to_float(s_D.get())
    H = to_float(s_H.get())
    W = to_float(s_W.get())
    U = to_float(s_U.get())

    s_Hr.config(text=f"H/D {fmt(H/D)}" if D and H else "")
    s_Wr.config(text=f"W/D {fmt(W/D)}" if D and W else "")
    s_Ur.config(text=f"U/D {fmt(U/D)}" if D and U else "")
    s_WH.config(text=f"W/H {fmt(W/H)}" if H and W else "")

def auto_fill_taxonomy(*args):
    """
    Auto-fill higher taxonomy based on species, genus, or family.
    Only sets species to "sp." once if empty.
    """
    all_species = load_species_json()
    species_name = s_species.get().strip()
    genus_name = s_genus.get().strip()
    family_name = s_family.get().strip()

    # Prevent overwriting while typing
    if getattr(auto_fill_taxonomy, "setting_sp", False):
        auto_fill_taxonomy.setting_sp = False
        return

    # Species match
    if species_name and genus_name:
        for sp in all_species:
            if sp["species"] == species_name and sp["genus"] == genus_name:
                s_genus.set(sp["genus"])
                s_family.set(sp["family"])
                s_order.set(sp["order"])
                s_class.set(sp["class"])
                s_phylum.set(sp["phylum"])
                return

    # Genus match
    if genus_name:
        for sp in all_species:
            if sp["genus"] == genus_name:
                s_family.set(sp["family"])
                s_order.set(sp["order"])
                s_class.set(sp["class"])
                s_phylum.set(sp["phylum"])
                if not species_name:
                    auto_fill_taxonomy.setting_sp = True
                    s_species.set("sp.")
                return

    # Family match
    if family_name:
        for sp in all_species:
            if sp["family"] == family_name:
                s_order.set(sp["order"])
                s_class.set(sp["class"])
                s_phylum.set(sp["phylum"])
                return

def save_species():
    D = to_float(s_D.get())
    H = to_float(s_H.get())
    W = to_float(s_W.get())
    U = to_float(s_U.get())

    species_data = {
        "phylum": s_phylum.get(),
        "class": s_class.get(),
        "order": s_order.get(),
        "family": s_family.get(),
        "genus": s_genus.get(),
        "species": s_species.get() if s_species.get() else "sp.",
        "period": s_period.get(),
        "locality": s_locality.get(),
        "D": D, "H": H, "W": W, "U": U,
        "ratios": calc_ratios(D,H,W,U)
    }

    if not species_data["genus"]:
        messagebox.showerror("Error","Genus is required.")
        return

    all_species = load_species_json()
    all_species.append(species_data)
    with open(SPECIES_JSON,"w") as f:
        json.dump(all_species,f,indent=2)
    messagebox.showinfo("Saved","Species saved.")

# ---------- Intelligent Species Suggestion ----------
def suggest_species(D,H,W,U):
    if not all([D,H,W,U]) or not os.path.exists(SPECIES_JSON):
        sp_suggest.set("No species match in the database")
        return

    specimen_ratios = calc_ratios(D,H,W,U)
    all_species = load_species_json()

    species_groups = {}
    genus_groups = {}
    family_groups = {}

    for sp in all_species:
        if "ratios" not in sp:
            continue
        key_species = (sp["genus"], sp["species"])
        key_genus = sp["genus"]
        key_family = sp["family"]
        r = sp["ratios"]
        species_groups.setdefault(key_species, []).append(r)
        genus_groups.setdefault(key_genus, []).append(r)
        family_groups.setdefault(key_family, []).append(r)

    def ratios_within_group(spec_ratios, group_ratios):
        for ratio_name in spec_ratios:
            values = [r[ratio_name] for r in group_ratios]
            if not (min(values) <= spec_ratios[ratio_name] <= max(values)):
                return False
        return True

    # Species level
    for (genus,species), group in species_groups.items():
        if ratios_within_group(specimen_ratios, group):
            sp_suggest.set(f"{genus} {species}")
            return

    # Genus level
    for genus, group in genus_groups.items():
        if ratios_within_group(specimen_ratios, group):
            sp_suggest.set(f"{genus} sp.")
            return

    # Family level
    for family, group in family_groups.items():
        if ratios_within_group(specimen_ratios, group):
            sp_suggest.set(f"{family} sp.")
            return

    sp_suggest.set("No species match in the database")

# ---------- Clear All ----------
def clear_all():
    for var in [sp_name, sp_D, sp_H, sp_W, sp_U]:
        var.set("")
    sp_suggest.set("N/A")
    sp_Hr.config(text="")
    sp_Wr.config(text="")
    sp_Ur.config(text="")
    sp_WH.config(text="")

    for var in [s_specimen_count, s_phylum, s_class, s_order, s_family, s_genus,
                s_species, s_period, s_locality, s_D, s_H, s_W, s_U]:
        var.set("")
    s_Hr.config(text="")
    s_Wr.config(text="")
    s_Ur.config(text="")
    s_WH.config(text="")

# ---------- GUI ----------
root = tk.Tk()
root.title("Ammonite Morphometrics")

# ===== Specimen Section =====
tk.Label(root,text="SPECIMEN DATA",font=("Arial",10,"bold")).grid(row=0,column=0,columnspan=4,pady=5)

sp_name = tk.StringVar()
sp_D = tk.StringVar()
sp_H = tk.StringVar()
sp_W = tk.StringVar()
sp_U = tk.StringVar()
sp_suggest = tk.StringVar(value="N/A")

tk.Label(root,text="Specimen").grid(row=1,column=0,sticky="e")
tk.Entry(root,textvariable=sp_name).grid(row=1,column=1)
tk.Label(root,text="D").grid(row=2,column=0)
tk.Label(root,text="H").grid(row=3,column=0)
tk.Label(root,text="W").grid(row=4,column=0)
tk.Label(root,text="U").grid(row=5,column=0)
tk.Label(root,text="Ratios").grid(row=2,column=2)

tk.Entry(root,textvariable=sp_D).grid(row=2,column=1)
tk.Entry(root,textvariable=sp_H).grid(row=3,column=1)
tk.Entry(root,textvariable=sp_W).grid(row=4,column=1)
tk.Entry(root,textvariable=sp_U).grid(row=5,column=1)

sp_Hr = tk.Label(root,anchor="w"); sp_Hr.grid(row=3,column=2)
sp_Wr = tk.Label(root,anchor="w"); sp_Wr.grid(row=4,column=2)
sp_Ur = tk.Label(root,anchor="w"); sp_Ur.grid(row=5,column=2)
sp_WH = tk.Label(root,anchor="w"); sp_WH.grid(row=6,column=2)

tk.Label(root,text="Suggested species:").grid(row=6,column=0)
tk.Label(root,textvariable=sp_suggest,fg="blue").grid(row=6,column=1)

for v in (sp_D,sp_H,sp_W,sp_U):
    v.trace_add("write", update_specimen_ratios)

tk.Button(root,text="Save Specimen",command=save_specimen).grid(row=7,column=0,columnspan=2)
tk.Button(root,text="Copy Specimen",command=copy_specimen).grid(row=7,column=2,columnspan=1)
tk.Button(root,text="Clear All",command=clear_all,bg="orange").grid(row=7,column=3)

# ===== Species Section =====
tk.Label(root,text="SPECIES DATA",font=("Arial",10,"bold")).grid(row=8,column=0,columnspan=4,pady=10)

s_specimen_count = tk.StringVar()
s_phylum = tk.StringVar()
s_class = tk.StringVar()
s_order = tk.StringVar()
s_family = tk.StringVar()
s_genus = tk.StringVar()
s_species = tk.StringVar()
s_period = tk.StringVar()
s_locality = tk.StringVar()
s_D = tk.StringVar(); s_H = tk.StringVar(); s_W = tk.StringVar(); s_U = tk.StringVar()

tk.Label(root,text="Specimen count").grid(row=9,column=0,sticky="e")
tk.Entry(root,textvariable=s_specimen_count).grid(row=9,column=1)
tk.Label(root,text="Ratios").grid(row=17,column=2)

for i,(lbl,var) in enumerate([
    ("Phylum",s_phylum),("Class",s_class),("Order",s_order),
    ("Family",s_family),("Genus",s_genus),("Species",s_species),
    ("Period",s_period),("Locality",s_locality)
]):
    tk.Label(root,text=lbl).grid(row=10+i,column=0,sticky="e")
    tk.Entry(root,textvariable=var).grid(row=10+i,column=1)

tk.Label(root,text="D").grid(row=18,column=0)
tk.Label(root,text="H").grid(row=19,column=0)
tk.Label(root,text="W").grid(row=20,column=0)
tk.Label(root,text="U").grid(row=21,column=0)

tk.Entry(root,textvariable=s_D).grid(row=18,column=1)
tk.Entry(root,textvariable=s_H).grid(row=19,column=1)
tk.Entry(root,textvariable=s_W).grid(row=20,column=1)
tk.Entry(root,textvariable=s_U).grid(row=21,column=1)

s_Hr = tk.Label(root,anchor="w"); s_Hr.grid(row=19,column=2)
s_Wr = tk.Label(root,anchor="w"); s_Wr.grid(row=20,column=2)
s_Ur = tk.Label(root,anchor="w"); s_Ur.grid(row=21,column=2)
s_WH = tk.Label(root,anchor="w"); s_WH.grid(row=22,column=2)

# Auto-fill triggers
for v in (s_species,s_genus,s_family):
    v.trace_add("write", auto_fill_taxonomy)
for v in (s_D,s_H,s_W,s_U):
    v.trace_add("write", update_species_ratios)

tk.Button(root,text="Save Species",command=save_species).grid(row=23,column=0,columnspan=2)

root.mainloop()
