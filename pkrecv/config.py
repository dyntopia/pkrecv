import configparser
import os
from typing import Any, Callable, List, Optional, Sequence, Union

from munch import Munch


class ConfigError(Exception):
    pass


class Config(configparser.ConfigParser):
    def __init__(self) -> None:
        super().__init__(dict_type=Munch)

    def read(  # type: ignore
            self,
            filenames: Union[str, Sequence[str]],
            encoding: Optional[str] = None
    ) -> List[str]:
        """
        Read one or more configuration files.
        """
        if isinstance(filenames, str):
            filenames = [filenames]
        filenames = [os.path.expanduser(f) for f in filenames]

        try:
            return super().read(filenames, encoding)
        except configparser.Error as e:
            raise ConfigError(e)

    def get_section(self, section: str, default: Any) -> Munch:
        """
        Retrieve all values in a section as a dictionary.
        """
        if not self.has_section(section):
            return default

        result = Munch()
        for option in self.options(section):
            value = self._convert(self.getboolean, section, option)
            if value is None:
                value = self._convert(self.getint, section, option)
            if value is None:
                value = self._convert(self.getfloat, section, option)
            if value is None:
                value = self.get(section, option)
            result[option] = value
        return result

    @staticmethod
    def _convert(function: Callable, section: str, option: str) -> Any:
        """
        Use the given function to convert an option in a section.
        """
        try:
            return function(section, option)
        except ValueError:
            return None
