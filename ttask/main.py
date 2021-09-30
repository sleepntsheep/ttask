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
    sort_tasks()
    
def done(task: Todo):
    task.completed ^= True
    sort_tasks()

def sort_tasks():
    global tasks
    tasks.sort(key=lambda x: x.priority, reverse=False)
    f = []
    uf = []
    for t in tasks:
        if t.completed: f.append(t)
        else: uf.append(t)
    tasks = uf + f

def get_input(win: 'curses._CursesWindow', prompt: str):
    curses.echo()
    y, x = win.getmaxyx()
    win.addstr(1, 1, prompt)
    input = win.getstr(1, len(prompt) + 2).decode()
    win.addstr(1, 1, ' '*x)
    curses.noecho()
    return input

def c_main(stdscr: 'curses._CursesWindow'):
    stdscr.keypad(True)
    stdscr.nodelay(0)
    curses.noecho()
    stdscr.refresh()

    y, x = stdscr.getmaxyx()
    task_index = 0
    key = None
    win1 = curses.newwin(y-3, x, 0, 0)
    win2 = curses.newwin(3, x, y-3, 0)

    while key != ord('q'):
        tasks_count = len(tasks)

        if task_index < 0:
            task_index = tasks_count - 1
        elif task_index > tasks_count -1:
            task_index = 0

        if tasks_count > 0: selected_task = tasks[task_index]
        else: selected_task = None

        ##### RENDERING
        win1.clear()
        win2.clear()
        
        for index, task in enumerate(tasks):
            win1.insstr(
                index+1, 1, f"({'-' if task.priority == 'Z' else task.priority}) [{ 'x' if task.completed else ' '}] {task.text}")

        # HIGHLIGHT SELECTED TASK
        win1.chgat(task_index+1, 1, curses.A_STANDOUT)

        win1.border(0)
        win2.border(0)
        win1.refresh()
        win2.refresh()

        ###### HANDLE KEYS
        key = stdscr.getch()
        if key == ord('a'):
            text = get_input(win2, 'ADD: Enter task name = ')
            if text != '':
                newtask = Todo(
                    text = text,
                    completed = False,
                    priority = 'Z', 
                )
                tasks.append(newtask)
            sort_tasks()

        elif key == ord('j') or key == 258: # DOWN
            task_index += 1
        elif key == ord('k') or key == 259: #UP
            task_index -= 1
        elif key == ord('d'): # MARK AS DONE/UNDONE
            done(selected_task)
        elif key == ord('r'): # REMOVE TASK
            if selected_task:
                del tasks[task_index]
                task_index -= 1
        elif key == ord('w'): # WRITE CHANGE TO FILE
            write(tasks)
        elif key == ord('e'): # EDIT PRIORITY
            switch_priority(selected_task)
            
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