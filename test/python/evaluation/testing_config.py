from argparse import Namespace

from src.python import MAIN_FOLDER
from src.python.evaluation.common.util import EvaluationArgument
from src.python.review.reviewers.perform_review import OutputFormat


def get_testing_arguments(to_add_traceback=None, to_add_tool_path=None, to_add_history=None) -> Namespace:
    testing_arguments = Namespace(format=OutputFormat.JSON.value,
                                  output_file_name=EvaluationArgument.RESULT_FILE_NAME_XLSX.value,
                                  output_folder_path=None,
                                  with_history=False)
    if to_add_traceback:
        testing_arguments.traceback = True

    if to_add_tool_path:
        testing_arguments.tool_path = MAIN_FOLDER.parent / 'review/run_tool.py'

    if to_add_history:
        testing_arguments.with_history = True

    testing_arguments.solutions_file_path = None
    testing_arguments.to_drop_nan = False

    return testing_arguments