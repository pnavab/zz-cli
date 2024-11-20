#!/usr/bin/env python
import sys
import os
import subprocess
import json
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from colorama import Fore, Back, Style, init
import webbrowser
import requests
import survey
import zz_json as helpers


init()
def color_text(text, color):
    return f"{color}{text}{Style.RESET_ALL}"


def main():
    if len(sys.argv) > 1:
        match sys.argv[1]:
            case "-h", "--help":
                help()
            case "open":
                if len(sys.argv) == 3:
                    project_open(sys.argv[2])
                elif len(sys.argv) == 2:
                    print(color_text("Missing alias in command", Fore.RED))
                elif len(sys.argv) == 4 and sys.argv[3] == "-r":
                    project_open(sys.argv[2], reload=True)
                else:
                    print(color_text("Invalid command!", Fore.RED))
                    help()
            case "add":
                if len(sys.argv) < 4:
                    if sys.argv[2] == ".":
                        add_current_directory()
                    else:
                        add(sys.argv[2])
                else:
                    help()
            case "rm":
                if len(sys.argv) < 4:
                    delete(sys.argv[2])
                else:
                    help()
            case "start":
                if len(sys.argv) < 4:
                    start(sys.argv[2])
                else:
                    help()
            case "list":
                list_all()
            case "ask":
                if len(sys.argv) < 3:
                    search()
                else:
                    help()
            case "create":
                if len(sys.argv) < 4:
                    git_create(sys.argv[2])
                else:
                    help()
            case "init":
                if len(sys.argv) < 3:
                    git_init()
                elif len(sys.argv) < 4:
                    git_init(sys.argv[2])
                else:
                    help()
            case "pa":
                if len(sys.argv) < 3:
                    git_push_all()
                else:
                    help()
            case "clone":
                if len(sys.argv) < 3:
                    git_clone()
                elif len(sys.argv) < 4:
                    git_clone(sys.argv[2])
                else:
                    help()
            case "make":
                if len(sys.argv) < 3:
                    make_project(sys.argv[2])
                else:
                    help()
            case _:
                print(color_text("Invalid command!", Fore.RED))
                help()
    else:
        help()


def help():
    print("="*80)
    print("Usage:")
    print(f"     Run {color_text("'zz add <alias>'", Fore.CYAN)} to add a path with a new alias")
    print(f"     Run {color_text("'zz add .'", Fore.CYAN)} to add the current path with a new alias")
    print(f"     Run {color_text("'zz open <alias>'", Fore.CYAN)} to open a previously added directory in VScode. Append '-r' to open in the same window")
    print(f"     Run {color_text("'zz start <alias>'", Fore.CYAN)} to run a previously added executable path")
    print(f"     Run {color_text("'zz ask'", Fore.CYAN)} to enable browser search mode")
    print(f"     Run {color_text("'zz init'", Fore.CYAN)} to initialize .git and commit all current content to a remote Github repository")
    print(f"     Run {color_text("'zz init <repo name>'", Fore.CYAN)} to create a remote Github repository with the name and push all current content to it")
    print(f"     Run {color_text("'zz pa'", Fore.CYAN)} to to push all code to Github using 'git add .' command")
    print(f"     Run {color_text("'zz clone <OPTIONAL: Github account>'", Fore.CYAN)} to fetch all repositories from the specified Github account and clone the selected one")
    print(f"     Run {color_text("'zz make <project_name>'", Fore.CYAN)} to create a new project in your specified projects directory")
    print("="*80)


def list_all():
    print(color_text("-----------------LIST-----------------", Fore.CYAN))
    print(helpers.get_all())


def project_open(alias, reload=False):
    project = helpers.get_directory_from_alias(alias)
    if project is None:
        print(color_text(f"Alias {alias} does not point to a directory", Fore.RED))
        return
    if project[0] == "\"" or project[0] == "\'":
        project = project[1:-1]
    try:
        if reload:
            subprocess.run(['code', '-r', project], shell=True)
        else:
            subprocess.run(['code', project], shell=True)
    except Exception as e:
        print(f"Error: {e}")


def add(alias):
    """
    Function to add an alias to the list, prompting user for a full file path to the directory
    """
    check_dir = helpers.get_directory_from_alias(alias)
    if check_dir is not None:
        print(color_text(f"Alias {alias} already points to {check_dir}", Fore.RED))
        help()
        return
    # Using PathCompleter for directory path completion
    directory = prompt('Enter the full path: ', completer=PathCompleter(), complete_while_typing=True, complete_in_thread=True)
    if helpers.add_entry(alias, directory):
        print(color_text(f"Successfully added '{alias}' pointing to '{directory}'", Fore.GREEN))
    else:
        print(color_text("Error adding pair", Fore.RED))


def add_current_directory():
    """
    Function to add the current directory path to the list, prompting user for an alias
    """
    directory = os.getcwd()
    alias = input("Enter the alias: ")
    check_dir = helpers.get_directory_from_alias(alias)
    if check_dir is not None:
        print(color_text(f"Alias {alias} already points to {check_dir}", Fore.RED))
        help()
        return
    if helpers.add_entry(alias, directory):
        print(color_text(f"Successfully added '{alias}' pointing to '{directory}'", Fore.GREEN))
    else:
        print(color_text("Error adding pair", Fore.RED))


