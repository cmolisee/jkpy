import os
import json
from datetime import date
from datetime import datetime
from pathlib import Path
from typing import TypedDict
from typing import Optional
from typing import List
from typing import Set
from typing import Tuple
from typing import Any
import polars as pl
from jkpy.utils import DateTimeEncoder
from jkpy.utils import Print
import shutil
import sys
import termios
import tty
from functools import partial

class DataType(TypedDict):
    # Configurations
    email: Optional[str]
    token: Optional[str]
    path: Optional[str]
    members: Optional[List[str]]
    teams: Optional[List[str]]
    statuses: Optional[List[str]]
    labels: Optional[List[str]]
    host: Optional[str] # HOST="https://creditonebank.atlassian.net"
    # Runtime data
    originaldata: Optional[pl.DataFrame]
    tempdata: Optional[List[Any]]
    # Cached/Temporary/Volatile data
    accounts: Optional[Set[Tuple[Any, ...]]]
    start: Optional[str]
    end: Optional[str]  

class AppModel:
    def __init__(self, options: List[str]):
        self.data_path=Path(os.path.join(Path.home(), "Documents/.jkpy/config.txt"))
        self.data: Optional[DataType] = dict()
        self.data["originaldata"]=None
        self.data["tempdata"]=[]
        self.data["accounts"]=set()
        self.data.update(self.get_data())
        
        if isinstance(self.data["start"], str):
            self.data["start"]=datetime.fromisoformat(self.data["start"])
            
        if isinstance(self.data["end"], str):
            self.data["end"]=datetime.fromisoformat(self.data["end"])
            
        # view configurations
        self.options=options
        self.selected=0
        self.is_running=True
        self._observers=[]
    
    def get_data(self) -> DataType:
        if not self.data_path.exists():
            data=dict.fromkeys(DataType.__annotations__.keys(), None)
                
            with Path(self.data_path).open('w', encoding='utf-8') as f:
                json.dump(data, f, cls=DateTimeEncoder)
                
        with self.data_path.open("r") as f:
            data=f.read()
        
        return json.loads(data) if data else {}
    
    def set_data(self, data: DataType) -> DataType:
        data=self.get_data()
        
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
            elif key in ["remove_members","remove_teams","remove_statuses","remove_labels"]:
                data_key=key.replace("remove_", "")
                data_list=data[data_key]
                
                updated_list=[item for item in data_list if item not in value]
                data[data_key]=sorted(updated_list)
            elif key in DataType.__annotations__.keys():
                data[key]=value
            else:
                continue # skip non-conforming keys
        
        with Path(self.data_path).open('w', encoding='utf-8') as f:
                json.dump(data, f, cls=DateTimeEncoder)
            
        return data
   
    def add_observer(self, observer) -> None:
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
        Print.green("Goodbye...\n")
        self.is_running=False
        
class AppView:
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
    
    def __init__(self, model: AppModel):
        self.model=model
        self.is_first_render=True
        self.lines_to_overwrite=0

    def _width(self):
        try:
            return round(shutil.get_terminal_size().columns*(2/3))
        except OSError: # Fallback
            return 64

    def line_break(self):
        return self.DASH*self._width()
    
    def banner(self):
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

    def instructions(self):
        return "Use UP/DOWN arrows to navigate, 'enter' to select, 'q' to quit"
    
    def clear_lines(self):
        for _ in range(self.lines_to_overwrite):
            # Move the cursor up one line
            sys.stdout.write("\x1b[1A") 
            # Clear the current line from the cursor to the end
            sys.stdout.write("\x1b[2K") 
        sys.stdout.flush()
    
    def update(self):
        self.render()
    
    def render(self):
        instructions=f"{Print.YELLOW}{self.instructions()}{Print.NC}"
        self.lines_to_overwrite=len(self.model.options)+len(instructions.splitlines())
        
        if not self.is_first_render:
            # move cursor to first line to overwrite
            print(f"\x1b[{self.lines_to_overwrite}A", end="")
        
        # all below content should be written over on each render
        print(f"\x1b[K{instructions}") 
        for idx, opt in enumerate(self.model.options):
            if idx==self.model.selected:
                print("\x1b[K"+f">{Print.CYAN}{opt}{Print.NC}<")
            else:
                print("\x1b[K"+f" {Print.CYAN}{opt}{Print.NC}")
        
        print("\x1b[K",end="",flush=True)
        self.is_first_render=False
        
    def reset(self):
        self.is_first_render=True
        
class AppController:
    def __init__(self, model: AppModel, view: AppView):
        self.model=model
        self.view=view
        self.handlers={}
        
    def register_handler(self, index: int, handler: Any) -> None:
        self.handlers[index]=handler

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
        # get the selected handler
        handler=self.handlers.get(self.model.selected)
        
        # clear lines and execute the handler
        if handler:
            print("executing the handler")
            self.view.clear_lines()
            handler(self.model, self.view)
        
        # re-render the view
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
            
def show_submenu(options: List[str], handlers: dict) -> None:
    options=options+["Back"]
    # create new instance of app mvc
    model=AppModel(options)
    view=AppView(model)
    controller=AppController(model, view)
    
    model.add_observer(view)
    
    # register all handlers
    for idx, handler in handlers.items():
        controller.register_handler(idx, partial(handler))
    
    def back(model, view): # stop the submenu process
        model.is_running=False
    
    controller.register_handler(len(options)-1, partial(back))
    
    try:
        controller.run()
    except KeyboardInterrupt:
        model.is_running=False
    
        