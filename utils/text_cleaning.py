import codecs
import re


class TextCleaner:
    @staticmethod
    def __remove_only_mentions(str_input: str) -> str:
        result = re.fullmatch(r"^[\s]*@\b[\S]+\b[\s]*$", str_input)
        return "" if result else str_input

    @staticmethod
    # Removes emoji and other invisible non-ascii characters (breaks supports for languages that don't use the latin alphabet):
    def __remove_nonascii_characters(str_input: str) -> str:
        result = codecs.encode(str_input, "utf-8")
        return result.decode("ascii", "ignore")

    @staticmethod
    def __remove_codeblocks(str_input: str) -> str:
        result = re.sub(r"```[^```]*```", "", str_input)
        return re.sub(r"`[^`]*`", "", str_input)

    @classmethod
    def clean(cls, str_input: str) -> str:
        output = str_input
        output = cls.__remove_nonascii_characters(output)
        output = cls.__remove_only_mentions(output)
        output = cls.__remove_codeblocks(output)
        return output