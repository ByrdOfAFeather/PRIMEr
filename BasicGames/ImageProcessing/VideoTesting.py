"""A file for scanning a video of mario gameplay for jumping
Author: Matthew Byrd
Date created: 8/31/2018
Date last modified: 9/18/2018
"""
from TemplateScanners import VideoScanner


jump_finder = VideoScanner(templates=["GarfieldJumping.png"])
run_finder = VideoScanner(templates=["GarfieldMoving.png"])

jumps = jump_finder.scan_video("Sources/Garfield.avi")
runs = run_finder.scan_video("Sources/Garfield.avi")

jump_run_dict = {}
for jump, run in zip(jumps, runs):
	jump_run_dict[jump]: run

with open("outputjumpstolands.txt", 'w') as f:
	f.write(str(jump_run_dict))
	f.close()

print(f"DIFFERENCE IN LENGTH IS {abs(len(jumps) - len(runs))}")
