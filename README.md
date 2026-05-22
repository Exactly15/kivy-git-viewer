# Offline Git Viewer - Kivy Edition

A lightweight desktop application built with Kivy to browse any Git repository offline.

## Features

- 📂 Browse local Git repositories
- 🌿 View all branches
- 📜 Explore commit history with author, date, and message
- 📄 View file contents and directory structure
- 📊 Repository statistics (commits, branches, contributors)
- 🎨 Clean, intuitive tabbed UI
- ⚡ Fast performance with offline browsing

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/Exactly15/kivy-git-viewer.git
cd kivy-git-viewer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

1. **Open Repository**: Click the "Open Repository" button in the top-left
2. **Browse**: Select any local Git repository directory from the file picker
3. **Navigate**:
   - **Commits Tab**: View commit history, click commits for detailed info
   - **Files Tab**: Browse the repository's file structure
   - **Stats Tab**: View repository statistics
   - **Branch Selector**: Switch between branches in the left sidebar

## Features in Detail

### Commits Tab
- View all commits in the current branch
- See commit hash, message, author, and date
- Click any commit to see full details including:
  - Full commit hash
  - Complete commit message
  - Author name and email
  - Number of files changed

### Files Tab
- Browse the entire file tree of the repository
- Navigate through directories
- View file contents in a popup window
- Support for text files (binary files show as "Binary file or empty")

### Stats Tab
- Total number of commits in the repository
- Number of branches
- Number of unique contributors

### Branch Navigation
- Left sidebar shows all available branches
- Click any branch to switch and reload all views
- Works across all tabs

## Requirements

- **Kivy 2.3.0+**: Modern UI framework for Python
- **GitPython 3.1.0+**: Git repository operations
- **Python 3.7+**: Core language

## Project Structure

```
kivy-git-viewer/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── buildozer.spec      # (Optional) For building mobile apps
```

## Architecture

The application consists of two main components:

### GitRepository Class
Handles all Git operations using GitPython:
- Branch listing and switching
- Commit history retrieval
- File tree navigation
- File content reading
- Repository statistics

### GitViewerApp Class
Kivy UI application that provides:
- Repository selection dialog
- Branch navigation sidebar
- Tabbed interface (Commits, Files, Stats)
- Popup dialogs for detailed views
- Real-time UI updates

## Performance Notes

- Large repositories (10,000+ commits) may take a moment to load
- File browsing is instant as it uses Git's efficient tree objects
- All operations are read-only (no modifications to the repository)

## Limitations

- Binary files display as "Binary file or empty"
- Large files may take time to load for display
- No support for submodules (yet)
- Limited to local repositories

## Future Enhancements

- [ ] Commit diff visualization
- [ ] Search functionality
- [ ] Graph visualization of commit history
- [ ] Blame view for files
- [ ] Tag support
- [ ] Stash viewing
- [ ] Mobile build support
- [ ] Dark theme

## Troubleshooting

### "Invalid git repository" error
- Make sure you selected a folder that contains a `.git` directory
- The folder should be a valid Git repository

### Application won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version is 3.7 or higher

### Slow performance on large repositories
- This is normal for repositories with 50,000+ commits
- Consider filtering commits or using a smaller test repository

## License

MIT License - feel free to use, modify, and distribute

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues or feature requests, please open an issue on GitHub.
