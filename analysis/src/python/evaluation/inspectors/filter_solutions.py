import argparse
import logging
from pathlib import Path
from typing import Set

from hyperstyle.src.python.review.application_config import LanguageVersion
from analysis.src.python.evaluation.common.pandas_util import (
    drop_duplicates,
    filter_df_by_language,
    get_solutions_df,
    write_df_to_file,
)
from analysis.src.python.evaluation.common.args_util import EvaluationRunToolArgument
from analysis.src.python.evaluation.common.file_util import AnalysisExtension, get_parent_folder, \
    get_restricted_extension

logger = logging.getLogger(__name__)


def parse_languages(value: str) -> Set[LanguageVersion]:
    passed_names = value.lower().split(',')
    allowed_names = {lang.value for lang in LanguageVersion}
    if not all(name in allowed_names for name in passed_names):
        raise argparse.ArgumentError('--languages', 'Incorrect --languages\' names')

    return {LanguageVersion(name) for name in passed_names}


def configure_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.long_name,
                        type=lambda value: Path(value).absolute(),
                        help=EvaluationRunToolArgument.SOLUTIONS_FILE_PATH.value.description)

    parser.add_argument('-l', '--languages',
                        help='Set of languages to keep in the dataset',
                        type=parse_languages,
                        default=set(LanguageVersion))

    parser.add_argument('--duplicates',
                        help='If True, drop duplicates in the "code" column.',
                        action='store_true')


def main() -> None:
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()

    solutions_file_path = args.solutions_file_path
    ext = get_restricted_extension(solutions_file_path, [AnalysisExtension.XLSX, AnalysisExtension.CSV])
    solutions_df = get_solutions_df(ext, solutions_file_path)

    filtered_df = filter_df_by_language(solutions_df, args.languages)
    if args.duplicates:
        filtered_df = drop_duplicates(filtered_df)
    output_path = get_parent_folder(Path(solutions_file_path))
    write_df_to_file(filtered_df, output_path / f'filtered_solutions{ext.value}', ext)


if __name__ == '__main__':
    main()
