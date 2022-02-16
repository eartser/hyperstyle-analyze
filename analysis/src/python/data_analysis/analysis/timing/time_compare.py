import argparse
import os
import sys
import time
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from hyperstyle.src.python.review.application_config import LanguageVersion
from hyperstyle.src.python.review.reviewers.common import LANGUAGE_TO_INSPECTORS

from analysis.src.python.data_analysis.model.column_name import SubmissionColumns
from analysis.src.python.data_analysis.utils.df_utils import read_df
from analysis.src.python.evaluation.common.parallel_util import run_and_wait


def run_hyperstyle(language: str, code: str, repeat: int = 5):
    language_version = LanguageVersion.from_value(language)

    language = LanguageVersion.from_value(language)
    inspectors = LANGUAGE_TO_INSPECTORS.get(language, [])

    inspectors_config = {
        'language_version': language_version,
        'n_cpu': 1,
    }

    if language.is_java():
        project_dir = 'template/java_template/java'
        main_path = os.path.join(project_dir, 'src/main/java/Main.java')
    elif language == LanguageVersion.PYTHON_3:
        project_dir = 'template/python_template'
        main_path = os.path.join(project_dir, 'main.py')
    else:
        raise NotImplementedError(f'{language} needs implementation.')

    with open(main_path, 'w+') as main_file:
        main_file.write(code)

    repeat_times = []

    for i in range(repeat):
        start_time = time.time()
        for inspector in inspectors:
            issues = inspector.inspect(main_path, inspectors_config)
        end_time = time.time()
        repeat_times.append(end_time - start_time)

    return np.array(repeat_times).mean()


def run_qodana(language: str, code: str, repeat: int = 5):
    language = LanguageVersion.from_value(language)

    results_dir = 'result'

    if language.is_java():
        qodana_image_path = 'jetbrains/qodana'
        project_dir = 'template/java_template/java'
        main_path = os.path.join(project_dir, 'src/main/java/Main.java')
        profile_path = 'profiles/java_profile_qodana.xml'
    elif language == LanguageVersion.PYTHON_3:
        qodana_image_path = 'jetbrains/qodana-python'
        project_dir = 'template/python_template'
        main_path = os.path.join(project_dir, 'main.py')
        profile_path = 'profiles/python_profile_qodana.xml'
    else:
        raise NotImplementedError(f'{language} needs implementation.')

    with open(main_path, 'w+') as main_file:
        main_file.write(code)

    command = [
        'docker', 'run',
        '-u', str(os.getuid()),
        '--rm',
        '-v', f'{Path(project_dir).resolve()}/:/data/project/',
        '-v', f'{Path(results_dir).resolve()}/:/data/results/',
        '-v', f'{Path(profile_path).resolve()}:/data/profile.xml',
        f'{qodana_image_path}',
    ]

    repeat_times = []
    for i in range(repeat):
        start_time = time.time()
        run_and_wait(command)
        end_time = time.time()
        repeat_times.append(end_time - start_time)

    return np.array(repeat_times).mean()


def time_evaluation(submissions_path: str, time_evaluation_path: str, submissions_ids: List[int], repeat: int):
    df_submissions = read_df(submissions_path)
    df_submissions = df_submissions[df_submissions[SubmissionColumns.ID].isin(submissions_ids)]

    result = {
        'id': [],
        'hyperstyle': [],
        'qodana': [],
    }

    for i, submissions in df_submissions.iterrows():
        result['id'].append(submissions[SubmissionColumns.ID])
        result['hyperstyle'].append(
            run_hyperstyle(submissions[SubmissionColumns.LANG], submissions[SubmissionColumns.CODE], repeat))
        result['qodana'].append(
            run_qodana(submissions[SubmissionColumns.LANG], submissions[SubmissionColumns.CODE], repeat))

    pd.DataFrame.from_dict(result).to_csv(time_evaluation_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('submissions_path', type=str,
                        help='Path to .csv file with preprocessed submissions with series')
    parser.add_argument('time_evaluation_path', type=str,
                        help='Path to .csv file with submissions client series statistics')
    parser.add_argument('--ids', nargs='+', type=int,
                        help='Ids of submissions to evaluate code quality analyzers time')
    parser.add_argument('--repeat', default=3, type=int,
                        help='Times to repeat time evaluation for averaging')

    args = parser.parse_args(sys.argv[1:])

    time_evaluation(args.submissions_path,
                    args.time_evaluation_path,
                    args.ids,
                    args.repeat)
