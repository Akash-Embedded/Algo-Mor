@echo off
:: Folder containing Excel files
set folder_path=.\indices

:: Loop through all Excel files in the folder
for %%f in (".\*.xlsx") do (
    echo Processing %%f
    python ..\backtrace\backtrace_short_term_cluster.py ".\indices%%f"
)

pause
