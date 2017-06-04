import os
import sys
import glob

def get_cwd():
    return os.environ.get("CWD", os.getcwd())

def compute_home_directory(path=""):
    # print("cHD path: " + path)
    home=os.environ.get("HOME", os.path.expanduser("~"))
    
    # print("cHD HOME: " + home)
    home_replaced=path.replace("~",home,1)
    # print("cHD repl: " + home_replaced)
    return path if home_replaced == "" else home_replaced

def compute_absolute_path(path=""):
    if not path.startswith("."):
        return path
    if path == "." or path == "./":
        return get_cwd()

    cwd=get_cwd()
    path_current=path
    # print("path_current: " + path_current)
    nr_parent_dirs=path_current.count("../")
    # print("nr_parent_dirs: " + str(nr_parent_dirs))
    nr_dirs_cwd=cwd.count("/")
    # print("nr_dirs_cwd: " + str(nr_dirs_cwd))

    if nr_parent_dirs > nr_dirs_cwd:
        print("Error: Invalid path '" + path + "' for current working directory '" + cwd + "'.")
        sys.exit(1)

    cwd_slash_positions=( [pos for pos, char in enumerate(cwd) if char == "/"])
    # print("cwd_slash_positions: ")
    # print(cwd_slash_positions)
    cwd_cut=cwd[:(cwd_slash_positions[nr_dirs_cwd - nr_parent_dirs])+1]
    # print("cwd_cut: " + cwd_cut)

    path_without_parents=path.replace("../", "")
    path_without_relative_path=path_without_parents.replace("./", "")

    # print("cAP cwd : "  + cwd)
    absolute_path=cwd_cut + path_without_relative_path
    # print("cAP abso: " + absolute_path)
    return absolute_path

def check_if_file_exists(path=None):
    return glob.glob(path)
