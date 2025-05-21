from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from utilities import _open_dialogs
from data_utils import (
    results_dir, mineral_favs_path, element_favs_path, ptable_path,
    mineral_db_path, gallery_dir, gallery_meta_path, log_path, chain_log_path,
    exports_dir, settings_path, library_file, load_settings, load_element_data
)
from mol_assembler import open_molecule_assembler
from math_tools_1 import (
    open_function_plotter,
    open_quadratic_solver,
    open_triangle_solver,
    open_algebric_calc,
    open_scinot_converter,
    open_vector_calculator
)
from chemtools import (
    open_mass_calculator,
    open_shell_visualizer,
    open_property_grapher,
    open_isotope_tool,
    open_phase_predictor,
    open_comparator,
    open_reaction_balancer,
)
from element_viewer import open_element_viewer
from bio_tools_1 import (
    open_transcription_tool,
    open_codon_lookup_tool,
    open_osmosis_tool,
    open_molecular_weight_calculator,
    open_ph_calculator,
    open_population_growth_calculator,
)
from bio_tools_2 import (
    open_reverse_complement_tool,
    open_translate_dna_tool,
    open_gc_content_tool,
    open_seq_file_parser_tool,
    open_pairwise_align_tool,
)
from geo_tools_1 import (
    open_mineral_id_tool,
    open_radioactive_dating_tool,
    open_plate_boundary_tool,
    open_mineral_explorer,
    open_plate_velocity_calculator,
    # open_geo_model_tool,
    open_half_life_calculator
)
from phys_tools_1 import(
    open_acceleration_calculator,
    open_drag_force_calculator,
    open_force_calculator,
    open_kinetic_energy_calculator,
    open_lens_calculator,
    open_ohms_law_tool,
    open_projectile_motion_tool,
    open_speed_calculator,
    open_terminal_velocity_calculator,
    open_unit_converter
)

class ToolkitHub(QDialog):
    def __init__(self, title, tools):
        super().__init__()
        self.setWindowTitle(f"{title} Toolkit")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"{title} Tools:"))
        for tool_name, tool_func in tools:
            btn = QPushButton(tool_name)
            btn.clicked.connect(tool_func)
            layout.addWidget(btn)
        self.setMinimumWidth(340)

def open_math_tools_hub():
    tools = [
        ("Function Plotter", open_function_plotter),
        ("Quadratic Solver", open_quadratic_solver),
        ("Triangle Solver", open_triangle_solver),
        ("Algebric Calculaltor", open_algebric_calc),
        ("Scientific Notation Converter", open_scinot_converter),
        ("Vector Calculator", open_vector_calculator),
    ]
    dlg = ToolkitHub("Math", tools)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_physics_tools_hub():
    tools = [
        ("Unit Converter", open_unit_converter),
        ("Terminal Velocity Calculator", open_terminal_velocity_calculator),
        ("Projectile Motion Tool", open_projectile_motion_tool),
        ("Ohm’s Law Calculator", open_ohms_law_tool),
        ("Lens & Mirror Equation", open_lens_calculator),
        ("Acceleration Calculator", open_acceleration_calculator),
        ("Drag Force Calculator", open_drag_force_calculator),
        ("Force Calculator", open_force_calculator),
        ("Kinetic Energy Calculator", open_kinetic_energy_calculator),
        ("Speed Calculator", open_speed_calculator),
    ]
    dlg = ToolkitHub("Physics", tools)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_chemistry_tools_hub():
    tools = [
        ("Mass Calculator", open_mass_calculator),
        ("Shell Visualizer", open_shell_visualizer),
        ("Property Grapher", open_property_grapher),
        ("Isotope Tool", open_isotope_tool),
        ("Phase Predictor", open_phase_predictor),
        ("Comparator", open_comparator),
        ("Reaction Balancer", open_reaction_balancer),
        ("Element Viewer", open_element_viewer),
        ("Molecular Assembler", open_molecule_assembler)
    ]
    dlg = ToolkitHub("Chemistry", tools)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_biology_tools_hub():
    tools = [
        ("DNA Transcription Tool", open_transcription_tool),
        ("Codon Lookup Tool", open_codon_lookup_tool),
        ("Osmosis Tool", open_osmosis_tool),
        ("Molecular Weight Calculator", open_molecular_weight_calculator),
        ("pH Calculator", open_ph_calculator),
        ("Population Growth Calculator", open_population_growth_calculator),
        ("Reverse Complement Tool", open_reverse_complement_tool),
        ("DNA→Protein Translator", open_translate_dna_tool),
        ("GC Content Tool", open_gc_content_tool),
        ("Sequence File Parser", open_seq_file_parser_tool),
        ("Pairwise Alignment Tool", open_pairwise_align_tool),
    ]
    dlg = ToolkitHub("Biology", tools)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))

def open_geology_tools_hub():
    tools = [
        ("Mineral ID Tool", open_mineral_id_tool),
        ("Radioactive Dating Tool", open_radioactive_dating_tool),
        ("Plate Boundary Tool", open_plate_boundary_tool),
        ("Mineral Explorer", open_mineral_explorer),
        ("Plate Velocity Calculator", open_plate_velocity_calculator),
        # ("Geo Model Tool", open_geo_model_tool), # Uncomment if implemented,
        ("Half Life Calculator", open_half_life_calculator),
    ]
    dlg = ToolkitHub("Geology", tools)
    dlg.show()
    _open_dialogs.append(dlg)
    dlg.finished.connect(lambda _: _open_dialogs.remove(dlg))
