#!/usr/bin/env python

""" Parse log file generated by OMEGA conformational search and
    output .txt file containing info of all molecules with warnings,
    then collect .pdb files of all molecules with warnings into logs folder.

    Author: Roy Nguyen
    Last edited: June 20, 2019
"""


import sys
import os
import shutil

log_folder = "Conformers-Logs"
pdb_folder = "Compound-3D-Structure"
failed_molecules = {}

def main():
    cwd = os.getcwd()
    log_folder_path = os.path.join(cwd, log_folder)
    log_files = [f for f in os.listdir(log_folder_path)
                if os.path.isfile(os.path.join(log_folder_path, f))]
    # Parse logs
    for log in log_files:
        if "Fails" not in log:
            parse_log(log, log_folder_path)
    #parse_log("Spectrum_ED.txt", log_folder_path)    # Debugging purposes

    # Collect .pdb files of all molecules with warnings
    pdb_folder_path = os.path.join(cwd, pdb_folder)
    get_pdb_fails(pdb_folder_path, log_folder_path)

    sys.stdout.write("Script finished! \n")
    return

def parse_log(log_file, log_folder):
    '''
    Filter log file for only molecules with warnings into seperate .txt file

    Args:
        log_file (string): name of log file
        log_folder (string): path to folder containing log files
    '''
    library_name = log_file[:log_file.index(".txt")]
    log_path = os.path.join(log_folder, log_file)
    output_name = library_name + "_Fails.txt"
    output_path = os.path.join(log_folder, output_name)
    output_txt = ""
    list_failed_molecules = []
    # Parse log file
    sys.stdout.write("Parsing log file of " + library_name + "...\n")
    with open(log_path, "r") as log:
        num_molecules = 0
        num_warnings = 0
        curr_paragraph = ""
        curr_molecule = ""
        for line in log:
            if "Title" in line:
                curr_molecule = extract_cmp_id(line)
                curr_paragraph = "Molecule: " + curr_molecule + "\n"
                num_molecules += 1
            if "Warning" in line:
                curr_paragraph += line
            if "---" in line and "Warning" in curr_paragraph:
                if "failed" in curr_paragraph:
                    curr_paragraph = "FAILED \n" + curr_paragraph
                    list_failed_molecules.append(curr_molecule)
                curr_paragraph += "----------------------------------\n"
                output_txt += curr_paragraph
                num_warnings += 1
                curr_paragraph = ""
                #list_failed_molecules.append(curr_molecule)
            if "Processed" in line:
                num_fails = output_txt.count("failed")
                output_txt += line
                output_txt += "Number of Warnings = " + str(num_warnings) + "\n"
                output_txt += "Number of Molecules Failed = " + str(num_fails)

    # Update dict of failed molecules
    failed_molecules[library_name] = list_failed_molecules

    # Write output
    with open(output_path, "w") as output:
        output.write(output_txt)

    sys.stdout.write("Done with " + library_name + "!\n")
    sys.stdout.write("\n")
    return

def get_pdb_fails(pdb_folder, log_folder):
    '''
    For each compound library, copy .pdb files of molecules with warnings
    into logs folder

    Args:
        pdb_folder (string): path to folder containing .pdb files
        log_folder (string): path to folder containing log files
    '''
    for library in failed_molecules.keys():
        sys.stdout.write("Collecting .pdb files of failed molecules in " + library + "...\n")
        library_pdbs = os.path.join(pdb_folder, library)
        output_folder = os.path.join(log_folder, library)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for mol in failed_molecules[library]:
            pdb_name = mol + ".pdb"
            pdb_file = os.path.join(library_pdbs, pdb_name)
            output = os.path.join(output_folder, pdb_name)
            shutil.copy(pdb_file, output)
        sys.stdout.write("Done with " + library + "!\n")
        sys.stdout.write("\n")

    return


def extract_cmp_id(line):
    '''
    Get compound ID from text line

    Args:
        line (string): text line containing compound ID

    Return:
        (string): compound ID
    '''
    start_index = line.index("=") + 2
    end_index = line.index("\n")
    if "  " in line:
        end_index = line.index("  ")
    cmp_id = line[start_index:end_index]
    return cmp_id
    
if __name__ == "__main__":
    main()