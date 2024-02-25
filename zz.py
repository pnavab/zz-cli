#!/usr/bin/env python
import sys
import os
import subprocess
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
from colorama import Fore, Back, Style, init
import webbrowser
import zz_json as helpers


init()
def color_text(text, color):
  return f"{color}{text}{Style.RESET_ALL}"


def main():
  if len(sys.argv) > 1:
    match sys.argv[1]:
      case "-h":
        help()
      case "open":
        if len(sys.argv) == 3:
          open(sys.argv[2])
        elif len(sys.argv) == 2:
          print(color_text("Missing alias in command", Fore.RED))
        elif len(sys.argv) == 4 and sys.argv[3] == "-r":
          open(sys.argv[2], reload=True)
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
      case "init":
        if len(sys.argv) < 3:
          git_init()
      case _:
        print(color_text("Invalid command!", Fore.RED))
        help()
  else:
    help()

def help():
  print("="*80)
  print("Usage:")
  print(f"   Run {color_text("'zz add <alias>'", Fore.CYAN)} to add a path with a new alias")
  print(f"   Run {color_text("'zz add .'", Fore.CYAN)} to add the current path with a new alias")
  print(f"   Run {color_text("'zz open <alias>'", Fore.CYAN)} to open a previously added directory in VScode. Append '-r' to open in the same window")
  print(f"   Run {color_text("'zz start <alias>'", Fore.CYAN)} to run a previously added executable path")
  print("="*80)

def list_all():
  print(color_text("-----------------LIST-----------------", Fore.CYAN))
  print(helpers.get_all())

def open(alias, reload=False):
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

def git_init():
  if os.path.exists(".git"):
    print("Git has already been initialized here")
  else:
    try:
      commit_message = "Initial commit from zz-cli"
      subprocess.run(["git", "init"], capture_output=True, text=True)
      subprocess.run(["git", "add", "."], capture_output=True, text=True)
      subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)
      subprocess.run(["git", "branch", "-M", "main"], capture_output=True, text=True)
      github_link = input("Enter github remote link: ")
      subprocess.run(["git", "remote", "add", "origin", github_link], capture_output=True, text=True)
      subprocess.run(["git", "push", "-u", "origin", "main"], capture_output=True, text=True)
      print(f"Successfully initialized git repo at {github_link}")
    except Exception as e:
      print("Error initializing git repository")

if __name__ == "__main__":
  main()