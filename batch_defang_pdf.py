from sys import argv, exit
from subprocess import run
from pathlib import Path

# Change these for your own output
ARGS_FOR_PDFTOCAIRO = "-png"

# Class for PDF file objects
class PdfFile:
    def __init__(self, directory):
        # Path of the original file
        self.directory = directory
        # Path of the folder to be made
        self.directory_scrubbed = str(directory).replace(str(root_directory), str(root_directory_scrubbed))
        self.directory_scrubbed = Path(self.directory_scrubbed.replace(".pdf", ""))
        self.output_file = str(self.directory_scrubbed) + "/" + self.directory_scrubbed.name


# INIT

# Check if directory argument is supplied
try:
    root_directory = Path(argv[-1])
except IndexError:
    print("Usage: py batch_defang_pdf.py [options] <directory of pdfs>")
    exit()

# Check if directory is valid
if not root_directory.exists():
    print("Error: Invalid directory supplied")
    exit()

# Check flags
if "-v" in argv or "--verbose" in argv:
    verbose = True
else:
    verbose = False

if "-d" in argv or "--deconstruct" in argv:
    deconstruct = True
else:
    deconstruct = False

if "-a" in argv or "--assemble" in argv:
    assemble = True
else:
    assemble = False

if deconstruct == False and assemble == False:
    print("Error: Please specifiy whether you want to:")
    print(" Deconstruct pdfs [-d | --deconstruct]")
    print(" Assemble pdfs [-a | --assemble]")
    exit()


# MAIN PROCESS STARTS HERE

# DECONSTRUCT PDFS
if deconstruct:
    # Make a scrubbed directory if needed
    root_directory_scrubbed = Path(str(root_directory) + "_scrubbed")
    if not root_directory_scrubbed.exists():
        root_directory_scrubbed.mkdir()
    
    # Get list of all pdfs
    pdf_directory_list = sorted(root_directory.glob(r'**/*.pdf'))
    if verbose:
        print("-- FOUND PDF FILES --", )
        for pdf in pdf_directory_list:
            print(pdf)
        print("Processing...")

    # Convert to objects and put them in a list
    pdf_list = []
    for pdf_directory in pdf_directory_list:
        pdf_list.append(PdfFile(pdf_directory))

    # Iterate over each pdf
    for pdf in pdf_list:
        # Make a folder for each file
        if not pdf.directory_scrubbed.exists():
            pdf.directory_scrubbed.mkdir(parents=True)

        # Call pdftocairo on each file
        # Usage: pdftocairo [options] <PDF-file> [<output-file>]
        run(["pdftocairo", "-png", "-r", "300", pdf.directory, pdf.output_file]) # ARGS GO HERE
        if verbose:
            print(f"Successfully processed: {pdf.directory_scrubbed}")
    
    print("-- Processing complete --")

# ASSEMBLE PDFS
if assemble:
    # Fix the directory if deconstructed in the same session
    if deconstruct:
        assembly_source_directory = Path(str(root_directory) + "_scrubbed")
    else:
        assembly_source_directory = root_directory

    # Get list of all .png files
    png_list = sorted(assembly_source_directory.glob(r'**/*.png'))

    # Add all unique parent directories to a list
    png_directory_list = []
    if verbose: print("-- FOUND PNG DIRECTORIES --")
    for png in png_list:
        if png.parent not in png_directory_list:
            png_directory_list.append(png.parent)
            if verbose: print(png.parent)
    
    # Call merge2pdf on each unique directory
    for png_directory in png_directory_list:
        # Make a folder for output if needed
        output_directory = Path(str(png_directory).replace(str(root_directory), str(str(root_directory) + "_defanged")))
        if not output_directory.parent.exists():
            output_directory.parent.mkdir(parents=True)
        
        # Assemble pngs into a pdf
        # Usage: merge2pdf output.pdf path/to/a/dir
        assembled_output_file = str(output_directory) + ".pdf"
        run(["merge2pdf", assembled_output_file, png_directory])

        if verbose: print(f"Successfully processed: {assembled_output_file}")