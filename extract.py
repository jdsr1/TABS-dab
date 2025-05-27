import pypdf
import re

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt


#
# Reference
#
# J. Comput. Chem. 25, 1157 (2004).
# Development and testing of a general amber force field
# J. Wang, R.M. Wolf, J.W. Caldwell, P.A. Kollman, D.A. Case
# https://doi.org/10.1002/jcc.20035

#
# parameters and initialization
#
MIN_ID = 1
MAX_ID = 1641
TABS_PDF = pypdf.PdfReader('1-s2.0-S2210271X14002400-mmc1.pdf')

pattern_value = re.compile(r'([A-Za-z_]+)= *([-0-9\.]+) ([a-z]+)')

console = Console()


#
# load molecule structure from TABS database based on id
#
def load_structure(mol_id:int) -> list:
    # initialization
    atoms = []
    values = []

    # read page and get lines
    page = TABS_PDF.pages[mol_id].extract_text()
    lines = page.split('\n')
    n_lines = len(lines)

    # process header
    name = lines[1]
    point_group = lines[2].split(':')[1]
    for il in range(3,8):
        value_entry = tuple(pattern_value.search(lines[il]).groups())
        values.append(value_entry)

    # get number of atoms and atomic coordinates
    n_atom = int(lines[8])

    for il in range(9, n_lines):
        atom_entry = lines[il].split()
        for i in range(1,4):
            atom_entry[i] = float(atom_entry[i])
        atoms.append(atom_entry)

    # end
    rv = [n_atom, atoms, name, values, point_group]
    return rv


#
# export molecule as xyz file
#
def export_molecule(mol_id:int, info=True) -> None:
    # get molecule information
    n_atom, atoms, name, values, point_group = load_structure(mol_id)

    # print molecule information
    if info:
        print(f"\n TABS ID     : {mol_id:05d}")
        print(f" Name (#Atom): {name} ({n_atom})")
        print(f" Properties  :")
        for value in values:
            q, v, u = value
            print(f"   {q} = {v} {u}")

    # open file and write coordinates
    file_name = f"TABS_{mol_id:05d}.xyz"
    with open(file_name, 'w') as out:
        out.write(f"{n_atom}\n#\n")
        for at in atoms:
            line = f"{at[0]:6s} {at[1]:+10.6f} {at[2]:+10.6f} {at[3]:+10.6f}\n"
            out.write(line)
    # end
    print(f" File name   : {file_name}\n")


#
# build quick database
#
def build_quick_db():
    table = Table.grid(padding=(0,2))
    table.add_column(justify="right", style="bold")
    table.add_column()
    table.add_column(justify="right")
    table.add_row("[yellow] ID [/yellow]",
                  "[bold yellow] Molecule name [/bold yellow]",
                  "[bold yellow] # of atoms [/bold yellow]")

    for mol_id in range(MIN_ID, MAX_ID + 1):
        data = load_structure(mol_id)
        name = data[2]
        n_atom = data[0]
        table.add_row(str(mol_id), name, str(n_atom))

    return table


#
# show menu
#
def show_menu() -> str:
    """Render the main menu and return the user's raw choice."""
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="right", style="bold")
    table.add_column()

    table.add_row("[magenta]1[/magenta]", "Export structure by ID")
    table.add_row("[magenta]2[/magenta]", "Export ALL structures")
    table.add_row("[magenta]3[/magenta]", "Print database (long)")
    table.add_row("[magenta]q[/magenta]", "Exit")

    console.print(Panel(table, title="Menu", expand=False))
    choice = Prompt.ask("[bold yellow]Select an option[/bold yellow]",
                        choices=["1", "2", "3", "q"])
    return choice


#
# main function and loop
#
def main() -> None:
    console.clear()
    console.rule("[bold green]TABS database extraction")
    build_db = True

    while True:
        choice = show_menu()

        # process single structure
        if choice == "1":
            while True:
                mol_id = IntPrompt.ask(f"Enter ID [{MIN_ID}–{MAX_ID}]")
                if MIN_ID <= mol_id <= MAX_ID:
                    break
                console.print(f"[red]Invalid ID.[/red]")
            export_molecule(mol_id)

        # process all structures
        elif choice == "2":
            for mol_id in range(MIN_ID, MAX_ID + 1):
                export_molecule(mol_id, info=False)

        # print database
        elif choice == "3":
            if build_db:
                table_db = build_quick_db()
                build_db = False

            console.print(Panel(table_db, title="TABS data", expand=False))

        # exit the program
        elif choice == "q":
            console.print("\n[bold green]Goodbye![/bold green]\n")
            break

        # back to the menu
        Prompt.ask("\nPress enter to return to the menu")
        console.clear()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user.[/bold red]")
