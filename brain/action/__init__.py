"""
Action — Motor output and policy execution.
"""
from typing import Any, Dict


class ActionModule:
    """Coordinates all action output.
    
    Converts internal decision representation into environment-compatible commands.
    """
    def __init__(self):
        self.last_motor_command = None
    
    def forward(self, inputs: Dict, state: Dict) -> tuple[Dict, Dict]:
        action = inputs.get("action")
        return {"motor_command": action}, {"last_command": action}
    
    def reset(self):
        self.last_motor_command = None
