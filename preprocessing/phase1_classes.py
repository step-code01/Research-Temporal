#phase1_classes.py

PHASE1_CLASSES = {
    "directional": {
        "Pushing something from left to right",
        "Pushing something from right to left",
        "Pulling something from left to right",
        "Pulling something from right to left",
        "Moving something up",
        "Moving something down",
        "Moving something towards the camera",
        "Moving something away from the camera",
        "Moving something closer to something",
        "Moving something away from something",
        "Moving something and something closer to each other",
        "Moving something and something away from each other",
        "Moving something and something so they pass each other",
    },

    "state_transition": {
        "Opening something",
        "Closing something",
        "Covering something with something",
        "Uncovering something",
        "Folding something",
        "Unfolding something",
        "Putting something onto something",
        "Taking something out of something",
        "Putting something into something",
        "Pulling something out of something",
        "Attaching something to something",
        "Removing something, revealing something behind",
        "Putting something upright on the table",
        "Laying something on the table on its side",
        "Putting something underneath something",
        "Putting something in front of something",
        "Putting something behind something",
    },

    "terminal_completion": {
        "Pretending to put something onto something",
        "Putting something onto something",
    }
}
