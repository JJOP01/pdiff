#!/usr/bin/env python3

import sys
import re

def read_entire_file(file_path):
    with open(file_path) as f:
        return f.read()

IGNORE = 'I'
ADD    = 'A'
REMOVE = 'R'
    
def trace_tables(distances, actions):
    for row in range(len(distances)):
        for col in range(len(distances[row])):
            item = distances[row][col]
            action = actions[row][col]
            print(f"{item} ({action})".ljust(6), end=' ')
        print()
    print()        

def edit_distance(s1, s2):
    m1 = len(s1)
    m2 = len(s2)
    
    distances = []
    actions = []
    for _ in range(m1 + 1):
        distances.append([0] * (m2 + 1))
        actions.append(['-'] * (m2 + 1))

    distances[0][0] = 0
    actions[0][0] = IGNORE
    for n2 in range(1, m2 + 1):
        n1 = 0
        distances[n1][n2] = n2
        actions[n1][n2] = ADD

    for n1 in range(1, m1 + 1):
        n2 = 0
        distances[n1][n2] = n1
        actions[n1][n2] = REMOVE

    for n1 in range(1, m1 + 1):
        for n2 in range(1, m2 + 1):
            if s1[n1-1] == s2[n2-1]:
                distances[n1][n2] = distances[n1-1][n2-1]
                actions[n1][n2] = IGNORE
                continue

            remove = distances[n1-1][n2]
            add = distances[n1][n2-1]
            
            distances[n1][n2] = remove
            actions[n1][n2] = REMOVE

            if distances[n1][n2] > add:
                distances[n1][n2] = add
                actions[n1][n2] = ADD

            distances[n1][n2] += 1

    patch = []
    n1 = m1
    n2 = m2
    while n1 > 0 or n2 > 0:
        action = actions[n1][n2]
        if action == ADD:
            n2 -= 1
            patch.append((ADD, n2, s2[n2]))
        elif action == REMOVE:
            n1 -= 1
            patch.append((REMOVE, n1, s1[n1]))
        elif action == IGNORE:
            n1 -= 1
            n2 -= 1
        else:
            assert False, "unreachable action"
    patch.reverse()
    return patch
    
def diff_subcommand(program_name, argv):
    if len(argv) < 2:
        print(f'Usage: {program_name} diff {SUBCOMMANDS["diff"].signature}')
        print("ERROR: not enough files were provided to generate difference")
        exit(1)
        
    file_path1, *argv = argv
    file_path2, *argv = argv
    lines1 = read_entire_file(file_path1).splitlines()
    lines2 = read_entire_file(file_path2).splitlines()

    patch = edit_distance(lines1, lines2)
    for (action, n, line)  in patch:
        print(f"{action} {n} {line}")
        
PATCH_LINE_REGEXP = re.compile("([AR]) (\d+) (.*)")

def line_as_patch_action(line):
    return  PATCH_LINE_REGEXP.match(line)
        
def patch_subcommand(program_name, argv):
    if len(argv) < 2:
        print(f'Usage: {program_name} patch  {SUBCOMMANDS["patch"].signature}')
        print("ERROR: not enough files were provided to patch a file")
        exit(1)
    file_path, *argv = argv
    patch_path, *argv = argv
    
    lines = read_entire_file(file_path).splitlines()
    patch = []
    ok = True
    for (row, line) in enumerate(read_entire_file(patch_path).splitlines()):
        if len(line) == 0: continue
        m = line_as_patch_action(line)
        if m is None:
            print(f"{patch_path}:{row+1}: Invalid patch action: {line}")
            ok = False
            continue
        patch.append((m.group(1), int(m.group(2)), m.group(3)))
    if not ok:
        exit(1)

    for (action, row, line) in reversed(patch):
        if action == ADD:
            lines.insert(row, line)
        elif action == REMOVE:
            lines.pop(row)
        else:
            assert False, "uncreachable"

    with open(file_path, "w") as f:
        for line in lines:
            f.write(line)
            f.write('\n')
            
def help_subcommand(program_name, argv):
    if len(argv) == 0:
        usage(program_name)
        exit(0)
    subcommand, *argv = argv
    if subcommand not in SUBCOMMANDS:
        usage(program_name)
        print(f"ERROR: unknown subcommand {subcommand}")
        exit(1)

    print(f"Usage: {subcommand} {SUBCOMMANDS[subcommand].signature}")
    print(f"    {SUBCOMMANDS[subcommand].description}")
    exit(0)

class SubCommand:
    def __init__(self, run, signature, description):
        self.run = run
        self.signature = signature
        self.description = description        
    
SUBCOMMANDS = {
    "diff": SubCommand( 
        run = diff_subcommand,
        signature = "<file1> <file2>",
        description = "print the difference between files to stdout"
    ),
    "patch": SubCommand(
        run = patch_subcommand,
        signature = "<file1> <file.patch>",
        description = "patch the file with the given patch"
    ),
    "help": SubCommand(
        run = help_subcommand,
        signature = "[subcommand]",
        description = "print this help"
    )
}

def usage(program_name):
    print(f"Usage: {program_name} <SUBCOMMAND> [OPTIONS]")
    print("SubCommands:")
    width = max([len(f'    {name} {subcmd.signature}')
                    for (name, subcmd) in SUBCOMMANDS.items()])
    for (name, subcmd) in SUBCOMMANDS.items():
        command = f'{name} {subcmd.signature}'.ljust(width)
        print(f'    {command}    {subcmd.description}')

def closest_subcommand(subcommand):
    candidates = sorted([name
                         for (name, definition) in SUBCOMMANDS.items()
                         if len(edit_distance(subcommand, name)) < 4])
    if len(candidates) > 0:
        print(f'--- Did you mean "{candidates[0]}"?')
    
        
def main():
    assert len(sys.argv) > 0
    program_name, *argv  = sys.argv
    
    if len(argv) == 0:
        usage(program_name)
        exit(1)

    subcommand, *argv = argv
    if subcommand not in SUBCOMMANDS:
        usage(program_name)
        print(f"ERROR: unknown subcommand {subcommand}")
        closest_subcommand(subcommand)
        exit(1)

    SUBCOMMANDS[subcommand].run(program_name, argv)
    
if __name__ == "__main__" and "__file__" in globals():
    main()
