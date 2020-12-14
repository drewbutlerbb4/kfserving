
from aif360.metrics import BinaryLabelDatasetMetric
import sys
from subprocess import PIPE, run


import enum

class ParseItem(enum.Enum):
    DATA = 0
    OBJECT = 1
    LIST = 2

def print_info(events, depth_stack, item_stack, cur_item):
    print("************************* Info ***********************************")
    #print(events)
    print(depth_stack)
    #print(item_stack)
    print(cur_item)

def parse_events(stdout):
    line_split = stdout.split('\n')
    line_iter = iter(line_split)

    depth_stack = [] # A stack to describe what is currently being parsed
    item_stack = []
    cur_item = {"key": "Data", "value": {}}

    events = []

    while True:
        try:
            line = next(line_iter).strip()
            if 'Data,' in line:
                depth_stack.append(ParseItem.DATA)
                item_stack.append(cur_item)
            elif '{' in line:
                depth_stack.append(ParseItem.OBJECT)
                item_stack.append(cur_item)
                if "\"" in line:
                    key = line.split('\"')[1]
                    cur_item = {"key": key, "value": {}}
                else:
                    cur_item = {"value": {}}
            elif '}' in line:
                if depth_stack.pop() != ParseItem.OBJECT:
                    print("Parsing failed: invalid string")
                    sys.exit()
                next_item = item_stack.pop()
                if "key" in cur_item.keys():
                    next_item["value"][cur_item["key"]] = cur_item["value"]
                    cur_item = next_item
                else:
                    try:
                        next_item["value"].append(cur_item["value"])
                        cur_item = next_item
                    except: # Root case
                        events.append(cur_item["value"])

                        depth_stack = []
                        item_stack = []
                        cur_item = {"key": "Data", "value": {}}
            elif '[' in line:
                depth_stack.append(ParseItem.LIST)
                item_stack.append(cur_item)
                if "\"" in line:
                    key = line.split('\"')[1]
                    cur_item = {"key": key, "value": []}
                else:
                    cur_item = {"value": []}
            elif ']' in line:
                #print_info(events, depth_stack, item_stack, cur_item)
                if depth_stack.pop() != ParseItem.LIST:
                    print("Parsing failed: invalid string")
                    sys.exit()
                next_item = item_stack.pop()
                if "key" in cur_item.keys():
                    next_item["value"][cur_item["key"]] = cur_item["value"]
                    cur_item = next_item
                else:
                    try:
                        next_item["value"].append(cur_item["value"])
                        cur_item = next_item
                    except:  # Root case
                        events.append(cur_item["value"])

                        depth_stack = []
                        item_stack = []
                        cur_item = {"key": "Data", "value": {}}
            elif len(depth_stack) > 0:
                try:
                    cur_item["value"].append(line.replace(',', ''))
                except:
                    key = line.split('\"')[1]
                    value = line[line.index(":") + 1: len(line) - 1]
                    cur_item["value"][key] = value
        except:
            for x in range(0, len(events)):
                print("Event (", x, "):", events[x])
            return events

command = ['sh', './get_logs.sh']
result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
#print(result)
#print(type(result.stdout))
#print(result.returncode, result.stdout, result.stderr)
events = parse_events(result.stdout)
print(events)

event_pairs = []
for event_iter in range(0, len(events), 2):
    event_pairs.append({"data": events[event_iter], "response": events[event_iter + 1]})