def start(alias):
    path = helpers.get_directory_from_alias(alias)
    if path is None:
        print(color_text(f"Alias {alias} does not point to a directory", Fore.RED))
        return
    if path[0] == "\"" or path[0] == "\'":
        path = path[1:-1]
    if path[-4:] != ".exe":
        print(color_text(f"Alias '{alias}' does not point to an executable path", Fore.RED))
        return
    subprocess.run([path], shell=True)


def delete(alias):
    if helpers.remove_entry(alias):
        print(color_text(f"Alias '{alias}' removed successfully", Fore.GREEN))
    else:
        print(color_text("That alias was not found", Fore.RED))


def search():
    query = input("Enter search query: ")
    search_url = f"https://www.google.com/search?q={query}"
    webbrowser.open_new_tab(search_url)


def git_create(repo_name):
    """
    Function to create the remote repository on github.com named by the parameter
    """
    token = helpers.get_github_token()
    is_private = input("Make this repo public? Default is private. (y): ")
    if(is_private == "yes" or is_private == "y" or is_private == "Yes"):
        is_private = r"false"
    else:
        is_private = r"true"
    result = subprocess.Popen(
        [
            'wsl', 'curl',
            '-L',
            '-X', 'POST',
            '-H', 'Accept: application/vnd.github+json',
            '-H', f'Authorization: Bearer {token}',
            '-H', 'X-Github-Api-Version: 2022-11-28',
            'https://api.github.com/user/repos',
            '-d', f'{{"name": "{repo_name}", "homepage":"https://github.com", "private":{is_private},"is_template":false}}'
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    stdout, stderr = result.communicate()
    if result.returncode == 0:
        response_data = json.loads(stdout.decode())
        if "message" in response_data and response_data["message"] == "Repository creation failed.":
            print(f"Failed to create repository {repo_name}")
            return False
        else:
            print(f"Repository {repo_name} created successfully")
            return True


def git_init(repo_name = None):
    """
    Function to initialize a git repo in the current directory if it does not already exist
    If a repo name is specified in the parameters, it will first create a remote repository under that name, then initialize the current directory and push all code there
    """
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"], capture_output=True, text=True)
    
    if repo_name is not None:
        if not git_create(repo_name):
            return
    github_link = f"https://github.com/pnavab/{repo_name}.git" if repo_name is not None else None

    try:
        commit_message = "Initial commit from zz-cli"
        subprocess.run(["git", "add", "."], capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
        subprocess.run(["git", "branch", "-M", "main"], capture_output=True, text=True)
        github_link = github_link if github_link is not None else input("Enter github remote link: ")
        subprocess.run(["git", "remote", "add", "origin", github_link], capture_output=True, text=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
        print(f"Successfully initialized git repo at {github_link}")
        webbrowser.open_new_tab(github_link)
    except Exception as e:
        print("Error initializing git repository")


def git_push_all():
    commit_message = input("Commit Message: ")
    subprocess.run(['git', 'add', '.'], shell=True)
    subprocess.run(['git', 'commit', '-m', commit_message], shell=True)
    subprocess.run(['git', 'push'], shell=True)


def git_clone(account_name = "pnavab"):
    token = helpers.get_github_token()
    repositories = []
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}", 
        "X-Github-Api-Version": "2022-11-28"
    }
    if account_name == "pnavab":
        response = requests.get("https://api.github.com/user/repos", headers=headers)
    else:
        response = requests.get(f"https://api.github.com/users/{account_name}/repos", headers=headers)
    response = response.json()

    for repo in response:
        repositories.append(repo["name"])
    current_directories = os.listdir()
    filtered_repositories = [repo for repo in repositories if repo not in current_directories]

    index = survey.routines.select('Select Repository to Clone: ',    options = filtered_repositories,    focus_mark = '> ',    evade_color = survey.colors.basic('yellow'))
    selected_repo = filtered_repositories[index]
    print("selected repo is", selected_repo)
    try:
        subprocess.run(["git", "clone", f"https://github.com/{account_name}/{selected_repo}.git"], shell=True)
        print(f"Successfully cloned {selected_repo}")
        open_vscode = input("Open the repository in VSCode? (y/n): ")
        if open_vscode == "y" or open_vscode == "yes" or open_vscode == "Y" or open_vscode == "Yes":
            subprocess.run(["code", selected_repo], shell=True)
    except Exception as e:
        print(f"Error cloning repository {selected_repo}")


def make_project(directory_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f'{dir_path}/env.json', 'r') as f:
        data = json.load(f)
        projects_dir = data.get('projects_directory', None)
        if projects_dir is not None:
            new_project_dir = f"{projects_dir}/{directory_name}"
            subprocess.run(["wsl", "mkdir", new_project_dir], shell=True)
            subprocess.run(["code", new_project_dir], shell=True)
        else:
            print(color_text("No projects directory found", Fore.RED))

if __name__ == "__main__":
    main()