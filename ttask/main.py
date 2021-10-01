from ttask.todotxtio import *
import curses
import os
from os.path import expanduser

home = expanduser("~")
todotxt = home+'/todo.txt'

def write(task: Todo):
    global todotxt
    to_file(todotxt, tasks)

def switch_priority(task: Todo):
    prioritys = ['A', 'B', 'C', 'D', 'Z']
    i = prioritys.index(task.priority)
    if i < len(prioritys) -1: i += 1
    else: i = 0
    task.priority = prioritys[i]
    
def done(task: Todo):
    task.completed ^= True

def sort_tasks():
    global tasks
    tasks.sort(key=lambda x: x.priority, reverse=False)
    tasks.sort(key=lambda x: x.completed, reverse=False)

def get_input(win: 'curses._CursesWindow', prompt: str):
    y, x = win.getmaxyx()
    win.border(0)
    win.addstr(1, 1, prompt)
    win.refresh()

    input = ''
    char = win.getch()
    if char == 10 or char == curses.KEY_ENTER:
        return ''

    while char != 27: #esc
        if char == 10 or char == curses.KEY_ENTER:
            return input.replace('\n','')
        else:
            if char == 8 or char == 127 or char == curses.KEY_BACKSPACE:
                if len(input) > 0: input = input[:-1]
            else:
                input += chr(char)
            win.clear()
            win.box()
            win.addstr(1, 1, prompt+input)
            win.refresh()
            char = win.getch()

def c_main(stdscr: 'curses._CursesWindow'):
    stdscr.keypad(True)
    stdscr.nodelay(0)
    curses.noecho()
    stdscr.refresh()

    y, x = stdscr.getmaxyx()
    task_index = 0
    key = None
    win2 = stdscr.subwin(3, x, y-3, 0)

    while key != ord('q'):
        tasks_count = len(tasks)

        if task_index < 0:
            task_index = tasks_count - 1
        elif task_index > tasks_count -1:
            task_index = 0

        if tasks_count > 0: selected_task = tasks[task_index]
        else: selected_task = None

        ##### RENDERING
        stdscr.clear()
        win2.clear()
        
        for index, task in enumerate(tasks):
            stdscr.insstr(
                index+1, 1, f"({'-' if task.priority == 'Z' else task.priority}) [{ 'x' if task.completed else ' '}] {task.text}")

        # HIGHLIGHT SELECTED TASK
        stdscr.chgat(task_index+1, 1, curses.A_STANDOUT)

        stdscr.border(0)
        stdscr.refresh()

        ###### HANDLE KEYS
        key = stdscr.getch()
        if key == ord('a'):
            text = get_input(win2, 'ADD: Enter task name = ')
            if text != '' and text:
                newtask = Todo(
                    text = text,
                    completed = False,
                    priority = 'Z', 
                )
                tasks.append(newtask)
        elif key == ord('j') or key == 258: # DOWN
            task_index += 1
        elif key == ord('k') or key == 259: #UP
            task_index -= 1
        elif key == ord('d'): # MARK AS DONE/UNDONE
            done(selected_task)
        elif key == ord('r'): # REMOVE TASK
            if selected_task:
                text = get_input(win2, 'Confirm (Y,n) = ')
                if text.lower() == 'y' or text == '':
                    del tasks[task_index]
                    task_index -= 1
        elif key == ord('w'): # WRITE CHANGE TO FILE
            write(tasks)
        elif key == ord('e'): # EDIT PRIORITY
            switch_priority(selected_task)
        elif key == ord('s'):
            sort_tasks()
            
    write(tasks)
    return

def main():
    global tasks
    if not os.path.exists(todotxt):
        open(todotxt, 'w').close()
    tasks = from_file(todotxt)
    sort_tasks()
    return curses.wrapper(c_main)

if __name__ == '__main__':
    exit(main()) 