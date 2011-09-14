#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

OPEN = '{'
CLOSE = '}'

if (len(sys.argv) > 1):
    if sys.argv[1] == '--paren':
        del(sys.argv[1])
        OPEN = '('
        CLOSE = ')'
    elif sys.argv[1] == '--square':
        del(sys.argv[1])
        OPEN = '['
        CLOSE = ']'
    elif sys.argv[1] == '--curly':
        del(sys.argv[1])
        OPEN = '{'
        CLOSE = '}'
    elif sys.argv[1] == '--angle':
        del(sys.argv[1])
        OPEN = '<'
        CLOSE = '>'

if len(sys.argv) < 2:
    print("Usage: copypasta.py [--paren|--square|--curly] [input file]")
    print(" --curly:  #{ ... } (default)")
    print(" --paren:  #( ... )")
    print(" --square: #[ ... ]")
    print(" --angle:  #< ... >")
    exit(1)
    
# read entire file
text = ''
with open(sys.argv[1], 'r') as f:
    text = f.read()
    
def parseCommandChunk(s):
    chunk = s
    command = chunk.replace('#' + OPEN, '', 1)[:-1].strip()
    fullCommand = command
    token = command.split()[0]
    command = command.replace(token, '', 1).strip()
    if token == 'for':
        key = command.split()[0]
        command = command.replace(key, '', 1).strip()
        inCheck = command.split()[0]
        if inCheck != 'in':
            sys.stderr.write("Error: 'in' expected.\n")
            exit(1)
        command = command.replace(inCheck, '', 1).strip()
        values = json.loads(command)
        return [None, 'for', key, values]
    elif token == 'end':
        return [None, 'end']
    else:
        return [None, 'var', fullCommand]
    
chunkList = []
    
# first pass: scan for places that look like #{ ... }
i = -1
while True:
    chunkStart = i + 1
    try:
        i = text.index('#' + OPEN, i + 1)
    except:
        break
    length = 2
    while (text[i:(i+length)].count(OPEN) != text[i:(i+length)].count(CLOSE)):
        length += 1
    # append preceding text chunk
    chunkList.append([text[chunkStart:i], 'text'])
    # append #{ ... } chunk
    chunkList.append(parseCommandChunk(text[i:(i+length)]))
    i += length - 1

chunkList.append([text[(i + 1):len(text)], 'text'])

# second pass: unroll the loops

def repeatChunkList(chunkList, key, values, localVars):
    for v in values:
        localVars[key] = v
        chunkIndex = 0
        while chunkIndex < len(chunkList):
            chunk = chunkList[chunkIndex]
            if chunk[1] == 'text':
                sys.stdout.write(chunk[0])
                chunkIndex += 1
            elif chunk[1] == 'for':
                # find matching end chunk
                balance = 1
                endChunkIndex = chunkIndex + 1
                while balance > 0:
                    if chunkList[endChunkIndex][1] == 'end':
                        balance -= 1
                    elif chunkList[endChunkIndex][1] == 'for':
                        balance += 1
                    if (balance == 0):
                        break
                    endChunkIndex += 1
                repeatChunkList(chunkList[(chunkIndex + 1):endChunkIndex], chunk[2], chunk[3], localVars)
                chunkIndex = endChunkIndex + 1
            elif chunk[1] == 'var':
                sys.stdout.write(str(eval(chunk[2], None, localVars)))
                chunkIndex += 1
    localVars[key] = None
                
repeatChunkList(chunkList, None, [None], dict())
