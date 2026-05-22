"""
Offline GitHub Viewer - A Kivy application for browsing local Git repositories
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

import git
from pathlib import Path
from datetime import datetime
import os

Window.size = (1200, 800)

class GitRepository:
    """Wrapper for git operations"""
    
    def __init__(self, path):
        try:
            self.repo = git.Repo(path)
            self.path = path
        except Exception as e:
            raise ValueError(f"Invalid git repository: {e}")
    
    def get_branches(self):
        """Get all branches"""
        return [head.name for head in self.repo.heads]
    
    def get_current_branch(self):
        """Get current branch"""
        return self.repo.active_branch.name
    
    def get_commits(self, branch='HEAD', max_count=50):
        """Get commits from a branch"""
        commits = []
        for commit in self.repo.iter_commits(branch, max_count=max_count):
            commits.append({
                'hash': commit.hexsha[:7],
                'message': commit.message.split('\n')[0],
                'author': commit.author.name,
                'date': datetime.fromtimestamp(commit.committed_date).strftime('%Y-%m-%d %H:%M'),
                'full_hash': commit.hexsha
            })
        return commits
    
    def get_commit_details(self, commit_hash):
        """Get detailed info about a commit"""
        commit = self.repo.commit(commit_hash)
        return {
            'hash': commit.hexsha,
            'message': commit.message,
            'author': f"{commit.author.name} <{commit.author.email}>",
            'date': datetime.fromtimestamp(commit.committed_date),
            'changes': len(commit.parents),
            'files': len(commit.stats.files)
        }
    
    def get_file_tree(self, branch='HEAD', path=''):
        """Get file tree for a branch"""
        try:
            tree = self.repo.tree(branch)
            if path:
                for part in path.split('/'):
                    tree = tree[part]
            
            items = []
            for item in tree:
                items.append({
                    'name': item.name,
                    'type': 'tree' if item.type == 'tree' else 'blob',
                    'path': f"{path}/{item.name}" if path else item.name
                })
            return items
        except Exception as e:
            return []
    
    def get_file_content(self, branch='HEAD', path=''):
        """Get file content"""
        try:
            blob = self.repo.tree(branch)[path]
            if blob.type == 'blob':
                return blob.data_stream.read().decode('utf-8', errors='ignore')
            return None
        except Exception as e:
            return f"Error reading file: {e}"
    
    def get_stats(self):
        """Get repository statistics"""
        commits = list(self.repo.iter_commits())
        branches = self.get_branches()
        
        return {
            'total_commits': len(commits),
            'branches': len(branches),
            'contributors': len(set(c.author.name for c in commits))
        }


class GitViewerApp(App):
    """Main Kivy application"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_repo = None
        self.current_branch = 'HEAD'
    
    def build(self):
        """Build the UI"""
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Header
        header = BoxLayout(size_hint_y=0.1, spacing=10)
        header.add_widget(Button(
            text='Open Repository',
            size_hint_x=0.2,
            on_press=self.show_file_chooser
        ))
        
        self.repo_label = Label(
            text='No repository loaded',
            size_hint_x=0.8
        )
        header.add_widget(self.repo_label)
        main_layout.add_widget(header)
        
        # Main content area
        content = BoxLayout(orientation='horizontal', spacing=10)
        
        # Left sidebar - Navigation
        sidebar = BoxLayout(orientation='vertical', size_hint_x=0.2, spacing=10)
        sidebar.add_widget(Label(text='Branches', size_hint_y=0.1, bold=True))
        
        self.branches_scroll = ScrollView()
        self.branches_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.branches_layout.bind(minimum_height=self.branches_layout.setter('height'))
        self.branches_scroll.add_widget(self.branches_layout)
        sidebar.add_widget(self.branches_scroll)
        
        sidebar.add_widget(Label(text='Info', size_hint_y=0.1, bold=True))
        self.info_label = Label(
            text='Load a repository',
            size_hint_y=0.3,
            markup=True
        )
        sidebar.add_widget(self.info_label)
        
        content.add_widget(sidebar)
        
        # Center - Main content (tabbed interface)
        center_layout = BoxLayout(orientation='vertical', spacing=10)
        
        # Tab buttons
        tab_layout = BoxLayout(size_hint_y=0.08, spacing=5)
        self.commit_btn = Button(text='Commits', on_press=self.show_commits_view)
        self.files_btn = Button(text='Files', on_press=self.show_files_view)
        self.graph_btn = Button(text='Stats', on_press=self.show_stats_view)
        
        tab_layout.add_widget(self.commit_btn)
        tab_layout.add_widget(self.files_btn)
        tab_layout.add_widget(self.graph_btn)
        center_layout.add_widget(tab_layout)
        
        # Content area
        self.content_scroll = ScrollView()
        self.content_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        self.content_scroll.add_widget(self.content_layout)
        center_layout.add_widget(self.content_scroll)
        
        content.add_widget(center_layout)
        main_layout.add_widget(content)
        
        return main_layout
    
    def show_file_chooser(self, instance):
        """Show file chooser dialog"""
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(filters=['isdir'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        btn_layout.add_widget(Button(
            text='Select',
            on_press=lambda x: self.load_repository(filechooser.path)
        ))
        btn_layout.add_widget(Button(
            text='Cancel',
            on_press=lambda x: popup.dismiss()
        ))
        content.add_widget(btn_layout)
        
        popup = Popup(title='Select Repository', content=content, size_hint=(0.9, 0.9))
        popup.open()
    
    def load_repository(self, path):
        """Load a git repository"""
        try:
            self.current_repo = GitRepository(path)
            self.repo_label.text = f'Repository: {Path(path).name}'
            self.refresh_ui()
            # Close popup if exists
            for widget in self.root.walk():
                if isinstance(widget, Popup):
                    widget.dismiss()
        except ValueError as e:
            self.repo_label.text = f'Error: {str(e)}'
    
    def refresh_ui(self):
        """Refresh all UI elements"""
        self.refresh_branches()
        self.refresh_info()
        self.show_commits_view(None)
    
    def refresh_branches(self):
        """Refresh branch list"""
        self.branches_layout.clear_widgets()
        if not self.current_repo:
            return
        
        branches = self.current_repo.get_branches()
        for branch in branches:
            btn = Button(
                text=branch,
                size_hint_y=None,
                height=40,
                on_press=lambda x, b=branch: self.switch_branch(b)
            )
            self.branches_layout.add_widget(btn)
    
    def switch_branch(self, branch_name):
        """Switch to a different branch"""
        self.current_branch = branch_name
        self.refresh_ui()
    
    def refresh_info(self):
        """Refresh repository info"""
        if not self.current_repo:
            return
        
        stats = self.current_repo.get_stats()
        self.info_label.text = (
            f'[b]Repository Stats[/b]\n'
            f'Commits: {stats["total_commits"]}\n'
            f'Branches: {stats["branches"]}\n'
            f'Contributors: {stats["contributors"]}'
        )
    
    def show_commits_view(self, instance):
        """Show commits view"""
        self.content_layout.clear_widgets()
        if not self.current_repo:
            self.content_layout.add_widget(Label(text='No repository loaded'))
            return
        
        commits = self.current_repo.get_commits(self.current_branch)
        
        for commit in commits:
            btn = Button(
                text=f"{commit['hash']} - {commit['message']}\n{commit['author']} ({commit['date']})",
                size_hint_y=None,
                height=60,
                on_press=lambda x, c=commit: self.show_commit_detail(c)
            )
            self.content_layout.add_widget(btn)
    
    def show_commit_detail(self, commit):
        """Show commit detail in popup"""
        details = self.current_repo.get_commit_details(commit['full_hash'])
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        info_text = (
            f"[b]Commit:[/b] {details['hash']}\n"
            f"[b]Author:[/b] {details['author']}\n"
            f"[b]Date:[/b] {details['date']}\n"
            f"[b]Files Changed:[/b] {details['files']}\n\n"
            f"[b]Message:[/b]\n{details['message']}"
        )
        
        content.add_widget(Label(
            text=info_text,
            markup=True,
            size_hint_y=0.9
        ))
        
        close_btn = Button(text='Close', size_hint_y=0.1)
        content.add_widget(close_btn)
        
        popup = Popup(title='Commit Details', content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_files_view(self, instance):
        """Show files view"""
        self.content_layout.clear_widgets()
        if not self.current_repo:
            self.content_layout.add_widget(Label(text='No repository loaded'))
            return
        
        self.show_file_tree()
    
    def show_file_tree(self, path=''):
        """Show file tree"""
        self.content_layout.clear_widgets()
        
        if path:
            back_btn = Button(
                text='← Back',
                size_hint_y=None,
                height=40,
                on_press=lambda x: self.show_file_tree(path.rsplit('/', 1)[0] if '/' in path else '')
            )
            self.content_layout.add_widget(back_btn)
        
        items = self.current_repo.get_file_tree(self.current_branch, path)
        
        for item in items:
            if item['type'] == 'tree':
                btn = Button(
                    text=f"📁 {item['name']}",
                    size_hint_y=None,
                    height=40,
                    on_press=lambda x, p=item['path']: self.show_file_tree(p)
                )
            else:
                btn = Button(
                    text=f"📄 {item['name']}",
                    size_hint_y=None,
                    height=40,
                    on_press=lambda x, p=item['path']: self.show_file_content(p)
                )
            self.content_layout.add_widget(btn)
    
    def show_file_content(self, path):
        """Show file content in popup"""
        content_text = self.current_repo.get_file_content(self.current_branch, path)
        
        if content_text is None:
            content_text = "(Binary file or empty)"
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        text_input = TextInput(
            text=content_text,
            readonly=True,
            multiline=True,
            size_hint_y=0.9
        )
        content.add_widget(text_input)
        
        close_btn = Button(text='Close', size_hint_y=0.1)
        content.add_widget(close_btn)
        
        popup = Popup(
            title=f'File: {path}',
            content=content,
            size_hint=(0.9, 0.9)
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_stats_view(self, instance):
        """Show statistics view"""
        self.content_layout.clear_widgets()
        if not self.current_repo:
            self.content_layout.add_widget(Label(text='No repository loaded'))
            return
        
        stats = self.current_repo.get_stats()
        self.content_layout.add_widget(Label(
            text=(
                f"[b]Repository Statistics[/b]\n\n"
                f"Total Commits: {stats['total_commits']}\n"
                f"Branches: {stats['branches']}\n"
                f"Contributors: {stats['contributors']}"
            ),
            markup=True,
            size_hint_y=0.5
        ))


if __name__ == '__main__':
    GitViewerApp().run()
