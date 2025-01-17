import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import transformers
from torch.utils.data import DataLoader
from transformers import RobertaForSequenceClassification
from analysis.src.python.evaluation.common.csv_util import write_dataframe_to_csv
from analysis.src.python.evaluation.qodana.imitation_model.common.evaluation_config import configure_arguments
from analysis.src.python.evaluation.qodana.imitation_model.common.metric import Measurer
from analysis.src.python.evaluation.qodana.imitation_model.common.util import DatasetColumnArgument, MeasurerArgument
from analysis.src.python.evaluation.qodana.imitation_model.dataset.dataset import QodanaDataset
from evaluation.common.util import AnalysisExtension


def get_predictions(eval_dataloader: torch.utils.data.DataLoader,
                    model: transformers.RobertaForSequenceClassification,
                    predictions: np.ndarray,
                    num_labels: int,
                    device: torch.device,
                    args: argparse.ArgumentParser) -> pd.DataFrame:
    start_index = 0
    for batch in eval_dataloader:
        with torch.no_grad():
            logits = model(input_ids=batch[DatasetColumnArgument.INPUT_IDS.value].to(device)).logits
            logits = logits.sigmoid().detach().cpu().numpy()
            predictions[start_index:start_index + args.batch_size, :num_labels] = (logits > args.threshold).astype(int)
            start_index += args.batch_size
    return pd.DataFrame(predictions, columns=range(num_labels), dtype=int)


def save_f1_scores(output_directory_path: Path, f1_score_by_class_dict: dict) -> None:
    f1_score_report_file_name = f'{MeasurerArgument.F1_SCORES_BY_CLS.value}{AnalysisExtension.CSV.value}'
    f1_score_report_path = Path(output_directory_path).parent / f1_score_report_file_name
    f1_score_report_df = pd.DataFrame({MeasurerArgument.F1_SCORE.value: f1_score_by_class_dict.values(),
                                       'inspection_id': range(len(f1_score_by_class_dict.values()))})
    write_dataframe_to_csv(f1_score_report_path, f1_score_report_df)


def main():
    parser = argparse.ArgumentParser()
    configure_arguments(parser)
    args = parser.parse_args()
    if args.output_directory_path is None:
        args.output_directory_path = Path(args.test_dataset_path).parent / f'predictions{AnalysisExtension.CSV.value}'

    test_dataset = QodanaDataset(args.test_dataset_path, args.context_length)
    num_labels = test_dataset[0][DatasetColumnArgument.LABELS.value].shape[0]
    eval_dataloader = DataLoader(test_dataset, batch_size=args.batch_size)
    predictions = np.zeros([len(test_dataset), num_labels], dtype=object)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    model = RobertaForSequenceClassification.from_pretrained(args.model_weights_directory_path,
                                                             num_labels=num_labels).to(device)
    model.eval()

    predictions = get_predictions(eval_dataloader, model, predictions, num_labels, device, args)
    true_labels = torch.tensor(pd.read_csv(args.test_dataset_path).iloc[:, 1:].to_numpy())
    metric = Measurer(args.threshold)
    f1_score_by_class_dict = metric.f1_score_by_classes(torch.tensor(predictions.to_numpy()), true_labels)

    print(f"{MeasurerArgument.F1_SCORE.value}:"
          f"{metric.get_f1_score(torch.tensor(predictions.to_numpy()), true_labels)}",
          f"\n{MeasurerArgument.F1_SCORES_BY_CLS.value}: {f1_score_by_class_dict}")

    write_dataframe_to_csv(args.output_directory_path, predictions)
    if args.save_f1_score:
        save_f1_scores(args.output_directory_path, f1_score_by_class_dict)


if __name__ == '__main__':
    sys.exit(main())
