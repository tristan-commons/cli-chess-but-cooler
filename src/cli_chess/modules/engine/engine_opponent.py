from abc import ABC, abstractmethod
import chess.engine


class EngineOpponent(ABC):
    """Defines the interface an offline engine opponent must implement.
       Each concrete opponent encapsulates everything specific to a single
       UCI engine (binary location, configuration, and search limit) so
       EngineModel can drive any of them identically.
    """
    @abstractmethod
    def get_binary_path(self) -> str:
        """Returns the absolute path to the engine binary to launch"""
        pass

    @abstractmethod
    def get_configuration(self, game_parameters: dict) -> dict:
        """Returns the UCI options to configure the engine with"""
        pass

    @abstractmethod
    def get_search_limit(self, game_parameters: dict) -> chess.engine.Limit:
        """Returns the search limit to use when requesting a move"""
        pass

    @abstractmethod
    def get_display_name(self, game_parameters: dict) -> str:
        """Returns the name to display for this opponent"""
        pass
