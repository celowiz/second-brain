# Contributing to My Second Brain

Welcome! This repository is my personal curation of valuable resources, and I'm happy to accept contributions that align with its purpose and quality standards.

## 🤝 Types of Contributions

You can contribute in several ways:

- Adding new books to the collection
- Suggesting courses, articles, or tools
- Fixing broken links or outdated information
- Adding interesting GitHub repositories
- Suggesting new categories or improving organization
- Translating content to English (preferred) or Portuguese

## 📚 Adding New Books

### File Format

Books are stored in `books.csv` with the following columns:

| Column | Description | Required | Example |
|--------|-------------|----------|---------|
| isbn | ISBN-10 or ISBN-13 | Yes | 9780132350884 |
| title | Book title | Yes | Clean Code |
| amazon | Amazon store URL | Yes | https://www.amazon.com/dp/0132350882 |
| categories | Categories separated by semicolons | Yes | Programming;Design Patterns |

### Available Categories

The following categories are currently supported:

**Topics**
- Finance
- Psychology
- Quant
- Statistics
- Design Patterns
- History
- Philosophy
- Society

**Types**
- Programming

**Languages**
- Python
- Java
- C

**Other**
- Biography
- Technology
- Advanced
- Intermediate
- Classic

### Project Setup

1. Make sure you have Python 3.x installed
2. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Steps to Contribute

1. Fork and clone the repository
2. Create a new branch: `git checkout -b add-book-name`
3. Install dependencies (see Project Setup above)
4. Add your book to `books.csv`
5. Test locally:
   ```bash
   python scripts/validate_csv.py
   python scripts/update_readme.py
   ```
5. Commit and push your changes
6. Open a Pull Request

### Automated Validation

The repository has automated checks that run on every Pull Request:

1. CSV format validation
2. Required columns check
3. ISBN format validation
4. Amazon URL validation
5. Categories validation
6. Table generation test

## 🔧 Other Contributions

### Updating Course List

1. Navigate to the Courses section in `README.md`
2. Add your course following the existing format
3. Include:
   - Course name and provider
   - Link to the course
   - Brief description
   - Prerequisites/difficulty level (if applicable)
   - Cost information (if applicable)

### Adding Tools or Resources

1. Find the appropriate section in `README.md`
2. Add your resource with:
   - Clear name and link
   - Brief description
   - Why it's valuable
   - Any relevant tags or categories

## 📋 Pull Request Process

1. Ensure your changes follow the repository's style and format
2. Update the README.md if needed
3. Include a clear PR description explaining:
   - What you added/changed
   - Why it's valuable
   - Any context or references
4. Watch for automated checks and fix any issues
5. Respond to review comments if any

## 🤔 Questions?

If you have questions or need help:
1. Check existing issues and PRs
2. Open a new issue with your question
3. Tag it appropriately (question, help wanted, etc.)

Thank you for contributing to this knowledge base! 🙏