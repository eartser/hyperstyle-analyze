import argparse
import logging
import sys
from pathlib import Path

from analysis.src.python.evaluation.common.pandas_util import get_solutions_df
from analysis.src.python.evaluation.common.args_util import EvaluationRunToolArgument
from analysis.src.python.evaluation.paper_evaluation.comparison_with_other_tools.tutor_statistics import (
    IssuesStatistics, TutorStatistics,
)
from analysis.src.python.evaluation.paper_evaluation.comparison_with_other_tools.util import ComparisonColumnName
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, get_restricted_extension

sys.path.append('')
sys.path.append('../../..')

logger = logging.getLogger(__name__)


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help='Local CSV-file path with feedback from different tools. '
                             'Your file must include column-names:'
                             f'"{ComparisonColumnName.STUDENT_ID.name}" and '
                             f'"{ComparisonColumnName.TASK_KEY.name}" and '
                             f'"{ComparisonColumnName.SOLUTION.name}" and '
                             f'"{ComparisonColumnName.TUTOR_ERROR.name}" and ')


def main() -> int:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)

    try:
        args = parser.parse_args()
        solutions_file_path = args.solutions_file_path
        extension = get_restricted_extension(solutions_file_path, [AnalysisExtension.CSV])
        solutions_df = get_solutions_df(extension, solutions_file_path)
        tutor_stat = TutorStatistics(solutions_df, to_drop_duplicates=True)
        tutor_stat.print_tasks_stat()
        tutor_stat.print_error_stat()
        print('ISSUES STAT:')
        issue_stat = IssuesStatistics(solutions_df)
        issue_stat.print_issues_stat()
        return 0

    except FileNotFoundError:
        logger.error('CSV-file with the specified name does not exists.')
        return 2

    except Exception:
        logger.exception('An unexpected error.')
        return 2


if __name__ == '__main__':
    sys.exit(main())
