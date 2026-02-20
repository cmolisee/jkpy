from __future__ import annotations
from typing import List
from typing import Any
from typing import Optional
import sys
import tty
import termios
from jkpy.utils import Ansi

class InputModel:
    def __init__(self, prompt):
        self.prompt=prompt
        self.result=""

    def set_result(self, text):
        self.result=text

    def get_result(self):
        return self.user_text
    
class InputView:
    def __init__(self, model: InputModel):
        self.model: InputModel=model
        
    def get_user_input(self):
        return input(f"{self.model.prompt}: ")
    
class InputController:
    def __init__(self, model: InputModel, view: InputView):
        self.model: InputModel=model
        self.view: InputView=view
        
    def run(self) -> Optional[str]:
        txt=self.view.get_user_input()
        self.model.set_result(txt)
        return self.model.get_result

class Input:
    @staticmethod
    def confirm(question: str) -> bool:
        model=InputModel(question)
        view=InputView(model)
        controller=InputController(model, view)
        
        # this won't work to intercept cancel/interrupt behavior
        # unless using ctrl+c
        # must implement a custom solution with key handler if we want
        # to use escape key for that... probs not worth it.
        result=controller.run()
        
        model.add_observer(view)
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