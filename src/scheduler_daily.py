import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

import subprocess
import time
import os
import sys


from app import app
from custom_dirs import RootDirectory

def git_workflow():
    try:
        print(f"Current directory: {os.getcwd()}")
        # Set the repo path (replace with your actual path)
        repo_path = RootDirectory.path
        os.chdir(repo_path)
        print(f"Switched to: {os.getcwd()}")
        # check git is accessible
        subprocess.run(["git", "--version"], check=True)
        # Add files
        subprocess.run(["git", "add", "."], check=True)
        # Commit
        subprocess.run(["git", "commit", "-m", f"Auto commit {time.ctime()}"], check=True)
        # Optional: Push
        subprocess.run(["git", "push"], check=True)
        print("Git workflow completed")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

# Test it
git_workflow()
