import os
from pcr import constant

default_protocol = [
    {'Label' : 1, 'Temp' : 60, 'Time' : 5}, 
    {'Label' : 2, 'Temp' : 90, 'Time' : 5}, 
    {'Label' : 3, 'Temp' : 65, 'Time' : 5},
    {'Label' :'GOTO','Temp' : 2,'Time' : 2},
    {'Label' : 4, 'Temp' : 40, 'Time' : 5}
]

PCR_PATH = 'C:\\mPCR'
RECENT_PROTOCOL_FILENAME = 'recent_protocol_python.txt'

class Protocol():
    def __init__(self, name, actions):
        self.name = name
        self.actions = actions

    def __getitem__(self, idx):
        return self.actions[idx]
    
    def __str__(self):
        _str = 'name : ' + self.name + '\n'
        for action in self.actions:
            _str += f'Label : {action["Label"]:>4}, Temp : {action["Temp"]:>3}, Time : {action["Time"]:>3}\n'
        return _str

    def __len__(self):
        return len(self.actions)

    

# get protocols
def list_protocols():
    # filtering extension
    files = list(filter(lambda x : x[-4:] == '.txt', os.listdir(constant.PATH)))
    protocols = [file[:-4] for file in files]   # slicing extension
    return protocols

# saving protocol
def save_protocol(protocol):
    path = os.path.join(constant.PATH, protocol.name) # protocol path
    actions = check_protocol(protocol)    # check protocol

    with open(path, 'w') as file:   # open protocol file
        # actions to text list ('label'\t'temp'\t'time')
        lines = ['{}\t{}\t{}'.format(*action.values()).strip() for action in actions]
        # write text list
        file.write('\n'.join(lines))

# loading protocol
def load_protocol(protocol_name):
    path = os.path.join(constant.PATH, protocol_name) # protocol path

    with open(path + ".txt", 'r') as file:   # open protocol file
        protocol_keys = ['Label', 'Temp', 'Time'] # protocol keys 
        lines = file.read().strip().split('\n')   # read text lines
        # list to dict (text to actions)  
        actions = [dict(zip(protocol_keys, line.split('\t'))) for line in lines] 
        # check protocol and return protocol
        actions = check_protocol(actions)
        return Protocol(protocol_name, actions)

# check protocol is valid 
def check_protocol(protocol):
    line_number = 0
    current_label = 1
    actions = []

    # Check Protocol (save & load)
    for line in protocol:
        line_number += 1

        # unpacking action to (label, temp, time)
        # Check the line
        label, temp, time = list(map(lambda x : int(x) if type(x) is str and x.isdigit() else x, list(line.values())))
        
        # check the label
        if label == 'SHOT':
            pass     # TODO : SHOT line check
    
        if label == 'GOTO':     # GOTO action check
            if current_label != 0 and current_label >= temp: 
                if not 1 <= time <= 100: 
                    print('Invalid GOTO count(1~100), line %d' %line_number)
                    break
            else:
                print('Invalid GOTO target label, line %d' %line_number)
                break
        # Normal action check 
        if type(label) is int:
            # protocol data can not be splited into label, temp, time.
            if len(line) != 3:
                print('Invalid protocol data, line %d' %line_number)
                break
            # label value is incorrect.
            if label != current_label:
                print('Invalid label value, line %d' %line_number)
                break
            current_label += 1

        # do not enter into this block
        else:
            pass
        
        actions.append({'Label' : label, 'Temp' : temp, 'Time' : time})
    return actions

def loadRecentProtocolName():
    try:
        with open(PCR_PATH + '\\' + RECENT_PROTOCOL_FILENAME, 'r') as file:
            protocol_name = file.readline()
            file.close()
        
        return protocol_name
    except FileNotFoundError as err:
        return

def saveRecentProtocolName(protocol_name=''):
    try:
        with open(PCR_PATH + '\\' + RECENT_PROTOCOL_FILENAME, 'w') as file:
            file.write(protocol_name)
            file.close()
        
        return protocol_name
    except FileNotFoundError as err:
        return
        



# print(list_protocols())

# #proto = load_protocol('test.txt')
# proto = load_protocol('shortProtocol.txt')
# proto.name = 'asdasd.txt'
# print(proto)
# save_protocol(proto)