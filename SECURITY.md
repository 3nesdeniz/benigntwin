# Security policy

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub: open the **Security** tab of this repository and choose **Report a vulnerability**. Do not open a public issue for anything that could expose credentials, private evaluation inputs or endpoint responses, or that leads to code execution.

A useful report contains the affected version and command, a minimal reproduction that uses synthetic data, what you expected and what happened, and the impact you see. Do not include live customer data or working credentials.

Reports are acknowledged as soon as practical and fixed before they are disclosed.

## Supported versions

Security fixes are made for the latest 1.x release.

## What the tool does with your data and code

BenignTwin is a local command-line tool. Its trust boundaries are:

| Action | What happens | What to keep in mind |
| --- | --- | --- |
| `--detector python:file.py:function` | the file is imported and run | only use code you trust |
| `--detector https://...` | every input text is sent to that endpoint | the endpoint and its logs must be approved for the data |
| `--detector hf:owner/model` | the model is downloaded and run locally | custom code from model repositories is never run; only `safetensors` weights are loaded unless you pass `--hf-allow-pickle` |
| `--dataset hf:owner/name` | files are downloaded from the Hugging Face Hub into a local cache | `HF_TOKEN` is sent only to the Hub |
| reports | written to the paths you choose | they contain ids and counts, never input text |

Detectors receive the input text and nothing else: no labels and no metadata.

Tokens are read from environment variables and are not written to reports. Values of extra HTTP headers and body fields are not written to reports either; avoid putting secrets on the command line, where the shell history keeps them.
