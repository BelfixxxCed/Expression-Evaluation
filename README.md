# Expression-Evaluation
 
A brief description of what this project does goes here.
 
## Getting Started
 
These instructions will help you set up a local copy of this project using a Python virtual environment (`venv`).
 
### Prerequisites
 
- Python 3.x installed ([download here](https://www.python.org/downloads/))
- Git installed
### 1. Clone the repository
 
```bash
git clone git@github.com:BelfixxxCed/Expression-Evaluation.git
cd Expression-Evaluation
```
 
### 2. Create a virtual environment
 
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
 
**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```
 
> If PowerShell blocks the activation script, run this once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
 
Once activated, your terminal prompt should be prefixed with `(venv)`.
 
### 3. Install dependencies
 
```bash
pip install -r requirements.txt
```
 
### 4. Run the project
 
```bash
python main.py
```
 
*(Replace with the actual entry point of your project.)*
 
### Deactivating the environment
 
When you're done working, you can exit the virtual environment with:
 
```bash
deactivate
```
 
## Project Structure
 
```
Expression-Evaluation/
├── venv/              # Virtual environment (not committed to Git)
├── .gitignore
├── requirements.txt
├── README.md
└── ...
```
 
## Contributing
 
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add some feature"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request
