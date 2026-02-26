from __future__ import annotations
from typing import List
from typing import Any
import sys
import tty
import termios
from jkpy.utils import Ansi

class OptionsModel:
    def __init__(self, question: str, options: List[str], allow_multi: bool=False) -> None:
        self.question: str=question
        self.options: List[str]=options
        self.selected: int=0
        self.allow_multi: bool=allow_multi
        self.result: List[str]=[]
        self.is_running: bool=True
        self._observers: List[Any]=[]
        
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
        if self.allow_multi:
            opt: str=self.options[self.selected]
            if opt in self.result:
                self.result.remove(opt)
            else:
                self.result.append(opt)
        else:
            self.result=[self.options[self.selected]]
        
    def stop(self) -> None:
        self.is_running=False
        
class OptionsView:
    def __init__(self, model: OptionsModel) -> None:
        self.model: OptionsModel=model
        self.is_first_render: bool=True
        self.lines_to_overwrite: int=0
    
    def clear(self) -> None:
        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1)) 
            sys.stdout.write(Ansi.erase_line()) 
        sys.stdout.flush()
        
    def update(self) -> None:
        self.render()
        
    def render(self) -> None:
        instruction: str="Use UP/DOWN arrows to navigate, 'space' to toggle selection, 'enter' to confirm, and 'q' to quit/cancel"
        self.lines_to_overwrite=len(self.model.options) \
            +len(self.model.question.splitlines()) \
            +len(instruction.splitlines())
        
        if not self.is_first_render:
            self.clear()
            
        sys.stdout.write(self.model.question+"\n")
        for idx, opt in enumerate(self.model.options):
                checkbox="[■]" if idx in self.model.result else "[ ]"
                if idx==self.model.selected:
                    print(f"\x1b[K {checkbox} >{opt}<")
                else:
                    print(f"\x1b[K {checkbox} {opt}")
        
        sys.stdout.flush()
        self.is_first_render=False
    
    def reset(self) -> None:
        self.is_first_render=True
        
class OptionsController:
    def __init__(self, model: OptionsModel, view: OptionsView) -> None:
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
                    return f"\x1b[{ch3}" if ch3 else "\x1b"
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
    def handle_input(self, key: str) -> None:
        if key=="\x1b[A": # up
            self.model.select_previous()
        elif key=="\x1b[B": # down
            self.model.select_next()
        elif key==" ": # space, toggle
            self.model.confirm_selection()
        elif key=="\n" or key=="\r": # enter
            self.model.stop()
        elif key=="\x1b": # escape, cancel
            self.model.result=[]
            self.model.stop()
            
    def run(self) -> List[str]:
        self.view.render()
        while self.model.is_running:
            key=self.get_key()
            self.handle_input(key)
            
        return self.model.result

class Options:
    @staticmethod
    def select(question: str, options: List[str]) -> List[str]:
        model: OptionsModel=OptionsModel(question, options)
        view: OptionsView=OptionsView(model)
        controller: OptionsController=OptionsController(model, view)
        
        model.add_observer(view)
        return controller.run()
    
    @staticmethod
    def multiselect(question: str, options: List[str]) -> List[str]:
        model: OptionsModel=OptionsModel(question, options, True)
        view: OptionsView=OptionsView(model)
        controller: OptionsController=OptionsController(model, view)
        
        model.add_observer(view)
        return controller.run()