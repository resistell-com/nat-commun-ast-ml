# nat-commun-ast-ml

Supplementary data and code to the manuscript.

### Installation guide for Windows

It is assumed that there is python interpreter installed in the system.

1. Open cmd tool
2. Type the following commands

        cd path_to_installation_folder
        git clone https://github.com/resistell-com/nat-commun-ast-ml.git
        cd nat-commun-ast-ml
        python -m venv .env
        .\.env\Scripts\activate.bat
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        jupyter notebook nat-commun-ast-ml.ipynb
		
After typing the last command the web browser window should open. From the Run menu select "Run All Cells" command. Then, the notebook code should run.
