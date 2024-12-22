from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class StoryContext:
    title: str = ""
    genre: str = ""
    central_theme: str = ""
    protagonist: Dict[str, Any] = field(default_factory=dict)
    antagonist: Dict[str, Any] = field(default_factory=dict)
    
    # Narrative tracking
    active_plot_threads: List[str] = field(default_factory=list)
    unresolved_tensions: List[str] = field(default_factory=list)
    character_arcs: Dict[str, List[str]] = field(default_factory=dict)

    def update(self, new_context: Dict[str, Any]):
        """
        Dynamically update story context
        """
        for key, value in new_context.items():
            if hasattr(self, key):
                setattr(self, key, value)