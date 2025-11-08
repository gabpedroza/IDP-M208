# M208 IDP repository
Please read this file for important setup instructions

## Prerequisites
- Python3
- pip
- git

## Setup Instructions
### Virtual Environment
Use a virtual environment for coding please so that you will have a clean, conflict-free installation of Python with only the required dependencies. Call it `idp-env`. To do this, in the main folder of this project:

`python3 -m venv idp-env`. This command will create the environment. First time only.

`pip install -r requirements.txt`. Install requirements automatically based on the specifications in the requirements file. If you install additional dependencies please update the file immediately. Only needs to be done whenever dependencies change.

`source idp-env/bin/activate` or `source idp-env/scripts/activate` depending on your system/Python version. This needs to be done EVERY time you reopen your command prompt/IDE.

## Version Control Practices
1. Commit every significant change. If unsure, err on the side of committing too much rather than too little.
2. Add a helpful commit message to EVERY commit so that people know what is going on/what has been changed.
3. Work on your own branch and resolve conflicts carefully before merging into `main`.