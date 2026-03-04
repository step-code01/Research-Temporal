## Temporal Research: Do models have perception of time like humans?

### I.i. Motivation: 
Have you ever wondered how do models even reason about time? If so, do they 'really' (quote-unqoute) understand it or do they fake it? <br>
 - SOTA video models answer temporal questions well enough that **we've stopped asking if they're actually reading motion** in the video itself. This repo investigates whether they actually are.

<img width="1777" height="595" alt="motivation (2)" src="https://github.com/user-attachments/assets/49998ea5-d351-42ad-b34c-311dc4e00f75" /> <br>

> **Note**: This study is an ongoing, systematic study and part of greater research into **how VideoLLMs represent and reason about time** at a mechanistic level. Not just whether they get the right answer, but **why**, and whether that why is the right reason.

---
### I.ii. The Core Question
When a video model correctly identifies motion direction, does it understand the sequence of frames, or is it pattern-matching on what frames tend to appear together?

These are very different things. One generalizes to causal reasoning. The other is a shortcut that breaks the moment the distribution shifts.

---

### II. Setup
### i. Repo Structure
```
├── v2.0.0_temporal_probing_poc.ipynb                  # Full POC with intervention analysis
├── preprocessing/                                      # Dataset curation scripts
├── embeddings/                                         # Cached layer representations
├── poc_videos/                                         # Curated SSv2 subset
├── results/                                            # Plots and summary report
└── 20bn-something-something-download-package-labels/  # SSv2 label files
```
### ii. Dependencies

```bash
pip install torch transformers decord scikit-learn matplotlib seaborn
```

Data requires SSv2 access. Preprocessing scripts in `/preprocessing` handle curation and class balancing.

---

### III. Phase 1: Proving the Problem Exists
<img width="12" height="12" alt="image" src="https://github.com/user-attachments/assets/7b8bc1f8-22f0-434c-a608-13a340bc65a3" />  **Status: Complete** : March 3, 2026 


 - **Hypothesis:** VideoMAE recognizes *what frames appear together*, not *in what order*, appearance shortcuts over true temporal structure.

 - **What I did:** Trained linear + MLP probes on VideoMAE layer representations (layers 0→11) to classify 6 motion directions across 600 curated SSv2 videos. Then tested the same probes on normal, reversed, and shuffled versions of each video.

 - **The diagnostic is simple:** if the model truly reads order, both interventions should hurt. If it's using shortcuts, only shuffling should.

<div align="center">
 
| Layer | Reversed | Shuffled |
|---|---|---|
| Accuracy drop (layer 9) | **0.8%** | **30.0%** |

</div>

Reversing time barely matters. Destroying frame order hurts **37× more**. Temporal features peak at layer 9 and are linearly separable: the model *has* organized motion information, just not by sequence.

**Conclusions:**
- VideoMAE reads frame-content co-occurrence, not motion sequences
- Temporal features are linearly separable and peak at layer 9, then degrade
- Reversing order (↓0.8%) vs shuffling (↓30%), **37× asymmetry** confirms shortcut behavior

<img width="2382" height="921" alt="intervention_analysis" src="https://github.com/user-attachments/assets/ef13b83c-ba47-45fd-abcf-faa3692ea736" />
<img width="2382" height="921" alt="accuracy_drops" src="https://github.com/user-attachments/assets/ee0afca3-a302-423a-bd2c-c413ecd255cf" />
<img width="2326" height="921" alt="intervention_heatmap" src="https://github.com/user-attachments/assets/d2dc5e91-9eee-448a-bca4-cce76fb80abc" />

> **Shortcut confirmed.** Works on benchmarks. Will break on anything requiring causal or procedural reasoning. <br>
> Detailed summary and individual layer report in the results folder of this repo.
---

### Roadmap

<div align="center">

| Phase | Goal | Status |
|---|---|---|
| II. Ablation across model sizes | Do smaller models take stronger shortcuts? Can we penalize it? | In Progress <img width="12" height="12" alt="image" src="https://github.com/user-attachments/assets/2a66c60a-5c27-477c-94e1-2efacc9f4ab6"/>|
| III. Attention map analysis across architectures | Move from correlation to causation, transformers vs SSMs, O(n²) vs linear attention tradeoffs | Planned |
| IV. Towards temporal grounding | Inducing an internal clock mech inspired from human body clock, positional encoding mods + order-contrastive training | Planned |

</div>
 
> Use attention visualization to move from correlation to causation. What are different architectures *actually attending to* when they classify motion? Does this differ between transformer-based models and State Space Models (SSMs)?
> Also exploring whether the O(n²) computational cost of full temporal attention can be replaced by linear attention mechanisms without losing order-sensitivity and what the tradeoffs are.

---

### Journal & Updates: <br>
3-3-26: Final Outputs & Results of Study obtained (Phase-1: Proving the hypothesized issue exists): (Detailed results in results folder of this repo) 

20-2-26: ~~fixing OOM errors while embedding extraction on "MCG-NJU/videomae-base-finetuned-kinetics"~~ Issue closed (Look at Issues closed tab for more details)
<img width="2736" height="682" alt="Screenshot 2026-02-20 154101" src="https://github.com/user-attachments/assets/c433fca8-f450-438a-ae06-46d417897b4f" />

8-2-26: succesfully debugged and wrote pipeline for dataset curation, creating a subset of ssv2 dataset with balanced classes. 
Issue was not normalizing before string matching in json, so it wasn't reading any videos.

---

## Limitations

- 600 videos is sufficient for a pilot but not for statistically robust claims across all SSv2 categories
- Some motion classes may look similar in forward and reverse, this could partially explain the low reverse-drop and warrants testing with more directionally asymmetric classes (already planned in phase-2).
- Results are specific to VideoMAE-base-kinetics; generalization to larger or more recent video models is an open question.

---
Courtesy of: 
 - Shaurya Gupta, B.E. Sophomore, Computer Science & Engineering Deptt, Thapar Institute of Engineering & Technology, Patiala. <br>
© Jan-March 2026. 

If you find this study useful, do let us know!
