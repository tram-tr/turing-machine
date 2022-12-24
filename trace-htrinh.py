#!/usr/bin/env python3
import sys
import os
import time
import csv
from tqdm import tqdm
from collections import deque

class Tape(object):
    def __init__(self, state, left = [], head = '_', right = []):
        self.state = state
        self.left = left
        self.head = head
        self.right = right

    def __str__(self):
        return ''.join(self.left) + ',' + self.state + ',' + self.head + ',' + ''.join(self.right)

class NTM(object):
    def __init__(self, file):
        self.input_file = file
        self.T = {} 
        with open(self.input_file) as file:
            for index, line in tqdm(enumerate(file), desc='Reading TM file...'):
                if index == 0:
                    self.name = line.rstrip().split(',')[0]
                elif index == 1:
                    self.states = list(filter(None, line.rstrip().split(',')))
                elif index == 2:
                    self.sigma = list(filter(None, line.rstrip().split(',')))
                elif index == 3:
                    self.gamma = list(filter(None, line.rstrip().split(',')))
                elif index == 4:
                    self.start = line.rstrip().split(',')[0]
                elif index == 5:
                    self.accept = list(filter(None, line.rstrip().split(',')))
                elif index == 6:
                    self.reject = line.rstrip().split(',')[0]
                else:
                    self.read_transition(line.rstrip())

    # read TM machine transitions
    def read_transition(self, transition):
        transition = transition.split(',')
        if (len(transition) == 3):
            curr, input_char, next = transition[0:3]
            write_char = input_char
            direction = 'R'
        else:
            curr, input_char, next, write_char, direction = transition[0:5]

        if curr not in self.T:
            self.T[curr] = {}
        if input_char not in self.T[curr]:
            self.T[curr][input_char] = []
        self.T[curr][input_char].append((next, write_char, direction))

    # get the next transitions
    def get_transition(self, tape):
        curr_state = tape.state
        head = tape.head

        # if there is no transition, return none
        if head not in self.T[curr_state]:
            return None
        else:
            new_tapes = []
            for transition in self.T[curr_state][head]:
                next, replace_char, direction = transition
                # replace curr head
                head = replace_char
                left = tape.left
                right = tape.right

                # get direction and update the tape
                if (direction == 'R'):
                    if len(tape.right) == 0:
                        right = ['_']
                    new_tape = Tape(state=next, left=left+[head], head=right[0], right=right[1:])

                else:
                    if len(tape.left) == 0:
                        left = ['_']
                    new_tape = Tape(state=next, left=left[:-1], head=left[-1], right=[head]+right)

                new_tapes.append(new_tape)
            return new_tapes

    # trace using bfs
    def trace(self, string, max_steps, output_file):
        string_list = list(string)
        tape = Tape(state = self.start, head = string_list[0], right = string_list[1:])
        queue = deque([(tape,0, [tape])])
        visited = {}
        steps = 0
        accept = False
        while len(queue) > 0 and steps < max_steps:
            curr, level, path = queue.popleft()    

            # keep track with the depth of the tree
            if level not in visited:
                visited[level] = []

            visited[level].append(tape)
            
            # check if current state is an accept state
            if (curr.state in self.accept):
                accept = True
                break

            if (curr.state in self.reject):
                continue
            
            # get next transitions
            next = self.get_transition(curr)

            # no next transition => reject states
            if next == None:
                continue
            else:
                for tape in next:
                    queue.append((tape, level+1, path+[tape]))
            steps += 1


        print(f'Depth of the tree of configurations: {max(visited.keys())}.')
        output_file.write(f'Depth of the tree of configurations: {max(visited.keys())}.\n')

        print(f'Total transitions: {steps}.')
        output_file.write(f'Total transitions: {steps}.\n')

        if (accept == True):
            print(f'String {string} accepted in {level} transitions.')
            output_file.write(f'String {string} accepted in {level} transitions. \n')
            for tape in path:
                print(tape)
                output_file.write(f'{tape}\n')

        else:
            if steps < max_steps:
                print(f'String {string} rejected in {max(visited.keys())} transitions.')
                output_file.write(f'String {string} rejected in {max(visited.keys())} transitions.\n')

            else:
                print(f'Execution stopped after {max_steps} max steps limit')
                output_file.write(f'Execution stopped after {max_steps} max steps limit.\n')
        
    
def main():
    file = input('Enter TM file name: ')
    machine = NTM(file)

    # if the file already exists, remove the current one
    file_name = machine.name.replace(' ', '')
    if os.path.exists(file_name+'-output.txt'):
        os.remove(file_name+'-output.txt')

    output_file = open(file_name+'-output.txt', 'a')
    output_file.write(f'Name of the machine: {machine.name}.\n\n')
    while (True): 
        input_string = input('Enter input string or endinput: ')
        if input_string == 'endinput':
            break
    
        max_steps = int(input('Enter max steps: '))
    
        print()
        print(f'Name of the machine: {machine.name}')
        print(f'Initial input string: {input_string}')
        output_file.write(f'Initial input string: {input_string}\n')

        machine.trace(input_string, max_steps, output_file)
        print()
        output_file.write('\n')
        
    output_file.close()
  

if __name__ == '__main__':
    main()
