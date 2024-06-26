import json
import shutil
from pathlib import Path
from typing import Dict

from stam_annotator.config import ROOT_DIR, AnnotationGroupEnum
from stam_annotator.github_token import GITHUB_TOKEN
from stam_annotator.stam_manager import combine_stams
from stam_annotator.to_stam_convertor.opf_to_stam import opf_to_stam_pipeline
from stam_annotator.to_stam_convertor.utility import (
    convert_yml_file_to_json,
    create_github_repo,
    get_folder_structure,
    make_local_folder,
    replace_parent_folder_name,
    upload_files_to_github_repo,
)
from stam_annotator.utility import (
    clone_github_repo,
    save_annotation_store,
    sort_dict_by_path_strings,
)

SOURCE_ORG = "OpenPecha-Data"
DESTINATION_ORG = "PechaData"


class PechaRepo:
    pecha_id: str
    source_org: str
    destination_org: str

    def __init__(self, id_: str, base_path: Path):
        self.pecha_id = id_
        self.source_org = SOURCE_ORG
        self.destination_org = DESTINATION_ORG
        self.base_path = base_path

    @property
    def pecha_repo_fn(self):
        return self.base_path / f"{self.destination_org}"

    @classmethod
    def from_id(cls, id_: str) -> "PechaRepo":
        cls.base_path = make_local_folder(ROOT_DIR / id_)
        return PechaRepo(id_, cls.base_path)

    def get_pecha_repo(self):
        destination_folder = self.base_path / self.source_org / self.pecha_id
        clone_github_repo(
            self.source_org, self.pecha_id, destination_folder, GITHUB_TOKEN
        )

    def convert_pecha_repo_to_stam(self):
        group_files = get_folder_structure(self.base_path / self.source_org)
        group_files = sort_dict_by_path_strings(group_files)
        make_local_folder(self.base_path / self.destination_org / self.pecha_id)
        for parent_dir, documents in group_files.items():
            new_parent_dir = replace_parent_folder_name(
                parent_dir, self.source_org, self.destination_org
            )
            """store all the converted stams in same dir and then combine"""
            stams_in_dir = []
            """loop through a files and folder in same dir."""
            for doc, tag in documents:
                if tag == "folder":
                    continue
                new_parent_dir.mkdir(parents=True, exist_ok=True)
                if not doc.endswith(".yml"):
                    shutil.copy(parent_dir / doc, new_parent_dir / doc)
                    continue
                if doc.endswith(".yml") and parent_dir.parent.name != "layers":
                    yml_file_path = parent_dir / doc
                    json_output_path = new_parent_dir / doc.replace(".yml", ".json")
                    convert_yml_file_to_json(yml_file_path, json_output_path)
                    continue

                """convert yml files in layers to stam"""
                if parent_dir.parent.name == "layers":
                    base_file_path = next(
                        self.pecha_repo_fn.rglob(f"{parent_dir.name}.txt")
                    )
                    curr_stam = opf_to_stam_pipeline(
                        self.pecha_id,
                        parent_dir / doc,
                        base_file_path,
                        AnnotationGroupEnum.structure_type,
                    )
                    if curr_stam:
                        stams_in_dir.append(curr_stam)
                    continue

            stams_count = len(stams_in_dir)
            if stams_count == 0:
                continue
            combined_stam = (
                stams_in_dir[0] if stams_count == 1 else combine_stams(stams_in_dir)
            )

            save_annotation_store(
                combined_stam,
                new_parent_dir / f"{parent_dir.name}.opf.json",
                self.base_path / self.destination_org / self.pecha_id,
            )
        print(f"[SUCCESS]: Pecha repo {self.pecha_id} converted to stam successfully")

    def upload_pecha_repo(self):
        org_name, repo_name = DESTINATION_ORG, self.pecha_id
        create_github_repo(org_name, repo_name, GITHUB_TOKEN)
        pecha_repo_path = self.base_path / self.destination_org / self.pecha_id
        repo_name = self.pecha_id
        upload_files_to_github_repo(org_name, repo_name, pecha_repo_path, GITHUB_TOKEN)
        print(f"[SUCCESS]: Pecha repo {repo_name} uploaded successfully")


class AlignmentRepo:
    alignment_id: str
    source_org: str
    destination_org: str
    pechas: Dict[str, PechaRepo]

    def __init__(self, id_: str, base_path: Path):
        self.alignment_id = id_
        self.source_org = SOURCE_ORG
        self.destination_org = DESTINATION_ORG
        self.base_path = base_path
        self.pecha_repos: Dict[str, PechaRepo] = {}

    @property
    def alignment_repo_fn(self):
        return (
            self.base_path
            / f"{self.destination_org}"
            / f"{self.alignment_id}"
            / f"{self.alignment_id}.opa"
            / "meta.json"
        )

    @classmethod
    def from_id(cls, id_: str) -> "AlignmentRepo":
        cls.base_path = make_local_folder(ROOT_DIR / id_)
        return AlignmentRepo(id_, cls.base_path)

    def load_pecha_repos(self):
        with open(self.alignment_repo_fn, encoding="utf-8") as file:
            data = json.load(file)
        pechas = data["pechas"]
        for pecha_id in pechas:
            self.pecha_repos[pecha_id] = PechaRepo.from_id(pecha_id)

    def get_alignment_repo(self):
        destination_folder = self.base_path / self.source_org
        clone_github_repo(
            self.source_org, self.alignment_id, destination_folder, GITHUB_TOKEN
        )

    def convert_alignment_repo_to_json(self):
        group_files = get_folder_structure(self.base_path / self.source_org)
        make_local_folder(self.base_path / self.destination_org)
        for parent_dir, documents in group_files.items():
            new_parent_dir = replace_parent_folder_name(
                parent_dir, self.source_org, self.destination_org
            )
            """loop through a files and folder in same dir."""
            for doc, tag in documents:
                if tag == "folder":
                    make_local_folder(new_parent_dir / doc)
                    continue
                if doc.endswith(".yml"):
                    yml_file_path = parent_dir / doc
                    new_file_name = doc.replace(".yml", ".json")
                    """normalize the name of alignment file"""
                    if doc != "meta.yml":
                        new_file_name = "alignment.json"
                    json_file_path = new_parent_dir / new_file_name
                    convert_yml_file_to_json(yml_file_path, json_file_path)
                    continue

                shutil.copy(parent_dir / doc, new_parent_dir / doc)
                continue

    def upload_alignment_repo(self):
        org_name, repo_name = DESTINATION_ORG, self.alignment_id
        create_github_repo(org_name, repo_name, GITHUB_TOKEN)

        alignment_repo_path = self.base_path / self.destination_org
        repo_name = self.alignment_id
        upload_files_to_github_repo(
            org_name, repo_name, alignment_repo_path, GITHUB_TOKEN
        )
        print(f"[SUCCESS]: Alignment repo {repo_name} uploaded successfully")

    def get_aligned_pechas(self):
        self.load_pecha_repos()
        for _, pecha in self.pecha_repos.items():
            pecha.get_pecha_repo()
            pecha.convert_pecha_repo_to_stam()

    def upload_aligned_pechas(self):
        for _, pecha_repo in self.pecha_repos.items():
            pecha_repo.upload_pecha_repo()


if __name__ == "__main__":
    alignment = AlignmentRepo.from_id("AB3CAED2A")
    alignment.get_alignment_repo()
    alignment.convert_alignment_repo_to_json()
    alignment.get_aligned_pechas()

    # alignment.upload_alignment_repo()
    # alignment.upload_aligned_pechas()
