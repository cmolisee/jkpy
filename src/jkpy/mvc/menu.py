from __future__ import annotations
import os
import json
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import Optional
from typing import List
from typing import Any
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Ansi
import shutil
import sys
import termios
import tty
from jkpy._types import MenuData


class MenuModel:
    def __init__(self, options: List[str]):
        self.config_path: Path=Path(os.path.join(Path.home(), "Documents/.jkpy/config.txt"))
        self.data: Optional[MenuData] = dict()
        
        # initialize runtime data
        self.data["originaldata"]=None
        self.data["tempdata"]=[]
        self.data["accounts"]=set()
        self.data.update(self.get_data())
        
        if isinstance(self.data["start"], str):
            self.data["start"]=datetime.fromisoformat(self.data["start"])
            
        if isinstance(self.data["end"], str):
            self.data["end"]=datetime.fromisoformat(self.data["end"])
            
        # view configurations
        self.options: List[str]=options
        self.selected: int=0
        self.is_running: bool=True
        # observers are expected to be a view class as part of the 
        # mvc pattern with an update() function
        self._observers: List[Any]=[]
    
    def get_data(self) -> MenuData:
        if not self.config_path.exists():
            data=dict.fromkeys(MenuData.__annotations__.keys(), None)
                
            with Path(self.config_path).open('w', encoding='utf-8') as f:
                json.dump(data, f, cls=DateTimeEncoder)
                
        with self.config_path.open("r") as f:
            data=f.read()
        
        return json.loads(data) if data else {}
    
    def set_data(self, data: MenuData) -> MenuData:
        data: MenuData=self.get_data()
        
        for key, value in data.items():
            if value is None:
                continue
            if key=="path":
                Path(value).mkdir(parents=True, exist_ok=True)
                data[key]=value
            elif key=="start":
                try:
                    data[key]=datetime.strptime(value, '%Y-%m-%d')
                except:
                    data[key]=date(date.today().year, 1, 1).isoformat()
            elif key=="end":
                try:
                    data[key]=datetime.strptime(value, '%Y-%m-%d')
                except:
                    data[key]=date.today().strftime("%Y-%m-%d")
            elif key in ["remove_members","remove_teams","remove_statuses","remove_labels","remove_ignore_labels"]:
                data_key=key.replace("remove_", "")
                data_list=data[data_key]
                
                updated_list=[item for item in data_list if item not in value]
                data[data_key]=sorted(updated_list)
            elif key in MenuData.__annotations__.keys():
                data[key]=value
            else:
                continue # skip non-conforming keys
        
        with Path(self.config_path).open('w', encoding='utf-8') as f:
                json.dump(data, f, cls=DateTimeEncoder)
            
        return data
   
    def add_observer(self, observer: Any) -> None:
        self._observers.append(observer)
        
    def notify_observers(self) -> None:
        for observer in self._observers:
            observer.update()
        
    def select_previous(self):
        self.selected=(self.selected-1)%len(self.options)
        self.notify_observers()
        
    def select_next(self):
        self.selected=(self.selected+1)%len(self.options)
        self.notify_observers()
        
    def stop(self):
        self.is_running=False
        
class MenuView:
    PLUS=r"""+"""
    BAR=r"""|"""
    DASH=r"""-"""
    BANNER_LARGE=[
        r"""     _   _  __  ____   __   __""",
        r"""    | | | |/ / |  _ \  \ \ / /""",
        r""" _  | | | ' /  | |_) |  \ V / """,
        r"""| |_| | | . \  |  __/    | |  """,
        r""" \___/  |_|\_\ |_|       |_|  """,
    ]
    BANNER_SMALL=[
        r"""     _   _  __ """,
        r"""    | | | |/ / """,
        r""" _  | | | ' /  """,
        r"""| |_| | | . \  """,
        r""" \___/  |_|\_\ """,
        r""" ____   __   __""",
        r"""|  _ \  \ \ / /""",
        r"""| |_) |  \ V / """,
        r"""|  __/    | |  """,
        r"""|_|       |_|  """,
    ]
    BANNER_SUBTITLE="""Tool for Generating KPI's in Jira"""
    
    def __init__(self, model: "MenuModel"):
        self.model=model
        self.is_first_render=True
        self.lines_to_overwrite=0

    def _width(self) -> int:
        try:
            return round(shutil.get_terminal_size().columns*(2/3))
        except OSError: # Fallback
            return 64

    def line_break(self) -> str:
        return self.DASH*self._width()
    
    def banner(self) -> str:
        width=self._width()
        horizontal_border=self.PLUS+self.DASH*(width-2)+self.PLUS
        empty_line=self.BAR+(" "*(width-2)+self.BAR)
        
        if width<20: # tiny size
            return self.BANNER_SUBTITLE
        elif width<40: # small size
            banner=self.BANNER_SMALL
        else: # regular size
            banner=self.BANNER_LARGE
            
        banner_parts=[]
        banner_parts.append(horizontal_border)
        banner_parts.append(empty_line)
        
        for ln in banner:
            banner_parts.append(self.BAR+" "+ln+(" "*(width-3-len(ln)))+self.BAR)
        
        if width>40: # add subtitle if regular size
            banner_parts.append(self.BAR+" "+self.BANNER_SUBTITLE+" "+(" "*(width-4-len(self.BANNER_SUBTITLE)))+self.BAR)
        
        banner_parts.append(empty_line)
        banner_parts.append(horizontal_border)
        return "\n".join(banner_parts)

    def instructions(self) -> str:
        return "Use UP/DOWN arrows to navigate, 'enter' to select, 'q' to quit"
    
    def clear(self) -> None:
        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1)) 
            sys.stdout.write(Ansi.erase_line()) 
        sys.stdout.flush()
    
    def update(self) -> None:
        self.render()
    
    def render(self):
        instructions=f"{Ansi.YELLOW}{self.instructions()}{Ansi.NC}"
        self.lines_to_overwrite=len(self.model.options)+len(instructions.splitlines())
        
        if not self.is_first_render:
            self.clear()
        
        sys.stdout.write(self.instructions+"\n")
        for idx, opt in enumerate(self.model.options):
            if idx==self.model.selected:
                sys.stdout.write(f">{Ansi.CYAN}{opt}{Ansi.RESET}<")
            else:
                sys.stdout.write(f" {Ansi.CYAN}{opt}{Ansi.RESET}")
        
        sys.stdout.flush()
        self.is_first_render=False
        
    def reset(self):
        self.is_first_render=True
        
class MenuController:
    def __init__(self, model: MenuModel, view: MenuView):
        self.model: MenuModel=model
        self.view: MenuView=view
        self.callbacks: dict={}
        
    def register_callback(self, index: int, callback: Any) -> None:
        self.callbacks[index]=callback

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
    
    def execute_selected(self) -> None:
        # get the selected callback
        callback=self.callbacks.get(self.model.selected)
        
        # clear lines and execute the callback
        if callback:
            self.view.clear()
            callback(self.model, self.view)
        
        # re-render the view after callback finishes
        if self.model.is_running:
            self.view.reset()
            self.view.render()
            
    def handle_input(self, key: str):
        if key=="\x1b[A":
            self.model.select_previous()
        elif key=="\x1b[B":
            self.model.select_next()
        elif key=="\n" or key=="\r":
            self.execute_selected()
        elif key=="q" or key=="Q":
            self.model.stop()
             
    def run(self) -> None:
        self.view.render()
        while self.model.is_running:
            key=self.get_key()
            self.handle_input(key)
