@echo off
cd D:\Akash\Share Market\Algo\MyAlgo\excels\Indices
:: Folder containing Excel files
set folder_path=.\indices

:: Loop through all Excel files in the folder
for %%f in (".\*.xlsx") do (
    echo Processing %%f
    python ..\..\backtrace\backtrace_short_term_cluster.py ".\excels\indices%%f"
    ::python ..\..\backtrace\backtrace_short_term_cluster.py ".\excels\indices%%f"
    ::python ..\..\tracking\trend.py ".\excels\indices%%f"
)

pause
