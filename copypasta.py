#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
For loops for text files!
"""

import sys
import json

OPEN = '#{'
CLOSE = '}'

def parse_command_chunk(chunk):
    """
    parse a command block and return chunk structure
    """
    command = chunk.replace(OPEN, '', 1)[:-1].strip()
    full_command = command
    token = command.split()[0]
    command = command.replace(token, '', 1).strip()
    if token == 'for':
        key = command.split()[0]
        command = command.replace(key, '', 1).strip()
        in_check = command.split()[0]
        if in_check != 'in':
            sys.stderr.write("Error: 'in' expected.\n")
            exit(1)
        command = command.replace(in_check, '', 1).strip()
        values = json.loads(command)
        return [None, 'for', key, values]
    elif token == 'end':
        return [None, 'end']
    else:
        return [None, 'var', full_command]
        
def repeat_chunk_list(chunk_list, key, values, local_vars):
    """
    traverse a chunk list and recurse if necessary
    """
    for value in values:
        local_vars[key] = value
        chunk_index = 0
        while chunk_index < len(chunk_list):
            chunk = chunk_list[chunk_index]
            if chunk[1] == 'text':
                sys.stdout.write(chunk[0])
                chunk_index += 1
            elif chunk[1] == 'for':
                # find matching end chunk
                balance = 1
                end_chunk_index = chunk_index + 1
                while balance > 0:
                    if chunk_list[end_chunk_index][1] == 'end':
                        balance -= 1
                    elif chunk_list[end_chunk_index][1] == 'for':
                        balance += 1
                    if (balance == 0):
                        break
                    end_chunk_index += 1
                repeat_chunk_list(
                    chunk_list[(chunk_index + 1):end_chunk_index], 
                    chunk[2], chunk[3], local_vars)
                chunk_index = end_chunk_index + 1
            elif chunk[1] == 'var':
                sys.stdout.write(str(eval(chunk[2], None, local_vars)))
                chunk_index += 1
    local_vars[key] = None
    
    
def handle_file(path):
    """
    copypasta an input file
    """
    # read entire file
    whole_text = ''
    with open(path, 'r') as fin:
        whole_text = fin.read()
    
    chunk_list = []
    
    # first pass: scan for places that look like #{ ... }
    i = -1
    while True:
        chunk_start = i + 1
        try:
            i = whole_text.index(OPEN, i + 1)
        except StandardError:
            break
        length = 2
        while (whole_text[i:(i+length)].count(OPEN[-1]) != 
            whole_text[i:(i+length)].count(CLOSE)):
            length += 1
        # append preceding text chunk
        chunk_list.append([whole_text[chunk_start:i], 'text'])
        # append #{ ... } chunk
        chunk_list.append(parse_command_chunk(whole_text[i:(i+length)]))
        i += length - 1

    chunk_list.append([whole_text[(i + 1):len(whole_text)], 'text'])

    # second pass: unroll the loops
    repeat_chunk_list(chunk_list, None, [None], dict())

if (len(sys.argv) > 1):
    if sys.argv[1] == '--tags':
        del(sys.argv[1])
        OPEN = sys.argv[1]
        del(sys.argv[1])
        CLOSE = sys.argv[1]
        del(sys.argv[1])

if len(sys.argv) < 2:
    print("Usage: copypasta.py [--tags OPEN CLOSE] [input file]")
    print("  You may specify your own OPEN and CLOSE tags, by default " +
          "they are '#{' and '}'.")
    exit(1)
    
handle_file(sys.argv[1])
