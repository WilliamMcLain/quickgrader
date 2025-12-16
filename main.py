import os
import re
from pathlib import Path
import PyPDF2
from collections import defaultdict

def extract_pdf_text(pdf_path):
    """Extract text from the first page of a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if len(pdf_reader.pages) > 0:
                first_page = pdf_reader.pages[0]
                return first_page.extract_text()
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return ""

def parse_assignment_info(text):
    """Parse assignment name and student name from PDF text."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    assignment_name = None
    student_name = None
    
    # Look for assignment name (typically contains "Homework #")
    for i, line in enumerate(lines):
        if 'Homework' in line and '#' in line:
            # Extract homework number
            match = re.search(r'Homework\s*#?\s*(\d+)', line, re.IGNORECASE)
            if match:
                assignment_name = f"Homework{match.group(1)}"
                break
    
    # Look for student name (appears after "Student" label)
    for i, line in enumerate(lines):
        if line.lower() == 'student' and i + 1 < len(lines):
            student_name = lines[i + 1]
            break
    
    return assignment_name, student_name

def format_student_name(name):
    """Format student name to 'Last, First Middle' format."""
    if not name:
        return None
    
    # Split name into parts
    parts = name.strip().split()
    
    if len(parts) == 0:
        return None
    elif len(parts) == 1:
        # Only one name provided
        return parts[0]
    elif len(parts) == 2:
        # First Last -> Last, First
        return f"{parts[1]}, {parts[0]}"
    else:
        # First Middle Last or First Middle1 Middle2 Last
        # Take first as first name, last as last name, everything in between as middle
        first = parts[0]
        last = parts[-1]
        middle = ' '.join(parts[1:-1])
        return f"{last}, {first} {middle}"

def rename_pdfs(folder_path):
    """Rename all PDFs in the specified folder."""
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"Error: Folder '{folder_path}' does not exist!")
        return
    
    if not folder.is_dir():
        print(f"Error: '{folder_path}' is not a directory!")
        return
    
    # Get all PDF files
    pdf_files = list(folder.glob('*.pdf'))
    
    if not pdf_files:
        print("No PDF files found in the specified folder.")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process.\n")
    
    # Track name occurrences for handling duplicates
    name_counts = defaultdict(int)
    rename_operations = []
    
    # First pass: extract info and build rename list
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        
        # Extract text from PDF
        text = extract_pdf_text(pdf_file)
        
        # Parse assignment and student info
        assignment_name, student_name = parse_assignment_info(text)
        
        if not assignment_name or not student_name:
            print(f"  ⚠ Could not extract required information. Skipping.")
            print(f"    Assignment: {assignment_name}, Student: {student_name}\n")
            continue
        
        # Format student name
        formatted_name = format_student_name(student_name)
        
        if not formatted_name:
            print(f"  ⚠ Could not format student name. Skipping.\n")
            continue
        
        # Build new filename
        base_name = f"BIOE252-Fall-{assignment_name}-{formatted_name}"
        name_counts[base_name] += 1
        
        # Handle duplicates
        if name_counts[base_name] > 1:
            new_filename = f"{base_name}{name_counts[base_name]}.pdf"
        else:
            new_filename = f"{base_name}.pdf"
        
        rename_operations.append((pdf_file, new_filename, assignment_name, formatted_name))
        print(f"  ✓ Will rename to: {new_filename}\n")
    
    # Second pass: perform renames
    if not rename_operations:
        print("No files to rename.")
        return
    
    print("\n" + "="*60)
    print("Starting rename operations...")
    print("="*60 + "\n")
    
    success_count = 0
    for old_path, new_filename, assignment, student in rename_operations:
        new_path = old_path.parent / new_filename
        
        try:
            old_path.rename(new_path)
            print(f"✓ Renamed: {old_path.name}")
            print(f"       to: {new_filename}")
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to rename {old_path.name}: {e}")
        print()
    
    print("="*60)
    print(f"Completed! Successfully renamed {success_count}/{len(rename_operations)} file(s).")
    print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("BIOE 252 Assignment PDF Renamer")
    print("="*60)
    print()
    
    # Change this path to your folder location
    folder_path = input("Enter the full path to the folder containing PDFs: ").strip()
    
    # Remove quotes if user pasted path with quotes
    folder_path = folder_path.strip('"').strip("'")
    
    print()
    rename_pdfs(folder_path)