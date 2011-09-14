#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

# read entire file
text = ''
with open(sys.argv[1], 'r') as f:
    text = f.read()
    
def parseCommandChunk(s):
    chunk = s
    command = chunk.replace('#{', '', 1)[:-1].strip()
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
        i = text.index("#{", i + 1)
    except:
        break
    length = 2
    while (text[i:(i+length)].count('{') != text[i:(i+length)].count('}')):
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
