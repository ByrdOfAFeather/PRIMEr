"""Code for editing a video
Author: Matthew Byrd
Date created: 9/28/2018
Date last modified: 9/28/2018
"""

from TemplateScannersThreaded import VideoScanner
from threading import Thread
from moviepy.editor import CompositeVideoClip, VideoFileClip


def get_timestamps():
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
	return jumps


timestamps = get_timestamps()
org_video = VideoFileClip("Sources/mmlevel1.mp4")
org_video = org_video.set_start(t=str(timestamps[0]))
org_video.write_videofile("test.mp4")