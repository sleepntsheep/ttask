import curses
from curses.textpad import Textbox
import time
import todotxtio
import os
import datetime
from os.path import expanduser
home = expanduser("~")

todotxt = home+'/todo.txt'

def write(task: todotxtio.Todo):
    global todotxt
    todotxtio.to_file(todotxt, tasks)

def switch_priority(task: todotxtio.Todo):
    prioritys = [None, 'A', 'B', 'C']
    i = prioritys.index(task.priority)
    if i < len(prioritys) -1: i += 1
    else: i = 0
    task.priority = prioritys[i]
    
def done(task: todotxtio.Todo):
    time_object = datetime.datetime.today()
    date = str(time_object)[0:10]
    if not task.completed:
        task.completed = True
        task.completion_date = date
    elif task.completed:
        task.completed = False
        task.completion_date = None

def sort_tasks():
    global tasks
    finished = []
    unfinished = []
    for task in tasks:
        if task.completed:
            finished.append(task)
        else:
            unfinished.append(task)
    unfinished_p = []
    for task in unfinished:
        if task.priority == 'A':
            unfinished_p.append(task)
    for task in unfinished:
        if task.priority == 'B':
            unfinished_p.append(task)
    for task in unfinished:
        if task.priority == 'C':
            unfinished_p.append(task)
    for task in unfinished:
        if task.priority == None:
            unfinished_p.append(task)
    tasks = unfinished_p + finished

def get_input(win: 'curses._CursesWindow', prompt: str):
    curses.echo()
    y, x = win.getmaxyx()
    win.addstr(1, 1, prompt)
    input = win.getstr(1, len(prompt) + 2).decode()
    win.addstr(1, 1, ' '*x)
    win.border()
    win.refresh()
    curses.noecho()
    return input

def c_main(stdscr: 'curses._CursesWindow'):
    stdscr.keypad(True)
    stdscr.nodelay(0) ## getch won't block
    curses.noecho()
    stdscr.refresh()

    y, x = stdscr.getmaxyx()

    task_index = 0
    property_index = 1
    key = ''
    column = 0
    time_object = datetime.datetime.today()
    date = str(time_object)[0:10]
    property_count = 8

    win1 = curses.newwin(y-3, int(x/2), 0, 0)
    win2 = curses.newwin(y-3, x - int(x/2), 0, int(x/2))
    win3 = curses.newwin(3, x, y-3, 0)

    while key != ord('q'):
        tasks_count = len(tasks)

        if task_index < 0:
            task_index = tasks_count - 1
        elif task_index > tasks_count -1:
            task_index = 0

        if property_index < 1:
            property_index = property_count
        elif property_index > property_count:
            property_index = 1

        if tasks_count > 0: selected_task = tasks[task_index]
        else: selected_task = None

        ##### RENDERING
        win1.clear()
        win2.clear()
        win3.clear()
        
        # RENDER ALL TASK
        for index, task in enumerate(tasks):
            win1.insstr(
                index+1, 1, f"[{'x' if task.completed else ' '}] {task.text}")

        # TASK PROPERTY
        if selected_task != None:
            property_count = len(vars(selected_task).items())
            win2.insstr(1, 1, f'Task: {selected_task.text}')
            win2.insstr(2, 1, f'Completed: {selected_task.completed}')
            win2.insstr(3, 1, f'Priority: {selected_task.priority}')
            win2.insstr(4, 1, f'Tags: {selected_task.tags}')
            win2.insstr(5, 1, f'Contexts: {selected_task.contexts}')
            win2.insstr(6, 1, f'Projects: {selected_task.projects}')
            win2.insstr(7, 1, f'Creation Date: {selected_task.creation_date}')
            win2.insstr(8, 1, f'Completion Date: {selected_task.completion_date}')

        else:
            property_count = 0

        # HIGHLIGHT SELECTED TASK
        if column == 0:
            win2.chgat(property_index, 1, curses.A_BOLD)
            win1.chgat(task_index+1, 1, curses.A_STANDOUT)
        elif column == 1:
            win1.chgat(task_index+1, 1, curses.A_BOLD)
            win2.chgat(property_index, 1, curses.A_STANDOUT)

        win1.border(0)
        win2.border(0)
        win3.border(0)
        win1.refresh()
        win2.refresh()

        ###### HANDLE KEYS
        key = stdscr.getch()
        if key == ord('a'):
            text = get_input(win3, 'ADD: Enter task name = ')
            if text != '':
                newtask = todotxtio.Todo(
                    text=text,
                    completed=False,
                    creation_date=date,
                    priority = None, 
                    tags = None,
                )
                tasks.append(newtask)
            sort_tasks()

        elif key == ord('j') or key == 258: # DOWN
            if column == 0:
                task_index += 1
            elif column == 1:
                property_index += 1
        elif key == ord('k') or key == 259: #UP
            if column == 0:
                task_index -= 1
            elif column == 1:
                property_index -= 1
        elif key == ord('d'): # MARK AS DONE/UNDONE
            if column == 0:
                done(selected_task)
        elif key == ord('r'): # REMOVE TASK
            if column == 0:
                if selected_task != None: del tasks[task_index]
                task_index -= 1
        elif key in [ord('h'), ord('l'), 260, 261]:
            column ^= True
        elif key == ord('w'):
            write(tasks)
        elif key == ord('e'):
            if column == 1:
                if property_index == 1:
                    text = get_input(win3, 'Enter new task name : ')
                    selected_task.text = text
                elif property_index == 2:
                    done(selected_task)
                elif property_index == 3:
                    switch_priority(selected_task)
        elif key == ord('f'):
            sort_tasks()
            task_index = 0
            
        ####
        win3.refresh()
        
        # DELAY

    # WRITE CHANGES TO FILE
    write(tasks)
    return

def main():
    global tasks
    if not os.path.exists(todotxt):
        open(todotxt, 'w').close()
    tasks = todotxtio.from_file(todotxt)
    sort_tasks()
    return curses.wrapper(c_main)

if __name__ == '__main__':
    exit(main()) 
