from __future__ import annotations
from typing import List
from typing import Any
from typing import Optional
import sys
from readchar import readkey
from readchar import key
from jkpy.utils import Ansi

class InputModel:
    def __init__(self, prompt: str) -> None:
        self.prompt: str=prompt
        self.result: Optional[str]=""
        self.is_running: bool=True
        self._observers: List[Any]=[]

    def add_observer(self, observer: Any) -> None:
        self._observers.append(observer)
        
    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update()

    def get_result(self) -> Optional[str]:
        return self.result
    
    def stop(self) -> None:
        self.is_running=False
    
class InputView:
    def __init__(self, model: InputModel) -> None:
        self.model: InputModel=model
        self.is_first_render: bool=True
        self.lines_to_overwrite: int=0
    
    def clear(self) -> None:
        # need to do a check if the cursor is on the same line as the text. in which case we don't go up a line but instead to the start of the line...
        if self.lines_to_overwrite==1:
            sys.stdout.write("\r")
            sys.stdout.write(Ansi.erase_line())
            sys.stdout.flush()
            return
        
        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1)) 
            sys.stdout.write(Ansi.erase_line()) 
        sys.stdout.flush()
    
    def update(self) -> None:
        self.render()

    def render(self) -> None:
        self.lines_to_overwrite=len(self.model.prompt.splitlines())
        
        if not self.is_first_render:
            self.clear()

        sys.stdout.write(self.model.prompt+" "+str(self.model.result))

        sys.stdout.flush()
        self.is_first_render=False
        
    def reset(self) -> None:
        self.is_first_render=True
    
class InputController:
    def __init__(self, model: InputModel, view: InputView) -> None:
        self.model: InputModel=model
        self.view: InputView=view

    def handle_input(self, k: str) -> None:
        if k in [key.ENTER, key.TAB]: # enter, submit
            self.model.stop()
        elif self.model.result and k==key.BACKSPACE: # backspace - delete should not be allowed
            self.model.result=self.model.result[:-1]
            self.view.update()
        elif k.isalnum() or k in [".","\\","/","?","-","&","%",",","\"","'","_","+","=","$","[","]","(",")",":"]: # char, update
            if not self.model.result:
                self.model.result=k
            elif len(self.model.result) < 50:
                self.model.result+=k
            self.view.update()
        
    def run(self) -> Optional[str]:
        self.view.render()
        while self.model.is_running:
            key=readkey()
            self.handle_input(key)
        
        print()
        return self.model.result

class Input:
    @staticmethod
    def confirm(question: str) -> bool:
        model: InputModel=InputModel(question+" (y/n)")
        view: InputView=InputView(model)
        controller: InputController=InputController(model, view)
        
        result=controller.run()
        print()

        if result and result.lower() in ("y", "yes"):
            return True
        
        return False
    
    @staticmethod
    def text(question: str) -> Optional[str]:
        model: InputModel=InputModel(question)
        view: InputView=InputView(model)
        controller: InputController=InputController(model, view)
        
        return controller.run()