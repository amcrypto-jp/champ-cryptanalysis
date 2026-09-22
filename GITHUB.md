# Publishing this release on GitHub

Use the **contents of `CHAMP-Review-v1.0.1/` as the repository root**. That places
`README.md`, `REPORT.md`, `CITATION.cff`, `code/`, `data/` and `evidence/` directly
in the repository. Include the hidden `.gitignore` and `.gitattributes` files.
Keep `LICENSE`, `LICENSING.md` and `LICENSES/` in the repository: the code is
licensed under MIT, and the report and original results under CC BY 4.0. The
[license scope](LICENSING.md) identifies the covered files and third-party
exceptions.
The public package is the intended publication boundary; the parent CHAMP
workspace contains separate source documents and working review material.

A suitable repository name is `champ-cryptanalysis`. Suggested description:

> Technical review of the CHAMP hash specification, with reproducible experiments and reduced-parameter collision certificates.

Create an empty public repository under the intended account, then commit and
push this package's contents. It already supplies the README, license notices, citation metadata
and Git settings, so a repository template is unnecessary. GitHub documents the
[repository creation steps](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository).

Before publishing, run from the repository root:

```sh
python3 verify_package.py
python3 run.py
```

The quick run checks the mathematical model and saved certificates without the
original submission files. See [REPRODUCING.md](REPRODUCING.md) for full coverage
and optional C/KAT and SageMath checks. Generated run directories are ignored by
Git; the recorded `evidence/` files remain tracked. The line-ending settings
preserve the bytes used by the file checksum manifest.

Publish a release with tag **`v1.0.1`** and title **`CHAMP technical assessment
v1.0.1`**, attaching `CHAMP-Review-v1.0.1.zip`, its `.sha256` sidecar and
`REPORT.pdf`. These archives are release assets; the repository itself should
contain the extracted files so readers can browse the code and cite the report.
Use [ANNOUNCEMENT.md](ANNOUNCEMENT.md) as the release description. GitHub's
[release documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
explains tags and asset attachments.

The Markdown report uses GitHub's documented
[`$...$` and `$$...$$` math syntax](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/writing-mathematical-expressions).
The HTML file is intended to be downloaded and opened locally; linking to it in
the repository does not itself configure a website. The preferred citation is
the technical report, using GitHub's
[CITATION.cff support](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files).

Once a repository URL or DOI is assigned, it can be added to `CITATION.cff` and
`references.bib`. If distributed files are edited, regenerate `SHA256SUMS` and
the release archive together; an old manifest intentionally fails after changes.
