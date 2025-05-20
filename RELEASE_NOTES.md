## Structural Overhaul

### Modular Refactor
- Reorganized the entire project directory:
  - `/tools` for code modules
  - `/databases` and `/interndatabases` for structured data
  - `/logs`, `/exports`, `/gallery`, `/images`, `/screenshots`, `/results` for outputs
  - `/documentations`, `/Fixers`, and others as needed
- Centralized all path references via `utilities.py`
- Converted all scripts to use absolute imports (`from xyz import ...`)
- Enforced script execution from project root (`python hub.py`)
- Auto-creation of all needed folders on runtime
- Cleaned up `.gitignore` and eliminated leftover or orphaned files

### Breaking Changes
- All scripts now depend on the root path
- Imports will fail if run from subfolders without adjusting paths
- Only essential files (`hub.py`, `.gitignore`, possibly one JSON) remain in root

## Feature Additions

### Tools
- Added new **Vector Calculator** with 3D plotting
- Added **Half Life Calculator** with decay curve visualization
- Added **Scientific Notation Converter**
- Added **Algebraic Calculator**
- Improved coder feature and internal tooling structure

## Documentation Updates

- README updated to reflect:
  - All new tools
  - AI assistant capabilities
  - Chain Mode, preload options, and export logging
- Portuguese translations fixed for clarity
- Expanded docs for models and their features

## Bug Fixes

- Fixed script startup issue caused by incorrect imports
- Resolved circular imports and matplotlib event loop errors
- Removed merge conflict markers and ensured all JSON is valid
- Fixed incorrect file paths in `data_utils.py`
- Corrected wording in README translations
- Removed redundant imports and outdated comments

## Testing

- Added unit tests for `parse_formula` function

## Git and Miscellaneous

- Cleaned `.gitignore` and removed unnecessary tracked files
- Fixed issues with `hub.py` not loading properly due to git state
- Added new file entries to `library_entries.json` and `.gitignore`
