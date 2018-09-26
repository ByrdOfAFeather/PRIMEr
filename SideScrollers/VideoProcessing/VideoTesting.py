"""A file for scanning a video of mario gameplay for jumping
Author: Matthew Byrd
Date created: 8/31/2018
Date last modified: 9/25/2018
"""
from TemplateScannersThreaded import VideoScanner
from threading import Thread

# No Threading is 18 minutes [Garfield]
# Time to beat 6 minutes [Garfield]

# No Threading is unknown
# Time to beat is 1 minute [Mega Man Level 1]


class JumpThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.output = []

	def run(self):
		jump_finder = VideoScanner(templates=["MegaManJumping.png"])

		jump_finder = jump_finder.thread_scanners("Sources/mmlevel1.mp4")
		for threads in jump_finder:
			threads.join()

		for jump_times in jump_finder:
			self.output.extend(jump_times.output)


class RunThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.output = []

	def run(self):
		run_finder = VideoScanner(templates=["MegaManMoving.png"])

		run_finder = run_finder.thread_scanners("Sources/mmlevel1.mp4")
		for threads in run_finder:
			threads.join()

		for run_times in run_finder:
			print(run_times)
			self.output.extend(run_times.output)


tester1 = JumpThread()
tester2 = RunThread()

print("Running Jumper Thread")
tester1.start()
print("Running Runner Thread")
tester2.start()

tester1.join()
tester2.join()

jumps = [f"j{j}" for j in tester1.output]
runs = [f"r{r}" for r in tester2.output]
jumps.extend(runs)
jumps.sort(key=lambda x: x.strip("j").strip("r"))

with open("outputjumpstolands.txt", 'w') as f:
	f.write(str(jumps))
	f.close()
