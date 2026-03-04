### Temporal Research: Do models have perception of time like humans?

Have you ever wondered how do models even reason about time? If so, do they 'really' (quote-unqoute) understand it or do they fake it?
Is it a bag of frames, sequential order? Who knows!

SOTA closed & open source models have started answering so good that we take everything for granted now, that we've stopped wondering whether they're actually **looking** at the motion in the video at the first place. 

I'm sort out to understand and do a exhaustive study on everything's out there on VideoLLMs and trying to understand how exactly do VideoLLMs understand time fundamentally and even **IF** they understand at first place. 
This research is being part of a greater project that uses it. 

Goals to achieve:
1. Explore all different parameter models sizes keeping model constant to understand whether shorter models take shortcuts? If true, penalizing them to get rid of bad behaviour.
2. Ablation study with varying models, parameter sizes and using attention maps to understand what is it currently doing/seeing (Causation vs correlation study).
3. Vary models and understand whether different architectures perceive time differently, and whether cross (inter) connection between these bag of frames which too expensive computationally by traditional attention methods being O(n^2) could be solved by linear attention ones (Space State Models) and what are the drawbacks/tradeoffs for that, and rectifying that.
4. Some sort of internal clock mechanism like human body does.

Conclusions:
1. My preliminary study concluded that "MCG-NJU/videomae-base-finetuned-kinetics" doesn't actually see frames but does guesswork since playing the the video in reverse doesn't hurt the accuracy. 
Suprisingly, shuffling the frames hurts more than reversing the frames.
2. More detailed results in the results folder below.
<img width="2382" height="921" alt="intervention_analysis" src="https://github.com/user-attachments/assets/ef13b83c-ba47-45fd-abcf-faa3692ea736" />
<img width="2382" height="921" alt="accuracy_drops" src="https://github.com/user-attachments/assets/ee0afca3-a302-423a-bd2c-c413ecd255cf" />
<img width="2326" height="921" alt="intervention_heatmap" src="https://github.com/user-attachments/assets/d2dc5e91-9eee-448a-bca4-cce76fb80abc" />


Journal updates: <br>
3-3-26: Final Outputs & Results of Study obtained (Phase-1: Proving the hypothesized issue exists): (Detailed results in results folder of this repo) 

20-2-26: fixing OOM errors while embedding extraction on "MCG-NJU/videomae-base-finetuned-kinetics"
<img width="2736" height="682" alt="Screenshot 2026-02-20 154101" src="https://github.com/user-attachments/assets/c433fca8-f450-438a-ae06-46d417897b4f" />

8-2-26: succesfully debugged and wrote pipeline for dataset curation, creating a subset of ssv2 dataset with balanced classes. 
Issue was not normalizing before string matching in json, so it wasn't reading any videos.

Courtesy of: 
 - Shaurya Gupta, B.E. Sophomore, Computer Science & Engineering Deptt. <br>

If you find this research useful, do let us know!
