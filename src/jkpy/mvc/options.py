from __future__ import annotations
from typing import List
from typing import Any
from typing import Optional
import sys
import tty
import termios
from jkpy.utils import Ansi

class OptionsModel:
    def __init__(self, prompt: str, options: List[str]):
        self.prompt=prompt
        self.options=options
        self.selected=0
        self.result=None
        self.is_running=True
        self._observers=[]
        
    def add_observer(self, observer) -> None:
        self._observers.append(observer)
        
    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update()
        
    def select_previous(self) -> None:
        self.selected=(self.selected-1)%len(self.options)
        self.notify_observers()
        
    def select_next(self) -> None:
        self.selected=(self.selected+1)%len(self.options)
        self.notify_observers()
        
    def confirm_selection(self) -> None:
        self.result=self.options[self.selected]
        
    def stop(self):
        self.is_running=False
        
class OptionsView:
    def __init__(self, model: OptionsModel):
        self.model: OptionsModel=model
        self.is_first_render: bool=True
        self.lines_to_overwrite: int=0
    
    def clear(self) -> None:
        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1)) 
            sys.stdout.write(Ansi.erase_line()) 
        sys.stdout.flush()
        
    def update(self):
        self.render()
        
    def render(self):
        self.lines_to_overwrite=len(self.model.options)+len(self.model.header.splitlines())
        
        if not self.is_first_render:
            self.clear()
            
        sys.stdout.write(self.model.prompt+"\n")
        for idx, opt in enumerate(self.model.options):
            if idx==self.model.selected:
                sys.stdout.write(f">{Ansi.CYAN}{opt}{Ansi.RESET}<")
            else:
                sys.stdout.write(f" {Ansi.CYAN}{opt}{Ansi.RESET}")
        
        sys.stdout.flush()
        self.is_first_render=False
    
    def reset(self):
        self.is_first_render=True
        
class OptionsController:
    def __init__(self, model: OptionsModel, view: OptionsView):
        self.model: OptionsModel=model
        self.view: OptionsView=view

    def get_key(self) -> str|Any:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch=="\x1b":
                ch2=sys.stdin.read(1)
                if ch2=="[":
                    ch3=sys.stdin.read(1)
                    return f"\x1b[{ch3}"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
    def handle_input(self, key: str):
        if key=="\x1b[A":
            self.model.select_previous()
        elif key=="\x1b[B":
            self.model.select_next()
        elif key=="\n" or key=="\r":
            self.model.confirm_selection()
            self.model.stop()
        elif key=="q" or key=="Q":
            self.model.stop()
            
    def run(self) -> Optional[str]:
        self.view.render()
        while self.model.is_running:
            key=self.get_key()
            self.handle_input(key)
            
        return self.model.result

class Options:
    @staticmethod
    def select(prompt: str, options: List[str]) -> Optional[str]:
        model=OptionsModel(prompt, options)
        view=OptionsView(model)
        controller=OptionsController(model, view)
        
        model.add_observer(view)
        try:
            return controller.run()
        except KeyboardInterrupt:
            model.stop()





def confirm(question: str) -> bool:
    print(f"{question} (y/n)", end="", flush=True)
    
    def read_yn():
        fd=sys.stdin.fileno()
        old_settings=termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch=sys.stdin.read(1).lower()
                if ch in ("y", "n", "\n", "\r"):
                    return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    while True:        
        key=read_yn()
        if key=="y":
            selected=True
        if key=="n":
            selected=False
        if key in ("\n", "\r"):
            return selected

def text_input(question: str, default: str="") -> Optional[str]:
    print(f"\x1b[1A", end="")
    Print.yellow("\x1b[K'enter' to confirm, 'escape' to cancel")
    print(question)
    # print("\x1b[1A") # cursor up 1 line
    # print("\x1b[3C") # cursor right 3 characters
    
    def read_text():
        fd=sys.stdin.fileno()
        old_settings=termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            text=default
            while True:
                ch=sys.stdin.read(1)
                if ch=="\x1b":
                    ch2=sys.stdin.read(1)
                    if ch2=="[":
                        sys.stdin.read(1)
                        continue
                    else:
                        return None
                elif ch=="\n" or ch=="\r":
                    return text
                elif ch=="\x7f":
                    if text:
                        text=text[:-1]
                        print("\b\b", end="", flush=True)
                elif ch=="\x03":
                    raise KeyboardInterrupt
                elif ord(ch) >= 32 and ord(ch) < 127:
                    if len(text) < 50:
                        text+=ch
                        print(ch, end="", flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    result=read_text()
    print()
    return result if result else None
    
def multiselect(question: str, options: List[str]) -> List[str]:
    selected=set()
    current=0
    is_running=True
    result=None
    
    def render():
        lines=len(options) + 1
        if render.is_first_render:
            render.is_first_render=False
        else:
            print(f"\x1b[{lines}A", end="")
            
        Print.yellow("Use UP/DOWN arrows to navigate, 'space' to toggle selection, 'enter' to confirm, and 'c' to cancel")
        print(question)
        
        for idx, opt in enumerate(options):
            checkbox="[■]" if idx in selected else "[ ]"
            if idx==selected:
                print(f"\x1b[K {checkbox} >{opt}<")
            else:
                print(f"\x1b[K {checkbox} {opt}")
        
        render.is_first_render=True
        
        def get_key():
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch=="\x1b":
                    ch2=sys.stdin.read(1)
                    if ch2=="[":
                        ch3=sys.stdin.read(1)
                        return f"\x1b[{ch3}"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        print()
        render()
        
        while is_running:
            key=get_key()
            
            if key=="\x1b[A":
                current=(current-1)%len(options)
            elif key=="\x1b[B":
                current=(current+1)%len(options)
            elif key==" ":
                if current in selected:
                    selected.remove(current)
                else:
                    selected.add(current)
                render()
            elif key=="\n" or key=="\r":
                result=[options[i] for i in sorted(selected)]
                is_running=False
            elif key=="c" or key=="C":
                result=[]
                is_running=False
    
    print()
    return result