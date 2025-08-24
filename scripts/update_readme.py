import sys
from pathlib import Path

def update_readme_with_table(readme_path: str, table_content: str):
    """Update the README.md file with the new table content."""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the position where we want to insert the table
    # Look for the sponsored note and the courses section
    sponsored_note = "💡 *This panel contains affiliate links. If you find something useful and make a purchase, I may earn a small commission* ☕. *Thanks for the support.* ❤"
    courses_section = "## 🎓 Learning Materials"

    # Split content by courses section
    if courses_section not in content:
        print("Error: Could not find the Courses section in README.md")
        return False

    parts = content.split(courses_section)
    if len(parts) != 2:
        print("Error: Invalid README.md structure")
        return False

    # Find the end of the sponsored note in the first part
    if sponsored_note not in parts[0]:
        print("Error: Could not find the sponsored note in README.md")
        return False

    # Split the first part at the sponsored note
    pre_note, post_note = parts[0].split(sponsored_note)
    
    # Reconstruct the content with the new table
    new_content = (
        f"{pre_note}{sponsored_note}\n\n"
        f"{table_content}\n\n"
        f"{courses_section}{parts[1]}"
    )

    # Write the updated content back to the file
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    # Get the project root directory (parent of scripts directory)
    root_dir = Path(__file__).parent.parent
    readme_path = root_dir / "README.md"
    
    # Generate the table
    from generate_books_table import generate_table_from_csv
    table_rows = generate_table_from_csv(str(root_dir / "books.csv"))
    
    # Create the complete table
    table_content = "| Cover | Title | Amazon | Categories |\n"
    table_content += "|:---:|:---|:---:|:---|\n"
    table_content += "\n".join(table_rows)
    
    # Update the README
    if update_readme_with_table(str(readme_path), table_content):
        print("Successfully updated README.md")
    else:
        print("Failed to update README.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
