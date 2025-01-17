import argparse
import logging
import sys
from enum import Enum

import pandas as pd

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import append_df, write_df
from analysis.src.python.data_analysis.utils.parsing_utils import str_to_datetime


def check_same_code(submission_0: pd.Series, submission_1: pd.Series) -> bool:
    """ Check if submission not the same as previous. """

    return submission_0[SubmissionColumns.CODE].strip() == submission_1[SubmissionColumns.CODE].strip()


def check_different_code(submission_0: pd.Series, submission_1: pd.Series, diff_ratio: float) -> bool:
    """ Check if submission not so different with previous (lines number does not changed in `diff_ratio` times). """

    code_0 = submission_0[SubmissionColumns.CODE]
    code_1 = submission_1[SubmissionColumns.CODE]
    code_lines_diff = len(code_0) / len(code_1)
    return not (1 / diff_ratio <= code_lines_diff <= diff_ratio)


class SubmissionsCheckStatus(Enum):
    OK = 'ok'
    SAME = 'same'
    DIFFERENT = 'different'


def filter_submissions_series(submissions_series: pd.DataFrame, diff_ratio: float) -> pd.DataFrame:
    """ Filter submissions in submission series (group of submissions by one user on one step). """

    logging.info(f'Processing submission series group {submissions_series.iloc[0][SubmissionColumns.GROUP]}')
    logging.info(f'Initial group shape {submissions_series.shape}')

    submissions_series = submissions_series.copy()
    submissions_series[SubmissionColumns.STATUS] = [SubmissionsCheckStatus.OK.value] * submissions_series.shape[0]
    submissions_series[SubmissionColumns.TIME] = submissions_series[SubmissionColumns.TIME].apply(str_to_datetime)
    submissions_series.sort_values([SubmissionColumns.TIME], inplace=True)

    prev_submission = None
    for i, submission in submissions_series.iterrows():
        if prev_submission is None:
            prev_submission = submission
            continue

        if check_same_code(prev_submission, submission):
            logging.info(f'Drop submission: '
                         f'user={submission[SubmissionColumns.USER_ID]} '
                         f'step={submission[SubmissionColumns.STEP_ID]} '
                         f'attempt={i + 1}: '
                         f'same submissions')
            submission[SubmissionColumns.STATUS] = SubmissionsCheckStatus.SAME.value
        elif check_different_code(submission, submission, diff_ratio):
            logging.info(f'Drop submission: '
                         f'user={submission[SubmissionColumns.USER_ID]} '
                         f'step={submission[SubmissionColumns.STEP_ID]} '
                         f'attempt={i + 1}: '
                         f'different submissions')
            submission[SubmissionColumns.STATUS] = SubmissionsCheckStatus.DIFFERENT.value

    logging.info(f'Final group shape {submissions_series.shape}')

    submissions_series = submissions_series[submissions_series[SubmissionColumns.STATUS] == SubmissionColumns.OK]
    submissions_series = submissions_series.drop([SubmissionColumns.STATUS], axis=1)
    group_size = submissions_series.shape[0]
    submissions_series[SubmissionColumns.ATTEMPT.value] = list(range(1, group_size + 1))
    submissions_series[SubmissionColumns.LAST_ATTEMPT.value] = [group_size] * group_size

    return submissions_series


def build_submission_series(submissions_path: str, output_path: str, diff_ration: float, chunk_size: int = 50000):
    """ Group given submissions to series (by one user on one step) and filter same or noise submissions.
        For each submission add it's series number, attempt in group (in sorted by time order)
        and total number of attempts in group.
    """

    df_submissions = pd.read_csv(submissions_path)
    df_submissions = df_submissions[df_submissions[SubmissionColumns.CODE].apply(lambda x: isinstance(x, str))]

    df_submissions[SubmissionColumns.GROUP] = df_submissions \
        .groupby([SubmissionColumns.USER_ID, SubmissionColumns.STEP_ID]).ngroup()

    min_group, max_group = df_submissions[SubmissionColumns.GROUP].min(), df_submissions[SubmissionColumns.GROUP].max()
    logging.info(f'Groups range: [{min_group}, {max_group}]')

    for i in range(min_group, max_group + 1, chunk_size):
        groups_range = [i, i + chunk_size - 1]
        logging.info(f'Processing groups: [{groups_range[0]}, {groups_range[1]}]')

        df_grouped_submission_series = df_submissions[df_submissions[SubmissionColumns.GROUP].isin(groups_range)] \
            .groupby([SubmissionColumns.GROUP], as_index=False)
        logging.info('Finish grouping')

        df_filtered_submission_series = df_grouped_submission_series \
            .apply(lambda g: filter_submissions_series(g, diff_ration))
        logging.info('Finish filtering')

        df_filtered_submission = df_filtered_submission_series.reset_index(drop=True)
        logging.info('Finish aggregation')

        if i == 0:
            write_df(df_filtered_submission, output_path)
        else:
            append_df(df_filtered_submission, output_path)
        logging.info('Finish saving results')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with submissions.')
    parser.add_argument('submissions_series_path', type=str,
                        help='Path to .csv file with filtered submissions with series info.')
    parser.add_argument('--diff-ratio', '-r', type=float, default=30.0,
                        help='Ration to remove submissions which has lines change more then in `diff_ratio` times.')

    args = parser.parse_args(sys.argv[1:])
    build_submission_series(args.submissions_path, args.submissions_series_path, args.diff_ratio)
