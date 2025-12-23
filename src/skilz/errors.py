"""Custom exceptions for Skilz."""


class SkilzError(Exception):
    """Base exception for all Skilz errors."""

    pass


class SkillNotFoundError(SkilzError):
    """Raised when a skill ID is not found in any registry."""

    def __init__(self, skill_id: str, searched_paths: list[str] | None = None):
        self.skill_id = skill_id
        self.searched_paths = searched_paths or []
        paths_msg = ""
        if self.searched_paths:
            paths_msg = f"\nSearched: {', '.join(self.searched_paths)}"
        super().__init__(f"Skill '{skill_id}' not found in registry.{paths_msg}")


class RegistryError(SkilzError):
    """Raised when there's an error loading or parsing the registry."""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Failed to load registry '{path}': {reason}")


class GitError(SkilzError):
    """Raised when a Git operation fails."""

    def __init__(self, operation: str, reason: str):
        self.operation = operation
        self.reason = reason
        super().__init__(f"Git {operation} failed: {reason}")


class InstallError(SkilzError):
    """Raised when skill installation fails."""

    def __init__(self, skill_id: str, reason: str):
        self.skill_id = skill_id
        self.reason = reason
        super().__init__(f"Failed to install '{skill_id}': {reason}")


class APIError(SkilzError):
    """Raised when an API request fails."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"API error: {reason}")
