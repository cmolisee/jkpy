from __future__ import annotations
import os
import json
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List
from typing import Any
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Ansi
import shutil
import sys
from readchar import readkey
from readchar import key
import termios

class MenuModel:
    def __init__(self, options: List[str]) -> None:
        self.config_path: Path=Path(os.path.join(Path.home(), "Documents/.jkpy/config.txt"))
        # Initialize
        self.data: Dict[str, Any]={
            "email": "",
            "token": "",
            "path": "",
            "members": list(),
            "teams": list(),
            "statuses": list(),
            "labels": list(),
            "ignore_labels": list(),
            "host": "",
            "data_frames": {},
            "start": date(date.today().year, 1, 1).isoformat(),
            "end": date.today().strftime("%Y-%m-%d"),
        }
        
        # update from saved configurations
        self.data|=self.get_configs()
        
        if isinstance(self.data["start"], str):
            self.data["start"]=datetime.fromisoformat(self.data["start"])
            
        if isinstance(self.data["end"], str):
            self.data["end"]=datetime.fromisoformat(self.data["end"])
            
        # mvc variables
        self.options: List[str]=options
        self.selected: int=0
        self.is_running: bool=True
        self._observers: List[Any]=[]
    
    def get_configs(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                data: str=f.read()
                return self.data|json.loads(data)
        except FileNotFoundError:
            print(Ansi.YELLOW+">>> Configuration file does not exist. Returning runtime configs.\n"+Ansi.RESET)
            return self.data
    
    def set_configs(self, config: Dict[str, Any]) -> Dict[str, Any]:
        keys=["email","token","path","members","teams","statuses","labels","ignore_labels","host","start","end"]
        # make directory if DNE
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.config_path, 'w') as f:
                for key, value in config.items():
                    if key=="path":
                        Path(value).mkdir(parents=True, exist_ok=True)
                        self.data[key]=value
                    elif key=="start":
                        try:
                            self.data[key]=datetime.strptime(value, '%Y-%m-%d')
                        except:
                            self.data[key]=date(date.today().year, 1, 1).isoformat()
                    elif key=="end":
                        try:
                            self.data[key]=datetime.strptime(value, '%Y-%m-%d')
                        except:
                            self.data[key]=date.today().strftime("%Y-%m-%d")
                    elif key in ["remove_members","remove_teams","remove_statuses","remove_labels","remove_ignore_labels"]:
                        data_key=key.replace("remove_", "")
                        data_list=self.data[data_key]
                        
                        updated_list=[item for item in data_list if item not in value]
                        self.data[data_key]=sorted(updated_list)
                    elif key in self.data.keys():
                        self.data[key]=value
                    else:
                        continue # skip non-conforming keys
                
                out={k: self.data[k] for k in keys if k in self.data}
                json.dump(out, f, cls=DateTimeEncoder)
        except Exception:
            pass
        
        return self.data
   
    def add_observer(self, observer: Any) -> None:
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
        
    def stop(self) -> None:
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
    
    def __init__(self, model: "MenuModel") -> None:
        self.model: MenuModel=model
        self.is_first_render: bool=True
        self.lines_to_overwrite: int=0

    def _width(self) -> int:
        try:
            return round(shutil.get_terminal_size().columns*(2/3))
        except OSError: # Fallback
            return 64

    def line_break(self) -> str:
        return self.DASH*self._width()
    
    def banner(self) -> str:
        width: int=self._width()
        horizontal_border: str=self.PLUS+self.DASH*(width-2)+self.PLUS
        empty_line: str=self.BAR+(" "*(width-2)+self.BAR)
        
        if width<20: # tiny size
            return self.BANNER_SUBTITLE
        elif width<40: # small size
            banner=self.BANNER_SMALL
        else: # regular size
            banner=self.BANNER_LARGE
            
        banner_parts: List[str]=[]
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
        return "Use UP/DOWN arrows to navigate, 'enter' to select, 'CTRL+C' to quit"
    
    def clear(self) -> None:
        for _ in range(self.lines_to_overwrite):
            sys.stdout.write(Ansi.up(1)) 
            sys.stdout.write(Ansi.erase_line()) 
        sys.stdout.flush()
    
    def update(self) -> None:
        self.render()
    
    def render(self) -> None:
        instructions: str=f"{Ansi.YELLOW}{self.instructions()}{Ansi.RESET}"
        self.lines_to_overwrite=len(self.model.options) \
            +len(instructions.splitlines())
        
        if not self.is_first_render:
            self.clear()
        
        sys.stdout.write(self.instructions()+"\n")
        for idx, opt in enumerate(self.model.options):
            if idx==self.model.selected:
                sys.stdout.write(f">{Ansi.CYAN}{opt}{Ansi.RESET}<\n")
            else:
                sys.stdout.write(f" {Ansi.CYAN}{opt}{Ansi.RESET}\n")
        
        sys.stdout.flush()
        self.is_first_render=False
        
    def reset(self) -> None:
        self.is_first_render=True
        
class MenuController:
    def __init__(self, model: MenuModel, view: MenuView) -> None:
        self.model: MenuModel=model
        self.view: MenuView=view
        self.callbacks: dict[int, Any]={}
        
    def register_callback(self, index: int, callback: Any) -> None:
        self.callbacks[index]=callback
    
    def execute_selected(self) -> None:
        # get the selected callback
        callback=self.callbacks.get(self.model.selected)
        
        # clear lines and execute the callback
        if callback:
            self.view.clear()
            callback(model=self.model, view=self.view)
        
        # re-render the view after callback finishes
        if self.model.is_running:
            self.view.reset()
            self.view.render()
            
    def handle_input(self, k: str) -> None:
        if k==key.UP : # up
            self.model.select_previous()
        elif k==key.DOWN: # down
            self.model.select_next()
        elif k in [key.ENTER, key.TAB]: # enter
            self.execute_selected()
             
    def run(self) -> None:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            self.view.render()
            while self.model.is_running:
                k=readkey()
                self.handle_input(k)
        except KeyboardInterrupt:
            sys.exit(0)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
