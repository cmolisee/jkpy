from textual.app import App
from textual.app import ComposeResult
from textual.containers import Container
from textual.containers import Vertical
from textual.widgets import Static
from textual.widgets import Button
from textual.binding import Binding

class Prompt(App):
    CSS="""
    Screen {
        align: center middle;
    }
    Container {
        width: 60;
        height: auto;
        background: %surface;
        border: thick $primary;
    }
    Vertical {
        padding: 1 2;
    }
    #title {
        text-align: center;
        text-style: bold;
        color: $warning;
        margin-bottom: 1;
    }
    #instruction {
        text-align: center;
        margin-bottom: 1;
    }
    Button {
        width: 100%;
        margin: 0 0 1 0;
    }
    """
    
    BINDINGS=[
        Binding("q", "quit", "Quit", show=False),
    ]
    
    def __init__(self, message: str, options: list[str]) -> None:
        super().__init__()
        self.message=message
        self.options=options
        self.selected_option: str=""
        
    def compose(self) -> ComposeResult:
        with Container():
            with Vertical():
                yield Static("Missing Field Detected", id="title")
                yield Static(self.message, id="instruction")
                
                for i, option in enumerate(self.options):
                    yield Button(option, id=f"option_{i}", variant="primary")
                    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id=event.button.id
        if button_id and button_id.startswith("option_"):
            index=int(button_id.split("_")[1])
            self.selected_option=self.options[index]
            self.exit()
            
    def on_mount(self) -> None:
        first_button=self.query_one("#option_0", Button)
        first_button.focus()
        
    def run(self, *args, **kwargs) -> str:
        super().run(*args, **kwargs)
        return self.selected_option