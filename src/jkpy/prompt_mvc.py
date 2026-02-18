from typing import List
from typing import Any
from typing import Optional
import sys
import tty
import termios
from jkpy.utils import Print

class PromptModel:
    def __init__(self, header: str, options: List[str]):
        self.header=header
        self.options=options
        self.selected=0
        self.result=None
        self.is_active=True
        self._observers=[]
        
    def add_observer(self, observer) -> None:
        self._observers.append(observer)
        
    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update()
        
    def select_previous(self):
        self.selected=(self.selected-1)%len(self.options)
        
    def select_next(self):
        self.selected=(self.selected+1)%len(self.options)
        
    def confirm_selection(self):
        self.result=self.options[self.selected]
        self.is_active=False
        
    def cancel(self):
        self.result=None
        self.is_active=False
        
class PromptView:
    def __init__(self, model: PromptModel):
        self.model=model
        self.is_first_render=True
        self.update_lines=0
        
    def update(self):
        self.render()
        
    def render(self):
        self.update_lines=len(self.model.options)+len(self.model.header.splitlines)
        
        if not self.is_first_render:
            print(f"\033[{self.update_lines}A", end="")
            
        print(f"{Print.YELLOW} \033[K self.model.prompt_header {Print.nc}")
        
        for idx, opt in enumerate(self.model.options):
            if idx==self.model.selected:
                print(f"\033[K >{Print.CYAN}{opt}{Print.NC}<")
            else:
                print(f"\033[K  {Print.CYAN}{opt}{Print.NC}")
        
        print("\033[K",end="",flush=True)
        self.is_first_render=False
        
    def render_confirmation(self):
        input(f"{self.header} (Y/n)?")
        
class PromptController:
    def __init__(self, model: PromptModel, view: PromptView):
        self.model=model
        self.view=view

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
            self.confirm_selection()
        elif key=="c" or key=="C":
            self.model.cancel()
            
    def run(self) -> Optional[str]:
        self.view.render()
        
        while self.model.is_active:
            key=self.get_key()
            self.handle_input(key)
            
            return self.model.result

def show_options_prompt(header: str, options: List[str]) -> Optional[str]:
    model=PromptModel(header, options)
    view=PromptView(model)
    controller=PromptController(model, view)
    
    model.add_observer(view)
    
    return controller.run()

def confirm(question: str) -> bool:
    print(f"{question} (y/n)", end="", flush=True)
    
    def read_yn():
        fd=sys.stdin.fileno()
        old_settings=termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch=sys.stdin.read(1).lower()
                if ch in ('y', 'n', '\x1b'):
                    return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            
    key=read_yn()
    print()
    return key=='y'

def text_input(question: str, default: str="") -> Optional[str]:
    Print.yellow("'enter' to confirm, 'escape' to cancel")
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
                    ch2=sys.stdn.read(1)
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
    is_active=True
    result=None
    
    def render():
        lines=len(options) + 1
        if render.is_first_render:
            render.is_first_render=False
        else:
            print(f"\033[{lines}A", end="")
            
        Print.yellow("Use UP/DOWN arrows to navigate, 'space' to toggle selection, 'enter' to confirm, and 'c' to cancel")
        print(question)
        
        for idx, opt in enumerate(options):
            checkbox="[■]" if idx in selected else "[ ]"
            if idx==selected:
                print(f"\033[K {checkbox} >{opt}<")
            else:
                print(f"\033[K {checkbox} {opt}")
        
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
        
        while is_active:
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
                is_active=False
            elif key=="c" or key=="C":
                result=[]
                is_active=False
    
    print()
    return result