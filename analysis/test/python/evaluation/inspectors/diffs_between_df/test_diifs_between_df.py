from pathlib import Path

import pytest
from hyperstyle.src.python.review.inspectors.inspector_type import InspectorType
from hyperstyle.src.python.review.inspectors.issue import IssueDifficulty, IssueType
from analysis.test.python.evaluation import INSPECTORS_DIR_PATH
from analysis.src.python.evaluation.common.pandas_util import get_solutions_df_by_file_path
from analysis.src.python.evaluation.common.csv_util import ColumnName
from analysis.src.python.evaluation.inspectors.common.statistics import PenaltyIssue
from analysis.src.python.evaluation.inspectors.diffs_between_df import find_diffs

RESOURCES_PATH = INSPECTORS_DIR_PATH / 'diffs_between_df'

EMPTY_DIFFS = {
    ColumnName.GRADE.value: [],
    ColumnName.DECREASED_GRADE.value: [],
    ColumnName.USER.value: 0,
    ColumnName.TRACEBACK.value: {},
    ColumnName.PENALTY.value: {},
}

INCORRECT_GRADE_DIFFS = {
    ColumnName.GRADE.value: [1, 2],
    ColumnName.DECREASED_GRADE.value: [],
    ColumnName.USER.value: 0,
    ColumnName.TRACEBACK.value: {},
    ColumnName.PENALTY.value: {},
}

ISSUES = {
    PenaltyIssue(
        origin_class='C0305',
        description='Trailing newlines',
        line_no=15,
        column_no=1,
        type=IssueType('CODE_STYLE'),

        file_path=Path(),
        inspector_type=InspectorType.UNDEFINED,
        influence_on_penalty=0,
        difficulty=IssueDifficulty.EASY,
    ), PenaltyIssue(
        origin_class='E211',
        description='whitespace before \'(\'',
        line_no=1,
        column_no=6,
        type=IssueType('CODE_STYLE'),

        file_path=Path(),
        inspector_type=InspectorType.UNDEFINED,
        influence_on_penalty=0,
        difficulty=IssueDifficulty.EASY,
    ),
}

ISSUES_DIFFS = {
    ColumnName.GRADE.value: [],
    ColumnName.DECREASED_GRADE.value: [],
    ColumnName.USER.value: 0,
    ColumnName.TRACEBACK.value: {
        1: ISSUES,
    },
    ColumnName.PENALTY.value: {},
}

MIXED_DIFFS = {
    ColumnName.GRADE.value: [2, 3],
    ColumnName.DECREASED_GRADE.value: [],
    ColumnName.USER.value: 0,
    ColumnName.TRACEBACK.value: {
        1: ISSUES,
    },
    ColumnName.PENALTY.value: {},
}

DECREASED_GRADE = {
    ColumnName.GRADE.value: [],
    ColumnName.DECREASED_GRADE.value: [2, 3],
    ColumnName.USER.value: 0,
    ColumnName.TRACEBACK.value: {},
    ColumnName.PENALTY.value: {},
}

TEST_DATA = [
    ('old_1.csv', 'new_1.csv', EMPTY_DIFFS),
    ('old_2.csv', 'new_2.csv', INCORRECT_GRADE_DIFFS),
    ('old_3.csv', 'new_3.csv', ISSUES_DIFFS),
    ('old_4.csv', 'new_4.csv', MIXED_DIFFS),
    ('old_5.csv', 'new_5.csv', DECREASED_GRADE),
]


@pytest.mark.parametrize(('old_file', 'new_file', 'diffs'), TEST_DATA)
def test(old_file: Path, new_file: Path, diffs: dict):
    old_df = get_solutions_df_by_file_path(RESOURCES_PATH / old_file)
    new_df = get_solutions_df_by_file_path(RESOURCES_PATH / new_file)
    actual_diffs = find_diffs(old_df, new_df)
    assert sorted(actual_diffs) == sorted(diffs)
