import argparse
import json
import zipfile

from pathlib import Path

import tqdm


def parse_args() -> tuple[Path, Path, Path]:
    parser = argparse.ArgumentParser(
        prog='Organic Summarizer',
        description='Given a git repository and a zip file containing organic json files, Organic Summarizer '
                    'will produce a json file which summarizes which smells were added and removed in each commit.')
    parser.add_argument('commit_list', help="path to a txt containing a list of commits for the repository"
                                            "(can be generated with 'git log --format='%%H' --reverse > FILENAME.txt')")
    parser.add_argument('input_zip', help="path to zip file containing organic json files")
    parser.add_argument('output_path', help="path for the output file (it will be a json file)")
    args = parser.parse_args()

    commit_list = Path(args.commit_list)
    input_file = Path(args.input_zip)
    if not commit_list.is_file() or not input_file.is_file():
        raise ValueError("The commit list and the input zip must be valid files.")
    output_file = Path(args.output_path)
    if not output_file.parent.is_dir():
        output_file.parent.mkdir(parents=True, exist_ok=True)

    return commit_list, input_file, output_file


def get_commit_organic_data(chash: str, zip_file: zipfile.ZipFile) -> dict:
    with zip_file.open(chash + ".json") as json_file:
        data = json.load(json_file)

    return data


def summarize_organic(data: dict) -> dict:
    result = {
        "num_class_lvl": 0,
        "num_method_lvl": 0,
        "class_smells": {
            "GodClass": 0,
            "ClassDataShouldBePrivate": 0,
            "ComplexClass": 0,
            "LazyClass": 0,
            "RefusedBequest": 0,
            "SpaghettiCode": 0,
            "SpeculativeGenerality": 0,
            "DataClass": 0,
            "BrainClass": 0
        },
        "method_smells": {
            "FeatureEnvy": 0,
            "LongMethod": 0,
            "LongParameterList": 0,
            "MessageChain": 0,
            "DispersedCoupling": 0,
            "IntensiveCoupling": 0,
            "ShotgunSurgery": 0,
            "BrainMethod": 0,
            "InflatedException": 0
        }
    }

    for klass in data:
        for smell in klass['smells']:
            result['num_class_lvl'] += 1
            result['class_smells'][smell['name']] += 1
        for method in klass['methods']:
            for smell in method['smells']:
                result['num_method_lvl'] += 1
                result['method_smells'][smell['name']] += 1

    return result


def compare_commits(previous_data: dict, current_data: dict) -> dict:
    result = dict()

    result['num_class_lvl'] = current_data['num_class_lvl']
    result['diff_class_lvl'] = 0
    result['num_method_lvl'] = current_data['num_method_lvl']
    result['diff_method_lvl'] = 0
    result['class_diff'] = {}
    result['method_diff'] = {}

    if previous_data:
        result['diff_class_lvl'] = current_data['num_class_lvl'] - previous_data['num_class_lvl']
        result['diff_method_lvl'] = current_data['num_method_lvl'] - previous_data['num_method_lvl']

        for key in current_data['class_smells'].keys():
            result['class_diff'][key] = current_data['class_smells'][key] - previous_data['class_smells'][key]
        for key in current_data['method_smells'].keys():
            result['method_diff'][key] = current_data['method_smells'][key] - previous_data['method_smells'][key]
    else:
        result['class_diff'] = {
            "GodClass": 0,
            "ClassDataShouldBePrivate": 0,
            "ComplexClass": 0,
            "LazyClass": 0,
            "RefusedBequest": 0,
            "SpaghettiCode": 0,
            "SpeculativeGenerality": 0,
            "DataClass": 0,
            "BrainClass": 0
        }
        result['method_diff'] = {
            "FeatureEnvy": 0,
            "LongMethod": 0,
            "LongParameterList": 0,
            "MessageChain": 0,
            "DispersedCoupling": 0,
            "IntensiveCoupling": 0,
            "ShotgunSurgery": 0,
            "BrainMethod": 0,
            "InflatedException": 0
        }

    return result


def summarize_commits(git_commits: list[str], zip_commits: list[str], zip_file: zipfile.ZipFile) -> dict:
    result_object = dict()
    current_commit_data = None

    for commit in tqdm.tqdm(git_commits):
        if (commit + ".json") in zip_commits:
            current_commit = commit
        else:
            continue

        previous_commit_data = current_commit_data
        current_commit_data = summarize_organic(get_commit_organic_data(current_commit, zip_file))

        result_object[current_commit] = compare_commits(previous_commit_data, current_commit_data)

    return result_object


def process_files(commit_list: Path, input_file: Path) -> dict:
    with commit_list.open() as file:
        commits = file.readlines()
    commits = [x.rstrip() for x in commits]
    organic_zip = zipfile.ZipFile(input_file)
    collected_commits = organic_zip.namelist()

    return summarize_commits(commits, collected_commits, organic_zip)


def run():
    commit_list, input_file, output_file = parse_args()
    print("Processing commits...")
    output = process_files(commit_list, input_file)
    with output_file.open("w") as jsonfile:
        json.dump(output, jsonfile)
    print("Saving " + str(output_file) + "...")


if __name__ == "__main__":
    run()