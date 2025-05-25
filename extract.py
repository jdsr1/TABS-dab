import pypdf
import re


#
# Reference
#
# J. Comput. Chem. 25, 1157 (2004).
# Development and testing of a general amber force field
# J. Wang, R.M. Wolf, J.W. Caldwell, P.A. Kollman, D.A. Case
# https://doi.org/10.1002/jcc.20035


#
# read PDF with TABS database structures
#
tabs_pdf = pypdf.PdfReader('1-s2.0-S2210271X14002400-mmc1.pdf')
number_of_pages = len(tabs_pdf.pages)


#
# re pattern for values 
#
pattern_value = re.compile(r'([A-Za-z_]+)= *([-0-9\.]+) ([a-z]+)')


#
# obtain molecule from TABS database
#
def get_molecule(mol_id:int):
    # initialization
    atoms = []
    values = []

    # read page and get lines
    page = tabs_pdf.pages[mol_id].extract_text()
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
def export_molecule(mol_id:int):
    # get molecule information
    n_atom, atoms, name, values, point_group = get_molecule(mol_id) 

    # print some info
    print(f"\n TABS ID     : {mol_id:05d}")
    print(f" Name (#Atom): {name} ({n_atom})")
    print(f" Properties  :")
    for value in values:
        q, v, u = value
        print(f"\t {q} = {v} {u}")

        
    # open file and write coordinates
    file_name = f"TABS_{mol_id:05d}.xyz"
    with open(file_name, 'w') as out:
        out.write(f"{n_atom}\n#\n")
        for at in atoms:
            line = f"{at[0]:6s} {at[1]:+10.6f} {at[2]:+10.6f} {at[3]:+10.6f}\n"
            out.write(line)
    # end
    print(f" File name   : {file_name}\n")
    return 0

#
# extract all 
#
print(f"\n TABS database extraction")
print(" Type MOL_ID [1-1641] or 0 (all): ", end='')
option = int(input())

if option == 0:
    for mol_id in range(1, number_of_pages):
        export_molecule(mol_id)
else:
    export_molecule(option)
