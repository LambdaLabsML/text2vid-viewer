from pathlib import Path
from utils.refresh_db import update_csv


def main():

    # csv_fpath is located in the parent of the script's parent directory
    csv_fpath = Path(__file__).resolve().parent.parent / "frontend/db.csv"

    # Call the function with the dynamically constructed path as a string
    update_csv(csv_fpath=str(csv_fpath))

if __name__ == "__main__":
    
    main()
