# Drug Concentration Calculator

Desktop app for lab drug solution and dilution calculations (Python, CustomTkinter, v3.0.0).

## Workflow
- Working copy on branch `claude/work`. The real repo is elsewhere.
- Commit after each task. Do not push.
- The GUI cannot run in this container (no display). After UI changes, say what I should check on Windows.
- Commit messages: simple conventional style, e.g. "fix: copied dialog follows dark mode".

## Structure
- `main_ctk.py`: entry point (CustomTkinter). Work here.
- `src/gui_integration_ctk.py`: dialogs and widgets for the CustomTkinter UI. Work here.
- `src/`: calculators, data_storage, formatters, pubchem_api
- `tests/test_api.py`: API tests

## Stack
- Python, uv (`pyproject.toml`), CustomTkinter
- Calculation history is an embedded ttk.Treeview.

## Code style
- Comments and docstrings only where meaningful. Don't describe the change process in comments.
- Descriptive variable names.

## Don't
- `main.py` and `src/gui_integration.py` are the old tkinter version. Don't edit them.
- Don't change the font size of the calculation history table.
- Don't touch packaging files (.spec, build scripts) unless asked.
