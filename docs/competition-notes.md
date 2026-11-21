# TimeNet Hackathon: competition notes

Notes on what the hackathon asks for, taken while planning. The status column says where this project stands against each item.

## 1. Challenge and submission requirements

- **Challenge:** TimeNet Online Hackathon (https://challenge.timenet.ai/).
- **Objective:** build a temporal AI application, onboard a new domain dataset into TimeNet's TimeF format, and fine-tune or train an open temporal foundation model such as OpenTSLM.

| # | Requirement | Status |
|---|---|---|
| 1 | Link to an opened or merged pull request on `OpenTSLM/TimeNet` adding the dataset connector | **Not opened.** Draft text in [pr/hydraulic.md](pr/hydraulic.md). The connector does not yet use TimeNet's base class or TimeF format |
| 2 | Public GitHub repository with the code, reproduction steps and a licence | This repository. MIT licence |
| 3 | Deployed public dashboard | **Not deployed yet.** A GitHub Pages workflow publishes it once Pages is enabled: [deployment.md](deployment.md) |
| 4 | Two to three minute video with burned-in captions | **Not recorded.** Script in [video-script.md](video-script.md) |
| 5 | `MODEL_CARD.md` | Written, for the LightGBM engine. There is no fine-tuned model to describe yet |
| 6 | Public posts on X and LinkedIn | **Drafts only**, in `posts/` |
| 7 | The official submission form (tally.so/r/J1qbyK) | Not known from this repository |

## 2. Judging criteria, as understood when planning

- **Technical rigour:** correct time-series handling, leak-free grouped evaluation, reproducible runs.
- **Novelty:** checking the numbers in a model's explanation against the signal, rather than trusting them.
- **Usability and presentation:** an interactive dashboard with clear visualisations.
- **Open-source contribution:** a connector that meets TimeNet's standards and passes its CI.

## 3. Datasets considered

| Round | Dataset | Licence | Status |
|---|---|---|---|
| 1 | UCI hydraulic test rig (#447) | CC BY 4.0 | Used. All results are on it |
| 2 | HUST bearings (Mendeley Data) | CC BY 4.0 | Connector and physics written, running on **synthetic stand-in data** only |
| 3 | CARE wind turbines | CC BY-SA 4.0 | Connector and physics written, running on **synthetic stand-in data** only. ShareAlike compatibility would need checking before using the real data. No fallback dataset has been prepared |

Whether #447 was already claimed in TimeNet's open or closed pull requests was checked once while planning, and should be checked again before opening the pull request.
