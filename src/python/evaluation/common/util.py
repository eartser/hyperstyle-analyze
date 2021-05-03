from enum import Enum, unique

from src.python.review.application_config import LanguageVersion
from src.python.review.common.file_system import Extension


@unique
class ColumnName(Enum):
    CODE = "code"
    LANG = "lang"
    LANGUAGE = "language"
    GRADE = "grade"


@unique
class EvaluationArgument(Enum):
    TRACEBACK = "traceback"
    RESULT_FILE_NAME = "results"
    RESULT_FILE_NAME_EXT = f"{RESULT_FILE_NAME}{Extension.XLSX.value}"


script_structure_rule = ("Please, make sure your XLSX-file matches following script standards: \n"
                         "1. Your XLSX-file should have 2 obligatory columns named:"
                         f"'{ColumnName.CODE.value}' & '{ColumnName.LANG.value}'. \n"
                         f"'{ColumnName.CODE.value}' column -- relates to the code-sample. \n"
                         f"'{ColumnName.LANG.value}' column -- relates to the language of a "
                         "particular code-sample. \n"
                         "2. Your code samples should belong to the one of the supported languages. \n"
                         "Supported languages are: Java, Kotlin, Python. \n"
                         f"3. Check that '{ColumnName.LANG.value}' column cells are filled with "
                         "acceptable language-names: \n"
                         f"Acceptable language-names are: {LanguageVersion.PYTHON_3.value}, "
                         f"{LanguageVersion.JAVA_8.value} ,"
                         f"{LanguageVersion.JAVA_11.value} and {LanguageVersion.KOTLIN.value}.")